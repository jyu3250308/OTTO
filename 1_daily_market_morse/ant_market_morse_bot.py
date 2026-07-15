import os
import requests
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM
from telegram import Bot, error
from apscheduler.schedulers.background import BackgroundScheduler

# --- Configuration & Setup ---
load_dotenv()

# Logger setup
# INFO 레벨 로그를 콘솔에 출력하고, 상세 포맷을 사용합니다.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment Variables
# .env 파일에서 텔레그램 봇 토큰, 채팅 ID, 스케줄 시간을 로드합니다.
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SCHEDULE_HOUR = int(os.getenv('SCHEDULE_HOUR', 9))  # 기본값: 한국 시간 (KST) 오전 9시
SCHEDULE_MINUTE = int(os.getenv('SCHEDULE_MINUTE', 0))  # 기본값: 0분

# Constants for AI models and scraping
# AI 모델 이름 정의
SUMMARIZER_MODEL_NAME = "google/pegasus-cnn_dailymail"
SENTIMENT_MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
# 각 뉴스 소스에서 가져올 기본 기사 개수
DEFAULT_NUM_ARTICLES_PER_SOURCE = 5
# 감성 분석 시 긍정/부정 판단을 위한 신뢰도 임계값
SENTIMENT_THRESHOLD = 0.7  

# 필수 환경 변수 누락 시 프로그램 즉시 종료
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    logger.error("환경 변수 누락: TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID가 설정되지 않았습니다. .env 파일을 확인해 주세요.")
    exit()

# Initialize Telegram Bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# --- AI Model Initialization ---
# AI 파이프라인 전역 변수 초기화 (모델 로딩 실패 시 None 유지)
summarizer_pipeline = None
sentiment_pipeline = None

def initialize_ai_models():
    """AI 모델 (요약 및 감성 분석)을 초기화합니다.
    모델 로딩 중 오류가 발생하면 해당 파이프라인을 None으로 설정합니다.
    """
    global summarizer_pipeline, sentiment_pipeline
    
    # Summarization Model (요약 모델)
    logger.info(f"AI 모델 초기화 중: 요약 모델 로딩 시작 ({SUMMARIZER_MODEL_NAME})...")
    try:
        # AutoTokenizer와 AutoModelForSeq2SeqLM을 사용하여 모델을 로드합니다.
        # Hugging Face 모델은 처음 로드 시 인터넷을 통해 다운로드됩니다.
        summarizer_tokenizer = AutoTokenizer.from_pretrained(SUMMARIZER_MODEL_NAME)
        summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(SUMMARIZER_MODEL_NAME)
        summarizer_pipeline = pipeline("summarization", model=summarizer_model, tokenizer=summarizer_tokenizer)
        logger.info("✅ 요약 모델 초기화 완료.")
    except Exception as e:
        logger.error(f"❌ 요약 모델 초기화 실패: {e}\n"\
                     "인터넷 연결 상태, 사용 가능한 메모리, 모델 이름 철자를 확인해 주세요.")
        summarizer_pipeline = None # 실패 시 파이프라인 비활성화

    # Sentiment Analysis Model (감성 분석 모델)
    logger.info(f"AI 모델 초기화 중: 감성 분석 모델 로딩 시작 ({SENTIMENT_MODEL_NAME})...")
    try:
        # AutoTokenizer와 AutoModelForSequenceClassification을 사용하여 모델을 로드합니다.
        sentiment_tokenizer = AutoTokenizer.from_pretrained(SENTIMENT_MODEL_NAME)
        sentiment_model = AutoModelForSequenceClassification.from_pretrained(SENTIMENT_MODEL_NAME)
        sentiment_pipeline = pipeline("sentiment-analysis", model=sentiment_model, tokenizer=sentiment_tokenizer)
        logger.info("✅ 감성 분석 모델 초기화 완료.")
    except Exception as e:
        logger.error(f"❌ 감성 분석 모델 초기화 실패: {e}\n"\
                     "인터넷 연결 상태, 사용 가능한 메모리, 모델 이름 철자를 확인해 주세요.")
        sentiment_pipeline = None # 실패 시 파이프라인 비활성화

# 봇 시작 시 AI 모델 초기화 함수 호출
initialize_ai_models()

# --- News Scraping ---

def fetch_news_from_yahoo_finance(num_articles: int = DEFAULT_NUM_ARTICLES_PER_SOURCE) -> list:
    """Yahoo Finance에서 최신 금융 뉴스 헤드라인, 링크 및 요약 내용을 가져옵니다.

    Args:
        num_articles (int): 가져올 기사의 최대 개수.

    Returns:
        list: 각 기사가 'title', 'link', 'content' 키를 가진 딕셔너리 리스트.
    """
    url = "https://finance.yahoo.com/news/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    articles = []
    logger.info(f"➡️ Yahoo Finance ({url})에서 뉴스 기사 {num_articles}개 가져오는 중...")
    try:
        response = requests.get(url, headers=headers, timeout=15) # 요청 타임아웃을 15초로 설정
        response.raise_for_status()  # 200 이외의 HTTP 상태 코드에 대해 예외 발생
        soup = BeautifulSoup(response.text, 'html.parser')

        # Yahoo Finance 뉴스 기사 요소는 동적으로 로드되거나 구조가 변경될 수 있습니다.
        # 주요 기사와 보조 기사에 대한 여러 셀렉터를 시도하여 안정성을 높입니다.
        news_items = soup.find_all('li', class_='stream-item')

        count = 0
        for item in news_items:
            if count >= num_articles:
                break
            
            title, link, summary_text = None, None, None

            # 첫 번째 패턴 (일반적인 큰 제목의 뉴스)
            link_tag_main = item.find('a', class_='Fw(b) Fz(20px) Lh(23px) LineClamp(2,46px) C($primaryColor) Td(n) D(ib) My(-1px) rpt-grid-layout__title')
            summary_tag_main = item.find('p', class_='Fz(14px) Lh(19px) LineClamp(3,57px) Mt(6px) C($primaryColor) rpt-grid-layout__summary')

            if link_tag_main and summary_tag_main:
                title = link_tag_main.get_text(strip=True)
                link = "https://finance.yahoo.com" + link_tag_main['href']
                summary_text = summary_tag_main.get_text(strip=True)
            else:
                # 두 번째 패턴 (데이터 테스트 ID를 사용하는 다른 형태의 뉴스)
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
            else:
                logger.debug(f"[Yahoo Finance] 기사 요소 (제목, 링크, 요약)를 찾을 수 없음. 아이템 스킵: {item.prettify()[:150]}...")

    except requests.exceptions.Timeout:
        logger.error(f"❌ Yahoo Finance 뉴스 가져오기 실패: 요청 시간 초과 ({url}). 인터넷 연결 또는 웹사이트 상태를 확인하세요.")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"❌ Yahoo Finance 뉴스 가져오기 실패: 네트워크 연결 오류 ({url}) - {e}. 인터넷 연결을 확인하세요.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ Yahoo Finance 뉴스 가져오기 실패: HTTP 오류 {response.status_code} - {e}. 웹사이트 구조가 변경되었을 수 있습니다.")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Yahoo Finance 뉴스 가져오기 실패: 일반적인 요청 오류 ({url}) - {e}")
    except Exception as e:
        logger.error(f"❌ Yahoo Finance 뉴스 크롤링 중 예상치 못한 오류 발생: {e}")
    finally:
        logger.info(f"✅ Yahoo Finance에서 총 {len(articles)}개의 기사를 가져왔습니다.")
    return articles

def fetch_news_from_investing_com(num_articles: int = DEFAULT_NUM_ARTICLES_PER_SOURCE) -> list:
    """Investing.com에서 최신 금융 뉴스 헤드라인, 링크 및 요약 내용을 가져옵니다.

    Args:
        num_articles (int): 가져올 기사의 최대 개수.

    Returns:
        list: 각 기사가 'title', 'link', 'content' 키를 가진 딕셔너리 리스트.
    """
    url = "https://www.investing.com/news/stock-market-news" # 주식 시장 뉴스 섹션 지정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.investing.com/' # Referer 헤더 추가로 봇 접근성 향상
    }
    articles = []
    logger.info(f"➡️ Investing.com ({url})에서 뉴스 기사 {num_articles}개 가져오는 중...")
    try:
        response = requests.get(url, headers=headers, timeout=15) # 요청 타임아웃을 15초로 설정
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Investing.com 뉴스 아이템은 'article' 태그 내에 'js-article-item' 클래스로 존재합니다.
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
            else:
                logger.debug(f"[Investing.com] 기사 요소 (제목, 링크, 요약)를 찾을 수 없음. 아이템 스킵: {item.prettify()[:150]}...")

    except requests.exceptions.Timeout:
        logger.error(f"❌ Investing.com 뉴스 가져오기 실패: 요청 시간 초과 ({url}). 인터넷 연결 또는 웹사이트 상태를 확인하세요.")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"❌ Investing.com 뉴스 가져오기 실패: 네트워크 연결 오류 ({url}) - {e}. 인터넷 연결을 확인하세요.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ Investing.com 뉴스 가져오기 실패: HTTP 오류 {response.status_code} - {e}. 웹사이트 구조가 변경되었을 수 있습니다.")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Investing.com 뉴스 가져오기 실패: 일반적인 요청 오류 ({url}) - {e}")
    except Exception as e:
        logger.error(f"❌ Investing.com 뉴스 크롤링 중 예상치 못한 오류 발생: {e}")
    finally:
        logger.info(f"✅ Investing.com에서 총 {len(articles)}개의 기사를 가져왔습니다.")
    return articles

def fetch_all_news(num_articles_per_source: int = DEFAULT_NUM_ARTICLES_PER_SOURCE) -> list:
    """여러 금융 뉴스 출처에서 뉴스를 종합하여 가져옵니다.

    Args:
        num_articles_per_source (int): 각 출처에서 가져올 기사의 개수.

    Returns:
        list: 모든 출처에서 가져온 기사 딕셔너리 리스트.
    """
    logger.info("📰 모든 뉴스 출처에서 뉴스 가져오기 시작...")
    all_news = []
    all_news.extend(fetch_news_from_yahoo_finance(num_articles_per_source))
    all_news.extend(fetch_news_from_investing_com(num_articles_per_source))
    logger.info(f"✅ 총 {len(all_news)}개의 기사를 가져왔습니다.")
    return all_news

# --- AI Processing ---

def analyze_sentiment(text: str) -> str:
    """주어진 텍스트의 감성을 분석하여 '긍정', '중립', 또는 '부정'을 반환합니다.

    감성 분석 모델 ('distilbert-base-uncased-finetuned-sst-2-english')은 'POSITIVE' 또는 'NEGATIVE' 레이블과 신뢰도 점수를 반환합니다.
    지정된 `SENTIMENT_THRESHOLD` (기본 0.7) 이상일 경우 '긍정' 또는 '부정'으로 판단하고, 그 외에는 '중립'으로 처리합니다.

    Args:
        text (str): 분석할 텍스트.

    Returns:
        str: 감성 분석 결과 ('긍정', '중립', '부정').
    """
    if sentiment_pipeline is None:
        logger.warning("⚠️ 감성 분석 모델이 초기화되지 않아 '중립'으로 처리합니다.")
        return "중립" 
    if not text or not text.strip():
        logger.debug("감성 분석할 텍스트가 비어 있어 '중립'으로 처리합니다.")
        return "중립" 

    try:
        result = sentiment_pipeline(text)[0]
        label = result['label']
        score = result['score']

        if label == 'POSITIVE' and score >= SENTIMENT_THRESHOLD: 
            return "긍정"
        elif label == 'NEGATIVE' and score >= SENTIMENT_THRESHOLD: 
            return "부정"
        else: 
            # 임계값 미만이거나, 'POSITIVE'/'NEGATIVE' 판단이 약할 경우 '중립'으로 처리
            return "중립"
    except Exception as e:
        logger.error(f"❌ 텍스트 감성 분석 중 오류 발생 (텍스트 미리보기: '{text[:50]}...'): {e}")
        return "중립"  # 오류 발생 시 기본값은 '중립'

def summarize_text(text: str, max_length: int = 100, min_length: int = 30) -> str:
    """주어진 텍스트를 Pegasus 모델을 사용하여 요약하고, 최대 3문장으로 제한합니다.

    Args:
        text (str): 요약할 텍스트.
        max_length (int): 요약문의 최대 길이 (토큰 기준).
        min_length (int): 요약문의 최소 길이 (토큰 기준).

    Returns:
        str: 요약된 텍스트. 모델 초기화 실패 시 안내 메시지 반환.
    """
    if summarizer_pipeline is None:
        logger.warning("⚠️ 요약 모델이 초기화되지 않아 요약 기능을 사용할 수 없습니다.")
        return "AI 요약 기능이 작동하지 않습니다." 
    if not text or not text.strip():
        logger.debug("요약할 텍스트가 비어 있어 '요약 불가'로 처리합니다.")
        return "요약 불가."

    try:
        # Pegasus 모델로 텍스트를 요약합니다. do_sample=False로 결정론적 요약 생성
        summary_list = summarizer_pipeline(text, max_length=max_length, min_length=min_length, do_sample=False)
        summary = summary_list[0]['summary_text']
        
        # 생성된 요약을 3문장으로 제한하기 위한 간단한 휴리스틱
        sentences = summary.replace('..', '.').split('.') # 중복 마침표 처리 후 분리
        filtered_sentences = [s.strip() for s in sentences if s.strip()] # 빈 문자열 제거
        
        # 상위 3문장만 선택하고, 마지막 문장에 마침표가 없으면 추가합니다.
        final_summary = ". ".join(filtered_sentences[:3])
        if final_summary and not final_summary.endswith('.'):
            final_summary += '.'
        
        return final_summary if final_summary else "요약 생성 실패."
    except Exception as e:
        logger.error(f"❌ 텍스트 요약 중 오류 발생 (텍스트 미리보기: '{text[:50]}...'): {e}")
        return "AI 요약 실패."

def calculate_ant_sentiment_index(sentiments: list) -> str:
    """뉴스 기사들의 개별 감성 리스트를 기반으로 전체 '개미 심리지수'를 계산합니다.

    감성 비율 차이가 20%p 이상일 경우 강한 감성으로 판단하고, 그 외에는 '중립'으로 판단합니다.

    Args:
        sentiments (list): '긍정', '중립', '부정'으로 구성된 감성 문자열 리스트.

    Returns:
        str: 계산된 '개미 심리지수' ('긍정', '중립', '부정').
    """
    if not sentiments:
        logger.debug("감성 리스트가 비어 있어 '중립'으로 심리지수를 계산합니다.")
        return "중립"

    positive_count = sentiments.count("긍정")
    negative_count = sentiments.count("부정")
    neutral_count = sentiments.count("중립")

    total = len(sentiments)
    if total == 0: # 혹시 모를 0 나누기 방지
        return "중립"

    pos_ratio = positive_count / total
    neg_ratio = negative_count / total

    # 긍정/부정 비율이 20%p(0.2) 이상 차이 날 경우 강한 감성으로 판단
    if pos_ratio > neg_ratio + 0.2: 
        return "긍정"
    elif neg_ratio > pos_ratio + 0.2: 
        return "부정"
    else: 
        # 비율 차이가 크지 않거나 비슷할 경우 '중립'으로 판단
        return "중립"

# --- Telegram Alerter ---

def send_telegram_message(message: str) -> None:
    """설정된 Telegram 채팅으로 메시지를 보냅니다.

    Args:
        message (str): 보낼 메시지 내용.
    """
    logger.info("💬 Telegram 메시지 전송 시도 중...")
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
        logger.info("✅ Telegram 메시지 전송 성공.")
    except error.Unauthorized:
        logger.error("❌ Telegram 메시지 전송 실패: 봇 토큰이 유효하지 않거나, 봇이 채팅방에 초대되지 않았거나, 접근 권한이 없습니다. .env 파일을 확인하거나 봇 설정을 점검하세요.")
    except error.BadRequest as e:
        logger.error(f"❌ Telegram 메시지 전송 실패: 잘못된 요청입니다. (예: Chat ID 오류, 메시지 길이 초과, 마크다운 형식 오류) - {e}")
    except error.TelegramError as e:
        logger.error(f"❌ Telegram API 오류 발생: {e}. Telegram 서비스 상태를 확인해 주세요.")
    except Exception as e:
        logger.error(f"❌ Telegram 메시지 전송 중 예상치 못한 오류 발생: {e}")

# --- Main Logic ---

def daily_market_morse():
    """매일 시장 분석을 수행하고 Telegram 알림을 보냅니다.

    이 함수는 뉴스 기사를 크롤링하고, AI 모델을 이용해 감성 분석 및 요약을 수행한 후,
    최종 시장 동향과 개미 심리지수를 Telegram으로 전송하는 전체 과정을 조율합니다.
    """
    logger.info("🚀 --- Daily Market Morse 작업 시작 --- 🚀")
    current_time_kst = datetime.now().strftime("%Y-%m-%d %H:%M KST")
    
    # AI 모델 초기화 상태를 다시 확인하여, 실패 시 알림 메시지 전송 및 작업 중단
    if summarizer_pipeline is None or sentiment_pipeline is None:
        error_message = (
            f"삐빅! 김개미 비상: {current_time_kst} AI 모델 초기화 실패. 뉴스 분석을 건너뜁니다.\n"
            "*자세한 로그를 확인하거나 인터넷 연결 상태 및 메모리 확보 여부를 확인해 주세요.*"
        )
        send_telegram_message(error_message)
        logger.error("❌ AI 모델이 초기화되지 않아 시장 분석을 건너뜁니다. 로그를 확인하세요.")
        logger.info("--- Daily Market Morse 작업 종료 (AI 모델 오류) ---")
        return

    # 1. 뉴스 기사 가져오기
    logger.info(f"단계 1/4: 뉴스 기사 가져오는 중 (각 출처당 {DEFAULT_NUM_ARTICLES_PER_SOURCE}개) ... ")
    news_articles = fetch_all_news(DEFAULT_NUM_ARTICLES_PER_SOURCE)
    
    if not news_articles:
        logger.warning("⚠️ 가져온 뉴스 기사가 없습니다. 분석을 건너뛰고 알림을 보냅니다.")
        send_telegram_message(
            f"삐빅! 김개미 비상: {current_time_kst} 오늘 시장 뉴스 가져오기 실패. (신호 없음)\n"
            "*자세한 로그를 확인하거나 웹사이트 구조 변경 여부를 확인해 주세요.*"
        )
        logger.info("--- Daily Market Morse 작업 종료 (뉴스 없음) ---")
        return

    all_article_sentiments = []
    combined_news_text = ""

    # 2. 뉴스 기사별 감성 분석 및 전체 요약 텍스트 취합
    logger.info(f"단계 2/4: 가져온 {len(news_articles)}개의 기사 분석 및 요약 텍스트 취합 중...")
    for i, article in enumerate(news_articles):
        article_title = article.get('title', '제목 없음')
        article_content = article.get('content', '')
        logger.info(f"  [뉴스 {i+1}/{len(news_articles)}] '{article_title}' 감성 분석 및 내용 취합...")
        
        if not article_content.strip():
            logger.warning(f"    [뉴스 {i+1}] '{article_title}' 기사에 내용이 없어 감성 분석 및 요약을 건너뜁니다.")
            continue

        sentiment = analyze_sentiment(article_content)
        all_article_sentiments.append(sentiment)
        combined_news_text += article_content + "\n\n" # 각 기사 내용을 결합하여 전체 시장 요약에 사용

    # 모든 기사의 감성 분석이 완료되었는지 확인
    if not all_article_sentiments:
        logger.warning("⚠️ 분석 가능한 기사 내용이 없어 개미 심리지수를 계산할 수 없습니다.")
        send_telegram_message(
            f"삐빅! 김개미 비상: {current_time_kst} 분석할 뉴스 내용이 없어 심리지수 계산 실패. (내용 없음)\n"
            "*자세한 로그를 확인해 주세요.*"
        )
        logger.info("--- Daily Market Morse 작업 종료 (분석할 내용 없음) ---")
        return

    # 3. 전체 시장 요약 및 개미 심리지수 계산
    logger.info("단계 3/4: 전체 시장 요약 및 개미 심리지수 계산 중...")
    # 전체 시장 요약은 개별 요약보다 길게 설정하여 맥락을 더 잘 전달합니다.
    overall_summary = summarize_text(combined_news_text, max_length=200, min_length=70) 
    logger.info(f"  전체 시장 요약: {overall_summary}")

    ant_sentiment = calculate_ant_sentiment_index(all_article_sentiments)
    logger.info(f"  개미 심리지수: {ant_sentiment}")

    # 4. Telegram 알림 메시지 포맷 및 전송
    logger.info("단계 4/4: Telegram 알림 메시지 생성 및 전송 준비 중...")
    
    message_title = f"*삐빅! 김개미 비상: {current_time_kst} Daily Market Morse*"
    message_summary = f"핵심 동향: {overall_summary}"
    message_sentiment = f"개미 심리지수: {ant_sentiment}"
    
    # Telegram 메시지 내용 구성 (Markdown 형식)
    alert_message = f"""{message_title}

_{message_summary}_

_{message_sentiment}_

_더 자세한 정보는 주요 뉴스 링크를 확인하세요:_"""
    
    # 가져온 기사 중 상위 3개 뉴스 링크를 메시지에 추가
    for i, article in enumerate(news_articles[:3]):
        alert_message += f"\n- [{article.get('title', '링크 없음')}]({article.get('link', '#')})"

    send_telegram_message(alert_message)
    logger.info("--- Daily Market Morse 작업 완료 ---")

# --- Scheduler Setup ---
# BackgroundScheduler를 사용하여 백그라운드에서 주기적으로 작업을 실행합니다.
# timezone을 "Asia/Seoul" (한국 표준시)로 설정하여 정확한 시간에 실행되도록 합니다.
scheduler = BackgroundScheduler(timezone="Asia/Seoul") 
scheduler.add_job(daily_market_morse, 'cron', hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE)

def start_bot():
    """스케줄러를 시작하고 스크립트가 계속 실행되도록 유지합니다."""
    logger.info(f"🗓️ 스케줄러가 매일 {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d} KST에 'daily_market_morse' 작업을 실행하도록 설정되었습니다.")
    scheduler.start()
    logger.info("봇이 백그라운드에서 실행 중입니다. Ctrl+C를 눌러 안전하게 종료하세요.")

    try:
        # 메인 스레드를 무한 루프로 유지하여 스케줄러가 백그라운드에서 계속 작동하도록 합니다.
        while True:
            time.sleep(5) # 시스템 리소스 절약을 위해 5초마다 대기
    except (KeyboardInterrupt, SystemExit):
        # Ctrl+C 또는 시스템 종료 신호 수신 시 스케줄러를 종료합니다.
        scheduler.shutdown()
        logger.info("⏳ 스케줄러가 종료되었습니다. 봇을 종료합니다.")

if __name__ == "__main__":
    # 스크립트가 직접 실행될 때 봇을 시작합니다.
    start_bot()
