import os
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from dotenv import load_dotenv
import logging
from typing import List, Dict, Any, Set # For type hints, enhancing readability

# --- Logging Configuration ---
# Configure logging to display messages with timestamps, log levels, and messages.
# INFO level messages and above will be shown.
# You can change to logging.DEBUG for more verbose output during development.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Use a logger instance for better control

# --- Environment Variable Loading ---
# Load environment variables from the .env file.
# This allows sensitive information (like API tokens) and configurations
# to be kept separate from the source code.
load_dotenv()
logger.info("Environment variables loaded from .env file.")

# --- Configuration from .env ---
# Retrieve configuration values from environment variables.
# Provide default values where appropriate to prevent crashes if variables are missing.
TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '') # Chat ID can be a string (e.g., for negative group IDs)

DAANGN_BASE_SEARCH_URL: str = "https://www.daangn.com/search/"
DAANGN_REGION_FILTER: str = os.getenv('DAANGN_REGION_FILTER', 'any').strip() # e.g., 'seoul-gangnam-gu' or 'any'

# Process keywords: split by comma, clean whitespace, convert to lowercase, remove empty strings.
KEYWORDS_RAW: str = os.getenv('KEYWORDS', '').strip()
KEYWORDS: List[str] = [k.strip().lower() for k in KEYWORDS_RAW.split(',') if k.strip()]

# Convert price limits to integers, with robust error handling.
try:
    MIN_PRICE: int = int(os.getenv('MIN_PRICE', 0))
    if MIN_PRICE < 0:
        logger.warning(f"MIN_PRICE was set to a negative value ({MIN_PRICE}). Resetting to 0.")
        MIN_PRICE = 0
except ValueError:
    logger.error("Invalid value for MIN_PRICE in .env. Defaulting to 0.")
    MIN_PRICE = 0

try:
    MAX_PRICE: int = int(os.getenv('MAX_PRICE', 999999999))
    if MAX_PRICE < MIN_PRICE:
        logger.warning(f"MAX_PRICE ({MAX_PRICE}) is less than MIN_PRICE ({MIN_PRICE}). Adjusting MAX_PRICE to MIN_PRICE.")
        MAX_PRICE = MIN_PRICE
except ValueError:
    logger.error("Invalid value for MAX_PRICE in .env. Defaulting to 999999999.")
    MAX_PRICE = 999999999

# Convert polling interval to integer.
try:
    POLLING_INTERVAL_SECONDS: int = int(os.getenv('POLLING_INTERVAL_SECONDS', 300)) # Default 5 minutes
    if POLLING_INTERVAL_SECONDS < 60:
        logger.warning(f"POLLING_INTERVAL_SECONDS was set too low ({POLLING_INTERVAL_SECONDS}). Minimum is 60 seconds. Resetting to 60.")
        POLLING_INTERVAL_SECONDS = 60
except ValueError:
    logger.error("Invalid value for POLLING_INTERVAL_SECONDS in .env. Defaulting to 300 seconds.")
    POLLING_INTERVAL_SECONDS = 300

# --- Telegram Bot Initialization ---
# Ensure essential Telegram configuration is present.
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN is not set. Please check your .env file.")
    exit(1)
if not TELEGRAM_CHAT_ID:
    logger.error("TELEGRAM_CHAT_ID is not set. Please check your .env file. Without it, messages cannot be sent.")
    # We allow the bot to start for scraping, but warn that messages won't work.
    # Optionally, you could exit here if messaging is strictly required for startup.
    # For this bot, if we can't notify, there's no point in running.
    exit(1)

try:
    bot: Bot = Bot(token=TELEGRAM_BOT_TOKEN)
    logger.info("Telegram bot object initialized successfully. Ready to send messages.")
except Exception as e:
    logger.critical(f"Failed to initialize Telegram bot with the provided token: {e}")
    logger.critical("Please ensure TELEGRAM_BOT_TOKEN is correct and has network access.")
    exit(1)

# --- Global State for tracking notified items ---
# A set is used for efficient O(1) average time complexity lookups.
# Storing item IDs to prevent sending duplicate notifications for the same item.
notified_item_ids: Set[str] = set()
logger.debug("Initialized global set for notified item IDs.")

# --- Helper Functions ---
def clean_price(price_str: str) -> int:
    """
    Removes non-numeric characters from a price string and converts it to an integer.
    Handles common formats like '10,000원'.
    """
    if not isinstance(price_str, str) or not price_str:
        return 0
    # Remove '원', commas, and leading/trailing whitespace
    cleaned = price_str.replace('원', '').replace(',', '').strip()
    try:
        return int(cleaned)
    except ValueError:
        logger.warning(f"Could not parse price string '{price_str}'. Returning 0.")
        return 0

def send_telegram_message(message: str) -> None:
    """
    Sends a formatted message to the configured Telegram chat ID.
    Uses HTML parse mode for rich text formatting.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Telegram bot token or chat ID is missing. Cannot send message.")
        return

    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML', disable_web_page_preview=False)
        logger.info(f"Successfully sent message to Telegram chat {TELEGRAM_CHAT_ID}.")
        logger.debug(f"Message content: {message[:100]}...") # Log first 100 chars of message
    except Exception as e:
        logger.error(f"Failed to send Telegram message to chat {TELEGRAM_CHAT_ID}: {e}")
        logger.debug(f"Failed message content: {message[:100]}...")

def scrape_daangn_items() -> List[Dict[str, Any]]:
    """
    Scrapes Daangn Market for items matching the configured keywords, region, and price filters.
    Returns a list of dictionaries, each representing a found item.
    """
    all_found_items: List[Dict[str, Any]] = []
    
    # Define standard headers to mimic a web browser request, reducing chances of being blocked.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Iterate through each keyword to perform separate searches.
    if not KEYWORDS:
        logger.warning("No keywords configured. Skipping Daangn scraping.")
        return []

    for keyword in KEYWORDS:
        encoded_keyword = requests.utils.quote(keyword) # URL-encode the keyword
        search_url = f"{DAANGN_BASE_SEARCH_URL}{encoded_keyword}"
        
        # Append region filter if specified and not 'any'
        if DAANGN_REGION_FILTER and DAANGN_REGION_FILTER != 'any':
            search_url += f"?region={DAANGN_REGION_FILTER}"

        logger.info(f"Attempting to scrape Daangn Market for keyword '{keyword}' at URL: {search_url}")

        try:
            # Send HTTP GET request with a timeout to prevent indefinite hangs.
            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            logger.debug(f"Successfully fetched URL: {search_url}")
        except requests.exceptions.Timeout:
            logger.error(f"Request timed out after 15 seconds for URL: {search_url}")
            continue
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred for URL {search_url}: {http_err} (Status: {response.status_code})")
            continue
        except requests.exceptions.RequestException as req_err:
            logger.error(f"An error occurred during the request for URL {search_url}: {req_err}")
            continue
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching {search_url}: {e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all article elements that represent a flea market item.
        # This class name is crucial for identifying individual listings.
        items = soup.find_all('article', class_='flea-market-article')
        if not items:
            logger.info(f"No articles found for keyword '{keyword}' on Daangn search page '{search_url}'.")
            continue # Move to the next keyword if no items are found for this one

        logger.debug(f"Found {len(items)} potential articles for keyword '{keyword}'.")

        for i, item in enumerate(items):
            try:
                # --- Extract Link and Item ID ---
                link_tag = item.find('a', class_='flea-market-article-link')
                if not link_tag or 'href' not in link_tag.attrs:
                    logger.debug(f"Item {i} for '{keyword}': No valid link tag found. Skipping.")
                    continue
                
                item_link = "https://www.daangn.com" + link_tag['href']
                item_id = item_link.split('/')[-1].split('?')[0] # Ensure only the item ID part, remove query params
                
                if not item_id:
                    logger.debug(f"Item {i} for '{keyword}': Could not extract item ID from link '{item_link}'. Skipping.")
                    continue
                
                # We check for `notified_item_ids` later, after all necessary info is extracted.
                # This ensures we log if other filters caused a skip, even if already notified.

                # --- Extract Title ---
                title_tag = item.find('h2', class_='article-title')
                title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

                # --- Extract Price ---
                price_tag = item.find('p', class_='article-price')
                price_str = price_tag.get_text(strip=True) if price_tag else "0원"
                price = clean_price(price_str)

                # --- Extract Region (neighborhood) ---
                region_tag = item.find('p', class_='article-region-name')
                region_name = region_tag.get_text(strip=True) if region_tag else "지역 정보 없음"
                
                # --- Apply Price Filter ---
                if not (MIN_PRICE <= price <= MAX_PRICE):
                    logger.debug(f"Skipping '{title}' (ID: {item_id}) due to price filter: {price_str} (Min:{MIN_PRICE:,}원, Max:{MAX_PRICE:,}원).")
                    continue

                # Add the item to our list if it passes all checks (except notification check).
                all_found_items.append({
                    'id': item_id,
                    'title': title,
                    'price': price,
                    'price_str': price_str,
                    'link': item_link,
                    'region': region_name
                })
                logger.debug(f"Successfully parsed item '{title}' (ID: {item_id}, Price: {price_str}, Region: {region_name}).")
                
            except AttributeError as ae:
                # Specific error for when .find() returns None and .get_text() or similar is called.
                logger.warning(f"Attribute error while parsing an item for keyword '{keyword}': {ae}. "
                               f"This might indicate a missing HTML element. Item HTML fragment: {item.prettify()[:500]}...")
            except Exception as e:
                # General exception for other unexpected parsing issues.
                logger.error(f"An unexpected error occurred while parsing an item for keyword '{keyword}': {e}. "
                             f"Item HTML fragment: {item.prettify()[:500]}...")
                continue
    
    logger.info(f"Finished scraping all keywords. Total unique potential items found: {len(all_found_items)}.")
    return all_found_items

def main() -> None:
    """
    Main loop to continuously monitor Daangn Market and send Telegram notifications
    for new items matching the criteria.
    """
    logger.info("--- Carrot-Blink: 🥕초광속 줍줍 Telegram Bot⚡️ started. ---")
    logger.info(f"Monitoring keywords: {', '.join(KEYWORDS) if KEYWORDS else '없음'}")
    logger.info(f"Price range: {MIN_PRICE:,}원 ~ {MAX_PRICE:,}원")
    logger.info(f"Region filter: {DAANGN_REGION_FILTER if DAANGN_REGION_FILTER != 'any' else '전체 지역'}")
    logger.info(f"Polling every {POLLING_INTERVAL_SECONDS} seconds.")
    
    # Send a startup message to Telegram to confirm bot is operational.
    startup_message = (
        "🥕<b>Carrot-Blink 봇이 시작되었습니다!</b>⚡️\n"
        f"모니터링 키워드: <b>{', '.join(KEYWORDS) if KEYWORDS else '없음'}</b>\n"
        f"가격 범위: <b>{MIN_PRICE:,}원 ~ {MAX_PRICE:,}원</b>\n"
        f"지역 필터: <b>{DAANGN_REGION_FILTER if DAANGN_REGION_FILTER != 'any' else '전체 지역'}</b>\n"
        f"매 <b>{POLLING_INTERVAL_SECONDS}초</b>마다 새로운 매물을 확인합니다."
    )
    send_telegram_message(startup_message)

    # Main infinite loop for continuous monitoring.
    while True:
        logger.info("\n--- Starting a new round of item checks ---")
        current_new_items: List[Dict[str, Any]] = [] # Items found in the current poll that haven't been notified yet.
        
        try:
            found_items = scrape_daangn_items()
            logger.info(f"Scraping completed. {len(found_items)} items passed initial filters for this round.")
            
            # Filter out already notified items and add new ones to `notified_item_ids`.
            for item in found_items:
                if item['id'] not in notified_item_ids:
                    current_new_items.append(item)
                    notified_item_ids.add(item['id']) # Add to set *before* sending, to prevent re-notification even if sending fails temporarily.
            
            if current_new_items:
                logger.info(f"Found {len(current_new_items)} truly new item(s)! Sending notifications...")
                for item in current_new_items:
                    message = (
                        "🚨 <b>새로운 꿀매물 발견!</b> 🚨\n"
                        f"<b>[제목]</b> {item['title']}\n"
                        f"<b>[가격]</b> {item['price_str']}\n"
                        f"<b>[지역]</b> {item['region']}\n"
                        f"<b>[링크]</b> <a href='{item['link']}'>매물 보러가기</a>"
                    )
                    send_telegram_message(message)
                    time.sleep(1) # Small delay to avoid hitting Telegram API rate limits if many items are found.
            else:
                logger.info("No new items found matching criteria in this round.")
        
        except KeyboardInterrupt:
            logger.info("Carrot-Blink bot manually stopped. Exiting.")
            send_telegram_message("🥕<b>Carrot-Blink 봇이 종료되었습니다.</b>⚡️")
            break # Exit the loop on Ctrl+C
        except Exception as e:
            # Catch any unexpected errors in the main loop to keep the bot running.
            logger.critical(f"An unexpected error occurred in the main monitoring loop: {e}", exc_info=True)
            send_telegram_message(f"⚠️ <b>Carrot-Blink 봇 오류 발생!</b> ⚠️\n"
                                  f"봇 실행 중 예기치 않은 오류가 발생했습니다: {e}\n"
                                  "다음 확인 주기에 다시 시도합니다.")
        
        logger.info(f"Waiting for {POLLING_INTERVAL_SECONDS} seconds before the next check...")
        time.sleep(POLLING_INTERVAL_SECONDS)

if __name__ == '__main__':
    main()
