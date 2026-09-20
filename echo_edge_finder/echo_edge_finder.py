import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import os
import pandas as pd
from datetime import datetime

# Define constants for better readability and easier modification
RECENT_COMMENTS_SPLIT_RATIO = 0.75 # Defines the threshold for 'recent' comments (e.g., 0.75 means last 25% are recent)
DEFAULT_KEYWORDS = 'update,relevant,feature,outdated,bug,question'

def load_comments_data(filepath: str = None) -> pd.DataFrame:
    """
    Loads comments from a specified CSV file. If no valid file is provided,
    or an error occurs during loading, it falls back to using sample data.

    Args:
        filepath (str): The path to the CSV file. The file must contain
                        'timestamp' and 'content' columns.

    Returns:
        pd.DataFrame: A DataFrame containing comments, sorted by timestamp.
    """
    if filepath:
        if not os.path.exists(filepath):
            print(f"[WARN] Specified file '{filepath}' does not exist. Attempting to use sample data.")
        elif not filepath.lower().endswith('.csv'):
            print(f"[WARN] Specified file '{filepath}' is not a CSV. Attempting to use sample data.")
        else:
            try:
                print(f"[INFO] Attempting to load data from '{filepath}'...")
                df = pd.read_csv(filepath)

                # Validate required columns
                required_columns = ['timestamp', 'content']
                if not all(col in df.columns for col in required_columns):
                    missing_cols = [col for col in required_columns if col not in df.columns]
                    raise ValueError(f"CSV must contain '{', '.join(required_columns)}' columns. Missing: {', '.join(missing_cols)}.")

                # Convert timestamp column to datetime objects, coercing errors to NaT
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df.dropna(subset=['timestamp'], inplace=True) # Remove rows where timestamp conversion failed
                
                if df.empty:
                    print(f"[WARN] No valid data found in '{filepath}' after processing. Using sample data instead.")
                else:
                    print(f"[INFO] Successfully loaded {len(df)} entries from '{filepath}'.")
                    return df.sort_values(by='timestamp').reset_index(drop=True)

            except pd.errors.EmptyDataError:
                print(f"[ERROR] '{filepath}' is empty. Using sample data instead.")
            except FileNotFoundError: # Should be covered by os.path.exists but good for robustness
                print(f"[ERROR] File '{filepath}' not found. Using sample data instead.")
            except Exception as e:
                print(f"[ERROR] Failed to load data from '{filepath}': {e}. Using sample data instead.")

    # Fallback to sample data if no file, file not found, or error during loading
    print(f"[INFO] No valid file provided or an error occurred. Using sample data for demonstration.")
    print(f"       To use your own data, run: python {os.path.basename(__file__)} --file your_data.csv")
    sample_data = [
        {'timestamp': '2023-01-01 10:00:00', 'content': 'Great video! So helpful.'},
        {'timestamp': '2023-01-02 11:00:00', 'content': 'I learned a lot from this.'},
        {'timestamp': '2023-01-03 12:00:00', 'content': 'What about X feature?'},
        {'timestamp': '2023-01-04 13:00:00', 'content': 'This part was confusing.'},
        {'timestamp': '2024-06-01 14:00:00', 'content': 'Is this still relevant in 2024? Great content, but outdated?'},
        {'timestamp': '2024-06-02 15:00:00', 'content': 'Totally agree! Need an update on X.'},
        {'timestamp': '2024-06-03 16:00:00', 'content': 'The explanation of Y was bad. Can you clarify?'},
        {'timestamp': '2024-06-04 17:00:00', 'content': 'This old video is amazing! Is there a new version?'} # Re-ignited interest
    ]
    df = pd.DataFrame(sample_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    print(f"[INFO] Loaded {len(df)} sample entries.")
    return df.sort_values(by='timestamp').reset_index(drop=True)

def detect_edge_signals(comments_df: pd.DataFrame, target_keywords_str: str = None) -> list:
    """
    Detects 'edge signals' in comments data by analyzing shifts in keywords,
    questions, and sentiment between older and more recent comments.

    Args:
        comments_df (pd.DataFrame): DataFrame containing 'timestamp' and 'content' columns.
        target_keywords_str (str): Comma-separated string of keywords to monitor for spikes.

    Returns:
        list: A list of strings, each describing a detected edge signal.
    """
    signals = []
    if comments_df.empty:
        print("[WARN] Comments DataFrame is empty, no signals to detect.")
        return signals

    total_comments = len(comments_df)
    # Split into old and recent data based on RECENT_COMMENTS_SPLIT_RATIO
    # e.g., if ratio is 0.75, the last 25% of comments are considered 'recent'.
    recent_idx_start = int(total_comments * RECENT_COMMENTS_SPLIT_RATIO)
    
    if recent_idx_start >= total_comments -1:
        print(f"[WARN] Not enough data to create distinct 'old' and 'recent' comment sets with ratio {RECENT_COMMENTS_SPLIT_RATIO}. Consider adjusting the ratio or adding more data. Processing all as 'recent'.")
        old_comments_list = []
        recent_comments_list = comments_df['content'].str.lower().tolist()
    else:
        old_comments_list = comments_df.iloc[:recent_idx_start]['content'].str.lower().tolist()
        recent_comments_list = comments_df.iloc[recent_idx_start:]['content'].str.lower().tolist()

    print(f"[INFO] Analyzing {total_comments} comments: {len(old_comments_list)} old, {len(recent_comments_list)} recent.")

    # Helper function for word counting (avoids repetition)
    def count_word_occurrences(comment_list, keywords):
        counts = {keyword: 0 for keyword in keywords}
        for comment in comment_list:
            for keyword in keywords:
                if keyword in comment:
                    counts[keyword] += 1
        return counts

    # --- 1. Keyword Spike Detection ---
    if target_keywords_str:
        target_keywords_lower = [k.strip().lower() for k in target_keywords_str.split(',') if k.strip()]
        if target_keywords_lower:
            print(f"[INFO] Detecting spikes for keywords: {', '.join(target_keywords_lower)}")
            old_keyword_counts = count_word_occurrences(old_comments_list, target_keywords_lower)
            recent_keyword_counts = count_word_occurrences(recent_comments_list, target_keywords_lower)

            for keyword in target_keywords_lower:
                old_count = old_keyword_counts.get(keyword, 0)
                recent_count = recent_keyword_counts.get(keyword, 0)
                # A simple rule: recent count is at least twice the old count and recent count is significant
                if recent_count > old_count * 2 and recent_count >= 2: # At least 2 occurrences for significance
                    signals.append(f"Keyword spike detected: '{keyword}' (Old: {old_count}, Recent: {recent_count}).")
        else:
            print("[INFO] No valid target keywords provided after parsing.")

    # --- 2. Question Pattern Detection (in recent comments) ---
    # This looks for comments that are likely questions or indicate new areas of interest/confusion.
    print("[INFO] Detecting new potential questions/interests in recent comments.")
    for comment in recent_comments_list:
        # Basic heuristic: contains '?' and is longer than a few words
        if '?' in comment and len(comment.split()) > 4:
            signals.append(f"Potential new question/interest: '{comment[:70]}{'...' if len(comment) > 70 else ''}'")

    # --- 3. Basic Sentiment Shift Detection ---
    # Monitors for a significant shift in common positive/negative terms.
    print("[INFO] Detecting sentiment shifts (positive/negative).")
    positive_words = ['great', 'amazing', 'love', 'helpful', 'awesome', 'excellent', 'fantastic']
    negative_words = ['bad', 'confusing', 'outdated', 'hate', 'problem', 'error', 'bug']
    
    old_pos_counts = count_word_occurrences(old_comments_list, positive_words)
    recent_pos_counts = count_word_occurrences(recent_comments_list, positive_words)
    old_neg_counts = count_word_occurrences(old_comments_list, negative_words)
    recent_neg_counts = count_word_occurrences(recent_comments_list, negative_words)

    total_old_pos = sum(old_pos_counts.values())
    total_recent_pos = sum(recent_pos_counts.values())
    total_old_neg = sum(old_neg_counts.values())
    total_recent_neg = sum(recent_neg_counts.values())

    # Thresholds for sentiment shift detection
    if total_recent_pos > total_old_pos * 2 and total_recent_pos >= 3: # Require at least 3 recent positive mentions
        signals.append(f"Significant increase in positive sentiment (Old: {total_old_pos}, Recent: {total_recent_pos}).")
    if total_recent_neg > total_old_neg * 2 and total_recent_neg >= 3: # Require at least 3 recent negative mentions
        signals.append(f"Significant increase in negative sentiment/issues (Old: {total_old_neg}, Recent: {total_recent_neg}).")

    print(f"[INFO] Detected {len(signals)} edge signals.")
    return signals

def save_signals_to_csv(signals: list, output_filename: str = "edge_signals.csv") -> None:
    """
    Saves detected signals to a CSV file. If the file already exists,
    new signals are appended, otherwise a new file is created.

    Args:
        signals (list): A list of strings, each representing a detected signal.
        output_filename (str): The name of the CSV file to save signals to.
    """
    if not signals:
        print("[INFO] No new edge signals to save.")
        return

    print(f"[INFO] Preparing to save {len(signals)} signals to '{output_filename}'...")
    signals_df = pd.DataFrame({
        'timestamp': [datetime.now()] * len(signals),
        'signal': signals
    })

    # Determine if header should be written (only if file doesn't exist)
    file_exists = os.path.exists(output_filename)
    mode = 'a' if file_exists else 'w'
    header = not file_exists
    
    try:
        signals_df.to_csv(output_filename, mode=mode, header=header, index=False, encoding='utf-8')
        print(f"[SUCCESS] Detected edge signals saved to '{output_filename}'.")
    except IOError as e:
        print(f"[ERROR] Failed to save signals to '{output_filename}' due to I/O error: {e}")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while saving signals to CSV: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Echo Edge Finder: Detects meaningful shifts in content engagement comments.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--file', 
        type=str, 
        help="Path to a CSV file containing 'timestamp' and 'content' columns. If not provided, sample data is used."
    )
    parser.add_argument(
        '--keywords', 
        type=str, 
        default=DEFAULT_KEYWORDS, 
        help=f"Comma-separated keywords to monitor for spikes. Default: '{DEFAULT_KEYWORDS}'."
    )
    args = parser.parse_args()

    print("\n--- Echo Edge Finder Initializing ---")
    print(f"[CONFIG] Data file: {args.file if args.file else 'Sample Data'}")
    print(f"[CONFIG] Monitored keywords: '{args.keywords}'")

    comments_data = load_comments_data(args.file)

    if not comments_data.empty:
        print("\n--- Starting Signal Detection ---")
        detected_signals = detect_edge_signals(comments_data, args.keywords)
        
        if detected_signals:
            print("\n--- Detected Edge Signals Summary ---")
            for i, signal in enumerate(detected_signals, 1):
                print(f"  {i}. {signal}")
            save_signals_to_csv(detected_signals)
        else:
            print("\n[INFO] No significant edge signals detected at this time. All clear!")
    else:
        print("\n[ERROR] No comments data available to process. Exiting.")

    print("\n--- Echo Edge Finder Finished ---")
    print("Hint: Schedule this script to run daily for continuous monitoring! (e.g., via cron job or Windows Task Scheduler)")
