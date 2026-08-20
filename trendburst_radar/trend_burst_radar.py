
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
import time
import random
from collections import deque
import json
import requests

# --- Constants ---
TREND_HISTORY_WINDOW = 5 # Number of past observations to consider for trend detection
BURST_THRESHOLD = 2.0 # Factor by which current usage must exceed average to be a burst
MONITOR_INTERVAL = 3 # Seconds between monitoring cycles (simulated)
OUTPUT_FILENAME = "detected_trends.csv"

# --- Demo Data (Fallback if no real data source) ---
DEMO_MEMES = ["cat-meme-v3", "doggo-challenge", "epic-fail-comp", "vibe-check-dance", "ai-art-trend"]
DEMO_KEYWORDS = ["#innovation", "#futuretech", "#web3", "#metaverse", "#generativeai", "#solarpunk"]

class TrendBurstDetector:
    def __init__(self):
        self.trend_data = {}

    def _update_trend_history(self, item, count):
        if item not in self.trend_data:
            self.trend_data[item] = deque(maxlen=TREND_HISTORY_WINDOW)
        self.trend_data[item].append(count)

    def detect_burst(self, current_trends):
        detected = []
        for item, current_count in current_trends.items():
            self._update_trend_history(item, current_count)
            history = list(self.trend_data[item])

            if len(history) < TREND_HISTORY_WINDOW: # Not enough data for comparison yet
                continue

            # Calculate average count from history (excluding current for a true 'burst' detection)
            historical_avg = sum(history[:-1]) / (len(history) -1) if len(history) > 1 else 0
            
            if historical_avg > 0 and current_count >= historical_avg * BURST_THRESHOLD:
                detected.append({
                    "item": item,
                    "current_count": current_count,
                    "historical_avg": historical_avg,
                    "timestamp": time.time()
                })
        return detected

def fetch_simulated_social_data():
    # Simulate real-time social media 'posts' traffic
    data = {}
    for _ in range(random.randint(5, 20)): # Simulate 5 to 20 'posts'
        item = random.choice(DEMO_MEMES + DEMO_KEYWORDS)
        # Introduce occasional 'bursts' for demonstration
        if random.random() < 0.1: # 10% chance to generate a high count for a random item
            data[item] = data.get(item, 0) + random.randint(5, 15) # Higher count
        else:
            data[item] = data.get(item, 0) + random.randint(1, 3)
    return data

def send_slack_notification(message, webhook_url):
    if not webhook_url or webhook_url == "YOUR_SLACK_WEBHOOK_URL":
        print("Slack webhook URL not configured. Skipping Slack notification.")
        return
    try:
        payload = {"text": message}
        response = requests.post(webhook_url, json=payload, timeout=5)
        response.raise_for_status()
        print(f"Slack notification sent: {message[:50]}...")
    except requests.exceptions.RequestException as e:
        print(f"Error sending Slack notification: {e}")

def save_trend_to_file(trend_info, filename):
    mode = 'a' if os.path.exists(filename) else 'w'
    with open(filename, mode, encoding='utf-8') as f:
        if mode == 'w': # Write header if file is new
            f.write("timestamp,item,current_count,historical_avg\n")
        ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(trend_info['timestamp']))
        f.write(f"{ts},{trend_info['item']},{trend_info['current_count']},{trend_info['historical_avg']:.2f}\n")
    print(f"Trend '{trend_info['item']}' saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="TrendBurst Radar: Detect emerging social media trends.")
    parser.add_argument('--output', type=str, default=OUTPUT_FILENAME,
                        help=f"Output CSV filename for detected trends. Default: {OUTPUT_FILENAME}")
    parser.add_argument('--slack_webhook', type=str, default=os.getenv('SLACK_WEBHOOK_URL'),
                        help="Slack webhook URL for notifications (can also be set via SLACK_WEBHOOK_URL env var).")
    args = parser.parse_args()

    print("\n🚀 TrendBurst Radar Initializing...")
    print(f"Output file: {args.output}")
    if not args.slack_webhook:
        print("No Slack webhook URL provided. Notifications will only be printed to console.")
        print("Set SLACK_WEBHOOK_URL environment variable or use --slack_webhook argument for Slack alerts.")
    else:
        print("Slack notifications enabled.")
    print("\n--- Running in Demo Mode (simulated data) ---")
    print(f"To use your own data, this section would integrate with actual social media APIs.")
    print("Now detecting trend bursts from simulated social media activity...\n")

    detector = TrendBurstDetector()

    try:
        while True:
            print(f"[{time.strftime('%H:%M:%S')}] Monitoring for new social signals...")
            current_social_signals = fetch_simulated_social_data()
            
            if not current_social_signals:
                print("No signals detected in this cycle.")
                time.sleep(MONITOR_INTERVAL)
                continue

            detected_bursts = detector.detect_burst(current_social_signals)

            if detected_bursts:
                for trend in detected_bursts:
                    message = (
                        f"🚨 TrendBurst Detected! 🚨\n"
                        f"Item: {trend['item']}\n"
                        f"Current Usage: {trend['current_count']}\n"
                        f"Historical Avg: {trend['historical_avg']:.2f}\n"
                        f"Potential viral content detected. Act fast!\n"
                    )
                    print("\n" + message)
                    send_slack_notification(message, args.slack_webhook)
                    save_trend_to_file(trend, args.output)
            else:
                print("No significant trend bursts detected yet.")

            time.sleep(MONITOR_INTERVAL)

    except KeyboardInterrupt:
        print("\nTrendBurst Radar stopped by user. Goodbye!")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

# --- For repeated use, you can schedule this script with cron (Linux/macOS) or Task Scheduler (Windows) ---
# Example for cron to run every 5 minutes:
# */5 * * * * /usr/bin/env python3 /path/to/trend_burst_radar.py --output /path/to/detected_trends.csv >> /var/log/trend_burst_radar.log 2>&1
