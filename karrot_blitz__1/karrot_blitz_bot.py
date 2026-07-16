import os
import requests
from bs4 import BeautifulSoup
import time
import json
from dotenv import load_dotenv
import re
import datetime
import traceback # Added for detailed error logging
from typing import List, Dict, Set, Any, Optional

# --- Constants & Configuration Loading ---

# Load environment variables from .env file
load_dotenv()

# Logger function for consistent output
def log(level: str, message: str, exc_info: bool = False) -> None:
    """Prints a formatted log message with a timestamp and specified level."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{level.upper()}]: {message}"
    if exc_info:
        log_message += f"\n{traceback.format_exc()}" # Append traceback if requested
    print(log_message)

# 텔레그램 봇 토큰 및 채팅 ID
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "").strip()

# 당근마켓 검색 키워드
# 쉼표(,)로 구분된 키워드 목록. 예: "아이패드,맥북"
KARROT_KEYWORDS_STR: str = os.getenv("KARROT_KEYWORDS", "아이폰,에어팟").strip()
KARROT_KEYWORDS: List[str] = [k.strip() for k in KARROT_KEYWORDS_STR.split(',') if k.strip()]

# 당근마켓 지역 URL
# 전체 당근마켓에서 검색하려면 https://www.daangn.com 을 사용합니다.
# 특정 지역을 지정하려면 https://www.daangn.com/regions/seoul-gangnam-gu 와 같이 사용합니다.
KARROT_BASE_URL: str = os.getenv("KARROT_BASE_URL", "https://www.daangn.com").strip()
if not KARROT_BASE_URL:
    KARROT_BASE_URL = "https://www.daangn.com" # Fallback if empty string is provided

# 최소/최대 가격 설정
# .env 파일에 설정이 없거나 잘못된 경우 기본값(0원 ~ 약 10억원)을 사용합니다.
DEFAULT_MAX_PRICE = 999999999 # Roughly 1 billion KRW
KARROT_MIN_PRICE: int
KARROT_MAX_PRICE: int

try:
    KARROT_MIN_PRICE = int(os.getenv("KARROT_MIN_PRICE", "0"))
except ValueError:
    log("WARN", "KARROT_MIN_PRICE 환경 변수가 유효한 숫자가 아닙니다. 기본값 0으로 설정합니다.")
    KARROT_MIN_PRICE = 0

try:
    KARROT_MAX_PRICE = int(os.getenv("KARROT_MAX_PRICE", str(DEFAULT_MAX_PRICE)))
except ValueError:
    log("WARN", f"KARROT_MAX_PRICE 환경 변수가 유효한 숫자가 아닙니다. 기본값 {DEFAULT_MAX_PRICE:n}으로 설정합니다.")
    KARROT_MAX_PRICE = DEFAULT_MAX_PRICE

# 매물 확인 간격 (초)
MIN_CHECK_INTERVAL = 30 # Recommended minimum interval to prevent IP blocking
CHECK_INTERVAL_SECONDS: int

try:
    CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
    if CHECK_INTERVAL_SECONDS < MIN_CHECK_INTERVAL:
        log("WARN", f"CHECK_INTERVAL_SECONDS가 너무 짧습니다 ({CHECK_INTERVAL_SECONDS}초). IP 차단 위험이 있으니 {MIN_CHECK_INTERVAL}초 이상으로 설정하는 것을 권장합니다. {MIN_CHECK_INTERVAL}초로 재설정합니다.")
        CHECK_INTERVAL_SECONDS = MIN_CHECK_INTERVAL
except ValueError:
    log("WARN", f"CHECK_INTERVAL_SECONDS 환경 변수가 유효한 숫자가 아닙니다. 기본값 60초로 설정합니다.")
    CHECK_INTERVAL_SECONDS = 60

# 이전에 발견된 매물 정보를 저장할 파일
SEEN_ITEMS_FILE: str = "seen_items.json"

# --- Global Variables ---
# 이전에 텔레그램 알림을 보냈던 매물의 URL을 저장하는 집합
seen_items: Set[str] = set()

# --- Utility Functions ---
def load_seen_items() -> None:
    """
    SEEN_ITEMS_FILE에서 이전에 발견된 매물 URL 목록을 로드하여 `seen_items` 전역 변수에 저장합니다.
    파일이 없거나 손상된 경우 새로운 집합을 초기화합니다.
    """
    global seen_items
    log("INFO", f"'{SEEN_ITEMS_FILE}' 파일에서 이전에 발견된 매물을 로드 시도 중...")
    if os.path.exists(SEEN_ITEMS_FILE):
        try:
            with open(SEEN_ITEMS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    seen_items = set(data)
                    log("INFO", f"'{SEEN_ITEMS_FILE}' 파일에서 {len(seen_items)}개의 매물을 성공적으로 불러왔습니다.")
                else:
                    log("WARN", f"'{SEEN_ITEMS_FILE}' 파일 내용이 유효한 리스트 형태가 아닙니다. 파일을 초기화합니다.")
                    seen_items = set()
        except json.JSONDecodeError as e:
            log("ERROR", f"'{SEEN_ITEMS_FILE}' 파일 파싱 중 오류 발생 ({e}). 파일이 손상되었거나 비어있을 수 있습니다. 새로 시작합니다.")
            seen_items = set()
        except IOError as e:
            log("ERROR", f"'{SEEN_ITEMS_FILE}' 파일 읽기 중 I/O 오류 발생 ({e}). 새로 시작합니다.")
            seen_items = set()
    else:
        log("INFO", f"'{SEEN_ITEMS_FILE}' 파일이 존재하지 않아 새로 생성합니다.")
        seen_items = set()

def save_seen_items() -> None:
    """
    현재 `seen_items` 집합에 있는 매물 URL 목록을 JSON 형식으로 SEEN_ITEMS_FILE에 저장합니다.
    """
    try:
        with open(SEEN_ITEMS_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(seen_items), f, ensure_ascii=False, indent=2)
        log("INFO", f"현재까지 발견된 매물 {len(seen_items)}개를 '{SEEN_ITEMS_FILE}' 파일에 성공적으로 저장했습니다.")
    except IOError as e:
        log("ERROR", f"'{SEEN_ITEMS_FILE}' 파일 쓰기 중 I/O 오류 발생: {e}")
    except Exception as e:
        log("ERROR", f"매물 저장 중 예상치 못한 오류 발생: {e}", exc_info=True)

def send_telegram_message(message: str) -> bool:
    """
    지정된 메시지를 텔레그램 봇을 통해 전송합니다.
    텔레그램 토큰 또는 채팅 ID가 설정되지 않은 경우 메시지를 보내지 않습니다.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log("WARN", "텔레그램 봇 토큰 또는 채팅 ID가 설정되지 않았습니다. 메시지를 보낼 수 없습니다.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML", # HTML 포맷 사용
        "disable_web_page_preview": False # 링크 미리보기 허용
    }
    try:
        log("INFO", "텔레그램 메시지 전송 시도 중...")
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status() # 200 이외의 응답 코드는 예외 발생
        log("INFO", "텔레그램 메시지 전송 성공.")
        return True
    except requests.exceptions.Timeout:
        log("ERROR", "텔레그램 메시지 전송 실패 - 요청 시간 초과 (Timeout).")
        return False
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 'N/A'
        response_text = e.response.text if e.response else 'N/A'
        log("ERROR", f"텔레그램 메시지 전송 실패 - HTTP 오류 발생: {e} (Status: {status_code}, 응답: {response_text})")
        return False
    except requests.exceptions.ConnectionError as e:
        log("ERROR", f"텔레그램 메시지 전송 실패 - 네트워크 연결 오류: {e}")
        return False
    except requests.exceptions.RequestException as e:
        log("ERROR", f"텔레그램 메시지 전송 중 알 수 없는 요청 오류 발생: {e}")
        return False

def clean_price_string(price_str: str) -> int:
    """
    가격 문자열에서 숫자만 추출하여 int로 변환합니다. '무료나눔' 등 숫자가 아닌 경우 0으로 처리합니다.
    """
    # Remove all non-digit characters. 'r' prefix for raw string to handle backslashes.
    cleaned_str = re.sub(r'[^\\d]', '', price_str) # \\d for \d in JSON string
    try:
        return int(cleaned_str)
    except ValueError:
        # '무료나눔', '가격제안' 등 숫자로 변환할 수 없는 경우 또는 빈 문자열인 경우 0으로 처리
        return 0

# --- Karrot Market Scraper ---
def scrape_karrot_market(keyword: str) -> List[Dict[str, Any]]:
    """
    주어진 키워드로 당근마켓을 스크래핑하여 새로운 매물 목록을 반환합니다.
    설정된 최소/최대 가격 범위 내의 매물만 필터링합니다.
    """
    # Construct search URL with optional price filters
    search_url_base = f"{KARROT_BASE_URL}/search/{keyword}"
    
    params: Dict[str, Any] = {}
    # Only add min_price param if it's greater than 0 to avoid unnecessary query string for default (0)
    if KARROT_MIN_PRICE > 0:
        params["min_price"] = KARROT_MIN_PRICE
    # Only add max_price param if it's less than the default max price
    if KARROT_MAX_PRICE < DEFAULT_MAX_PRICE:
        params["max_price"] = KARROT_MAX_PRICE

    # Append query parameters if any
    search_url = search_url_base
    if params:
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        search_url = f"{search_url_base}?{query_string}"

    log("INFO", f"'{keyword}' 키워드로 당근마켓 검색 요청 중: {search_url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    found_items: List[Dict[str, Any]] = []
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Select all article elements that represent a flea market item
        articles = soup.select('article.flea-market-article')
        
        if not articles:
            log("INFO", f"'{keyword}' 키워드에 대한 매물을 찾을 수 없거나, HTML 구조가 변경되었을 수 있습니다. (URL: {search_url})")
            return []

        for article in articles:
            # Extract relevant information using robust selectors
            link_tag = article.select_one('a.flea-market-article-link')
            title_tag = article.select_one('h2.article-title')
            price_tag = article.select_one('p.article-price')
            region_tag = article.select_one('p.article-region-name')
            
            # Ensure all critical elements are found to avoid NoneType errors
            if all([link_tag, title_tag, price_tag, region_tag]):
                item_url = "https://www.daangn.com" + link_tag['href']
                item_title = title_tag.get_text(strip=True)
                item_price_str = price_tag.get_text(strip=True)
                item_region = region_tag.get_text(strip=True)

                item_price_numeric = clean_price_string(item_price_str)

                # Re-verify price against configured min/max, in case URL filtering was imperfect or for '무료나눔' type items
                if KARROT_MIN_PRICE <= item_price_numeric <= KARROT_MAX_PRICE:
                    found_items.append({
                        'title': item_title,
                        'price': item_price_str, # Keep original price string for display
                        'region': item_region,
                        'url': item_url,
                        'keyword': keyword # Record which keyword found this item
                    })

        log("INFO", f"키워드 '{keyword}'에서 {len(found_items)}개의 유효한 매물을 발견했습니다.")
        return found_items

    except requests.exceptions.Timeout:
        log("ERROR", f"당근마켓 스크래핑 중 시간 초과 (Timeout) 발생 (키워드: '{keyword}', URL: {search_url})")
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 'N/A'
        log("ERROR", f"당근마켓 스크래핑 중 HTTP 오류 발생: {e} (키워드: '{keyword}', URL: {search_url}, Status: {status_code})")
        if status_code == 403:
            log("WARN", "403 Forbidden: IP 차단 또는 요청 제한이 의심됩니다. CHECK_INTERVAL_SECONDS를 늘려주세요.")
    except requests.exceptions.ConnectionError as e:
        log("ERROR", f"당근마켓 스크래핑 중 네트워크 연결 오류 발생: {e} (키워드: '{keyword}', URL: {search_url})")
    except requests.exceptions.RequestException as e:
        log("ERROR", f"당근마켓 스크래핑 중 알 수 없는 요청 오류 발생: {e} (키워드: '{keyword}', URL: {search_url})")
    except Exception as e:
        log("CRITICAL", f"당근마켓 스크래핑 중 예상치 못한 치명적인 오류 발생: {e}", exc_info=True)
    return []

# --- Main Bot Logic ---
def run_bot() -> None:
    """
    Karrot Blitz 봇의 메인 실행 로직입니다. 설정된 간격마다 당근마켓을 스크래핑하고 알림을 보냅니다.
    """
    global seen_items

    log("INFO", f"\n{'='*60}\nKarrot Blitz 봇이 시작됩니다.\n{'='*60}")
    log("INFO", "현재 설정 요약:")
    log("INFO", f"  - 검색 키워드: '{', '.join(KARROT_KEYWORDS) if KARROT_KEYWORDS else '설정되지 않음'}'")
    log("INFO", f"  - 검색 기본 URL: '{KARROT_BASE_URL}'")
    log("INFO", f"  - 가격 범위: {KARROT_MIN_PRICE:n}원 ~ {KARROT_MAX_PRICE:n}원")
    log("INFO", f"  - 체크 간격: {CHECK_INTERVAL_SECONDS}초")
    log("INFO", f"  - 텔레그램 알림: {'활성화' if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else '비활성화 (토큰 또는 채팅 ID 누락)'}")
    log("INFO", f"{'='*60}")

    # Initial validation for critical configurations
    if not KARROT_KEYWORDS:
        log("CRITICAL", "검색 키워드(KARROT_KEYWORDS)가 설정되지 않았습니다. .env 파일을 확인해주세요. 봇을 종료합니다.")
        return
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log("WARN", "텔레그램 봇 토큰 또는 채팅 ID가 설정되지 않아 텔레그램 알림 기능이 비활성화됩니다. .env 파일을 확인해주세요.")
        # Bot can still run, just won't send Telegram messages

    # Load previously seen items at startup
    load_seen_items()

    while True:
        try:
            current_run_new_items: List[Dict[str, Any]] = []
            log("INFO", f"\n{'~'*50}\n새로운 매물 확인 사이클 시작... (현재 시각: {datetime.datetime.now():%Y-%m-%d %H:%M:%S})\n{'~'*50}")

            for keyword_idx, keyword in enumerate(KARROT_KEYWORDS):
                log("INFO", f"[{keyword_idx + 1}/{len(KARROT_KEYWORDS)}] 키워드 '{keyword}'에 대한 매물 검색 중...")
                items_from_keyword = scrape_karrot_market(keyword)
                
                if not items_from_keyword:
                    log("INFO", f"키워드 '{keyword}'에서 이번 사이클에 새로운 매물을 찾지 못했습니다.")
                    continue

                for item in items_from_keyword:
                    # Check if the item URL has been seen before
                    if item['url'] not in seen_items:
                        log("ALERT", f"새 매물 발견! [{item['keyword']}] - {item['title']} ({item['price']}) - {item['url']}")
                        current_run_new_items.append(item)
                        seen_items.add(item['url']) # Add to seen_items immediately to prevent duplicate processing within the same run or subsequent runs

            if current_run_new_items:
                log("INFO", f"이번 사이클에서 총 {len(current_run_new_items)}개의 새로운 매물을 찾았습니다. 텔레그램으로 알림을 보냅니다.")
                for item_idx, item in enumerate(current_run_new_items):
                    log("INFO", f"[{item_idx + 1}/{len(current_run_new_items)}] 텔레그램 알림 전송 중: '{item['title']}'...")
                    message = (
                        f"<b>✨ 새 당근마켓 꿀매물 발견! ✨</b>\n\n"
                        f"📦 <b>{item['title']}</b>\n"
                        f"💰 가격: {item['price']}\n"
                        f"📍 지역: {item['region']}\n"
                        f"🔗 <a href='{item['url']}'>매물 바로가기</a>\n\n"
                        f"#KarrotBlitz #당근마켓 #꿀매물"
                    )
                    send_telegram_message(message)
                    time.sleep(1) # Wait 1 second to prevent Telegram API rate limiting
                save_seen_items() # Save updated seen_items after sending all new item notifications
            else:
                log("INFO", "이번 사이클에서는 새로운 매물을 찾지 못했습니다.")

        except KeyboardInterrupt:
            log("INFO", f"\n사용자에 의해 봇이 중지되었습니다. 최종 매물 목록을 저장합니다.")
            save_seen_items()
            break # Exit the infinite loop
        except Exception as e:
            log("CRITICAL", f"봇 실행 중 예상치 못한 치명적인 오류 발생: {e}", exc_info=True)
            log("CRITICAL", f"오류 발생에도 불구하고 봇은 다음 사이클을 위해 {CHECK_INTERVAL_SECONDS}초 대기 후 재시도합니다.")

        log("INFO", f"다음 확인까지 {CHECK_INTERVAL_SECONDS}초 대기합니다...")
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_bot()
