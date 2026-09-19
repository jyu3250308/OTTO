
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
import random
import time
import datetime
import pandas as pd
import requests # For sending notifications

# --- Constants ---
SLACK_WEBHOOK_URL_PLACEHOLDER = os.getenv("SLACK_WEBHOOK_URL", "YOUR_SLACK_WEBHOOK_URL_HERE")
ALERT_THRESHOLD_PERCENT = 50 # Percentage increase to trigger an alert
LOOKBACK_PERIOD = 5 # Number of previous data points for calculating average

def load_data(filepath=None):
    """Loads content sharing data from a CSV or generates sample data if no file is provided."""
    if filepath and os.path.exists(filepath):
        print(f"🔄 Loading content sharing data from {filepath}...")
        try:
            df = pd.read_csv(filepath)
            if 'timestamp' not in df.columns or 'shares' not in df.columns:
                raise ValueError("CSV must contain 'timestamp' and 'shares' columns.")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values(by='timestamp').reset_index(drop=True)
            print(f"✅ Data loaded successfully. Total entries: {len(df)}")
            return df
        except Exception as e:
            print(f"❌ Error loading data from {filepath}: {e}. Falling back to sample data.")
            return generate_sample_data()
    else:
        print("💡 No file path provided or file not found. Generating sample data for demonstration.")
        return generate_sample_data()

def generate_sample_data():
    """Generates sample content sharing data for demonstration."""
    print("✨ Generating sample content sharing data...")
    timestamps = [datetime.datetime.now() - datetime.timedelta(minutes=(100 - i) * 5) for i in range(100)]
    shares = [random.randint(10, 100) for _ in range(100)]
    # Introduce a sudden spike for demo purposes
    spike_start_index = random.randint(30, 70)
    for i in range(spike_start_index, spike_start_index + 5):
        if i < len(shares):
            shares[i] = max(shares[i-1] + random.randint(50, 200), 100) if i > 0 else random.randint(100, 300)
    df = pd.DataFrame({'timestamp': timestamps, 'shares': shares, 'content_id': [f'content_{random.randint(1,5)}' for _ in range(100)]})
    print("✅ Sample data generated.")
    return df

def detect_viral_pulse(df, threshold_percent=ALERT_THRESHOLD_PERCENT, lookback_period=LOOKBACK_PERIOD):
    """Detects significant spikes in share counts indicating a viral pulse."""
    viral_events = []
    print(f"🔍 Monitoring for viral pulses with threshold: {threshold_percent}% increase over last {lookback_period} periods.")

    if len(df) < lookback_period + 1:
        print(f"⚠️ Not enough data points ({len(df)}) to apply lookback period of {lookback_period}.")
        return viral_events

    for i in range(lookback_period, len(df)):
        current_shares = df.loc[i, 'shares']
        previous_shares = df.loc[i-lookback_period:i-1, 'shares']

        if not previous_shares.empty:
            average_prev_shares = previous_shares.mean()
            if average_prev_shares == 0: # Avoid division by zero
                percentage_increase = float('inf') if current_shares > 0 else 0
            else:
                percentage_increase = ((current_shares - average_prev_shares) / average_prev_shares) * 100
            
            if percentage_increase >= threshold_percent:
                timestamp = df.loc[i, 'timestamp']
                content_id = df.loc[i, 'content_id'] if 'content_id' in df.columns else 'N/A'
                event = {
                    'timestamp': timestamp,
                    'content_id': content_id,
                    'current_shares': current_shares,
                    'avg_previous_shares': round(average_prev_shares, 2),
                    'percentage_increase': round(percentage_increase, 2),
                    'message': f"🚨 Viral Pulse Detected for {content_id}! {round(percentage_increase, 2)}% increase!"
                }
                viral_events.append(event)
                print(f"    {event['message']} at {timestamp}")
    if not viral_events:
        print("    No viral pulses detected in the provided data.")
    return pd.DataFrame(viral_events)

def send_alert(message):
    """Sends an alert message, e.g., to a Slack webhook or prints it."""
    if SLACK_WEBHOOK_URL_PLACEHOLDER and SLACK_WEBHOOK_URL_PLACEHOLDER != "YOUR_SLACK_WEBHOOK_URL_HERE":
        try:
            headers = {'Content-type': 'application/json'}
            payload = {'text': message}
            response = requests.post(SLACK_WEBHOOK_URL_PLACEHOLDER, json=payload, headers=headers, timeout=5)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            print(f"✉️ Alert sent successfully to Slack.")
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send Slack alert: {e}. Printing to console instead.")
            print(f"[ALERT] {message}")
    else:
        print(f"[ALERT - No Slack URL configured] {message}")
        print("💡 Tip: Set the SLACK_WEBHOOK_URL environment variable or modify the code to use Slack.")

def save_viral_events(viral_df, output_filename="viral_pulse_events.csv"):
    """Saves detected viral events to a CSV file."""
    if not viral_df.empty:
        output_filepath = os.path.join(os.getcwd(), output_filename)
        viral_df.to_csv(output_filepath, index=False, mode='a', header=not os.path.exists(output_filepath))
        print(f"💾 Viral events saved/appended to {output_filepath}")
        print("✅ Tangible output created! Share this file to showcase detected viral opportunities.")
    else:
        print("No viral events to save.")

def main():
    parser = argparse.ArgumentParser(description="ViralPulse Pinger: Monitor content for viral spikes and alert creators.")
    parser.add_argument('--file', type=str, help='Path to a CSV file containing content sharing data (columns: timestamp, shares, content_id).')
    args = parser.parse_args()

    print("🚀 Starting ViralPulse Pinger...")

    # 1. Load or generate data
    df = load_data(args.file)
    if df.empty:
        print("Exiting: No data to process.")
        return

    # 2. Detect viral pulses
    viral_events_df = detect_viral_pulse(df)

    # 3. Send alerts for detected pulses
    if not viral_events_df.empty:
        for _, event in viral_events_df.iterrows():
            alert_message = f"🔥 Viral Golden Time for '{event['content_id']}'! Shares surged by {event['percentage_increase']}% to {event['current_shares']} at {event['timestamp']}. Act NOW!"
            send_alert(alert_message)

    # 4. Save learned 'trigger conditions' (represented by detected events)
    save_viral_events(viral_events_df)

    print("✨ ViralPulse Pinger finished its monitoring cycle.")
    print("--------------------------------------------------------------------------------")
    print("💡 To use this repeatedly, schedule it with cron (Linux/macOS) or Task Scheduler (Windows). ")
    print("   Example (Linux/macOS): Add '0 * * * * python3 /path/to/viral_pulse_pinger.py --file my_data.csv' to your crontab to run hourly.")
    print("--------------------------------------------------------------------------------")

if __name__ == "__main__":
    main()
