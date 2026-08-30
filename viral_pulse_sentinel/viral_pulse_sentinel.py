# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
import argparse
import datetime
import random
import csv
import os
import feedparser
import time

# Reconfigure stdout/stderr for UTF-8 in Windows
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# --- Constants ---
RSS_FEED_URL = "http://rss.cnn.com/rss/cnn_topstories.rss" # Example public RSS feed
CONTENT_TYPES = {
    "challenge": ["challenge", "viral", "trend", "new", "game"],
    "tutorial": ["how to", "guide", "learn", "tutorial", "step-by-step"],
    "news": ["breaking", "report", "update", "news", "says", "source"],
    "review": ["review", "test", "hands-on", "opinion", "product"]
}

# --- Data Loading and Simulation ---
def load_data_from_csv(file_path: str) -> list:
    """Loads social data from a CSV file."""
    print(f"[INFO] Attempting to load data from CSV: {file_path}")
    data = []
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader):
                try:
                    timestamp = datetime.datetime.fromisoformat(row['timestamp'])
                    content_type = row.get('content_type', 'general').lower()
                    engagement_score = float(row['engagement_score'])
                    data.append({'timestamp': timestamp, 'content_type': content_type, 'engagement_score': engagement_score})
                except (ValueError, KeyError) as e:
                    print(f"[WARNING] Skipping row {i+1} due to data error in {file_path}: {e}")
        print(f"[SUCCESS] Loaded {len(data)} data points from {file_path}.")
        return data
    except FileNotFoundError:
        print(f"[ERROR] Data file not found: {file_path}.")
        return []
    except Exception as e:
        print(f"[ERROR] Failed to read CSV file {file_path}: {e}")
        return []

def fetch_and_simulate_social_data(num_entries: int = 50) -> list:
    """Fetches recent data from RSS feed and simulates engagement."""
    print(f"[INFO] Fetching recent public data from {RSS_FEED_URL} to simulate trends...")
    simulated_data = []
    try:
        feed = feedparser.parse(RSS_FEED_URL)
        if not feed.entries:
            print("[WARNING] RSS feed returned no entries. Cannot simulate.")
            return []

        for entry in random.sample(feed.entries, min(num_entries, len(feed.entries))):
            title = entry.get('title', '').lower()
            summary = entry.get('summary', '').lower() if entry.get('summary') else ''
            published_parsed = entry.get('published_parsed')

            if not published_parsed: continue
            dt_object = datetime.datetime.fromtimestamp(time.mktime(published_parsed))

            content_type = "general"
            for c_type, keywords in CONTENT_TYPES.items():
                if any(k in title or k in summary for k in keywords):
                    content_type = c_type; break
            
            engagement_score = random.uniform(0.3, 0.7)
            if content_type in ["challenge", "tutorial"] or any(k in title for k in ["viral", "popular", "trend"]):
                engagement_score += random.uniform(0.1, 0.3)
            simulated_data.append({'timestamp': dt_object, 'content_type': content_type, 'engagement_score': min(engagement_score, 1.0)})
        print(f"[INFO] Successfully simulated {len(simulated_data)} data points from RSS feed.")
        return simulated_data
    except Exception as e:
        print(f"[ERROR] Failed to fetch or parse RSS feed: {e}.")
        return []

def generate_mock_data(num_entries: int = 200) -> list:
    """Generates sample mock data for demonstration."""
    print(f"[INFO] Generating {num_entries} sample mock data points for demonstration.")
    data = []
    now = datetime.datetime.now()
    content_types_list = list(CONTENT_TYPES.keys()) + ["general"]
    for _ in range(num_entries):
        timestamp = now - datetime.timedelta(hours=random.randint(0, 72), minutes=random.randint(0, 59))
        content_type = random.choice(content_types_list)
        engagement_score = random.uniform(0.1, 1.0)
        if timestamp.hour in [10, 14, 20]: engagement_score += random.uniform(0.1, 0.2)
        if content_type == "challenge" and timestamp.hour == 14: engagement_score += random.uniform(0.2, 0.3)
        data.append({'timestamp': timestamp, 'content_type': content_type, 'engagement_score': min(engagement_score, 1.0)})
    print(f"[SUCCESS] Generated {len(data)} mock data points.")
    return data

# --- Analysis Logic ---
def analyze_viral_patterns(data: list) -> list:
    """Analyzes engagement patterns based on content type, hour, and day of week."""
    print("[INFO] Analyzing viral patterns...")
    patterns = {}
    for item in data:
        key = (item['content_type'], item['timestamp'].hour, item['timestamp'].weekday())
        patterns.setdefault(key, {'total_engagement': 0, 'count': 0})
        patterns[key]['total_engagement'] += item['engagement_score']
        patterns[key]['count'] += 1

    report_data = []
    for (content_type, hour, day_of_week), stats in patterns.items():
        avg_engagement = stats['total_engagement'] / stats['count']
        report_data.append({
            'content_type': content_type,
            'hour_of_day': hour,
            'day_of_week': datetime.date(1900, 1, 1).replace(weekday=day_of_week).strftime('%A'),
            'average_engagement_score': round(avg_engagement, 4),
            'data_points_count': stats['count']
        })
    print(f"[INFO] Analysis complete. Generated {len(report_data)} pattern entries.")
    return report_data

def predict_optimal_time(report_data: list, target_content_type: str) -> dict or None:
    """Predicts the optimal upload time for a given content type."""
    print(f"[INFO] Predicting optimal time for content type: '{target_content_type}'...")
    filtered_data = [item for item in report_data if item['content_type'] == target_content_type]
    if not filtered_data:
        print(f"[WARNING] No analysis data for '{target_content_type}'. Cannot predict.")
        return None

    optimal_entry = max(filtered_data, key=lambda x: x['average_engagement_score'])
    print(f"[SUCCESS] Optimal time predicted for '{target_content_type}'.")
    return optimal_entry

# --- File Operations ---
def save_notification(message: str, content_type: str = "general"):
    """Saves an optimal time notification to a text file."""
    filename = f"viral_pulse_notification_{content_type}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("ViralPulse Sentinel - Optimal Upload Time Alert\n")
            f.write("------------------------------------------\n")
            f.write(message)
            f.write("\n\nTip: Consider scheduling your content around this time for maximum impact!")
        print(f"[SUCCESS] Notification saved to {filename}")
    except IOError as e:
        print(f"[ERROR] Could not save notification to file: {e}")

def save_viral_pattern_report(report_data: list):
    """Saves the full viral pattern report to a CSV file."""
    filename = f"viral_pattern_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    if not report_data:
        print("[WARNING] No report data to save."); return

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = report_data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(report_data)
        print(f"[SUCCESS] Viral pattern report saved to {filename}")
    except IOError as e:
        print(f"[ERROR] Could not save viral pattern report to file: {e}")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while saving CSV: {e}")

# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(description="ViralPulse Sentinel: Predicts optimal social media upload times.")
    parser.add_argument("--content-type", type=str, default="general", help="Target content type for prediction.")
    parser.add_argument("--data-file", type=str, help="Path to a CSV file containing social data (timestamp, content_type, engagement_score).")
    parser.add_argument("--mock-only", action="store_true", help="Force using only mock data.")
    args = parser.parse_args()

    print("\n🚀 Starting ViralPulse Sentinel...")

    social_data = []
    data_source_info = ""

    if args.data_file:
        social_data = load_data_from_csv(args.data_file)
        if social_data: data_source_info = f"custom CSV file ({args.data_file})"

    if not social_data and not args.mock_only:
        social_data = fetch_and_simulate_social_data()
        if social_data: data_source_info = "public RSS feed data (simulated)"

    if not social_data:
        print("[INFO] No valid external data found or --mock-only flag active. Falling back to internal sample data.")
        print("       지금은 샘플 데이터입니다. 본인 파일을 쓰려면 python viral_pulse_sentinel.py --data-file 내파일.csv")
        social_data = generate_mock_data()
        if not data_source_info: data_source_info = "internal mock data"

    if not social_data:
        print("[CRITICAL] No data available for analysis. Exiting.")
        return
    
    print(f"[INFO] Proceeding with analysis based on {data_source_info}...")

    viral_pattern_report = analyze_viral_patterns(social_data)
    optimal_time_prediction = predict_optimal_time(viral_pattern_report, args.content_type)

    if optimal_time_prediction:
        message = (
            f"Content Type: {optimal_time_prediction['content_type'].upper()}\n"
            f"Predicted Optimal Upload Time: {optimal_time_prediction['day_of_week']} at {optimal_time_prediction['hour_of_day']}:00 (average)\n"
            f"Average Engagement Score: {optimal_time_prediction['average_engagement_score']:.2f}\n"
            f"Based on {optimal_time_prediction['data_points_count']} data points."
        )
        print("\n🔔 Optimal Upload Time Detected!\n" + message)
        save_notification(message, args.content_type)
    else:
        print(f"[WARNING] Could not determine optimal upload time for '{args.content_type}'.")

    save_viral_pattern_report(viral_pattern_report)

    print("\n✨ ViralPulse Sentinel finished. Check generated files for insights.")
    print("------------------------------------------------------------------")
    print("Example usage:")
    print("  python viral_pulse_sentinel.py --content-type challenge")
    print("  python viral_pulse_sentinel.py --data-file my_social_data.csv")
    print("  python viral_pulse_sentinel.py --mock-only --content-type tutorial")

if __name__ == "__main__":
    main()
