import random
import datetime
import time

# --- Configuration ---
MOCK_COMMIT_CHANCE_PER_TICK = 0.6  # Chance to "detect brain activity" and commit in EEG Sync Mode
MAX_COMMIT_MESSAGES = [
    "Refactor: Optimize brainwave parsing logic for enhanced idleness detection",
    "Feat: Implement advanced napping analytics module",
    "Bug: Fix issue where ambition was accidentally detected (hotfix)",
    "Docs: Update README with new 'sleep-driven development' philosophy",
    "Chore: Automate grass growth; manual labor is for suckers",
    "Style: Adjust code indentation to match pillow creases",
    "WIP: Integrating dream patterns into commit frequency algorithm",
    "Perf: Reduce CPU usage by offloading computation to REM cycles",
    "Feat: Add 'existential dread' error handler for commit failures",
    "Refactor: Simplified thought process to 'no thought' for better commit efficiency"
]

MOCK_CODE_SNIPPETS = [
    "def calculate_laziness_index(brain_activity_data):\\n    return sum(data) / len(data) * 0.001 # Extremely lazy",
    "// This entire module is an elaborate excuse to nap.\\nfunction procrastinate_effectively() { return true; }",
    "/*\\n * TODO: Add actual code. For now, just a comment.\\n */\\nconst FAKE_DATA = { status: 'napping', uptime: '100% idle' };",
    "SELECT * FROM thoughts WHERE thought_content IS NULL; -- Maximizing 'no-thought' for productivity",
    "from sleeping_library import deep_sleep_mode\\ndeep_sleep_mode.activate(duration_hours=8)"
]

# --- Mocking Functions ---

def simulate_eeg_activity() -> bool:
    """
    Mocks EEG activity detection based on random chance.
    In a real scenario, this would read user activity data.
    """
    print("  [MOCK] Simulating EEG activity scan...")
    # Simulate some "quiet" periods, making commits less frequent but still present
    return random.random() < MOCK_COMMIT_CHANCE_PER_TICK

def generate_decoy_commit_content() -> dict:
    """
    Mocks LM Bionic AI to generate plausible but fake commit messages and code snippets.
    """
    print("  [MOCK] LM Bionic AI generating decoy content...")
    message = random.choice(MAX_COMMIT_MESSAGES)
    code_snippet = random.choice(MOCK_CODE_SNIPPETS)
    return {"message": message, "content": code_snippet}

def perform_mock_git_commit(message: str, content: str, commit_date: datetime.datetime = None):
    """
    Simulates a Git commit. In a real scenario, this would execute git commands.
    """
    date_str = commit_date.strftime('%Y-%m-%d %H:%M:%S') if commit_date else "now"
    print(f"--- FAKE COMMIT ({date_str}) ---")
    print(f"  COMMIT MESSAGE: {message}")
    print(f"  COMMIT CONTENT: \"\"\"{content}\"\"\"")
    print(f"  [MOCK] Executing: git add .")
    print(f"  [MOCK] Executing: git commit -m \"{message}\" {'--date=\"' + commit_date.isoformat() + '\"' if commit_date else ''}")
    print(f"  [MOCK] Executing: git push origin main")
    print("  [MOCK] GitHub grass successfully 'fertilized'!")
    print("----------------------------\\n")
    # In a real scenario, you'd handle git command execution and error checking here.
    # e.g., subprocess.run(["git", "commit", "-m", message], check=True)

# --- Core Modes ---

def eeg_sync_mode(duration_minutes: int = 5):
    """
    '뇌파 동기화' 모드: Simulates real-time commit generation based on 'EEG activity'.
    """
    print(f"[EEG Sync Mode] Activating for {duration_minutes} minutes... (Simulated)")
    end_time = time.time() + duration_minutes * 60
    commit_count = 0

    while time.time() < end_time:
        if simulate_eeg_activity():
            try:
                decoy_data = generate_decoy_commit_content()
                perform_mock_git_commit(decoy_data["message"], decoy_data["content"])
                commit_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to simulate commit: {e}")
        else:
            print("  [EEG Sync Mode] No significant 'brainwave activity' detected. Sleeping...")
        time.sleep(random.randint(10, 30)) # Simulate irregular checks

    print(f"[EEG Sync Mode] Session ended. Total {commit_count} fake commits generated.")

def time_warp_grass_recovery(days_ago: int = 7):
    """
    '타임 워프' 잔디 복구: Generates commits for a specified period in the past.
    """
    print(f"[Time Warp Mode] Initiating grass recovery for the last {days_ago} days...")
    today = datetime.date.today()
    commit_count = 0

    for i in range(days_ago, 0, -1):
        past_date = today - datetime.timedelta(days=i)
        # For simplicity, generate 1-3 commits per past day
        num_commits_for_day = random.randint(1, 3)
        print(f"  [Time Warp Mode] Filling {past_date.strftime('%Y-%m-%d')} with {num_commits_for_day} commits.")
        for j in range(num_commits_for_day):
            commit_time = datetime.datetime.combine(past_date, datetime.time(random.randint(9, 23), random.randint(0, 59)))
            try:
                decoy_data = generate_decoy_commit_content()
                perform_mock_git_commit(decoy_data["message"], decoy_data["content"], commit_time)
                commit_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to simulate time-warp commit for {past_date}: {e}")
            time.sleep(0.5) # Small delay for simulation realism

    print(f"[Time Warp Mode] Grass recovery completed. Total {commit_count} past commits generated.")

# --- Main Execution ---

if __name__ == "__main__":
    print("EEG-Comm-AI-t: '뇌파 잔디 자동 동기화봇' v1.0 activated!")
    print("--------------------------------------------------\\n")

    # Example usage:
    # 1. Simulate real-time brainwave-driven commits for a short period
    eeg_sync_mode(duration_minutes=1) # Run for 1 simulated minute

    # 2. Simulate time warp to fill grass for the last 3 days
    print("\\n--- Switching to Time Warp Mode ---\\n")
    time_warp_grass_recovery(days_ago=3)

    print("\\nEEG-Comm-AI-t has finished its operations. Go back to sleep!")
