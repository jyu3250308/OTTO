import datetime
import json
import requests
import os

# --- Configuration ---
# Replace with your actual Slack Webhook URL if you want to receive notifications.
# If left as 'YOUR_SLACK_WEBHOOK_URL', the bot will only save to a file.
SLACK_WEBHOOK_URL = 'YOUR_SLACK_WEBHOOK_URL'
OUTPUT_DIR = 'humor_reports' # Directory to save summary files

# --- Mocking Functions for External Services ---

def mock_fetch_reddit_hot_posts():
    """
    Mocks fetching popular humor posts from Reddit.
    In a real scenario, this would use an API (e.g., PRAW) or web scraping.
    Returns a list of dictionaries, each representing a humor post.
    """
    print("[MOCK] Fetching top humor posts from Reddit...")
    mock_posts = [
        {"title": "Why don't scientists trust atoms? Because they make up everything!", "url": "https://www.reddit.com/r/jokes/mock1"},
        {"title": "I told my wife she was drawing her eyebrows too high. She looked surprised.", "url": "https://www.reddit.com/r/jokes/mock2"},
        {"title": "What do you call a fake noodle? An impasta!", "url": "https://www.reddit.com/r/jokes/mock3"},
        {"title": "Parallel lines have so much in common. It's a shame they'll never meet.", "url": "https://www.reddit.com/r/puns/mock4"},
        {"title": "My computer died today. I\u2019m sad because it was my best friend. And my only friend.", "url": "https://www.reddit.com/r/funny/mock5"}
    ]
    print(f"[MOCK] Fetched {len(mock_posts)} humor posts.")
    return mock_posts

def mock_ai_summarize_humor(posts):
    """
    Mocks an AI summarizing a list of humor posts.
    In a real scenario, this would call an LLM API (e.g., OpenAI GPT-3.5/4).
    """
    print("[MOCK] AI is summarizing the humor posts...")
    if not posts:
        return "No humor posts to summarize today."

    summary_text = (
        "✨ AI-powered Humor Digest ✨\n\n"
        "Today's top trending humor on Reddit includes a mix of wordplay, observational jokes, "
        "and relatable tech humor. The AI has identified common themes around surprising "
        "revelations, identity, and the inherent nature of things.\n\n"
        "Here are some highlights:\n"
        f"- Atom jokes: '{posts[0]['title']}'\n"
        f"- Eyebrow humor: '{posts[1]['title']}'\n"
        f"- Pasta puns: '{posts[2]['title']}'\n"
        "\nEnjoy your daily dose of laughter!"
    )
    print("[MOCK] AI summary generated.")
    return summary_text

# --- Output and Notification Functions ---

def save_summary_to_file(summary_text):
    """
    Saves the AI-generated summary to a timestamped text file.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(OUTPUT_DIR, f"reddit_humor_summary_{timestamp}.txt")
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(summary_text)
        print(f"✅ Summary successfully saved to '{filepath}'")
        return filepath
    except IOError as e:
        print(f"❌ Error saving summary to file: {e}")
        return None

def send_slack_message(message):
    """
    Sends the AI summary to Slack using a webhook.
    """
    if SLACK_WEBHOOK_URL == 'YOUR_SLACK_WEBHOOK_URL':
        print("💡 Slack Webhook URL is a placeholder. Skipping Slack notification.")
        print("   To enable Slack notifications, replace 'YOUR_SLACK_WEBHOOK_URL' with your actual webhook.")
        return False

    try:
        headers = {'Content-type': 'application/json'}
        payload = {'text': message}
        response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        print("✅ Slack message sent successfully.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending Slack message: {e}")
        return False

# --- Main Bot Logic ---

def main():
    """
    Main function to orchestrate the Reddit humor analysis and Slack notification.
    """
    print("🚀 Starting AI Reddit Humor Bot...")
    
    try:
        # 1. Fetch Reddit posts (mocked)
        reddit_posts = mock_fetch_reddit_hot_posts()
        
        # 2. AI Summarize humor (mocked)
        ai_summary = mock_ai_summarize_humor(reddit_posts)
        
        # 3. Save summary to file
        saved_file_path = save_summary_to_file(ai_summary)
        if saved_file_path:
            # os.path.abspath returns platform specific paths, e.g., C:\foo\bar on Windows.
            # json.dumps will correctly escape '\' to '\\' when this string is serialized.
            ai_summary += f"\n\n(Full report saved to: {os.path.abspath(saved_file_path)})"
        
        # 4. Send summary to Slack
        send_slack_message(ai_summary)
        
        print("✅ AI Reddit Humor Bot finished its run.")
    
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
    # To run this bot automatically, you can schedule it using tools like Cron (Linux/macOS)
    # or Task Scheduler (Windows).
    # Example for Cron: '0 * * * * python /path/to/reddit_humor_bot.py' (runs every hour)
