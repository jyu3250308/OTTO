import os
import requests
from bs4 import BeautifulSoup
import time
import json
from dotenv import load_dotenv
import re
import datetime
import traceback
from typing import List, Dict, Set, Any, Optional

# --- Constants & Configuration Loading ---

# Load environment variables from .env file at the very beginning.
# This ensures all subsequent os.getenv calls can access these variables.
load_dotenv()

# --- Logging Setup ---
def log(level: str, message: str, exc_info: bool = False) -> None:
    """
    Prints a formatted log message with a timestamp and specified level.
    Levels: INFO, WARN, ERROR, CRITICAL, ALERT (for new item notifications).
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level.upper()}]: {message}"
    if exc_info:
        # Append detailed traceback information if an exception occurred
        log_message += f"\n{traceback.format_exc()}"
    print(log_message)

# --- Environment Variable Configuration ---

# Telegram Bot Token (REQUIRED)
# Obtained from @BotFather on Telegram. Used to send messages.
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
# Telegram Chat ID (REQUIRED)
# The ID of the chat (private or group) where notifications will be sent.
# Can be obtained by sending a message to your bot and checking
# 'https://api.telegram.org/bot[YOUR_TELEGRAM_BOT_TOKEN]/getUpdates'.
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# Karrot Market Search Keywords (REQUIRED)
# A comma-separated list of keywords to search for. Each keyword will be searched individually.
# Example: "아이패드,맥북,에어팟"
KARROT_KEYWORDS_STR: str = os.getenv("KARROT_KEYWORDS", "아이폰,에어팟").strip()
KARROT_KEYWORDS: List[str] = [k.strip() for k in KARROT_KEYWORDS_STR.split(',') if k.strip()]

# Karrot Market Base URL (OPTIONAL, default: entire Daangn Market)
# The base URL for Daangn Market. Use 'https://www.daangn.com' for the entire market.
# To specify a region, use a URL like 'https://www.daangn.com/regions/seoul-gangnam-gu'.
KARROT_BASE_URL: str = os.getenv("KARROT_BASE_URL", "https://www.daangn.com").strip()
if not KARROT_BASE_URL:
    log("WARN", "KARROT_BASE_URL 환경 변수가 비어 있습니다. 기본값 'https://www.daangn.com'으로 설정합니다.")
    KARROT_BASE_URL = "https://www.daangn.com" # Fallback if empty string is provided

# Minimum and Maximum Price Settings (OPTIONAL, defaults: 0 ~ ~1 billion KRW)
# Only items within this price range (inclusive) will trigger notifications.
# The `DEFAULT_MAX_PRICE` is a large number to effectively mean "no upper limit" by default.
DEFAULT_MAX_PRICE = 999999999 # Roughly 1 billion KRW, used as a default upper bound.

KARROT_MIN_PRICE: int
KARROT_MAX_PRICE: int

try:
    KARROT_MIN_PRICE = int(os.getenv("KARROT_MIN_PRICE", "0"))
    if KARROT_MIN_PRICE < 0:
        log("WARN", f"KARROT_MIN_PRICE 환경 변수({KARROT_MIN_PRICE})가 0보다 작습니다. 기본값 0으로 설정합니다.")
        KARROT_MIN_PRICE = 0
except ValueError:
    log("WARN", "KARROT_MIN_PRICE 환경 변수가 유효한 숫자가 아닙니다. 기본값 0으로 설정합니다.")
    KARROT_MIN_PRICE = 0

try:
    KARROT_MAX_PRICE = int(os.getenv("KARROT_MAX_PRICE", str(DEFAULT_MAX_PRICE)))
    if KARROT_MAX_PRICE < 0:
        log("WARN", f"KARROT_MAX_PRICE 환경 변수({KARROT_MAX_PRICE})가 0보다 작습니다. 기본값 {DEFAULT_MAX_PRICE:n}으로 설정합니다.")
        KARROT_MAX_PRICE = DEFAULT_MAX_PRICE
except ValueError:
    log("WARN", f"KARROT_MAX_PRICE 환경 변수가 유효한 숫자가 아닙니다. 기본값 {DEFAULT_MAX_PRICE:n}으로 설정합니다.")
    KARROT_MAX_PRICE = DEFAULT_MAX_PRICE

# Check Interval (REQUIRED, default: 60 seconds)
# How often the bot will scrape Daangn Market for new items.
# MIN_CHECK_INTERVAL is enforced to prevent IP blocking.
MIN_CHECK_INTERVAL = 30 # Recommended minimum interval to prevent IP blocking
CHECK_INTERVAL_SECONDS: int

try:
    CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
    if CHECK_INTERVAL_SECONDS < MIN_CHECK_INTERVAL:
        log("WARN",
            f"CHECK_INTERVAL_SECONDS가 너무 짧습니다 ({CHECK_INTERVAL_SECONDS}초). "
            f"IP 차단 위험이 있으니 {MIN_CHECK_INTERVAL}초 이상으로 설정하는 것을 권장합니다. "
            f"강제로 {MIN_CHECK_INTERVAL}초로 재설정합니다."
        )
        CHECK_INTERVAL_SECONDS = MIN_CHECK_INTERVAL
except ValueError:
    log("WARN", f"CHECK_INTERVAL_SECONDS 환경 변수가 유효한 숫자가 아닙니다. 기본값 60초로 설정합니다.")
    CHECK_INTERVAL_SECONDS = 60

# File to store previously found item URLs to prevent duplicate notifications.
SEEN_ITEMS_FILE: str = "seen_items.json"

# --- Global Variables ---
# A set to store URLs of items for which Telegram notifications have already been sent.
seen_items: Set[str] = set()

# --- Utility Functions ---
def load_seen_items() -> None:
    """
    Loads previously seen item URLs from the `SEEN_ITEMS_FILE` into the global `seen_items` set.
    If the file is missing, corrupted, or invalid, `seen_items` will be initialized as an empty set.
    """
    global seen_items
    log("INFO", f"'{SEEN_ITEMS_FILE}' 파일에서 이전에 발견된 매물 목록을 로드 시도 중...")
    if os.path.exists(SEEN_ITEMS_FILE):
        try:
            with open(SEEN_ITEMS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    seen_items = set(data)
                    log("INFO", f"'{SEEN_ITEMS_FILE}' 파일에서 {len(seen_items)}개의 매물을 성공적으로 불러왔습니다.")
                else:
                    log("WARN",
                        f"'{SEEN_ITEMS_FILE}' 파일 내용이 유효한 리스트 형태가 아닙니다. "
                        f"파일이 손상되었거나 형식이 잘못되었을 수 있습니다. 새로 시작합니다."
                    )
                    seen_items = set()
        except json.JSONDecodeError as e:
            log("ERROR",
                f"'{SEEN_ITEMS_FILE}' 파일 파싱 중 오류 발생: {e}. "
                f"파일이 손상되었거나 비어있을 수 있습니다. 새로 시작합니다."
            )
            seen_items = set()
        except IOError as e:
            log("ERROR",
                f"'{SEEN_ITEMS_FILE}' 파일 읽기 중 I/O 오류 발생: {e}. "
                f"파일 권한 문제 등이 있을 수 있습니다. 새로 시작합니다."
            )
            seen_items = set()
        except Exception as e:
            log("ERROR",
                f"'{SEEN_ITEMS_FILE}' 파일 로드 중 예상치 못한 오류 발생: {e}. "
                f"새로 시작합니다.", exc_info=True
            )
            seen_items = set()
    else:
        log("INFO", f"'{SEEN_ITEMS_FILE}' 파일이 존재하지 않습니다. 새로운 매물 목록으로 시작합니다.")
        seen_items = set()

def save_seen_items() -> None:
    """
    Saves the current `seen_items` set (converted to a list) to `SEEN_ITEMS_FILE` in JSON format.
    """
    try:
        with open(SEEN_ITEMS_FILE, 'w', encoding='utf-8') as f:
            # Convert set to list for JSON serialization. Use indent for readability.
            json.dump(list(seen_items), f, ensure_ascii=False, indent=2)
        log("INFO", f"현재까지 발견된 매물 {len(seen_items)}개를 '{SEEN_ITEMS_FILE}' 파일에 성공적으로 저장했습니다.")
    except IOError as e:
        log("ERROR", f"'{SEEN_ITEMS_FILE}' 파일 쓰기 중 I/O 오류 발생: {e}")
    except Exception as e:
        log("ERROR", f"매물 저장 중 예상치 못한 오류 발생: {e}", exc_info=True)

def send_telegram_message(message: str) -> bool:
    """
    Sends a given message via the Telegram bot.
    Notifications are skipped if `TELEGRAM_BOT_TOKEN` or `TELEGRAM_CHAT_ID` are not set.
    Returns True on success, False on failure.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log("WARN", "텔레그램 봇 토큰 또는 채팅 ID가 설정되지 않았습니다. 메시지를 보낼 수 없습니다.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML", # Allows using HTML tags in the message (e.g., &lt;b&gt;, &lt;a href="..."&gt;)
        "disable_web_page_preview": False # Allows showing a preview for URLs in the message
    }
    try:
        log("INFO", "텔레그램 메시지 전송 시도 중...")
        response = requests.post(url, json=payload, timeout=10) # Set a timeout for the request
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        log("INFO", "텔레그램 메시지 전송 성공.")
        return True
    except requests.exceptions.Timeout:
        log("ERROR", "텔레그램 메시지 전송 실패: 요청 시간 초과 (Timeout). 네트워크 문제 또는 텔레그램 서버 응답 지연일 수 있습니다.")
        return False
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 'N/A'
        response_text = e.response.text if e.response else 'N/A'
        log("ERROR",
            f"텔레그램 메시지 전송 실패: HTTP 오류 발생. (Status: {status_code}, 응답: {response_text}). "
            f"채팅 ID 또는 토큰이 잘못되었거나 텔레그램 API 문제일 수 있습니다."
        )
        return False
    except requests.exceptions.ConnectionError as e:
        log("ERROR", f"텔레그램 메시지 전송 실패: 네트워크 연결 오류 발생: {e}. 인터넷 연결을 확인해주세요.")
        return False
    except requests.exceptions.RequestException as e:
        log("ERROR", f"텔레그램 메시지 전송 중 알 수 없는 요청 오류 발생: {e}", exc_info=True)
        return False
    except Exception as e:
        log("ERROR", f"텔레그램 메시지 전송 중 예상치 못한 오류 발생: {e}", exc_info=True)
        return False

def clean_price_string(price_str: str) -> int:
    """
    Extracts only digits from a price string and converts it to an integer.
    Handles non-numeric values like '무료나눔' or '가격제안' by returning 0.
    """
    # Remove all non-digit characters (including commas, '원', spaces).
    # The regex r'[^\d]' matches any character that is NOT a digit.
    cleaned_str = re.sub(r'[^\d]', '', price_str)
    try:
        return int(cleaned_str) if cleaned_str else 0
    except ValueError:
        # This case should ideally not be hit if regex works correctly,
        # but provides an additional safety net for unexpected strings.
        log("WARN", f"가격 문자열 '{price_str}'을(를) 숫자로 변환할 수 없습니다. 0으로 처리합니다.")
        return 0

# --- Karrot Market Scraper ---
def scrape_karrot_market(keyword: str) -> List[Dict[str, Any]]:
    """
    Scrapes Daangn Market for items matching the given keyword.
    Filters items based on the configured minimum and maximum price range.
    Returns a list of dictionaries, each representing a found item.
    """
    # Construct search URL with optional price filters.
    # Daangn's search URL structure: KARROT_BASE_URL/search/{keyword}?min_price={val}&max_price={val}
    search_url_base = f"{KARROT_BASE_URL}/search/{keyword}"

    params: Dict[str, Any] = {}
    # Add min_price parameter only if it's greater than 0 to avoid unnecessary query string for default.
    if KARROT_MIN_PRICE > 0:
        params["min_price"] = KARROT_MIN_PRICE
    # Add max_price parameter only if it's less than the very large default max price.
    if KARROT_MAX_PRICE < DEFAULT_MAX_PRICE:
        params["max_price"] = KARROT_MAX_PRICE

    # Append query parameters if any are present.
    search_url = search_url_base
    if params:
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        search_url = f"{search_url_base}?{query_string}"

    log("INFO", f"키워드 '{keyword}'에 대한 당근마켓 검색 요청 중. URL: {search_url}")

    # Standard User-Agent to mimic a web browser, reducing chances of being blocked.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    found_items: List[Dict[str, Any]] = []
    try:
        response = requests.get(search_url, headers=headers, timeout=15) # Set a reasonable timeout
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        
        log("INFO", f"'{keyword}' 검색 결과 페이지를 성공적으로 가져왔습니다. HTML 파싱 시작.")
        soup = BeautifulSoup(response.text, 'html.parser')
        # Select all article elements that represent a flea market item.
        # This selector is crucial and might need adjustment if Daangn's HTML structure changes.
        articles = soup.select('article.flea-market-article')
        
        if not articles:
            log("INFO",
                f"'{keyword}' 키워드에 대한 매물을 찾을 수 없거나, 당근마켓 HTML 구조가 변경되었을 수 있습니다. "
                f"(URL: {search_url}). 다음 키워드로 넘어갑니다."
            )
            return []

        log("INFO", f"'{keyword}' 키워드에서 {len(articles)}개의 잠재적 매물 아티클을 발견했습니다. 정보 추출 시작.")
        for i, article in enumerate(articles):
            log("DEBUG", f"  매물 아티클 [{i+1}/{len(articles)}] 처리 중...") # Added for detailed debugging if needed

            # Extract relevant information using robust CSS selectors.
            link_tag = article.select_one('a.flea-market-article-link')
            title_tag = article.select_one('h2.article-title')
            price_tag = article.select_one('p.article-price')
            region_tag = article.select_one('p.article-region-name')
            
            # Ensure all critical elements are found to prevent `NoneType` errors.
            if all([link_tag, title_tag, price_tag, region_tag]):
                item_url = "https://www.daangn.com" + link_tag['href']
                item_title = title_tag.get_text(strip=True)
                item_price_str = price_tag.get_text(strip=True)
                item_region = region_tag.get_text(strip=True)

                item_price_numeric = clean_price_string(item_price_str)

                # Re-verify price against configured min/max. This is important
                # because the URL parameters might not always perfectly filter
                # all edge cases (e.g., '무료나눔' items might slip through).
                if KARROT_MIN_PRICE <= item_price_numeric <= KARROT_MAX_PRICE:
                    found_items.append({
                        'title': item_title,
                        'price': item_price_str, # Keep original price string for display in message
                        'region': item_region,
                        'url': item_url,
                        'keyword': keyword # Record which keyword found this item for context
                    })
                    log("DEBUG", f"    유효한 매물 추출: '{item_title}' ({item_price_str}, {item_region})")
                else:
                    log("DEBUG", f"    가격 범위 밖 매물 스킵: '{item_title}' (가격: {item_price_numeric:n}원)")
            else:
                log("WARN",
                    f"    매물 정보를 완전히 추출할 수 없는 아티클 발견. 일부 셀렉터가 None을 반환했습니다. "
                    f"HTML 구조 변경 가능성. 아티클 내용: {article.prettify()[:200]}..."
                )

        log("INFO", f"키워드 '{keyword}'에 대한 유효한 매물 {len(found_items)}개를 최종적으로 수집했습니다.")
        return found_items

    except requests.exceptions.Timeout:
        log("ERROR",
            f"당근마켓 스크래핑 중 시간 초과 (Timeout) 발생 (키워드: '{keyword}', URL: {search_url}). "
            f"네트워크 연결 문제 또는 서버 응답 지연일 수 있습니다."
        )
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 'N/A'
        log("ERROR",
            f"당근마켓 스크래핑 중 HTTP 오류 발생: {e} (키워드: '{keyword}', URL: {search_url}, Status: {status_code})."
        )
        if status_code == 403:
            log("CRITICAL",
                "403 Forbidden: IP 차단 또는 요청 제한이 의심됩니다. "
                "CHECK_INTERVAL_SECONDS를 충분히 늘려주세요. 현재 값: {CHECK_INTERVAL_SECONDS}초."
            )
        elif status_code == 404:
            log("WARN",
                f"404 Not Found: 검색 URL이 유효하지 않을 수 있습니다. 키워드 또는 KARROT_BASE_URL 설정을 확인해주세요. URL: {search_url}"
            )
    except requests.exceptions.ConnectionError as e:
        log("ERROR",
            f"당근마켓 스크래핑 중 네트워크 연결 오류 발생: {e} (키워드: '{keyword}', URL: {search_url}). "
            f"인터넷 연결을 확인하거나 잠시 후 다시 시도해주세요."
        )
    except requests.exceptions.RequestException as e:
        log("ERROR",
            f"당근마켓 스크래핑 중 알 수 없는 요청 오류 발생: {e} (키워드: '{keyword}', URL: {search_url})", exc_info=True
        )
    except Exception as e:
        log("CRITICAL",
            f"당근마켓 스크래핑 중 예상치 못한 치명적인 오류 발생: {e} (키워드: '{keyword}', URL: {search_url})", exc_info=True
        )
    return [] # Return empty list on any scraping error

# --- Main Bot Logic ---
def run_bot() -> None:
    """
    Main execution logic for the Karrot Blitz bot.
    It scrapes Daangn Market at regular intervals and sends notifications for new items.
    """
    global seen_items

    log("INFO", f"\n{'='*60}\n✨ Karrot Blitz 봇이 시작됩니다! ✨\n{'='*60}")
    log("INFO", ">> 현재 설정 요약:")
    log("INFO", f"  - 검색 키워드: '{', '.join(KARROT_KEYWORDS) if KARROT_KEYWORDS else '설정되지 않음'}'")
    log("INFO", f"  - 검색 기본 URL: '{KARROT_BASE_URL}'")
    log("INFO", f"  - 가격 범위: {KARROT_MIN_PRICE:n}원 ~ {KARROT_MAX_PRICE:n}원")
    log("INFO", f"  - 체크 간격: {CHECK_INTERVAL_SECONDS}초")
    log("INFO", f"  - 텔레그램 알림: {'활성화' if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else '비활성화 (토큰 또는 채팅 ID 누락)'}")
    log("INFO", f"{'='*60}")

    # Initial validation for critical configurations. Bot cannot run without keywords.
    if not KARROT_KEYWORDS:
        log("CRITICAL", "검색 키워드(KARROT_KEYWORDS)가 설정되지 않았습니다. '.env' 파일을 확인해주세요. 봇을 종료합니다.")
        return # Exit if no keywords are set.
    
    # Warn if Telegram is not configured, but allow the bot to run without notifications.
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log("WARN", "텔레그램 봇 토큰 또는 채팅 ID가 설정되지 않아 텔레그램 알림 기능이 비활성화됩니다. '.env' 파일을 확인해주세요.")

    # Load previously seen items at startup to avoid re-notifying.
    load_seen_items()

    log("INFO", f"봇이 매물 감시 모드에 진입합니다. 첫 번째 확인을 시작합니다...")

    while True:
        try:
            current_run_new_items: List[Dict[str, Any]] = []
            log("INFO",
                f"\n{'~'*60}\n새로운 매물 확인 사이클 시작... (현재 시각: {datetime.datetime.now():%Y-%m-%d %H:%M:%S})\n{'~'*60}"
            )

            # Iterate through each keyword configured by the user.
            for keyword_idx, keyword in enumerate(KARROT_KEYWORDS):
                log("INFO",
                    f"[{keyword_idx + 1}/{len(KARROT_KEYWORDS)}] "
                    f"키워드 '{keyword}'에 대한 당근마켓 매물 검색을 시작합니다."
                )
                items_from_keyword = scrape_karrot_market(keyword)
                
                if not items_from_keyword:
                    log("INFO", f"키워드 '{keyword}'에서 이번 사이클에 새로운 매물을 찾지 못했습니다.")
                    continue # Move to the next keyword

                log("INFO", f"키워드 '{keyword}'에서 {len(items_from_keyword)}개의 매물을 찾았습니다. 신규 매물 확인 중...")
                for item in items_from_keyword:
                    # Check if the item URL has been seen before.
                    if item['url'] not in seen_items:
                        log("ALERT",
                            f"✨ 신규 매물 발견! ✨ "
                            f"[{item['keyword']}] - {item['title']} ({item['price']}) - {item['url']}"
                        )
                        current_run_new_items.append(item)
                        # Add to seen_items immediately to prevent duplicate processing
                        # within the same run or subsequent runs in case of early exit.
                        seen_items.add(item['url'])
                    else:
                        log("DEBUG", f"  기존 매물 확인: '{item['title']}' - 스킵.")

            if current_run_new_items:
                log("INFO",
                    f"이번 사이클에서 총 {len(current_run_new_items)}개의 새로운 매물을 찾았습니다. "
                    f"텔레그램으로 알림을 보냅니다."
                )
                for item_idx, item in enumerate(current_run_new_items):
                    log("INFO",
                        f"[{item_idx + 1}/{len(current_run_new_items)}] "
                        f"텔레그램 알림 전송 중: '{item['title']}' ({item['url']})"
                    )
                    message = (
                        f"&lt;b&gt;✨ 새 당근마켓 꿀매물 발견! ✨&lt;/b&gt;\n\n"
                        f"📦 &lt;b&gt;{item['title']}&lt;/b&gt;\n"
                        f"💰 가격: {item['price']}\n"
                        f"📍 지역: {item['region']}\n"
                        f"🔗 &lt;a href='{item['url']}'&gt;매물 바로가기&lt;/a&gt;\n\n"
                        f"#KarrotBlitz #당근마켓 #꿀매물"
                    )
                    send_telegram_message(message)
                    time.sleep(1) # Wait 1 second to prevent Telegram API rate limiting (max 30 msg/sec for bot, 1 msg/sec for chat)
                
                # Save updated seen_items after sending all new item notifications in this cycle.
                save_seen_items()
                log("INFO", "이번 사이클의 모든 신규 매물 알림 전송 및 저장 완료.")
            else:
                log("INFO", "이번 사이클에서는 새로운 매물을 찾지 못했습니다. 다음 확인을 기다립니다.")

        except KeyboardInterrupt:
            # Handle graceful shutdown on Ctrl+C.
            log("INFO", f"\n사용자에 의해 봇이 중지되었습니다. 최종 매물 목록을 저장합니다.")
            save_seen_items()
            log("INFO", "봇이 종료됩니다. 안녕히 계세요! 👋")
            break # Exit the infinite loop.
        except Exception as e:
            # Catch any unexpected errors during the main loop to prevent bot from crashing.
            log("CRITICAL",
                f"봇 실행 중 예상치 못한 치명적인 오류 발생: {e}. "
                f"자세한 내용은 로그를 확인해주세요.", exc_info=True
            )
            log("CRITICAL",
                f"오류 발생에도 불구하고 봇은 안정적인 운영을 위해 "
                f"다음 사이클까지 {CHECK_INTERVAL_SECONDS}초 대기 후 재시도합니다."
            )

        log("INFO", f"다음 매물 확인까지 {CHECK_INTERVAL_SECONDS}초 대기합니다...")
        time.sleep(CHECK_INTERVAL_SECONDS)