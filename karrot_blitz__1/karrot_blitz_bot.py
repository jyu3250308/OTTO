import os
import requests
from bs4 import BeautifulSoup
import time
import json
from dotenv import load_dotenv
import re
import datetime
from typing import List, Dict, Set, Any

# --- Configuration Load and Validation ---
load_dotenv() # .env 파일에서 환경 변수를 로드합니다.

# 텔레그램 봇 토큰 및 채팅 ID
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

# 당근마켓 검색 키워드
# 쉼표(,)로 구분된 키워드 목록. 예: "아이패드,맥북"
KARROT_KEYWORDS_STR: str = os.getenv("KARROT_KEYWORDS", "아이폰,에어팟")
KARROT_KEYWORDS: List[str] = [k.strip() for k in KARROT_KEYWORDS_STR.split(',') if k.strip()]

# 당근마켓 지역 URL
# 전체 당근마켓에서 검색하려면 https://www.daangn.com 을 사용하세요.
# 특정 지역을 지정하려면 https://www.daangn.com/regions/seoul-gangnam-gu 와 같이 사용합니다.
KARROT_BASE_URL: str = os.getenv("KARROT_BASE_URL", "https://www.daangn.com")

# 최소/최대 가격 설정
# .env 파일에 설정이 없거나 잘못된 경우 기본값(0원 ~ 약 10억원)을 사용합니다.
try:
    KARROT_MIN_PRICE: int = int(os.getenv("KARROT_MIN_PRICE", 0))
except ValueError:
    print(f"[{datetime.datetime.now()}] WARN: KARROT_MIN_PRICE 환경 변수가 유효한 숫자가 아닙니다. 기본값 0으로 설정합니다.")
    KARROT_MIN_PRICE = 0

try:
    KARROT_MAX_PRICE: int = int(os.getenv("KARROT_MAX_PRICE", 999999999)) # 약 10억
except ValueError:
    print(f"[{datetime.datetime.now()}] WARN: KARROT_MAX_PRICE 환경 변수가 유효한 숫자가 아닙니다. 기본값 999999999로 설정합니다.")
    KARROT_MAX_PRICE = 999999999

# 매물 확인 간격 (초)
try:
    CHECK_INTERVAL_SECONDS: int = int(os.getenv("CHECK_INTERVAL_SECONDS", 60))
    if CHECK_INTERVAL_SECONDS < 10:
        print(f"[{datetime.datetime.now()}] WARN: CHECK_INTERVAL_SECONDS가 너무 짧습니다 ({CHECK_INTERVAL_SECONDS}초). IP 차단 위험이 있으니 30초 이상으로 설정하는 것을 권장합니다. 60초로 재설정합니다.")
        CHECK_INTERVAL_SECONDS = 60
except ValueError:
    print(f"[{datetime.datetime.now()}] WARN: CHECK_INTERVAL_SECONDS 환경 변수가 유효한 숫자가 아닙니다. 기본값 60초로 설정합니다.")
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
    print(f"[{datetime.datetime.now()}] INFO: '{SEEN_ITEMS_FILE}' 파일에서 이전에 발견된 매물을 로드 시도 중...")
    if os.path.exists(SEEN_ITEMS_FILE):
        try:
            with open(SEEN_ITEMS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    seen_items = set(data)
                    print(f"[{datetime.datetime.now()}] INFO: '{SEEN_ITEMS_FILE}' 파일에서 {len(seen_items)}개의 매물을 성공적으로 불러왔습니다.")
                else:
                    print(f"[{datetime.datetime.now()}] WARN: '{SEEN_ITEMS_FILE}' 파일 내용이 유효한 리스트 형태가 아닙니다. 파일을 초기화합니다.")
                    seen_items = set()
        except json.JSONDecodeError as e:
            print(f"[{datetime.datetime.now()}] ERROR: '{SEEN_ITEMS_FILE}' 파일 파싱 중 오류 발생 ({e}). 파일이 손상되었거나 비어있습니다. 새로 시작합니다.")
            seen_items = set()
        except IOError as e:
            print(f"[{datetime.datetime.now()}] ERROR: '{SEEN_ITEMS_FILE}' 파일 읽기 중 I/O 오류 발생 ({e}). 새로 시작합니다.")
            seen_items = set()
    else:
        print(f"[{datetime.datetime.now()}] INFO: '{SEEN_ITEMS_FILE}' 파일이 존재하지 않아 새로 생성합니다.")
        seen_items = set()

def save_seen_items() -> None:
    """
    현재 `seen_items` 집합에 있는 매물 URL 목록을 JSON 형식으로 SEEN_ITEMS_FILE에 저장합니다.
    """
    try:
        with open(SEEN_ITEMS_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(seen_items), f, ensure_ascii=False, indent=2)
        print(f"[{datetime.datetime.now()}] INFO: 현재까지 발견된 매물 {len(seen_items)}개를 '{SEEN_ITEMS_FILE}' 파일에 성공적으로 저장했습니다.")
    except IOError as e:
        print(f"[{datetime.datetime.now()}] ERROR: '{SEEN_ITEMS_FILE}' 파일 쓰기 중 I/O 오류 발생: {e}")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] ERROR: 매물 저장 중 예상치 못한 오류 발생: {e}")

def send_telegram_message(message: str) -> bool:
    """
    지정된 메시지를 텔레그램 봇을 통해 전송합니다.
    텔레그램 토큰 또는 채팅 ID가 설정되지 않은 경우 메시지를 보내지 않습니다.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[{datetime.datetime.now()}] WARN: 텔레그램 봇 토큰 또는 채팅 ID가 설정되지 않았습니다. 메시지를 보낼 수 없습니다.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML", # HTML 포맷 사용
        "disable_web_page_preview": False # 링크 미리보기 허용
    }
    try:
        print(f"[{datetime.datetime.now()}] INFO: 텔레그램 메시지 전송 시도 중...")
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status() # 200 이외의 응답 코드는 예외 발생
        print(f"[{datetime.datetime.now()}] INFO: 텔레그램 메시지 전송 성공.")
        return True
    except requests.exceptions.Timeout:
        print(f"[{datetime.datetime.now()}] ERROR: 텔레그램 메시지 전송 실패 - 요청 시간 초과 (Timeout).")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"[{datetime.datetime.now()}] ERROR: 텔레그램 메시지 전송 실패 - HTTP 오류 발생: {e} (응답: {e.response.text if e.response else 'N/A'})")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"[{datetime.datetime.now()}] ERROR: 텔레그램 메시지 전송 실패 - 네트워크 연결 오류: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.datetime.now()}] ERROR: 텔레그램 메시지 전송 중 알 수 없는 요청 오류 발생: {e}")
        return False

def clean_price_string(price_str: str) -> int:
    """
    가격 문자열에서 숫자만 추출하여 int로 변환합니다. '무료나눔' 등 숫자가 아닌 경우 0으로 처리합니다.
    """
    cleaned_str = price_str.replace('원', '').replace(',', '').strip()
    try:
        return int(cleaned_str)
    except ValueError:
        # '무료나눔', '가격제안' 등 숫자로 변환할 수 없는 경우 0으로 처리
        return 0

# --- Karrot Market Scraper ---
def scrape_karrot_market(keyword: str) -> List[Dict[str, Any]]:
    """
    주어진 키워드로 당근마켓을 스크래핑하여 새로운 매물 목록을 반환합니다.
    """
    search_url = f"{KARROT_BASE_URL}/search/{keyword}"
    
    # 가격 필터링 파라미터 설정
    params: Dict[str, Any] = {}
    if KARROT_MIN_PRICE > 0: # 최소 가격이 0보다 큰 경우에만 파라미터 추가
        params["min_price"] = KARROT_MIN_PRICE
    if KARROT_MAX_PRICE < 999999999: # 최대 가격이 기본값보다 작은 경우에만 파라미터 추가
        params["max_price"] = KARROT_MAX_PRICE

    # 검색 URL에 가격 파라미터 추가
    if params:
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        search_url = f"{search_url}?{query_string}"

    print(f"[{datetime.datetime.now()}] INFO: '{keyword}' 키워드로 당근마켓 검색 요청 중: {search_url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    found_items: List[Dict[str, Any]] = []
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status() # 200 이외의 응답 코드는 예외 발생
        
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = soup.select('article.flea-market-article')
        
        if not articles:
            print(f"[{datetime.datetime.now()}] INFO: '{keyword}' 키워드에 대한 매물을 찾을 수 없거나, HTML 구조가 변경되었을 수 있습니다. (URL: {search_url})")
            return []

        for article in articles:
            link_tag = article.select_one('a.flea-market-article-link')
            title_tag = article.select_one('h2.article-title')
            price_tag = article.select_one('p.article-price')
            region_tag = article.select_one('p.article-region-name')

            # 필수 요소가 모두 존재하는지 확인
            if all([link_tag, title_tag, price_tag, region_tag]):
                item_url = "https://www.daangn.com" + link_tag['href']
                item_title = title_tag.get_text(strip=True)
                item_price_str = price_tag.get_text(strip=True)
                item_region = region_tag.get_text(strip=True)

                item_price_numeric = clean_price_string(item_price_str)

                # 파싱된 가격이 설정된 최소/최대 가격 범위 내에 있는지 다시 확인 (스크래핑 시점 기준)
                if KARROT_MIN_PRICE <= item_price_numeric <= KARROT_MAX_PRICE:
                    found_items.append({
                        'title': item_title,
                        'price': item_price_str, # 원본 가격 문자열 유지
                        'region': item_region,
                        'url': item_url,
                        'keyword': keyword # 어떤 키워드에서 발견되었는지 기록
                    })
        print(f"[{datetime.datetime.now()}] INFO: '{keyword}' 키워드에서 {len(found_items)}개의 매물을 발견했습니다.")
        return found_items

    except requests.exceptions.Timeout:
        print(f"[{datetime.datetime.now()}] ERROR: 당근마켓 스크래핑 중 시간 초과 (Timeout) 발생 (키워드: '{keyword}', URL: {search_url})")
    except requests.exceptions.HTTPError as e:
        print(f"[{datetime.datetime.now()}] ERROR: 당근마켓 스크래핑 중 HTTP 오류 발생: {e} (키워드: '{keyword}', URL: {search_url}, 응답: {e.response.status_code if e.response else 'N/A'})")
    except requests.exceptions.ConnectionError as e:
        print(f"[{datetime.datetime.now()}] ERROR: 당근마켓 스크래핑 중 네트워크 연결 오류 발생: {e} (키워드: '{keyword}', URL: {search_url})")
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.datetime.now()}] ERROR: 당근마켓 스크래핑 중 알 수 없는 요청 오류 발생: {e} (키워드: '{keyword}', URL: {search_url})")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] CRITICAL: 당근마켓 스크래핑 중 예상치 못한 치명적인 오류 발생: {e} (키워드: '{keyword}', URL: {search_url})")
    return []

# --- Main Bot Logic ---
def run_bot() -> None:
    """
    Karrot Blitz 봇의 메인 실행 로직입니다. 설정된 간격마다 당근마켓을 스크래핑하고 알림을 보냅니다.
    """
    global seen_items

    print(f"\n{'='*50}")
    print(f"[{datetime.datetime.now()}] INFO: Karrot Blitz 봇이 시작됩니다.")
    print(f"{'='*50}")
    print(f"[{datetime.datetime.now()}] INFO: 현재 설정 요약:")
    print(f"  - 검색 키워드: '{', '.join(KARROT_KEYWORDS) if KARROT_KEYWORDS else '설정되지 않음'}'")
    print(f"  - 검색 기본 URL: '{KARROT_BASE_URL}'")
    print(f"  - 가격 범위: {KARROT_MIN_PRICE:n}원 ~ {KARROT_MAX_PRICE:n}원")
    print(f"  - 체크 간격: {CHECK_INTERVAL_SECONDS}초")
    print(f"  - 텔레그램 알림: {'활성화' if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else '비활성화 (토큰/ID 누락)'}")
    print(f"{'='*50}")

    if not KARROT_KEYWORDS:
        print(f"[{datetime.datetime.now()}] CRITICAL: 검색 키워드(KARROT_KEYWORDS)가 설정되지 않았습니다. .env 파일을 확인해주세요. 봇을 종료합니다.")
        return
    
    # 이전에 발견된 매물 목록을 불러옵니다.
    load_seen_items()

    while True:
        try:
            current_run_new_items: List[Dict[str, Any]] = []
            print(f"\n[{datetime.datetime.now()}] INFO: 새로운 매물 확인 사이클 시작...")

            for keyword in KARROT_KEYWORDS:
                print(f"[{datetime.datetime.now()}] INFO: 키워드 '{keyword}'에 대한 매물 검색 중...")
                items = scrape_karrot_market(keyword)
                
                if not items:
                    print(f"[{datetime.datetime.now()}] INFO: 키워드 '{keyword}'에서 새로운 매물을 찾지 못했습니다.")
                    continue

                for item in items:
                    # URL을 기준으로 이전에 본 적 없는 매물인지 확인
                    if item['url'] not in seen_items:
                        print(f"[{datetime.datetime.now()}] ALERT: 새 매물 발견! [{keyword}] - {item['title']} ({item['price']}) - {item['url']}")
                        current_run_new_items.append(item)
                        seen_items.add(item['url']) # 발견 즉시 seen_items에 추가
                    # else:
                        # print(f"[{datetime.datetime.now()}] DEBUG: 이미 확인된 매물: {item['title']}") # 디버깅용

            if current_run_new_items:
                print(f"[{datetime.datetime.now()}] INFO: 이번 사이클에서 총 {len(current_run_new_items)}개의 새로운 매물을 찾았습니다. 텔레그램으로 알림을 보냅니다.")
                for item in current_run_new_items:
                    message = (
                        f"<b>✨ 새 당근마켓 꿀매물 발견! ✨</b>\n\n"
                        f"📦 <b>{item['title']}</b>\n"
                        f"💰 가격: {item['price']}\n"
                        f"📍 지역: {item['region']}\n"
                        f"🔗 <a href='{item['url']}'>매물 바로가기</a>\n\n"
                        f"#KarrotBlitz #당근마켓 #꿀매물"
                    )
                    send_telegram_message(message)
                    time.sleep(1) # 텔레그램 API 요청 과부하 방지를 위해 1초 대기
                save_seen_items() # 새로운 매물 알림 후, 변경된 seen_items를 저장
            else:
                print(f"[{datetime.datetime.now()}] INFO: 이번 사이클에서는 새로운 매물을 찾지 못했습니다.")

        except KeyboardInterrupt:
            print(f"\n[{datetime.datetime.now()}] INFO: 사용자에 의해 봇이 중지되었습니다. 최종 매물 목록을 저장합니다.")
            save_seen_items()
            break
        except Exception as e:
            print(f"[{datetime.datetime.now()}] CRITICAL: 봇 실행 중 예상치 못한 치명적인 오류 발생: {e}")
            print(f"[{datetime.datetime.now()}] CRITICAL: 오류 발생에도 불구하고 봇은 다음 사이클을 위해 {CHECK_INTERVAL_SECONDS}초 대기합니다.")
            # 치명적인 오류 발생 시에도 봇이 멈추지 않고 재시도하도록 설정 (필요에 따라 종료 또는 로직 변경 가능)

        print(f"[{datetime.datetime.now()}] INFO: 다음 확인까지 {CHECK_INTERVAL_SECONDS}초 대기합니다...")
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_bot()
