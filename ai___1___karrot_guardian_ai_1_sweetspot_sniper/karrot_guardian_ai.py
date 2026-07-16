import os
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import json
import logging
import sys
from typing import List, Dict, Tuple, Any

from telegram import Bot
from telegram.error import TelegramError 
from dotenv import load_dotenv

# --- 1. Logging Setup ---
# Configure logging to display info level messages and above, with a clear timestamp and log level.
# The logging format includes time, log level, and the message for easy tracing.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# For more detailed debugging, uncomment the line below to see DEBUG level messages:
# logging.getLogger().setLevel(logging.DEBUG) 

# --- 2. Environment Variables Loading ---
# Load environment variables from a .env file. This practice helps keep sensitive information 
# and configuration parameters separate from the main codebase, enhancing security and flexibility.
try:
    load_dotenv()
    logging.info("✅ .env 파일에서 환경 변수를 성공적으로 로드했습니다.")
except Exception as e:
    logging.error(f"❌ .env 파일 로드 중 오류 발생: {e}. 환경 변수가 제대로 설정되지 않을 수 있습니다.")
    sys.exit(1) # Consider this critical as config will likely fail

# --- 3. Configuration ---
# Telegram Bot Token: Essential for authenticating with the Telegram Bot API.
TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
# Telegram Chat ID: The specific chat (user or group) where notifications will be sent.
TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '')

# Search keywords for Karrot Market. Keywords are split by comma, whitespace is removed, 
# and empty strings are filtered out to ensure only valid keywords are used.
SEARCH_KEYWORDS: List[str] = [kw.strip() for kw in os.getenv('SEARCH_KEYWORDS', '아이패드, 맥북, 의자, 무료나눔').split(',') if kw.strip()]

# Price threshold in KRW. Items priced at or below this value are considered 'sweet-spot' deals.
# Default is 1000 KRW, roughly equivalent to 1 USD, making it a "Sweet-Spot Sniper".
# It's explicitly mentioned as 1$ Sweet-Spot Sniper in the README, so 1000 KRW is a good default.
try:
    PRICE_THRESHOLD_KRW: int = int(os.getenv('PRICE_THRESHOLD_KRW', '1000'))
    if PRICE_THRESHOLD_KRW < 0:
        logging.warning(f"⚠️ 'PRICE_THRESHOLD_KRW' 환경 변수가 음수({PRICE_THRESHOLD_KRW})로 설정되었습니다. 0으로 조정합니다.")
        PRICE_THRESHOLD_KRW = 0
except ValueError:
    logging.error("❌ 'PRICE_THRESHOLD_KRW' 환경 변수 값이 유효한 숫자가 아닙니다. 기본값 1000으로 설정합니다.")
    PRICE_THRESHOLD_KRW = 1000

# Interval in seconds between each full scraping cycle. A longer interval helps avoid 
# overwhelming the server, reduces the risk of IP bans, and conserves resources.
try:
    SCRAPE_INTERVAL_SECONDS: int = int(os.getenv('SCRAPE_INTERVAL_SECONDS', '300')) # Default: 300 seconds (5 minutes)
    if SCRAPE_INTERVAL_SECONDS < 60: # Enforce a minimum interval to be polite
        logging.warning(f"⚠️ 'SCRAPE_INTERVAL_SECONDS' 환경 변수가 너무 짧게({SCRAPE_INTERVAL_SECONDS}초) 설정되었습니다. 최소 60초로 조정합니다.")
        SCRAPE_INTERVAL_SECONDS = 60
except ValueError:
    logging.error("❌ 'SCRAPE_INTERVAL_SECONDS' 환경 변수 값이 유효한 숫자가 아닙니다. 기본값 300초로 설정합니다.")
    SCRAPE_INTERVAL_SECONDS = 300

# --- 4. Global State for Tracking Found Items ---
# File path to store previously found items. This prevents sending duplicate notifications 
# and allows the bot to resume its state across restarts.
FOUND_ITEMS_FILE: str = 'found_items.json'
# Cache dictionary to hold found items: {'item_id': {'title': ..., 'price': ..., 'link': ..., 'scraped_at': ...}}
# Using a global dictionary for simplicity in this script, managed by dedicated load/save functions.
found_items_cache: Dict[str, Dict[str, Any]] = {} 

def load_found_items() -> None:
    """
    Loads previously found items from a JSON file into the global cache.
    This function is designed to be robust against common file-related errors 
    such as file not found or malformed JSON, starting with an empty cache if issues occur.
    """
    global found_items_cache
    if os.path.exists(FOUND_ITEMS_FILE):
        try:
            with open(FOUND_ITEMS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure the loaded data is a list before converting to a dictionary.
                if isinstance(data, list):
                    # Reconstruct cache with item 'id' as keys for efficient lookup and to mirror the item structure.
                    found_items_cache = {item['id']: item for item in data if 'id' in item}
                    logging.info(f"💾 Cache loaded successfully: Found {len(found_items_cache)} items from '{FOUND_ITEMS_FILE}'.")
                else:
                    logging.error(f"❌ '{FOUND_ITEMS_FILE}' 파일의 형식이 올바르지 않습니다 (JSON 배열이 아님). 빈 캐시로 시작합니다.")
                    found_items_cache = {}
        except FileNotFoundError:
            # This specific check might seem redundant due to os.path.exists, but adds clarity if file vanishes mid-op.
            logging.warning(f"⚠️ '{FOUND_ITEMS_FILE}' not found during load attempt. Starting with an empty cache.")
            found_items_cache = {}
        except json.JSONDecodeError as e:
            logging.error(f"❌ Error decoding JSON from '{FOUND_ITEMS_FILE}': {e}. Starting with an empty cache to prevent further issues.")
            found_items_cache = {} # Reset cache if file is corrupted
        except IOError as e:
            logging.error(f"❌ IO error while loading '{FOUND_ITEMS_FILE}': {e}. Starting with an empty cache.")
            found_items_cache = {}
        except Exception as e:
            logging.error(f"❌ An unexpected error occurred while loading '{FOUND_ITEMS_FILE}': {e}. Starting with an empty cache.", exc_info=True)
            found_items_cache = {}
    else:
        logging.info(f"✨ No existing cache file ('{FOUND_ITEMS_FILE}') found. Starting with an empty cache for new items.")

def save_found_items() -> None:
    """
    Saves the current state of found items from the global cache to a JSON file.
    This ensures data persistence across multiple runs of the program. Error handling 
    is included to manage potential file writing issues.
    """
    try:
        # Convert cache values (which are the item dictionaries) to a list for JSON serialization.
        # Using ensure_ascii=False allows for direct storage of Korean characters, and indent=4 
        # makes the JSON file human-readable.
        with open(FOUND_ITEMS_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(found_items_cache.values()), f, ensure_ascii=False, indent=4)
        logging.info(f"✅ Cache saved: {len(found_items_cache)} items successfully written to '{FOUND_ITEMS_FILE}'.")
    except IOError as e:
        logging.error(f"❌ Failed to save items to '{FOUND_ITEMS_FILE}': {e}")
    except Exception as e:
        logging.error(f"❌ An unexpected error occurred while saving '{FOUND_ITEMS_FILE}': {e}", exc_info=True)

def send_telegram_message(bot: Bot, chat_id: str, message: str) -> bool:
    """
    Sends a formatted message via the Telegram bot to the specified chat ID.
    Uses HTML parse mode for rich text formatting. Includes robust error handling 
    for Telegram API-specific issues and general network problems.
    Returns True on successful delivery, False on failure.
    """
    if not chat_id:
        logging.error("❌ Telegram Chat ID가 설정되지 않아 메시지를 보낼 수 없습니다.")
        return False
    if not message.strip():
        logging.warning("⚠️ 전송할 Telegram 메시지가 비어있습니다. 전송을 건너뜁니다.")
        return False

    try:
        logging.debug(f"Attempting to send Telegram message to chat ID: {chat_id}")
        bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML', disable_web_page_preview=False)
        logging.info(f"✈️ Telegram message sent successfully to chat ID: {chat_id}.")
        return True
    except TelegramError as e:
        logging.error(f"❌ Failed to send Telegram message (Telegram API Error): {e}")
        # Specific TelegramError handling for common issues
        if "Bad Request: chat not found" in str(e):
            logging.error("❗ 오류: Telegram Chat ID를 다시 확인해주세요. 봇이 해당 채팅으로 메시지를 보낼 수 없습니다.")
        elif "Forbidden: bot was blocked by the user" in str(e):
            logging.error("❗ 오류: 사용자가 봇을 차단했습니다. 봇을 다시 활성화해야 합니다.")
        return False
    except requests.exceptions.ConnectionError as e:
        logging.error(f"❌ Telegram API 연결 오류 발생: {e}. 네트워크 연결을 확인해주세요.")
        return False
    except Exception as e:
        logging.error(f"❌ An unexpected error occurred while sending Telegram message: {e}", exc_info=True)
        return False

def get_karrot_search_url(keyword: str) -> str:
    """
    Generates the Karrot Market search URL for a given keyword.
    The keyword is URL-encoded to handle special characters correctly.
    Note: Karrot Market's region filtering is complex and often client-side. 
    This scraper primarily focuses on keyword search across general listings.
    """
    encoded_keyword = requests.utils.quote(keyword)
    return f"https://www.daangn.com/search/{encoded_keyword}"

def scrape_karrot_market(keyword: str) -> List[Dict[str, Any]]:
    """
    Scrapes Karrot Market for items matching the specified keyword.
    It simulates a web browser request to fetch HTML content and then parses it 
    to extract item details like title, price, and link.
    Includes robust error handling for network issues, HTTP errors, and parsing failures.
    Returns a list of dictionaries, each representing an item found.
    """
    url = get_karrot_search_url(keyword)
    # Define a standard set of headers to mimic a common web browser. This helps 
    # reduce the chances of being blocked by the website's anti-scraping measures.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Connection': 'keep-alive',
    }
    
    items: List[Dict[str, Any]] = []
    logging.info(f"🔍 Starting to scrape Karrot Market for keyword: '{keyword}' at URL: {url}")
    
    try:
        # Send a GET request with defined headers and a reasonable timeout to prevent indefinite waits.
        response = requests.get(url, headers=headers, timeout=20) # Increased timeout to 20 seconds for stability
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx status codes)
        
        # Parse the HTML content using BeautifulSoup's 'html.parser'.
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all article links, which contain individual item details. 
        # The class 'flea-market-article-link' is specific to Karrot Market's structure.
        articles = soup.find_all('a', class_='flea-market-article-link')

        if not articles:
            logging.warning(f"⚠️ No articles found for keyword '{keyword}' on Karrot Market. This might be due to no results, a temporary issue, or a change in the website's HTML structure.")
            # Uncomment the line below for deeper debugging of the HTML structure if articles are unexpectedly not found.
            # logging.debug(f"Partial HTML for debugging (first 2000 chars):\n{soup.prettify()[:2000]}") 
            return [] # Return an empty list if no articles are found

        logging.info(f"🔎 Found {len(articles)} potential articles for keyword '{keyword}'. Parsing details...")

        # Iterate through each found article to extract relevant information.
        for i, article in enumerate(articles):
            log_prefix = f"[Keyword: '{keyword}', Article {i+1}/{len(articles)}]"
            try:
                item_link_suffix = article.get('href', '')
                if not item_link_suffix.startswith('/articles/'):
                    logging.debug(f"{log_prefix} Skipping due to unexpected link format: {item_link_suffix}")
                    continue

                item_link = "https://www.daangn.com" + item_link_suffix
                
                # Extract unique ID from the link (e.g., from /articles/1234567890 -> 1234567890).
                item_id = item_link_suffix.split('/')[-1]
                if not item_id.isdigit(): # Ensure it's a valid numerical ID fragment for consistent tracking.
                    logging.warning(f"🚫 {log_prefix} Skipping article with non-numeric item_id: '{item_id}' from link: {item_link}")
                    continue 

                # Safely extract title and price tags
                title_tag = article.find('h2', class_='article-title')
                price_tag = article.find('p', class_='article-price')
                
                title = title_tag.get_text(strip=True) if title_tag else '제목 없음'
                price_str = price_tag.get_text(strip=True) if price_tag else '0원' # Default if price tag is missing

                if not title_tag:
                    logging.debug(f"{log_prefix} Title tag not found. Defaulting to '제목 없음'.")
                if not price_tag:
                    logging.debug(f"{log_prefix} Price tag not found. Defaulting to '0원'.")

                price_value = 0
                if '무료' in price_str or '나눔' in price_str:
                    price_value = 0
                    logging.debug(f"{log_prefix} Price is '무료/나눔'. Setting price_value to 0.")
                elif '가격 제안' in price_str or '시세' in price_str:
                    price_value = -1 # Special value to indicate "price suggestion" or unknown price, excluded from 'sweet spot'.
                    logging.debug(f"{log_prefix} Price is '가격 제안/시세'. Setting price_value to -1.")
                else:
                    try:
                        # Clean price string by removing '원' and commas, then convert to integer.
                        price_value = int(price_str.replace('원', '').replace(',', '').strip())
                        logging.debug(f"{log_prefix} Successfully parsed price '{price_str}' to {price_value:,}원.")
                    except ValueError:
                        logging.warning(f"⚠️ {log_prefix} Could not parse price '{price_str}' for item '{title}'. Defaulting to 0. Error: ValueError")
                        price_value = 0 # Default to 0 if parsing fails gracefully.
                        
                item_data = {
                    'id': item_id,
                    'title': title,
                    'price': price_value,
                    'link': item_link,
                    'scraped_at': datetime.now().isoformat()
                }
                items.append(item_data)
                logging.debug(f"✨ {log_prefix} Successfully parsed item: ID={item_id}, Title='{title}', Price={price_value:,}원.")

            except AttributeError as e:
                # This could happen if a `find` call returns None and then `.get_text()` is called on it.
                logging.warning(f"⚠️ {log_prefix} AttributeError during parsing (link: {article.get('href', 'N/A')}): {e}. Skipping this article.")
                continue
            except Exception as e:
                logging.warning(f"🚫 {log_prefix} An unexpected error occurred during article parsing (link: {article.get('href', 'N/A')}): {e}. Skipping this article to continue with others.", exc_info=True)
                continue # Skip malformed or problematic articles and continue with the next one.

    except requests.exceptions.Timeout:
        logging.error(f"❌ Timeout error during scraping for keyword '{keyword}'. The server took too long to respond (timeout set to 20s).")
    except requests.exceptions.ConnectionError as e:
        logging.error(f"❌ Connection error during scraping for keyword '{keyword}'. Please check your network connectivity or the URL: {e}")
    except requests.exceptions.HTTPError as e:
        logging.error(f"❌ HTTP error during scraping for keyword '{keyword}': {e.response.status_code} - {e.response.reason}. URL: {url}")
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ A general Request error occurred during scraping for keyword '{keyword}': {e}")
    except Exception as e:
        logging.critical(f"❌ An unhandled critical error occurred during scraping for keyword '{keyword}': {e}", exc_info=True)
    
    logging.info(f"✅ Finished scraping for keyword '{keyword}'. Found {len(items)} valid items in this batch.")
    return items

def is_sweet_spot(item: Dict[str, Any], keywords: List[str], price_threshold_krw: int) -> Tuple[bool, str]:
    """
    Determines if an item qualifies as a 'sweet-spot' deal based on its price and title matching search keywords.
    Returns a tuple: (True, "reason for sweet spot") if it qualifies, 
    otherwise (False, "reason for not being sweet spot").
    """
    item_title_lower = item['title'].lower()
    
    # 1. Price check:
    # Items with "가격 제안" or unknown price are explicitly excluded from being a "sweet spot".
    if item['price'] == -1: 
        return False, "❌ 가격 제안/알 수 없음 (Price Suggestion/Unknown)"
    # Check if the item's price is strictly below or equal to the defined threshold.
    if item['price'] > price_threshold_krw:
        return False, f"❌ 가격 {item['price']:,}원 (기준: {price_threshold_krw:,}원 초과)"

    # 2. Keyword check:
    # Ensure at least one of the configured search keywords (case-insensitively) is present in the item's title.
    # The comparison should also handle spaces in keywords correctly.
    matched_keywords = [kw for kw in keywords if kw.lower() in item_title_lower]
    if not matched_keywords:
        return False, "❌ 키워드 불일치 (Keyword Mismatch)"
    
    # If both price and keyword criteria are met, it's a sweet spot!
    return True, f"✅ 꿀템 발견! (일치 키워드: {', '.join(matched_keywords)})"

def format_telegram_message(item: Dict[str, Any]) -> str:
    """
    Formats an item's details into an HTML-formatted message string, suitable for Telegram bots.
    This includes the item title, price, and a clickable link to the product page.
    """
    # Format price for display, handling the special -1 value for "가격 제안".
    price_display = f"{item['price']:,}원" if item['price'] >= 0 else "가격 제안"
    
    return (
        f"<b>🚨 1$ 꿀템 스나이퍼 발견! 🚨</b>\n\n"
        f"<b>💎 아이템:</b> {item['title']}\n"
        f"<b>💰 가격:</b> {price_display}\n"
        f"<b>🔗 링크:</b> <a href='{item['link']}'>상품 페이지 바로가기</a>\n\n"
        f"지금 바로 득템하세요! 🚀"
    )

def main() -> None:
    """
    Main function to initialize and run the Karrot Guardian AI.
    It orchestrates environment variable loading, Telegram bot initialization, 
    persistent cache management, periodic web scraping, item filtering based on criteria,
    and sending notifications for 'sweet-spot' deals.
    """
    logging.info("🚀 Karrot Guardian AI: 1$ Sweet-Spot Sniper를 시작합니다!")

    # --- Initial Configuration Validation ---
    # Critical environment variables are checked to ensure the bot can function. 
    # The program exits if any essential configuration is missing.
    if not TELEGRAM_BOT_TOKEN:
        logging.critical("❌ FATAL: 'TELEGRAM_BOT_TOKEN'이 .env 파일에 설정되지 않았습니다. 프로그램을 종료합니다.")
        sys.exit(1) # Exit with an error code
    if not TELEGRAM_CHAT_ID:
        logging.critical("❌ FATAL: 'TELEGRAM_CHAT_ID'가 .env 파일에 설정되지 않았습니다. 프로그램을 종료합니다.")
        sys.exit(1)
    if not SEARCH_KEYWORDS:
        logging.critical("❌ FATAL: 'SEARCH_KEYWORDS'가 .env 파일에 설정되지 않았습니다. 최소 하나 이상의 키워드를 제공해야 합니다. 프로그램을 종료합니다.")
        sys.exit(1)
    
    logging.info("⚙️ 환경 변수 및 초기 설정 검증 완료.")
    logging.info(f"✔️ 검색 키워드: {', '.join(SEARCH_KEYWORDS)}")
    logging.info(f"✔️ 최대 꿀템 가격: {PRICE_THRESHOLD_KRW:,}원")
    logging.info(f"✔️ 스크래핑 주기: {SCRAPE_INTERVAL_SECONDS}초")


    # Initialize Telegram Bot with the provided token.
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        # Verify bot token by getting bot info - this makes sure token is valid early
        bot_info = bot.get_me()
        logging.info(f"🤖 Telegram 봇 초기화 완료: @{bot_info.username} ({bot_info.first_name})")
    except TelegramError as e:
        logging.critical(f"❌ FATAL: Telegram 봇 초기화 실패 (토큰 오류 또는 네트워크 문제): {e}. 프로그램을 종료합니다.", exc_info=True)
        sys.exit(1)
    except Exception as e:
        logging.critical(f"❌ FATAL: Telegram 봇 초기화 중 예상치 못한 오류 발생: {e}. 프로그램을 종료합니다.", exc_info=True)
        sys.exit(1)

    # Load previously found items from the cache file to prevent duplicate notifications.
    load_found_items() 

    # --- Initial Profit Challenge Summary ---
    total_found_at_start = len(found_items_cache)
    # Calculate total 'value' for items priced 0 or above (exclude -1 for '가격 제안').
    total_potential_savings_at_start = sum(item['price'] for item in found_items_cache.values() if item['price'] >= 0)
    
    logging.info("\n--- 📊 오또의 수익 챌린지 대시보드 (초기 로드) ---")
    logging.info(f"📈 총 발견 꿀템 수: {total_found_at_start}개")
    logging.info(f"💰 총 잠재적 절약 금액 (발견된 아이템 가격 합계): {total_potential_savings_at_start:,}원")
    logging.info("-------------------------------------------------")

    # --- Main Scraping Loop ---
    while True:
        cycle_start_time = datetime.now()
        logging.info(f"\n--- 🔄 새로운 스크래핑 주기 시작: {cycle_start_time.strftime('%Y-%m-%d %H:%M:%S')} ---")
        logging.info(f"✔️ 현재 캐시에 {len(found_items_cache)}개의 이전 발견 아이템이 있습니다.")
        
        all_scraped_items_this_cycle: List[Dict[str, Any]] = []
        for i, keyword in enumerate(SEARCH_KEYWORDS):
            logging.info(f"➡️ 키워드 '{keyword}' ({i+1}/{len(SEARCH_KEYWORDS)})에 대한 스크래핑을 시작합니다...")
            scraped_items = scrape_karrot_market(keyword)
            all_scraped_items_this_cycle.extend(scraped_items)
            logging.info(f"✨ 키워드 '{keyword}'에서 {len(scraped_items)}개의 아이템을 스크래핑했습니다.")
            if i < len(SEARCH_KEYWORDS) - 1: # Only sleep if it's not the last keyword
                logging.debug(f"짧은 지연 (1초) 후 다음 키워드로 넘어갑니다.")
                time.sleep(1) # Small delay between keyword searches to be polite to the server

        logging.info(f"✔️ 모든 키워드에 대한 스크래핑 완료. 이번 주기에서 총 {len(all_scraped_items_this_cycle)}개의 아이템을 발견했습니다.")

        current_cycle_new_alerts = 0
        processed_items_count = 0
        total_items_to_check = len(all_scraped_items_this_cycle)

        logging.info(f"Filtering {total_items_to_check} scraped items for new sweet spots...")
        if total_items_to_check == 0:
            logging.info("이번 주기에서 스크랩된 아이템이 없어 필터링할 내용이 없습니다.")
        else:
            for item in all_scraped_items_this_cycle:
                processed_items_count += 1
                item_progress_log = f"({processed_items_count}/{total_items_to_check})"

                # Check if the item has already been processed in previous cycles to avoid duplicate notifications.
                if item['id'] not in found_items_cache:
                    is_sweet, reason = is_sweet_spot(item, SEARCH_KEYWORDS, PRICE_THRESHOLD_KRW)
                    
                    if is_sweet:
                        logging.info(f"🎉 NEW SWEET SPOT FOUND! {item_progress_log} ID: {item['id']}, Title: '{item['title']}', Price: {item['price']:,}원. Reason: {reason}")
                        
                        telegram_message = format_telegram_message(item)
                        logging.info(f"Attempting to send Telegram notification for item ID: {item['id']} ('{item['title']}')...")
                        if send_telegram_message(bot, TELEGRAM_CHAT_ID, telegram_message):
                            # Only add to cache if Telegram message was sent successfully to confirm delivery.
                            found_items_cache[item['id']] = item 
                            current_cycle_new_alerts += 1
                            logging.debug(f"Item {item['id']} successfully added to cache after successful notification.")
                        else:
                            logging.error(f"⚠️ Telegram message failed for item {item['id']} ('{item['title']}'). Item not added to cache; will retry in a future cycle if found again.")
                else:
                    logging.debug(f"Item {item_progress_log} already seen (ID: {item['id']}, Title: '{item['title']}'). Skipping notification.")
        
        # --- End of Cycle Summary and Cache Management ---
        if current_cycle_new_alerts > 0:
            save_found_items() # Save cache if any new items were successfully notified and added during this cycle.
            logging.info(f"\n--- 📊 오또의 수익 챌린지 대시보드 (현재 업데이트) ---")
            logging.info(f"📈 총 발견 꿀템 수: {len(found_items_cache)}개")
            total_potential_savings = sum(item['price'] for item in found_items_cache.values() if item['price'] >= 0)
            logging.info(f"💰 총 잠재적 절약 금액 (발견된 아이템 가격 합계): {total_potential_savings:,}원")
            logging.info("-------------------------------------------------")
        else:
            logging.info("😴 이번 주기에는 새로운 꿀템이 발견되지 않았습니다.")

        logging.info(f"--- 💤 스크래핑 주기 완료. 다음 스크래핑까지 {SCRAPE_INTERVAL_SECONDS}초 대기합니다. ---\n")
        time.sleep(SCRAPE_INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("👋 Karrot Guardian AI가 사용자 요청으로 종료됩니다. 다음에 또 만나요!")
        sys.exit(0) # Exit cleanly
    except Exception as e:
        logging.critical(f"❌ Unhandled critical error in main execution: {e}. Program will terminate.", exc_info=True)
        sys.exit(1) # Exit with an error code