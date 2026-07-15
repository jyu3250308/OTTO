import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import json
import re
import sys # Added for sys.exit

# --- Configuration & Environment Variable Loading ---
# Load environment variables from .env file
load_dotenv()

# Define constants for file paths and URLs
SEEN_ITEMS_FILE = "seen_items.json"
DAANGN_BASE_URL = "https://www.daangn.com"
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Get configuration from environment variables, with defaults and type casting
# TELEGRAM_BOT_TOKEN: Mandatory for notifications
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# TELEGRAM_CHAT_ID: Mandatory for notifications
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# SEARCH_KEYWORDS: Comma-separated string, default to common items if not set
SEARCH_KEYWORDS_STR = os.getenv('SEARCH_KEYWORDS', '아이폰,맥북').strip()
# Convert keywords string to a list, filtering out empty strings
SEARCH_KEYWORDS = [kw.strip() for kw in SEARCH_KEYWORDS_STR.split(',') if kw.strip()]

# SCRAPING_INTERVAL_SECONDS: Time in seconds between full scraping cycles, default to 5 minutes (300s)
try:
    SCRAPING_INTERVAL_SECONDS = int(os.getenv('SCRAPING_INTERVAL_SECONDS', 300))
    if SCRAPING_INTERVAL_SECONDS <= 0:
        print("[WARNING] SCRAPING_INTERVAL_SECONDS는 양수여야 합니다. 기본값 300초로 설정합니다.", file=sys.stderr)
        SCRAPING_INTERVAL_SECONDS = 300
except ValueError:
    print("[WARNING] SCRAPING_INTERVAL_SECONDS 값이 유효하지 않습니다. 기본값 300초로 설정합니다.", file=sys.stderr)
    SCRAPING_INTERVAL_SECONDS = 300

# MAX_PAGES_TO_SCRAPE: Maximum number of pages to scrape per keyword, default to 3 pages
try:
    MAX_PAGES_TO_SCRAPE = int(os.getenv('MAX_PAGES_TO_SCRAPE', 3))
    if MAX_PAGES_TO_SCRAPE <= 0:
        print("[WARNING] MAX_PAGES_TO_SCRAPE는 양수여야 합니다. 기본값 3페이지로 설정합니다.", file=sys.stderr)
        MAX_PAGES_TO_SCRAPE = 3
except ValueError:
    print("[WARNING] MAX_PAGES_TO_SCRAPE 값이 유효하지 않습니다. 기본값 3페이지로 설정합니다.", file=sys.stderr)
    MAX_PAGES_TO_SCRAPE = 3

# --- Global State ---
# A set to store URLs of items that have already been seen/notified, to prevent duplicate alerts.
seen_item_urls = set()

# --- Utility Functions ---

def load_seen_items() -> None:
    """
    Loads previously seen item URLs from a JSON file into the global `seen_item_urls` set.
    Handles file not found, JSON decoding errors, and incorrect file formats gracefully.
    """
    global seen_item_urls # Declare intent to modify the global variable
    if os.path.exists(SEEN_ITEMS_FILE):
        try:
            with open(SEEN_ITEMS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    seen_item_urls = set(data)
                    print(f"[INFO] '{SEEN_ITEMS_FILE}'에서 {len(seen_item_urls)}개의 이전에 감지된 아이템 URL을 성공적으로 로드했습니다.")
                else:
                    print(f"[WARNING] '{SEEN_ITEMS_FILE}' 파일 형식이 올바르지 않습니다 (기대: 리스트). 파일을 초기화합니다.", file=sys.stderr)
                    seen_item_urls = set() # Reset to an empty set
        except FileNotFoundError:
            # This case should ideally be caught by os.path.exists, but good for robustness
            print(f"[WARNING] '{SEEN_ITEMS_FILE}' 파일을 찾을 수 없습니다. 새로운 파일로 시작합니다.", file=sys.stderr)
            seen_item_urls = set()
        except json.JSONDecodeError:
            print(f"[ERROR] '{SEEN_ITEMS_FILE}' 파일 파싱 오류. 파일이 손상되었을 수 있습니다. 파일을 초기화합니다.", file=sys.stderr)
            seen_item_urls = set() # Reset to an empty set
        except Exception as e:
            print(f"[ERROR] '{SEEN_ITEMS_FILE}' 로딩 중 예상치 못한 오류 발생: {e}. 파일을 초기화합니다.", file=sys.stderr)
            seen_item_urls = set()
    else:
        print(f"[INFO] '{SEEN_ITEMS_FILE}' 파일이 존재하지 않습니다. 새로운 파일로 시작합니다.")

def save_seen_items() -> None:
    """
    Saves the current set of seen item URLs to a JSON file.
    """
    try:
        with open(SEEN_ITEMS_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(seen_item_urls), f, ensure_ascii=False, indent=2)
        print(f"[INFO] 현재 {len(seen_item_urls)}개의 아이템 URL을 '{SEEN_ITEMS_FILE}'에 저장했습니다.")
    except IOError as e:
        print(f"[ERROR] '{SEEN_ITEMS_FILE}' 저장 중 입출력 오류 발생: {e}", file=sys.stderr)
    except Exception as e:
        print(f"[ERROR] '{SEEN_ITEMS_FILE}' 저장 중 예상치 못한 오류 발생: {e}", file=sys.stderr)


def send_telegram_message(message: str) -> bool:
    """
    Sends a message to the configured Telegram chat.
    Args:
        message (str): The text message to send. Supports HTML parsing.
    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERROR] 텔레그램 봇 토큰 또는 채팅 ID가 설정되지 않았습니다. 알림을 보낼 수 없습니다. .env 파일을 확인해주세요.", file=sys.stderr)
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML' # Allows basic HTML tags like <b>, <i>, <a>
    }
    try:
        print(f"[INFO] 텔레그램 메시지 전송 시도: {message[:70]}...") # Log start of send attempt
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

        # Check for Telegram API specific errors in the response body
        response_json = response.json()
        if not response_json.get('ok'):
            error_description = response_json.get('description', '알 수 없는 텔레그램 API 오류')
            print(f"[ERROR] 텔레그램 API 오류 발생: {error_description} (Code: {response_json.get('error_code')})", file=sys.stderr)
            return False

        print(f"[INFO] 텔레그램 메시지 성공적으로 전송 완료.")
        return True
    except requests.exceptions.Timeout:
        print(f"[ERROR] 텔레그램 메시지 전송 시간 초과. 네트워크 상태를 확인해주세요.", file=sys.stderr)
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"[ERROR] 텔레그램 서버 연결 실패: {e}. 네트워크 연결을 확인해주세요.", file=sys.stderr)
        return False
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] 텔레그램 메시지 전송 HTTP 오류 발생: {e.response.status_code} - {e.response.text}", file=sys.stderr)
        return False
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 텔레그램 메시지 전송 중 알 수 없는 요청 오류 발생: {e}", file=sys.stderr)
        return False
    except json.JSONDecodeError:
        print(f"[ERROR] 텔레그램 응답을 JSON으로 파싱하는 데 실패했습니다.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[CRITICAL] 텔레그램 메시지 전송 중 예기치 않은 오류 발생: {e}", file=sys.stderr)
        return False

# --- Daangn Market Scraping Function ---

def scrape_daangn(keyword: str) -> list:
    """
    Scrapes Daangn Market for items matching the given keyword across multiple pages.
    Filters out '거래완료' or '판매완료' items.

    Args:
        keyword (str): The search keyword to use for scraping.

    Returns:
        list: A list of dictionaries, each representing a newly found item.
    """
    found_items = []
    print(f"\n[INFO] 🔍 키워드 '{keyword}'로 당근마켓 스크래핑을 시작합니다...")

    for page in range(1, MAX_PAGES_TO_SCRAPE + 1):
        search_url = f"{DAANGN_BASE_URL}/search/{keyword}/articles?page={page}"
        print(f"[INFO]   ➡️ 페이지 {page}/{MAX_PAGES_TO_SCRAPE} 스크래핑 시도: {search_url}")
        
        try:
            headers = {'User-Agent': USER_AGENT}
            response = requests.get(search_url, headers=headers, timeout=15)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all article cards that represent individual postings
            articles = soup.find_all('article', class_='flea-card-item')
            
            if not articles:
                print(f"[INFO]   ℹ️ 페이지 {page}에서 더 이상 새로운 게시글을 찾을 수 없습니다. 키워드 '{keyword}' 스크래핑을 중단합니다.")
                break # No more articles on this page, or subsequent pages, so stop
            
            print(f"[INFO]   ✅ 페이지 {page}에서 {len(articles)}개의 게시글 카드를 찾았습니다. 처리 중...")

            for article in articles:
                link_tag = article.find('a', class_='flea-card-link')
                if not link_tag or 'href' not in link_tag.attrs:
                    # print("[DEBUG]   링크 태그를 찾을 수 없거나 href 속성이 없습니다. 게시글 스킵.")
                    continue

                item_url = DAANGN_BASE_URL + link_tag['href']
                
                # Check if this item has already been seen in previous cycles
                if item_url in seen_item_urls:
                    # print(f"[DEBUG]   이미 감지된 아이템 URL 스킵: {item_url}")
                    continue # Skip processing if already seen

                title_tag = article.find('h2', class_='card-title')
                price_tag = article.find('div', class_='card-price')
                region_tag = article.find('div', class_='card-region-name')
                status_tag = article.find('p', class_='card-text trade-counts') # Often contains '거래완료'

                title = title_tag.get_text(strip=True) if title_tag else '제목 없음'
                price = price_tag.get_text(strip=True) if price_tag else '가격 미정'
                region = region_tag.get_text(strip=True) if region_tag else '지역 미상'
                status = status_tag.get_text(strip=True) if status_tag else ''

                # Filter out items that are already marked as sold or completed
                if '거래완료' in status or '판매완료' in status:
                    # print(f"[DEBUG]   '거래완료' 또는 '판매완료'된 아이템 스킵: '{title}'")
                    continue

                # Construct item information dictionary
                item_info = {
                    'title': title,
                    'price': price,
                    'region': region,
                    'url': item_url,
                    'keyword': keyword # Record which keyword found this item
                }
                found_items.append(item_info)
                # No need to add to seen_item_urls here, it's done in main() after filtering new items

            # Introduce a small delay to be polite to the server and avoid rate limiting
            time.sleep(2) 

        except requests.exceptions.Timeout:
            print(f"[ERROR]   당근마켓 스크래핑 시간 초과 (키워드: '{keyword}', 페이지: {page}). 네트워크 상태를 확인해주세요.", file=sys.stderr)
            break # Stop current keyword scraping
        except requests.exceptions.ConnectionError as e:
            print(f"[ERROR]   당근마켓 서버 연결 실패 (키워드: '{keyword}', 페이지: {page}): {e}. 네트워크 연결을 확인해주세요.", file=sys.stderr)
            break # Stop current keyword scraping
        except requests.exceptions.HTTPError as e:
            print(f"[ERROR]   당근마켓 스크래핑 HTTP 오류 발생 (키워드: '{keyword}', 페이지: {page}): {e.response.status_code} - {e.response.text}", file=sys.stderr)
            if e.response.status_code == 404:
                print(f"[INFO]   페이지 {page}는 존재하지 않는 것 같습니다. 스크래핑을 중단합니다.")
            break # Stop current keyword scraping
        except requests.exceptions.RequestException as e:
            print(f"[ERROR]   당근마켓 스크래핑 중 알 수 없는 요청 오류 발생 (키워드: '{keyword}', 페이지: {page}): {e}", file=sys.stderr)
            break # Stop current keyword scraping
        except Exception as e:
            print(f"[CRITICAL]   당근마켓 스크래핑 중 예상치 못한 오류 발생 (키워드: '{keyword}', 페이지: {page}): {e}", file=sys.stderr)
            break # Stop current keyword scraping
    
    print(f"[INFO] 🎯 키워드 '{keyword}' 스크래핑 완료. 총 {len(found_items)}개의 잠재적 새 게시글 발견 (판매완료/중복 제외).")
    return found_items

# --- Main Execution Logic ---

def main() -> None:
    """
    Main function to initialize the scraper and run the continuous scraping loop.
    """
    print("🥕 Hyper-Bunny Beat: 당근마켓 알림 폭격기가 시작됩니다! 🥕")
    print("---------------------------------------------------------")
    
    # Validate critical environment variables
    if not TELEGRAM_BOT_TOKEN:
        print("[CRITICAL] TELEGRAM_BOT_TOKEN이 설정되지 않았습니다. 텔레그램 알림 없이 시작합니다.", file=sys.stderr)
    if not TELEGRAM_CHAT_ID:
        print("[CRITICAL] TELEGRAM_CHAT_ID가 설정되지 않았습니다. 텔레그램 알림 없이 시작합니다.", file=sys.stderr)
    if not SEARCH_KEYWORDS:
        print("[CRITICAL] 검색 키워드가 설정되지 않았습니다. 'SEARCH_KEYWORDS' 환경 변수를 확인해주세요. 프로그램이 종료됩니다.", file=sys.stderr)
        sys.exit(1) # Exit if no keywords are set

    print(f"[INFO] ⚙️ 설정된 검색 키워드: {', '.join(SEARCH_KEYWORDS)}")
    print(f"[INFO] ⏳ 스크래핑 주기: {SCRAPING_INTERVAL_SECONDS}초")
    print(f"[INFO] 📄 각 키워드당 최대 스크래핑 페이지 수: {MAX_PAGES_TO_SCRAPE} 페이지")
    print("---------------------------------------------------------")

    load_seen_items() # Load previously seen items at startup

    try:
        while True:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[INFO] ========================================================")
            print(f"[INFO] 🚀 새 스크래핑 주기 시작: {current_time}")
            print(f"[INFO] ========================================================")
            
            new_items_this_cycle_count = 0
            current_seen_count_before_cycle = len(seen_item_urls) # Snapshot current count

            for keyword in SEARCH_KEYWORDS:
                items = scrape_daangn(keyword)
                print(f"[INFO] 키워드 '{keyword}'에서 {len(items)}개의 잠재적 새 아이템을 검토합니다.")
                for item in items:
                    if item['url'] not in seen_item_urls:
                        new_items_this_cycle_count += 1
                        seen_item_urls.add(item['url']) # Mark as seen
                        
                        # Prepare Telegram alert message
                        alert_message = (
                            f"✨ 당근마켓에 새 글이 올라왔어요! (키워드: &lt;b&gt;{item['keyword']}&lt;/b&gt;)\n"
                            f"&lt;b&gt;제목:&lt;/b&gt; {item['title']}\n"
                            f"&lt;b&gt;가격:&lt;/b&gt; {item['price']}\n"
                            f"&lt;b&gt;지역:&lt;/b&gt; {item['region']}\n"
                            f"&lt;a href=\"{item['url']}\"&gt;➡️ 게시글 바로가기&lt;/a&gt;"
                        )
                        print(f"[ALERT] 🔔 새로운 아이템 발견! '{item['title']}' - {item['price']} ({item['url']})")
                        send_telegram_message(alert_message)
                    # else:
                        # print(f"[DEBUG]   '{item['title']}' 아이템은 이미 이전에 감지되었습니다. 스킵.")
            
            if new_items_this_cycle_count == 0:
                print(f"\n[INFO] 이번 주기 ({current_time})에는 새로운 아이템이 발견되지 않았습니다. 😴")
            else:
                print(f"\n[INFO] 🎉 이번 주기 ({current_time})에서 총 {new_items_this_cycle_count}개의 새로운 아이템을 발견하고 알림을 보냈습니다.")
            
            # Save seen items to file only if there were changes in the set
            if len(seen_item_urls) != current_seen_count_before_cycle:
                save_seen_items()
            else:
                print("[INFO] 'seen_items.json'에 변경사항이 없어 저장하지 않습니다.")

            print(f"[INFO] ⏳ 다음 스크래핑까지 {SCRAPING_INTERVAL_SECONDS}초 대기합니다...")
            time.sleep(SCRAPING_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n[INFO] 🛑 사용자에 의해 프로그램이 종료되었습니다.")
    except Exception as e:
        print(f"\n[CRITICAL] ❌ 예기치 않은 오류로 프로그램이 종료되었습니다: {e}", file=sys.stderr)
    finally:
        # Ensure seen items are always saved upon program exit (graceful or error)
        print("[INFO] 💾 프로그램 종료 전 마지막으로 감지된 아이템 목록을 저장합니다.")
        save_seen_items()
        print("[INFO] 🔚 Hyper-Bunny Beat 프로그램이 종료됩니다.")

if __name__ == "__main__":
    main()
