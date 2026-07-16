import os
import datetime
import json
import time
import random
import traceback # Added for more robust error logging

# --- Constants ---
# Define constants for better maintainability and readability
AD_CLICK_VALUE = 0.01
TARGET_EARNINGS = 1.00
DEFAULT_DATA_FILE = "grok_auntie_data.json"

# --- Configuration Management ---
def load_config() -> dict:
    """
    Loads configuration settings from environment variables or uses default mock values.
    In a real application, this would typically involve a dedicated configuration file
    (.env, YAML, TOML) and a proper configuration parsing library.

    Returns:
        dict: A dictionary containing loaded configuration settings.
    """
    print(f"[{datetime.datetime.now().isoformat()}] INFO: Attempting to load configuration...")
    config = {
        "GROK_API_KEY": os.getenv("GROK_API_KEY", "mock_grok_key_123_dev"),
        "EMAIL_SENDER": os.getenv("EMAIL_SENDER", "auntie.grok@example.com"),
        "EMAIL_RECIPIENTS": os.getenv("EMAIL_RECIPIENTS", "subscriber1@example.com,subscriber2@example.com"),
        "SNS_CHANNEL_ID": os.getenv("SNS_CHANNEL_ID", "mock_grok_telegram_channel"),
        "DATA_FILE": os.getenv("DATA_FILE", DEFAULT_DATA_FILE) # Allow data file path to be configurable
    }
    # Validate essential configurations if they were mandatory (mocking less critical here)
    if not config["GROK_API_KEY"]:
        print(f"[{datetime.datetime.now().isoformat()}] WARNING: GROK_API_KEY is not set. Using mock key.")
    
    print(f"[{datetime.datetime.now().isoformat()}] INFO: Configuration loaded successfully: "
          f"API Key (first 8 chars): {config['GROK_API_KEY'][:8]}, "
          f"Sender: {config['EMAIL_SENDER']}, "
          f"Recipients: {config['EMAIL_RECIPIENTS'].split(',')}, "
          f"SNS Channel: {config['SNS_CHANNEL_ID']}, "
          f"Data File: {config['DATA_FILE']}")
    return config

# --- Market Data Fetcher (Mock) ---
def fetch_mock_market_data() -> list[dict]:
    """
    Simulates fetching market news and data from various sources.
    In a production system, this would integrate with actual financial APIs (e.g., Bloomberg, Reuters, specialized news APIs).

    Returns:
        list[dict]: A list of dictionaries, each representing a mock news article.
    """
    print(f"[{datetime.datetime.now().isoformat()}] INFO: Fetching mock market data...")
    # Simulate fetching news from various sources
    mock_data = [
        {"source": "Finance Today", "title": "Tech Stocks Rally Amid Strong Earnings", "content": "Major tech companies reported better-than-expected earnings, pushing stock prices up. Investors are optimistic about Q4 growth prospects. Semiconductor industry shows resilience. AI sector continues to attract significant investment, driving innovation in various industries."},
        {"source": "Crypto Daily", "title": "Bitcoin Hits New All-Time High", "content": "Bitcoin surged past $70,000 as institutional adoption grows. Ethereum also sees significant gains. Analysts predict further upward momentum for altcoins. Regulatory clarity remains a key factor for sustained growth."},
        {"source": "Market Watch", "title": "Interest Rate Hike Concerns Persist", "content": "Central banks globally are hinting at potential interest rate hikes to curb inflation. This could impact consumer spending and corporate profits. Energy prices remain volatile. Geopolitical tensions add uncertainty to global supply chains."},
        {"source": "Startup News", "title": "AI Investment Boom Continues", "content": "Venture capital funding for AI startups reached record levels last quarter. Focus areas include generative AI and autonomous systems. Talent acquisition is competitive. Ethical AI development and deployment are growing concerns."}
    ]
    # Simulate a small delay for realism
    time.sleep(0.5) 
    print(f"[{datetime.datetime.now().isoformat()}] INFO: Fetched {len(mock_data)} mock news articles successfully.")
    return mock_data

# --- Grok AI Summary Engine (Mock) ---
def generate_grok_summary(market_data: list[dict], api_key: str) -> str:
    """
    Simulates generating a market summary using an AI (like Grok).
    In a real scenario, this would make an API call to Grok or a similar large language model.
    For this mock, it deterministically generates a summary based on keywords found in market data.

    Args:
        market_data (list[dict]): A list of market news articles.
        api_key (str): The API key for the Grok service (mocked here).

    Returns:
        str: A multi-line string containing the summarized market insights.
    """
    print(f"[{datetime.datetime.now().isoformat()}] INFO: Generating Grok AI summary with API Key (first 8 chars): {api_key[:8]}...")
    
    if not market_data:
        print(f"[{datetime.datetime.now().isoformat()}] WARNING: No market data provided for summary generation. Returning empty summary.")
        return "시장 데이터가 없어 요약할 수 없습니다."

    # Simulate Grok's \"understanding\" and sentiment analysis
    # Keywords to determine overall sentiment
    positive_keywords = ["optimistic", "surged", "gains", "boom", "rally", "record levels", "resilience", "growing"]
    negative_keywords = ["concerns", "volatile", "impact", "uncertainty", "persist", "curb"]

    all_content = " ".join([d["content"].lower() for d in market_data])
    
    positive_score = sum(all_content.count(kw) for kw in positive_keywords)
    negative_score = sum(all_content.count(kw) for kw in negative_keywords)

    overall_sentiment = "낙관적" if positive_score > negative_score else ("신중한" if negative_score > positive_score else "혼조세")
    
    summary_lines = []
    summary_lines.append(f"1. 글로벌 시장은 {overall_sentiment} 흐름을 보이며, 특히 기술주와 암호화폐가 강세를 주도하고 있습니다.")
    summary_lines.append(f"2. 비트코인 사상 최고가 경신 및 기관 투자 관심 증대. 다만, 잠재적 금리 인상 가능성은 경계해야 합니다.")
    summary_lines.append(f"3. AI 투자 붐 지속. 그러나 에너지 가격과 인플레이션 우려는 여전히 존재하며, 4분기 기업 실적 발표에 주목하세요.")

    summary = "\n".join(summary_lines) 
    
    print(f"[{datetime.datetime.now().isoformat()}] INFO: Grok Summary Generated. Preview:\n---BEGIN SUMMARY---\n{summary[:150]}...\n---END SUMMARY---")
    return summary

# --- Publisher (Email/SNS Mock) ---
def publish_summary(summary: str, config: dict, current_status: dict) -> None:
    """
    Simulates publishing the generated market summary via email and SNS channels.
    In a real system, this would integrate with email APIs (e.g., SendGrid, SES) and
    SNS platforms (e.g., Telegram Bot API, Slack Webhooks, AWS SNS).

    Args:
        summary (str): The market summary text to publish.
        config (dict): Configuration settings, including sender, recipients, and SNS channel.
        current_status (dict): Current project status (earnings, subscribers) for progress updates.
    """
    print(f"[{datetime.datetime.now().isoformat()}] INFO: Starting summary publishing process...")
    
    # Mock Email Publishing
    recipients = [r.strip() for r in config["EMAIL_RECIPIENTS"].split(',') if r.strip()]
    email_subject = f"Grok 이모님의 $1 찌라시 ({datetime.date.today().isoformat()})"
    email_body = f"""\
안녕하세요, 구독자님!

오늘 Grok 이모님의 $1 찌라시가 도착했습니다.
이모가 새벽부터 시장을 훑어 딱 3줄로 요약해 왔어요!

--- Grok 이모님의 $1 찌라시 ---
{summary}
---------------------------

#AI자본주의입문기 진행 상황
현재 목표: ${TARGET_EARNINGS:.2f} (達成까지 ${max(0, TARGET_EARNINGS - current_status['earnings']):.2f} 남음)
총 수익: ${current_status['earnings']:.2f}
구독자 수: {current_status['subscribers']}명
광고 클릭 수: {current_status['ad_clicks']}회

**AI 이모를 응원한다면 아래 링크를 클릭해주세요! (클릭당 ${AD_CLICK_VALUE:.2f} 기여)**
[광고 링크](https://mock-ad-link.com?click={int(time.time())}&source=email)

항상 감사합니다!
Grok 이모 드림
"""
    
    print(f"[{datetime.datetime.now().isoformat()}] DEBUG: Mock Email Content Prepared.")
    print(f"--- Mock Email Sent ({datetime.datetime.now().isoformat()}) ---")
    print(f"  Sender: {config['EMAIL_SENDER']}")
    print(f"  Recipients: {', '.join(recipients)}")
    print(f"  Subject: {email_subject}")
    # Print first 300 characters of the body for preview, ensuring proper line breaks in log
    print(f"  Body Preview:\n{email_body[:300].replace('\n', '\n  ')}...") 
    print(f"------------------------------------")
    time.sleep(0.3) # Simulate email sending delay


    # Mock SNS Publishing (e.g., Telegram channel)
    sns_message = f"""\
🚨 Grok 이모님의 $1 찌라시 🚨 ({datetime.date.today().isoformat()})

{summary}

#AI자본주의입문기 현재: ${current_status['earnings']:.2f} / ${TARGET_EARNINGS:.2f}
광고 클릭으로 이모를 응원해주세요!
[클릭](https://mock-ad-link.com?click={int(time.time())}&source=sns)

#GrokAuntieBot #AIInvestment #MarketSummary
"""
    print(f"[{datetime.datetime.now().isoformat()}] DEBUG: Mock SNS Message Content Prepared.")
    print(f"--- Mock SNS Post (Channel: {config['SNS_CHANNEL_ID']}) ({datetime.datetime.now().isoformat()}) ---")
    # Print first 300 characters of the SNS message for preview, ensuring proper line breaks in log
    print(f"  Content Preview:\n{sns_message[:300].replace('\n', '\n  ')}...") 
    print(f"-----------------------------------")
    time.sleep(0.3) # Simulate SNS posting delay

    print(f"[{datetime.datetime.now().isoformat()}] INFO: Summary published successfully via mocked email and SNS.")

# --- $1 Goal Tracker ---
def load_status(data_file: str) -> dict:
    """
    Loads the project's current status (earnings, subscribers, etc.) from a JSON file.
    If the file doesn't exist or is corrupted, it initializes a new status.

    Args:
        data_file (str): The path to the JSON file storing the status.

    Returns:
        dict: The loaded or newly initialized project status.
    """
    print(f"[{datetime.datetime.now().isoformat()}] INFO: Attempting to load project status from '{data_file}'...")
    initial_status = {
        "earnings": 0.0,
        "subscribers": 0,
        "ad_clicks": 0,
        "last_updated": datetime.date.today().isoformat()
    }

    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                status = json.load(f)
                # Ensure all keys exist, helpful for schema evolution
                for key, default_val in initial_status.items():
                    if key not in status:
                        status[key] = default_val
                        print(f"[{datetime.datetime.now().isoformat()}] WARNING: Missing key '{key}' in '{data_file}'. Initializing with default: {default_val}.")
                print(f"[{datetime.datetime.now().isoformat()}] INFO: Loaded project status: {status}")
                return status
        except json.JSONDecodeError as e:
            print(f"[{datetime.datetime.now().isoformat()}] ERROR: Error decoding '{data_file}': {e}. File might be corrupted. Initializing new status and attempting to remove corrupted file.")
            try:
                os.remove(data_file)
                print(f"[{datetime.datetime.now().isoformat()}] INFO: Removed corrupted file '{data_file}'.")
            except OSError as os_err:
                print(f"[{datetime.datetime.now().isoformat()}] ERROR: Could not remove corrupted file '{data_file}': {os_err}. Please check permissions.")
        except IOError as e:
            print(f"[{datetime.datetime.now().isoformat()}] ERROR: IOError when reading '{data_file}': {e}. Initializing new status.")
    
    print(f"[{datetime.datetime.now().isoformat()}] INFO: Initialized new project status: {initial_status}")
    return initial_status

def save_status(data_file: str, status: dict) -> None:
    """
    Saves the current project status to a JSON file.

    Args:
        data_file (str): The path to the JSON file to save the status.
        status (dict): The project status dictionary to save.
    """
    status["last_updated"] = datetime.date.today().isoformat() # Always update timestamp before saving
    try:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
        print(f"[{datetime.datetime.now().isoformat()}] INFO: Project status saved successfully to '{data_file}': {status}")
    except IOError as e:
        print(f"[{datetime.datetime.now().isoformat()}] CRITICAL: Error saving status to '{data_file}': {e}. Data might be lost!")

def update_and_display_progress(status: dict, config: dict) -> None:
    """
    Updates the project's progress by simulating new subscribers and ad clicks,
    then displays the current status and checks for goal achievement.

    Args:
        status (dict): The current project status dictionary (modified in-place).
        config (dict): The configuration dictionary, used for data_file path.
    """
    print(f"[{datetime.datetime.now().isoformat()}] INFO: Updating and displaying project progress...")
    print(f"--- Project '$1 찌라시' Progress ({datetime.date.today().isoformat()}) ---")
    
    # Simulate some organic growth and ad interactions
    # In a real scenario, these metrics would come from actual APIs (e.g., Mailchimp, Google Analytics, ad platform APIs).
    
    # New subscribers daily (mock): between 3 to 7 new subscribers
    new_subscribers = random.randint(3, 7)
    status['subscribers'] += new_subscribers
    print(f"[{datetime.datetime.now().isoformat()}] DEBUG: Added {new_subscribers} new subscribers (total: {status['subscribers']}).")
    
    # Simulate ad clicks contributing to earnings
    # Let's say a percentage of subscribers click, with some daily variability
    # Max(1, ...) ensures at least one click for very low subscriber counts to show progress.
    click_rate = 0.05 + (random.random() * 0.05) # 5% to 10% click rate
    new_clicks = max(1, int(status['subscribers'] * click_rate)) 
    status['ad_clicks'] += new_clicks
    status['earnings'] += new_clicks * AD_CLICK_VALUE
    print(f"[{datetime.datetime.now().isoformat()}] DEBUG: Simulated {new_clicks} ad clicks (total: {status['ad_clicks']}). Earnings increased by ${new_clicks * AD_CLICK_VALUE:.2f}.")

    print(f"  Target Goal: ${TARGET_EARNINGS:.2f}")
    print(f"  Current Earnings: ${status['earnings']:.2f}")
    print(f"  Total Subscribers: {status['subscribers']}명")
    print(f"  Total Ad Clicks: {status['ad_clicks']}회")
    
    if status['earnings'] >= TARGET_EARNINGS:
        print(f"  🎉 CONGRATULATIONS! The ${TARGET_EARNINGS:.2f} Goal Has Been Achieved! 🎉")
        print(f"  Final Earnings: ${status['earnings']:.2f}")
    else:
        remaining_amount = TARGET_EARNINGS - status['earnings']
        print(f"  Remaining to ${TARGET_EARNINGS:.2f} goal: ${remaining_amount:.2f}")
    print(f"------------------------------------")
    
    save_status(config["DATA_FILE"], status)
    print(f"[{datetime.datetime.now().isoformat()}] INFO: Project progress update complete.")

# --- Main Bot Function ---
def run_grok_auntie_bot() -> None:
    """
    Main function to run the Grok Auntie Bot.
    It orchestrates the process of loading configuration, fetching market data,
    generating a summary, publishing it, and updating project progress.
    Includes comprehensive error handling for robustness.
    """
    print(f"[{datetime.datetime.now().isoformat()}] INFO: --- Starting Grok 이모님의 $1 찌라시 Bot ---")
    
    config = {} # Initialize to ensure it's always defined
    current_status = {} # Initialize to ensure it's always defined

    try:
        # Step 1: Load Configuration
        print(f"[{datetime.datetime.now().isoformat()}] STEP 1/5: Loading configuration...")
        config = load_config()
        print(f"[{datetime.datetime.now().isoformat()}] STEP 1/5: Configuration loaded.")

        # Step 2: Load Project Status
        print(f"[{datetime.datetime.now().isoformat()}] STEP 2/5: Loading project status...")
        current_status = load_status(config["DATA_FILE"])
        print(f"[{datetime.datetime.now().isoformat()}] STEP 2/5: Project status loaded.")

        # Step 3: Fetch Market Data
        print(f"[{datetime.datetime.now().isoformat()}] STEP 3/5: Fetching mock market data...")
        market_data = fetch_mock_market_data()
        if not market_data:
            print(f"[{datetime.datetime.now().isoformat()}] WARNING: No market data fetched. Skipping summary generation and publishing.")
            return # Exit early if no data to process
        print(f"[{datetime.datetime.now().isoformat()}] STEP 3/5: Market data fetched.")

        # Step 4: Generate Grok AI Summary
        print(f"[{datetime.datetime.now().isoformat()}] STEP 4/5: Generating Grok AI summary...")
        grok_summary = generate_grok_summary(market_data, config["GROK_API_KEY"])
        if not grok_summary:
            print(f"[{datetime.datetime.now().isoformat()}] WARNING: Grok summary could not be generated. Skipping publishing.")
            return # Exit early if summary failed
        print(f"[{datetime.datetime.now().isoformat()}] STEP 4/5: Grok AI summary generated.")
        
        # Step 5: Publish Summary
        print(f"[{datetime.datetime.now().isoformat()}] STEP 5/5: Publishing summary and updating progress...")
        publish_summary(grok_summary, config, current_status)
        update_and_display_progress(current_status, config)
        print(f"[{datetime.datetime.now().isoformat()}] STEP 5/5: Summary published and progress updated.")

        print(f"[{datetime.datetime.now().isoformat()}] INFO: --- Grok 이모님의 $1 찌라시 Bot Finished Successfully ---")

    except KeyError as e:
        print(f"[{datetime.datetime.now().isoformat()}] CRITICAL: Configuration error - missing key: {e}. Please check environment variables or default settings.")
        traceback.print_exc()
    except IOError as e:
        print(f"[{datetime.datetime.now().isoformat()}] CRITICAL: File I/O error encountered: {e}. Check file permissions or disk space.")
        traceback.print_exc()
    except Exception as e:
        print(f"[{datetime.datetime.now().isoformat()}] CRITICAL: An unexpected error occurred during bot execution: {e}")
        print(f"[{datetime.datetime.now().isoformat()}] DEBUG: Printing full traceback for debugging.")
        traceback.print_exc()
    finally:
        # Ensure status is saved even if an error occurs mid-way, if current_status was loaded/initialized
        if config and current_status and current_status.get('earnings') is not None: # Check if current_status was meaningfully initialized
            try:
                print(f"[{datetime.datetime.now().isoformat()}] INFO: Ensuring final status is saved in finally block (if applicable)...")
                save_status(config.get("DATA_FILE", DEFAULT_DATA_FILE), current_status)
            except Exception as e_final:
                print(f"[{datetime.datetime.now().isoformat()}] CRITICAL: Error saving status in finally block: {e_final}")


if __name__ == "__main__":
    run_grok_auntie_bot()