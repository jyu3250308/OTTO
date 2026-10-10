
# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import os
import datetime
import feedparser
import requests # For optional Slack notifications

FEED_FALLBACK_URL = "https://www.theverge.com/rss/index.xml" # A public tech news feed for demo
KEYWORDS_FOR_HACKS = ["api", "beta", "new feature", "experimental", "undocumented", "hack", "trick", "algorithm update", "early access", "platform change"]
OUTPUT_FILE = "platform_recipes.txt"

def detect_hidden_feature(title, summary):
    """Checks if title or summary contains keywords indicating a hidden feature or exploit."""
    text_to_check = (title + " " + summary).lower()
    for keyword in KEYWORDS_FOR_HACKS:
        if keyword in text_to_check:
            return True
    return False

def generate_guidelines(title):
    """Generates AI-like (rule-based) usage guidelines for a detected feature."""
    guidelines = []
    title_lower = title.lower()
    if "api" in title_lower:
        guidelines.append("Explore new data integration possibilities.")
    if "beta" in title_lower or "experimental" in title_lower:
        guidelines.append("Test with a small, engaged audience first; expect changes.")
    if "algorithm update" in title_lower:
        guidelines.append("Analyze impact on reach/visibility and adapt content strategy.")
    if not guidelines:
        guidelines.append("Investigate further for competitive advantage.")
    return " ".join(guidelines)

def send_slack_notification(message, webhook_url):
    """Sends a notification to a Slack channel if a webhook URL is provided."""
    if webhook_url and webhook_url != "YOUR_SLACK_WEBHOOK":
        try:
            response = requests.post(webhook_url, json={"text": message}, timeout=5)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            print(f"[NOTIF] Slack notification sent successfully.")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to send Slack notification: {e}")
    else:
        print("[INFO] Slack webhook not configured or invalid. Skipping notification.")

def main():
    parser = argparse.ArgumentParser(description="Algo-Alchemist: Discover hidden platform recipes.")
    parser.add_argument("--feed_url", type=str, help="RSS feed URL to monitor (e.g., YouTube Creator Blog).")
    args = parser.parse_args()

    feed_url = args.feed_url or os.getenv("ALCHEMIST_FEED_URL", FEED_FALLBACK_URL)
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL", "YOUR_SLACK_WEBHOOK") # Default placeholder

    if feed_url == FEED_FALLBACK_URL:
        print("\n[INFO] No custom feed URL provided. Running in demo mode with a generic tech news feed.")
        print(f"[INFO] To use your own feed, run: python {os.path.basename(__file__)} --feed_url 'YOUR_RSS_URL'\n")

    print(f"[INFO] Monitoring feed: {feed_url}")
    print(f"[INFO] Results will be saved to: {OUTPUT_FILE}")

    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo:
            print(f"[WARNING] Feed parsing error: {feed.bozo_exception}")

        discovered_recipes = []
        for entry in feed.entries:
            title = entry.get('title', 'No Title')
            summary = entry.get('summary', entry.get('description', 'No Summary'))
            link = entry.get('link', '#')

            if detect_hidden_feature(title, summary):
                guidelines = generate_guidelines(title)
                recipe_text = f"\n--- Recipe Discovered! ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---\n"
                recipe_text += f"Title: {title}\n"
                recipe_text += f"Link: {link}\n"
                recipe_text += f"Summary: {summary[:200]}...\n"
                recipe_text += f"AI Guideline: {guidelines}\n"
                recipe_text += "--------------------------------------\n"
                discovered_recipes.append(recipe_text)
                print(f"[FOUND] New recipe detected: '{title}'")
                send_slack_notification(f"Algo-Alchemist found a new recipe: {title} - {link}", slack_webhook_url)

        if discovered_recipes:
            with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
                for recipe in discovered_recipes:
                    f.write(recipe)
            print(f"[SUCCESS] {len(discovered_recipes)} new recipe(s) saved to {OUTPUT_FILE}")
        else:
            print("[INFO] No new hidden features or platform recipes detected this run.")

    except Exception as e:
        print(f"[CRITICAL] An error occurred: {e}")

    print("\n[INFO] To run this bot regularly (e.g., daily), consider using a task scheduler (Cron on Linux/macOS, Task Scheduler on Windows).")
    print("       Example for Cron: 0 9 * * * python /path/to/algo_alchemist_bot.py --feed_url 'YOUR_RSS_URL' > /dev/null 2>&1\n")

if __name__ == "__main__":
    main()