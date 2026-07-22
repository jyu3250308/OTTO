import os
import requests
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from google import genai
from google.genai import types
from apscheduler.schedulers.background import BackgroundScheduler

# --- Configuration & Setup ---
load_dotenv()

# Logger setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
SCHEDULE_HOUR = int(os.getenv('SCHEDULE_HOUR', 9))  # 기본값: KST 오전 9시
SCHEDULE_MINUTE = int(os.getenv('SCHEDULE_MINUTE', 0))  # 기본값: 0분

# Constants
DEFAULT_NUM_ARTICLES_PER_SOURCE = 5

# 필수 환경 변수 누락 시 프로그램 즉시 종료
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    logger.error("환경 변수 누락: TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 설정되지 않았습니다. .env 파일을 확인해 주세요.")
    exit(1)

if not GEMINI_API_KEY:
    logger.error("환경 변수 누락: GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해 주세요.")
    exit(1)

# Initialize Gemini Client
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info("✅ Gemini API 클라이언트 초기화 완료.")
except Exception as e:
    logger.error(f"❌ Gemini API 클라이언트 초기화 실패: {e}")
    exit(1)

# --- News Scraping ---

def fetch_news_from_yahoo_finance(num_articles: int = DEFAULT_NUM_ARTICLES_PER_SOURCE) -> list:
    """Yahoo Finance에서 최신 금융 뉴스 헤드라인, 링크 및 요약 내용을 가져옵니다."""
    url = "https://finance.yahoo.com/news/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    articles = []
    logger.info(f"➡️ Yahoo Finance ({url})에서 뉴스 기사 {num_articles}개 가져오는 중...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Yahoo Finance 뉴스 기사 stream-item 파싱
        news_items = soup.find_all('li', class_='stream-item')

        count = 0
        for item in news_items:
            if count >= num_articles:
                break
            
            title, link, summary_text = None, None, None

            # 첫 번째 패턴
            link_tag_main = item.find('a', class_='Fw(b) Fz(20px) Lh(23px) LineClamp(2,46px) C($primaryColor) Td(n) D(ib) My(-1px) rpt-grid-layout__title')
            summary_tag_main = item.find('p', class_='Fz(14px) Lh(19px) LineClamp(3,57px) Mt(6px) C($primaryColor) rpt-grid-layout__summary')

            if link_tag_main and summary_tag_main:
                title = link_tag_main.get_text(strip=True)
                link = "https://finance.yahoo.com" + link_tag_main['href']
                summary_text = summary_tag_main.get_text(strip=True)
            else:
                # 두 번째 패턴
                link_tag_alt = item.find('a', {'data-test-id': 'StreamArticleTitle'})
                summary_tag_alt = item.find('p', {'data-test-id': 'StreamArticleSummary'})
                if link_tag_alt and summary_tag_alt:
                    title = link_tag_alt.get_text(strip=True)
                    link = "https://finance.yahoo.com" + link_tag_alt['href']
                    summary_text = summary_tag_alt.get_text(strip=True)
            
            if title and link and summary_text:
                articles.append({'title': title, 'link': link, 'content': summary_text})
                logger.debug(f"[Yahoo Finance] 기사 발견: '{title}'")
                count += 1

    except Exception as e:
        logger.error(f"❌ Yahoo Finance 뉴스 크롤링 중 오류 발생: {e}")
    finally:
        logger.info(f"✅ Yahoo Finance에서 총 {len(articles)}개의 기사를 가져왔습니다.")
    return articles

def fetch_news_from_investing_com(num_articles: int = DEFAULT_NUM_ARTICLES_PER_SOURCE) -> list:
    """Investing.com에서 최신 금융 뉴스 헤드라인, 링크 및 요약 내용을 가져옵니다."""
    url = "https://www.investing.com/news/stock-market-news"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.investing.com/'
    }
    articles = []
    logger.info(f"➡️ Investing.com ({url})에서 뉴스 기사 {num_articles}개 가져오는 중...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        news_items = soup.find_all('article', class_='js-article-item', limit=num_articles)

        for item in news_items:
            link_tag = item.find('a', class_='title')
            summary_tag = item.find('p', class_='textDiv')
            
            if link_tag and summary_tag:
                title = link_tag.get_text(strip=True)
                link = "https://www.investing.com" + link_tag['href']
                summary_text = summary_tag.get_text(strip=True)
                articles.append({'title': title, 'link': link, 'content': summary_text})
                logger.debug(f"[Investing.com] 기사 발견: '{title}'")

    except Exception as e:
        logger.error(f"❌ Investing.com 뉴스 크롤링 중 오류 발생: {e}")
    finally:
        logger.info(f"✅ Investing.com에서 총 {len(articles)}개의 기사를 가져왔습니다.")
    return articles

def fetch_all_news(num_articles_per_source: int = DEFAULT_NUM_ARTICLES_PER_SOURCE) -> list:
    """여러 금융 뉴스 출처에서 뉴스를 종합하여 가져옵니다."""
    logger.info("📰 모든 뉴스 출처에서 뉴스 가져오기 시작...")
    all_news = []
    all_news.extend(fetch_news_from_yahoo_finance(num_articles_per_source))
    all_news.extend(fetch_news_from_investing_com(num_articles_per_source))
    logger.info(f"✅ 총 {len(all_news)}개의 기사를 가져왔습니다.")
    return all_news

# --- Gemini API AI Processing ---

def analyze_sentiment(text: str) -> str:
    """Gemini API를 사용하여 기사 본문의 시장 감성을 분석하여 '긍정', '부정', '중립' 중 하나를 반환합니다."""
    if not text or not text.strip():
        return "중립"

    prompt = (
        "너는 금융 시장 심리 분석가야. 다음 뉴스 내용을 바탕으로 시장 참여자들의 심리를 "
        "'긍정', '부정', '중립' 중 딱 하나로만 대답해줘. 다른 설명이나 수식어는 절대 넣지 말고 "
        "오직 '긍정', '부정', '중립' 세 단어 중 하나만 텍스트로 반환해.\n\n"
        f"뉴스 내용: {text}"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        result = response.text.strip()
        if "긍정" in result:
            return "긍정"
        elif "부정" in result:
            return "부정"
        else:
            return "중립"
    except Exception as e:
        logger.error(f"❌ Gemini 감성 분석 실패: {e}")
        return "중립"

def summarize_text(text: str) -> str:
    """Gemini API를 사용하여 기사를 한국어로 번역 및 최대 3문장 요약합니다."""
    if not text or not text.strip():
        return "요약 불가."

    prompt = (
        "너는 금융 전문 기자이자 요약 에이전트야. 다음 제공되는 뉴스 기사 내용(영어일 수 있음)을 "
        "한국어로 자연스럽게 번역하면서, 핵심 금융 동향 위주로 최대 3문장 이내로 명확하게 요약해줘.\n"
        "설명글이나 인사말, 주석 같은 부가 텍스트는 일체 쓰지 말고 오직 요약문만 반환해.\n\n"
        f"기사 내용:\n{text}"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        summary = response.text.strip()
        return summary
    except Exception as e:
        logger.error(f"❌ Gemini 요약 생성 실패: {e}")
        return "AI 요약 실패."

def calculate_ant_sentiment_index(sentiments: list) -> str:
    """뉴스 감성 분포를 통해 최종 개미 심리지수를 결정합니다."""
    if not sentiments:
        return "중립"

    positive_count = sentiments.count("긍정")
    negative_count = sentiments.count("부정")
    total = len(sentiments)

    pos_ratio = positive_count / total
    neg_ratio = negative_count / total

    # 긍정/부정 비율이 20%p 이상 차이 날 때 강한 감성으로 진단
    if pos_ratio > neg_ratio + 0.2:
        return "긍정 📈"
    elif neg_ratio > pos_ratio + 0.2:
        return "부정 📉"
    else:
        return "중립 ⚖️"

# --- Telegram Alerter (direct HTTP requests) ---

def send_telegram_message(message: str) -> None:
    """python-telegram-bot 라이브러리 없이 HTTP requests를 직접 이용해 메시지를 안전하게 전송합니다."""
    logger.info("💬 Telegram 메시지 전송 시도 중...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            logger.info("✅ Telegram 메시지 전송 성공.")
        else:
            logger.error(f"❌ Telegram 메시지 전송 실패 (HTTP {response.status_code}): {response.text}")
    except Exception as e:
        logger.error(f"❌ Telegram 메시지 전송 중 예외 발생: {e}")

# --- Main Logic ---

def daily_market_morse():
    """매일 금융 뉴스를 수집, 분석하여 텔레그램 채널로 리포트를 발행합니다."""
    logger.info("🚀 --- Daily Market Morse 작업 시작 --- 🚀")
    current_time_kst = datetime.now().strftime("%Y-%m-%d %H:%M KST")
    
    # 1. 뉴스 기사 가져오기
    news_articles = fetch_all_news(DEFAULT_NUM_ARTICLES_PER_SOURCE)
    
    if not news_articles:
        logger.warning("⚠️ 가져온 뉴스 기사가 없습니다. 발행 작업을 중단합니다.")
        send_telegram_message(
            f"⚠️ *[삐빅! 김개미 비상: {current_time_kst}]*\n"
            "오늘 시장 금융 뉴스 데이터를 수집하지 못했습니다. (네트워크 혹은 사이트 구조 점검 필요)"
        )
        return

    all_article_sentiments = []
    combined_news_text = ""

    # 2. 뉴스 기사 분석 및 요약 텍스트 취합
    logger.info(f"단계 2/3: 가져온 {len(news_articles)}개의 기사 감성 분석 진행 중...")
    for i, article in enumerate(news_articles):
        article_title = article.get('title', '제목 없음')
        article_content = article.get('content', '')
        
        if not article_content.strip():
            continue

        # 개별 기사 감성 분석
        sentiment = analyze_sentiment(article_content)
        all_article_sentiments.append(sentiment)
        combined_news_text += f"- {article_title}: {article_content}\n\n"

    # 3. 전체 시장 요약 및 개미 심리지수 계산
    logger.info("단계 3/3: 전체 시장 번역 요약 및 심리지수 산출 중...")
    overall_summary = summarize_text(combined_news_text)
    ant_sentiment = calculate_ant_sentiment_index(all_article_sentiments)

    # 4. Telegram 알림 메시지 구성 및 전송
    message_title = f"📢 *[삐빅! 김개미 비상: {current_time_kst} Daily Market Morse]*"
    
    alert_message = (
        f"{message_title}\n\n"
        f"📊 *오늘의 시장 핵심 요약*\n"
        f"{overall_summary}\n\n"
        f"🐜 *개미 투자자 심리지수*: {ant_sentiment}\n\n"
        f"🔗 *주요 뉴스 기사 원문 링크:*"
    )
    
    # 상위 3개 링크 첨부
    for i, article in enumerate(news_articles[:3]):
        alert_message += f"\n- [{article.get('title')}]({article.get('link')})"

    send_telegram_message(alert_message)
    logger.info("🎉 --- Daily Market Morse 작업 완료 --- 🎉")

# --- Scheduler Setup ---
scheduler = BackgroundScheduler(timezone="Asia/Seoul")
scheduler.add_job(daily_market_morse, 'cron', hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE)

def start_bot():
    """스케줄러 기동 및 프로세스 유지"""
    logger.info(f"🗓️ 스케줄러 등록 완료: 매일 {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d} KST에 분석 실행")
    scheduler.start()
    logger.info("🤖 봇이 백그라운드에서 정상 작동 중입니다. Ctrl+C를 눌러 종료하세요.")

    try:
        while True:
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("⏳ 스케줄러가 성공적으로 종료되었습니다. 봇을 종료합니다.")

if __name__ == "__main__":
    # 실행인자에 --now 가 있으면 즉시 1회 실행 후 스케줄러 시작
    import sys
    if "--now" in sys.argv:
        logger.info("⚡ [즉시 실행 옵션 감지] daily_market_morse()를 즉시 1회 실행합니다.")
        daily_market_morse()
    start_bot()
