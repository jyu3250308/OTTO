
# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import requests
import feedparser
import os
import argparse
import collections
import datetime

# --- Configuration & Constants ---
# Default RSS feeds for demonstration if no custom feeds are provided
DEFAULT_RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://www.theverge.com/rss/index.xml",
    "https://techcrunch.com/feed/"
]

MIN_KEYWORD_LENGTH = 3
TOP_N_TRENDS = 5

# --- Helper Functions ---
def fetch_rss_feed(url):
    """Fetches and parses an RSS feed from the given URL."""
    try:
        feed = feedparser.parse(url)
        if feed.bozo: # Checks for well-formedness
            print(f"[WARNING] Malformed RSS feed detected for {url}: {feed.bozo_exception}")
        return feed
    except Exception as e:
        print(f"[ERROR] Could not fetch RSS feed from {url}: {e}")
        return None

def analyze_content_for_keywords(entries):
    """Analyzes feed entries to extract and count keywords."""
    all_text = []
    for entry in entries:
        title = entry.get('title', '')
        summary = entry.get('summary', '') or entry.get('description', '')
        all_text.append(title)
        all_text.append(summary)
    
    full_text = ' '.join(all_text).lower()
    # Simple tokenization: split by non-alphanumeric, filter short words
    words = [word for word in 
             ' '.join(filter(str.isalnum, full_text.split())).split()
             if len(word) >= MIN_KEYWORD_LENGTH and not word.isdigit()]
    
    return collections.Counter(words)

def get_trending_insights(keyword_counts):
    """Identifies 'rising waves' and 'tides' based on keyword counts."""
    total_words = sum(keyword_counts.values())
    if total_words == 0:
        return [], []

    # 'Rising Wave': Top N keywords by frequency (simplified for a single run)
    rising_waves = keyword_counts.most_common(TOP_N_TRENDS)

    # 'Tide/Saturation': Keywords that are highly frequent and potentially generic/overused
    # In a real system, this would compare against a baseline. Here, we identify
    # keywords that are very common and not new (e.g., 'news', 'technology', 'world')
    # For this simplified version, let's just pick the absolute most frequent ones above a high threshold.
    saturated_threshold_ratio = 0.02 # e.g., if a word makes up >2% of all words
    tides = [(word, count) for word, count in keyword_counts.items() 
             if count / total_words >= saturated_threshold_ratio and word not in [item[0] for item in rising_waves]]
    
    # Sort tides by frequency, descending
    tides = sorted(tides, key=lambda x: x[1], reverse=True)[:TOP_N_TRENDS]

    return rising_waves, tides

def save_report(report_content, filename="trend_report.txt"):
    """Saves the trend analysis report to a text file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"[SUCCESS] Trend report saved to {filename}")
    except IOError as e:
        print(f"[ERROR] Could not save report to {filename}: {e}")

# --- Main Logic ---
def main():
    parser = argparse.ArgumentParser(
        description="Content Surf AI: Monitors content trends from RSS feeds."
    )
    parser.add_argument(
        "-f", "--feeds", nargs='*', 
        help="List of RSS feed URLs to monitor (e.g., 'url1 url2'). If omitted, uses default feeds."
    )
    args = parser.parse_args()

    selected_feeds = args.feeds if args.feeds else DEFAULT_RSS_FEEDS

    if not args.feeds:
        print("[INFO] No custom RSS feeds provided. Using sample data from default feeds for demonstration.")
        print("       To use your own feeds, run with: python content_surf_ai.py -f 'http://yourfeed1.com/rss' 'http://yourfeed2.com/rss'")

    print(f"[INFO] Monitoring {len(selected_feeds)} RSS feeds...")

    all_keywords_counter = collections.Counter()
    total_processed_entries = 0

    for url in selected_feeds:
        print(f"[INFO] Processing feed: {url}")
        feed = fetch_rss_feed(url)
        if feed and feed.entries:
            all_keywords_counter.update(analyze_content_for_keywords(feed.entries))
            total_processed_entries += len(feed.entries)
        else:
            print(f"[WARNING] No entries found or failed to process feed: {url}")
    
    if total_processed_entries == 0:
        print("[ERROR] No content processed from any feeds. Exiting.")
        return

    print(f"[INFO] Total entries processed: {total_processed_entries}")

    rising_waves, tides = get_trending_insights(all_keywords_counter)

    report_lines = [
        "# Content Surf AI: Trend Monitoring Report",
        f"Report Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Monitored Feeds: {len(selected_feeds)}",
        f"Total Keywords Analyzed: {sum(all_keywords_counter.values())}",
        "\n--- Rising Waves (New Opportunities) ---"
    ]
    if rising_waves:
        for i, (keyword, count) in enumerate(rising_waves):
            report_lines.append(f"{i+1}. {keyword.capitalize()} (Count: {count})")
    else:
        report_lines.append("No distinct rising waves detected at this time.")

    report_lines.append("\n--- Incoming Tides (Potential Saturation) ---")
    if tides:
        for i, (keyword, count) in enumerate(tides):
            report_lines.append(f"{i+1}. {keyword.capitalize()} (Count: {count})")
        report_lines.append("\nConsider exploring related but less saturated topics if you are focusing on these areas.")
    else:
        report_lines.append("No significant saturation detected.")

    report_content = "\n".join(report_lines)
    print("\n" + report_content)
    save_report(report_content)

    print("\n[INFO] This script can be scheduled to run daily using cron (Linux/macOS) or Task Scheduler (Windows).")
    print("       Example (Linux cron): `0 9 * * * python /path/to/content_surf_ai.py` (runs every day at 9 AM)")

if __name__ == "__main__":
    main()
