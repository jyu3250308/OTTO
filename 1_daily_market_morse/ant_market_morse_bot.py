import os
import requests
import logging
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM
from telegram import Bot, error
from apscheduler.schedulers.background import BackgroundScheduler

# --- Configuration & Setup ---
load_dotenv()

# Logger setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SCHEDULE_HOUR = int(os.getenv('SCHEDULE_HOUR', 9)) # Default to 9 AM KST
SCHEDULE_MINUTE = int(os.getenv('SCHEDULE_MINUTE', 0)) # Default to 0 minutes

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    logger.error("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set. Please check your .env file.")
    exit()

# Initialize Telegram Bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# --- AI Model Initialization ---
# Summarization Model
logger.info("Initializing summarization model...")
summarizer_model_name = "google/pegasus-cnn_dailymail"
try:
    summarizer_tokenizer = AutoTokenizer.from_pretrained(summarizer_model_name)
    summarizer_model = AutoModelForSeq2SeqLM.from_pretrained(summarizer_model_name)
    summarizer_pipeline = pipeline("summarization", model=summarizer_model, tokenizer=summarizer_tokenizer)
    logger.info("Summarization model initialized.")
except Exception as e:
    logger.error(f"Failed to initialize summarization model: {e}. Please ensure you have internet access for model download or sufficient memory.")
    summarizer_pipeline = None # Set to None to handle later

# Sentiment Analysis Model
logger.info("Initializing sentiment analysis model...")
sentiment_model_name = "distilbert-base-uncased-finetuned-sst-2-english"
try:
    sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
    sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)
    sentiment_pipeline = pipeline("sentiment-analysis", model=sentiment_model, tokenizer=sentiment_tokenizer)
    logger.info("Sentiment analysis model initialized.")
except Exception as e:
    logger.error(f"Failed to initialize sentiment analysis model: {e}. Please ensure you have internet access for model download or sufficient memory.")
    sentiment_pipeline = None # Set to None to handle later

# --- News Scraping ---
def fetch_news_from_yahoo_finance(num_articles=5):
    """Fetches recent financial news headlines and links from Yahoo Finance."""
    url = "https://finance.yahoo.com/news/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    articles = []
    try:
        logger.info(f"Fetching news from {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')

        # Yahoo Finance news articles are typically found in 'li' elements within specific 'ul'
        # with a 'stream-content' class, containing 'div' with 'mb-10' class for the link.
        news_items = soup.find_all('li', class_='stream-item', limit=num_articles * 2) # Fetch more to filter for actual articles

        count = 0
        for item in news_items:
            if count >= num_articles:
                break
            # Find the 'a' tag which contains the article link and title
            link_tag = item.find('a', class_='Fw(b) Fz(20px) Lh(23px) LineClamp(2,46px) C($primaryColor) Td(n) D(ib) My(-1px) rpt-grid-layout__title')
            summary_tag = item.find('p', class_='Fz(14px) Lh(19px) LineClamp(3,57px) Mt(6px) C($primaryColor) rpt-grid-layout__summary')

            if link_tag and summary_tag:
                title = link_tag.get_text(strip=True)
                link = "https://finance.yahoo.com" + link_tag['href']
                summary_text = summary_tag.get_text(strip=True)
                articles.append({'title': title, 'link': link, 'content': summary_text})
                logger.debug(f"Found article: {title}")
                count += 1
            else:
                # Fallback for other structures or less prominent news items
                link_tag_alt = item.find('a', {'data-test-id': 'StreamArticleTitle'})
                summary_tag_alt = item.find('p', {'data-test-id': 'StreamArticleSummary'})
                if link_tag_alt and summary_tag_alt:
                    title = link_tag_alt.get_text(strip=True)
                    link = "https://finance.yahoo.com" + link_tag_alt['href']
                    summary_text = summary_tag_alt.get_text(strip=True)
                    articles.append({'title': title, 'link': link, 'content': summary_text})
                    logger.debug(f"Found alt article: {title}")
                    count += 1


    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news from Yahoo Finance: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Yahoo Finance scraping: {e}")
    finally:
        logger.info(f"Finished fetching {len(articles)} articles from Yahoo Finance.")
    return articles

def fetch_news_from_investing_com(num_articles=5):
    """Fetches recent financial news headlines and links from Investing.com."""
    url = "https://www.investing.com/news/stock-market-news" # Specific to stock market news
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.investing.com/'
    }
    articles = []
    try:
        logger.info(f"Fetching news from {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Investing.com news items are often within 'article' tags
        news_items = soup.find_all('article', class_='js-article-item', limit=num_articles)

        for item in news_items:
            link_tag = item.find('a', class_='title')
            summary_tag = item.find('p', class_='textDiv') # The actual summary text
            if link_tag and summary_tag:
                title = link_tag.get_text(strip=True)
                link = "https://www.investing.com" + link_tag['href']
                summary_text = summary_tag.get_text(strip=True)
                articles.append({'title': title, 'link': link, 'content': summary_text})
                logger.debug(f"Found article: {title}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching news from Investing.com: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Investing.com scraping: {e}")
    finally:
        logger.info(f"Finished fetching {len(articles)} articles from Investing.com.")
    return articles

def fetch_all_news(num_articles_per_source=3):
    """Combines news from multiple sources."""
    all_news = []
    all_news.extend(fetch_news_from_yahoo_finance(num_articles_per_source))
    all_news.extend(fetch_news_from_investing_com(num_articles_per_source))
    logger.info(f"Total articles fetched: {len(all_news)}")
    return all_news

# --- AI Processing ---
def analyze_sentiment(text):
    """Analyzes the sentiment of the given text and returns '긍정', '중립', or '부정'."""
    if sentiment_pipeline is None:
        return "중립" # Model failed to initialize
    try:
        if not text.strip():
            return "중립" # Handle empty text
        result = sentiment_pipeline(text)[0]
        label = result['label']
        score = result['score']

        # 'distilbert-base-uncased-finetuned-sst-2-english' outputs 'POSITIVE' or 'NEGATIVE'
        # with a score. We can define a threshold for '중립'.
        if label == 'POSITIVE' and score > 0.7: # Strong positive
            return "긍정"
        elif label == 'NEGATIVE' and score > 0.7: # Strong negative
            return "부정"
        else: # Weak positive/negative or close to 0.5 score
            return "중립"
    except Exception as e:
        logger.error(f"Error analyzing sentiment for text: '{text[:50]}...' - {e}")
        return "중립" # Default to neutral on error

def summarize_text(text, max_length=100, min_length=30):
    """Summarizes the given text into 3 sentences or less."""
    if summarizer_pipeline is None:
        return "AI 요약 기능이 작동하지 않습니다." # Model failed to initialize
    try:
        if not text.strip():
            return "요약 불가." # Handle empty text
        # The Pegasus model typically generates coherent summaries.
        # We can try to limit it to a few sentences by controlling max_length and min_length.
        summary_list = summarizer_pipeline(text, max_length=max_length, min_length=min_length, do_sample=False)
        summary = summary_list[0]['summary_text']
        # Simple heuristic to limit to 3 sentences
        sentences = summary.split('.')
        # Filter out empty strings and take up to 3 sentences
        filtered_sentences = [s.strip() for s in sentences if s.strip()]
        return ". ".join(filtered_sentences[:3]) + ("." if filtered_sentences and not filtered_sentences[-1].endswith('.') else "")
    except Exception as e:
        logger.error(f"Error summarizing text: '{text[:50]}...' - {e}")
        return "AI 요약 실패."

def calculate_ant_sentiment_index(sentiments):
    """Calculates the overall '개미 심리지수' based on a list of sentiments."""
    if not sentiments:
        return "중립"

    positive_count = sentiments.count("긍정")
    negative_count = sentiments.count("부정")
    neutral_count = sentiments.count("중립")

    total = len(sentiments)
    if total == 0:
        return "중립"

    pos_ratio = positive_count / total
    neg_ratio = negative_count / total

    if pos_ratio > neg_ratio + 0.2: # Significantly more positive
        return "긍정"
    elif neg_ratio > pos_ratio + 0.2: # Significantly more negative
        return "부정"
    else: # Balanced or slightly skewed
        return "중립"

# --- Telegram Alerter ---
def send_telegram_message(message):
    """Sends a message to the configured Telegram chat."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
        logger.info("Telegram message sent successfully.")
    except error.TelegramError as e:
        logger.error(f"Error sending Telegram message: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while sending Telegram message: {e}")

# --- Main Logic ---
def daily_market_morse():
    """Main function to perform daily market analysis and send alerts."""
    logger.info("--- Daily Market Morse started ---")
    
    if summarizer_pipeline is None or sentiment_pipeline is None:
        error_message = "삐빅! 김개미 비상: AI 모델 초기화 실패. 뉴스 분석을 건너뜁니다." \
                        "\n자세한 로그를 확인하거나 인터넷 연결 상태 및 메모리를 확인해 주세요."
        send_telegram_message(error_message)
        logger.error(error_message.replace('\n', ' '))
        return

    alert_messages = []

    # 1. Fetch News
    news_articles = fetch_all_news(num_articles_per_source=5)
    if not news_articles:
        logger.warning("No news articles fetched. Skipping analysis.")
        send_telegram_message("삐빅! 김개미 비상: 오늘 시장 뉴스 가져오기 실패. (신호 없음)")
        return

    all_article_sentiments = []
    combined_news_text = ""
    for i, article in enumerate(news_articles):
        logger.info(f"Processing article {i+1}/{len(news_articles)}: {article['title']}")
        content_to_analyze = article['content'] # Use the scraped summary/content
        
        if not content_to_analyze.strip():
            logger.warning(f"Article '{article['title']}' has no content for analysis. Skipping sentiment/summary.")
            continue

        sentiment = analyze_sentiment(content_to_analyze)
        all_article_sentiments.append(sentiment)
        combined_news_text += content_to_analyze + " " # Combine for overall summary later

    # 2. Generate Overall Market Summary
    overall_summary = summarize_text(combined_news_text, max_length=150, min_length=50) # Slightly longer for overall summary
    logger.info(f"Overall Market Summary: {overall_summary}")

    # 3. Calculate Ant Sentiment Index
    ant_sentiment = calculate_ant_sentiment_index(all_article_sentiments)
    logger.info(f"Ant Sentiment Index: {ant_sentiment}")

    # 4. Format and Send Alert
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M KST")
    
    message_title = f"*삐빅! 김개미 비상: {current_time} Daily Market Morse*"
    message_summary = f"핵심 동향: {overall_summary}"
    message_sentiment = f"개미 심리지수: {ant_sentiment}"
    
    alert_message = f"""{message_title}

_{message_summary}_

_{message_sentiment}_

_더 자세한 정보는 뉴스 링크를 확인하세요:_
"""
    # Add top 3 news links if available
    for i, article in enumerate(news_articles[:3]):
        alert_message += f"\n- [{article['title']}]({article['link']})"

    send_telegram_message(alert_message)
    logger.info("--- Daily Market Morse completed ---")

# --- Scheduler Setup ---
scheduler = BackgroundScheduler(timezone="Asia/Seoul") # Set timezone to KST
scheduler.add_job(daily_market_morse, 'cron', hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE)

def start_bot():
    """Starts the scheduler and keeps the script running."""
    logger.info(f"Scheduler set to run daily at {SCHEDULE_HOUR:02d}:{SCHEDULE_MINUTE:02d} KST.")
    scheduler.start()
    logger.info("Press Ctrl+C to exit.")

    try:
        # Keep the main thread alive
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shutdown. Exiting.")

if __name__ == "__main__":
    start_bot()
