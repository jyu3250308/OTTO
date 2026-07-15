#!/usr/bin/env python3

import os
import subprocess
import datetime
import time
import random
import sys
from dotenv import load_dotenv

# --- Configuration & Setup ---

def load_environment_variables():
    """
    Loads environment variables from a .env file and validates their presence.
    """
    print("INFO: Loading environment variables from .env file...")
    load_dotenv()

    global GITHUB_TOKEN, GITHUB_USERNAME, GITHUB_EMAIL, DUMMY_REPO_URL, LOCAL_REPO_PATH

    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
    GITHUB_EMAIL = os.getenv("GITHUB_EMAIL")
    DUMMY_REPO_URL = os.getenv("DUMMY_REPO_URL")
    LOCAL_REPO_PATH = "grass_grok_repo" # Local directory to clone the dummy repo

    required_vars = {
        "GITHUB_TOKEN": GITHUB_TOKEN,
        "GITHUB_USERNAME": GITHUB_USERNAME,
        "GITHUB_EMAIL": GITHUB_EMAIL,
        "DUMMY_REPO_URL": DUMMY_REPO_URL,
    }

    missing_vars = [name for name, value in required_vars.items() if not value]

    if missing_vars:
        print(f"ERROR: The following essential environment variables are missing or empty: {', '.join(missing_vars)}")
        print("ERROR: Please ensure they are correctly set in your .env file.")
        sys.exit(1)
    print("INFO: All required environment variables loaded successfully.")

# Global variables (initialized by load_environment_variables)
GITHUB_TOKEN = None
GITHUB_USERNAME = None
GITHUB_EMAIL = None
DUMMY_REPO_URL = None
LOCAL_REPO_PATH = "grass_grok_repo"

# --- Helper Functions ---

def run_git_command(args, cwd=None, check=True, capture_output=False, env=None):
    """
    Executes a git command and handles potential errors.

    Args:
        args (list): A list of strings representing the git command and its arguments.
        cwd (str, optional): The current working directory for the command. Defaults to None.
        check (bool, optional): If True, raise a CalledProcessError on non-zero exit codes.
                                Defaults to True.
        capture_output (bool, optional): If True, capture stdout and stderr. Defaults to False.
        env (dict, optional): A dictionary of environment variables for the subprocess.
                              Defaults to None (inherits parent's environment).

    Returns:
        str or True: The captured stdout if capture_output is True, otherwise True for success.

    Raises:
        subprocess.CalledProcessError: If the git command returns a non-zero exit code and check is True.
        FileNotFoundError: If the 'git' command is not found.
        Exception: For any other unexpected errors.
    """
    cmd = ["git"] + args
    cmd_str = ' '.join(cmd)
    print(f"DEBUG: Executing Git command: {cmd_str}")

    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=capture_output,
            text=True,
            encoding='utf-8', # Ensure consistent encoding for output
            env=env
        )
        if capture_output:
            # DEBUG: print(f"DEBUG: Git command stdout: {result.stdout.strip()}")
            return result.stdout.strip()
        print(f"DEBUG: Git command '{cmd_str}' executed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Git command failed with exit code {e.returncode}: {cmd_str}")
        if e.stdout: print(f"ERROR: Stdout: {e.stdout.strip()}")
        if e.stderr: print(f"ERROR: Stderr: {e.stderr.strip()}")
        raise # Re-raise the exception after logging
    except FileNotFoundError:
        print("FATAL ERROR: 'git' command not found. Please ensure Git is installed and in your system's PATH.")
        sys.exit(1) # Critical error, exit immediately
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while running git command '{cmd_str}': {e}")
        raise

def setup_git_config():
    """
    Sets up global Git user name and email if not already set, using the provided environment variables.
    """
    print("INFO: Initiating Git user configuration setup...")
    try:
        # Check and set user.name
        current_user_name = run_git_command(["config", "user.name"], capture_output=True, check=False)
        if not current_user_name:
            run_git_command(["config", "--global", "user.name", GITHUB_USERNAME])
            print(f"INFO: Git global user.name set to '{GITHUB_USERNAME}'.")
        elif current_user_name != GITHUB_USERNAME:
            print(f"WARNING: Git global user.name is currently '{current_user_name}', but .env specifies '{GITHUB_USERNAME}'. Using .env value for commits.")
            # For commits, we will explicitly set author, so this is just a warning
        else:
            print(f"INFO: Git global user.name is already set to '{current_user_name}'.")

        # Check and set user.email
        current_user_email = run_git_command(["config", "user.email"], capture_output=True, check=False)
        if not current_user_email:
            run_git_command(["config", "--global", "user.email", GITHUB_EMAIL])
            print(f"INFO: Git global user.email set to '{GITHUB_EMAIL}'.")
        elif current_user_email != GITHUB_EMAIL:
            print(f"WARNING: Git global user.email is currently '{current_user_email}', but .env specifies '{GITHUB_EMAIL}'. Using .env value for commits.")
            # For commits, we will explicitly set author, so this is just a warning
        else:
            print(f"INFO: Git global user.email is already set to '{current_user_email}'.")

        print("INFO: Git user configuration setup complete.")
    except Exception as e:
        print(f"ERROR: Failed to set up Git configuration: {e}")
        raise

def clone_or_pull_repo(repo_url, local_path):
    """
    Clones the repository if it doesn't exist locally, otherwise pulls the latest changes.
    """
    if os.path.exists(local_path):
        print(f"INFO: Local repository directory '{local_path}' already exists. Attempting to pull latest changes...")
        try:
            # Ensure the correct remote URL is set for pull/push, including token
            repo_url_with_token = repo_url.replace("https://", f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@")
            run_git_command(["remote", "set-url", "origin", repo_url_with_token], cwd=local_path)
            print("INFO: Remote URL updated with token for secure access.")
            
            run_git_command(["pull", "origin", "main"], cwd=local_path)
            print(f"INFO: Successfully pulled latest changes from 'main' branch for '{local_path}'.")
        except Exception as e:
            print(f"WARNING: Failed to pull latest changes for '{local_path}'. This might lead to push conflicts later if other changes exist. Error: {e}")
            print("WARNING: Ottos_GrassGroK will attempt to force push its commits, potentially overwriting remote history.")
            # In case of pull failure, the push_commits function will attempt a force push later.
    else:
        print(f"INFO: Local repository directory '{local_path}' does not exist. Cloning from '{repo_url}'...")
        try:
            # Inject token into URL for cloning
            repo_url_with_token = repo_url.replace("https://", f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@")
            run_git_command(["clone", repo_url_with_token, local_path])
            print(f"SUCCESS: Successfully cloned '{repo_url}' into '{local_path}'.")
        except Exception as e:
            print(f"FATAL ERROR: Failed to clone repository '{repo_url}' into '{local_path}'. Please check DUMMY_REPO_URL and GITHUB_TOKEN permissions. Error: {e}")
            sys.exit(1)

def get_commits_for_date(date_obj, local_path):
    """
    Checks if there's at least one commit on a specific date in the local repository
    by the configured GITHUB_EMAIL. Returns the count of commits for that day.

    Args:
        date_obj (datetime.date): The date to check for commits.
        local_path (str): The path to the local Git repository.

    Returns:
        int: The number of commits found for the specified date.
    """
    date_str = date_obj.strftime("%Y-%m-%d")
    start_of_day = f"{date_str} 00:00:00"
    end_of_day = f"{date_str} 23:59:59"

    try:
        # Use --author for precise filtering by email as specified in .env
        commit_log = run_git_command(
            ["log", "--oneline", f"--after={start_of_day}", f"--before={end_of_day}", "--author", GITHUB_EMAIL],
            cwd=local_path,
            capture_output=True,
            check=False # Don't check for errors, as no commits is a valid outcome
        )
        num_commits = len(commit_log.splitlines()) if commit_log else 0
        return num_commits
    except Exception as e:
        print(f"WARNING: Could not retrieve commit history for {date_str} for user {GITHUB_EMAIL}. Error: {e}")
        return 0 # Assume no commits if retrieval fails

def generate_stealth_commit(date_obj, local_path, commit_message=None):
    """
    Creates a 'stealth' commit on a specified date with a randomized timestamp.

    Args:
        date_obj (datetime.date): The target date for the commit.
        local_path (str): The path to the local Git repository.
        commit_message (str, optional): A specific commit message. If None, a random message is generated.

    Returns:
        bool: True if the commit was created successfully, False otherwise.
    """
    print(f"INFO: Attempting to generate stealth commit for {date_obj.strftime('%Y-%m-%d')}...")

    # Randomize commit time within business hours for a natural look
    commit_time = date_obj.replace(
        hour=random.randint(9, 17), # 9 AM to 5 PM
        minute=random.randint(0, 59),
        second=random.randint(0, 59)
    )
    git_date_format = commit_time.strftime("%Y-%m-%d %H:%M:%S")

    dummy_file_path = os.path.join(local_path, "_groked_grass.txt")
    
    # Predefined random commit messages
    commit_messages = [
        f"GrassGrok: Maintaining digital garden on {date_obj.strftime('%Y-%m-%d')}",
        f"GrassGrok: Quick check-in for greenifying contributions on {date_obj.strftime('%Y-%m-%d')}",
        f"GrassGrok: Automated commit to keep the grass healthy on {date_obj.strftime('%Y-%m-%d')}",
        f"GrassGrok: Minor update for commit consistency on {date_obj.strftime('%Y-%m-%d')}",
        f"GrassGrok: Ensuring the commit streak continues on {date_obj.strftime('%Y-%m-%d')}",
        f"GrassGrok: Secretly nurturing contribution graph on {date_obj.strftime('%Y-%m-%d')}",
        f"GrassGrok: A tiny seed planted today on {date_obj.strftime('%Y-%m-%d')}"
    ]
    message = commit_message if commit_message else random.choice(commit_messages)

    try:
        # Ensure the file exists, append content to ensure change detection
        print(f"DEBUG: Appending content to dummy file '{dummy_file_path}'...")
        with open(dummy_file_path, "a", encoding='utf-8') as f:
            f.write(f"# Groked by Ottos_GrassGroK on {commit_time.isoformat()}\n")
            f.write(f"# {message}\n")
            f.write(f"Commit ID: {random.getrandbits(32):08x}\n")
            f.write("-" * 20 + "\n")
        print(f"INFO: File '{dummy_file_path}' updated successfully.")

        print("DEBUG: Staging changes with 'git add'...")
        run_git_command(["add", dummy_file_path], cwd=local_path)
        print("INFO: Changes successfully staged.")
        
        print(f"DEBUG: Committing changes for {date_obj.strftime('%Y-%m-%d')}...")
        run_git_command([
            "commit",
            f"--date={git_date_format}",
            f"--author={GITHUB_USERNAME} <{GITHUB_EMAIL}>",
            "-m", message
        ], cwd=local_path)
        
        print(f"SUCCESS: Stealth commit successfully created for {date_obj.strftime('%Y-%m-%d')} with message: '{message}'")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create commit for {date_obj.strftime('%Y-%m-%d')}. Error: {e}")
        # Attempt to reset local changes to avoid a dirty working directory from failed commit
        try:
            print("DEBUG: Attempting to reset any staged changes due to commit failure...")
            run_git_command(["reset", "HEAD"], cwd=local_path, check=False)
            run_git_command(["checkout", "--", dummy_file_path], cwd=local_path, check=False)
            print("DEBUG: Local changes reset.")
        except Exception as reset_e:
            print(f"WARNING: Failed to reset local changes after commit error: {reset_e}")
        return False

def push_commits(local_path):
    """
    Pushes all local commits to the remote repository using the provided token.
    This function attempts a standard push first. If it fails, it will attempt a force push.
    """
    print("INFO: Initiating push of generated commits to remote repository...")
    try:
        # Ensure the correct remote URL is set with the token for push operation
        remote_url = DUMMY_REPO_URL.replace("https://", f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@")
        run_git_command(["remote", "set-url", "origin", remote_url], cwd=local_path)
        print("INFO: Remote URL updated with token for secure push access.")

        print(f"DEBUG: Attempting standard push to 'origin/main' from '{local_path}'...")
        run_git_command(["push", "origin", "main"], cwd=local_path)
        print("SUCCESS: All generated commits successfully pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"WARNING: Standard push failed (exit code {e.returncode}). This might happen if remote has diverging history (e.g., failed pull earlier).")
        print(f"WARNING: Error details: {e.stderr.strip()}")
        print("INFO: Attempting a force push to ensure consistency of contributions graph...")
        try:
            run_git_command(["push", "--force", "origin", "main"], cwd=local_path)
            print("SUCCESS: Force push completed. Contribution graph should now be updated.")
        except Exception as force_e:
            print(f"FATAL ERROR: Force push also failed. Please manually resolve repository state or check token permissions. Error: {force_e}")
            sys.exit(1)
    except Exception as e:
        print(f"FATAL ERROR: An unexpected error occurred during push operation: {e}")
        print("FATAL ERROR: Please verify your GITHUB_TOKEN, GITHUB_USERNAME, and DUMMY_REPO_URL.")
        sys.exit(1)

def analyze_and_fill_grass(days_to_check=90):
    """
    Analyzes the last 'days_to_check' days for missing commits and fills them if none are found.
    """
    print(f"\n--- [단계 2/3] AI 잔디 패턴 분석 & 자동 채우기: 지난 {days_to_check}일간 잔디 분석 시작 ---")
    today = datetime.date.today()
    filled_count = 0
    days_processed = 0

    for i in range(1, days_to_check + 1): # Start from yesterday, up to days_to_check ago
        target_date = today - datetime.timedelta(days=i)
        date_str = target_date.strftime("%Y-%m-%d")
        days_processed += 1

        print(f"PROGRESS: ({days_processed}/{days_to_check}) Checking commits for {date_str}...")
        try:
            num_commits = get_commits_for_date(target_date, LOCAL_REPO_PATH)
            if num_commits == 0:
                print(f"ACTION: No commits found for {date_str}. Generating a stealth commit now.")
                if generate_stealth_commit(target_date, LOCAL_REPO_PATH):
                    filled_count += 1
                    print(f"INFO: Successfully generated commit for {date_str}.")
                else:
                    print(f"WARNING: Failed to generate commit for {date_str}. Moving to next day.")
            else:
                print(f"INFO: {num_commits} commit(s) found for {date_str}. No action needed.")
        except Exception as e:
            print(f"ERROR: Problem analyzing or filling grass for {date_str}: {e}. Skipping this day.")
            continue
        time.sleep(random.uniform(0.1, 0.5)) # Small delay to make logs more readable and less aggressive

    if filled_count > 0:
        print(f"\nINFO: Successfully generated {filled_count} stealth commit(s) for missing days.")
        push_commits(LOCAL_REPO_PATH)
    else:
        print("\nINFO: All checked days already have commits or no new commits were successfully generated.")
    
    print("--- 잔디 분석 및 채우기 완료 ---")

def visualize_grass(days_to_display=365):
    """
    Fetches commit data for the past 'days_to_display' and visualizes it as a Voxel art
    in the console, simulating GitHub's contribution graph.
    """
    print(f"\n--- [단계 3/3] Voxel 잔디 현황판: 현재 GitHub 잔디 상황 시각화 (최근 {days_to_display}일) ---")
    
    today = datetime.date.today()
    
    # Calculate the earliest date for the visualization window
    earliest_date_window = today - datetime.timedelta(days=days_to_display - 1) # This is the actual oldest day in our window.
    
    # Find the Monday of the week containing earliest_date_window. GitHub graph starts its grid from Monday.
    # weekday() returns 0 for Monday, 6 for Sunday.
    start_of_viz_week = earliest_date_window - datetime.timedelta(days=earliest_date_window.weekday())

    print(f"INFO: Fetching commit history since {start_of_viz_week.strftime('%Y-%m-%d')} for {GITHUB_EMAIL}...")
    try:
        all_commit_dates_str = run_git_command(
            ["log", "--pretty=format:%ad", "--date=short", f"--since={start_of_viz_week.strftime('%Y-%m-%d')}", "--author", GITHUB_EMAIL],
            cwd=LOCAL_REPO_PATH,
            capture_output=True,
            check=False
        )
        
        commit_counts = {} # {datetime.date: count}
        for line in all_commit_dates_str.splitlines():
            try:
                commit_date = datetime.datetime.strptime(line, "%Y-%m-%d").date()
                commit_counts[commit_date] = commit_counts.get(commit_date, 0) + 1
            except ValueError:
                print(f"WARNING: Could not parse commit date from Git log line: '{line}'. Skipping.")
                continue

        # Voxel character mapping based on commit count
        # Level 0: ' ' (0 commits)
        # Level 1: '.' (1-2 commits)
        # Level 2: '+' (3-5 commits)
        # Level 3: '#' (6+ commits)
        VOXEL_CHARS = [' ', '.', '+', '#'] 

        def get_voxel_char(count):
            if count == 0: return VOXEL_CHARS[0]
            if count <= 2: return VOXEL_CHARS[1]
            if count <= 5: return VOXEL_CHARS[2]
            return VOXEL_CHARS[3]

        # --- Prepare the grid for visualization ---
        # GitHub's graph typically shows about 53 weeks. Let's make it dynamic.
        # The number of columns needed for the visualization
        num_cols = (today - start_of_viz_week).days // 7 + 1
        if (today - start_of_viz_week).days % 7 != 0: # If the last week isn't full, still need a column
            num_cols += 1
        
        # Ensure we don't exceed a reasonable max number of columns for display
        max_display_cols = 55 # Approx. 1 year + a bit
        num_cols = min(num_cols, max_display_cols)

        grid_data = [[' ' for _ in range(num_cols)] for _ in range(7)] # 7 days of the week
        
        current_date = start_of_viz_week
        col_idx = 0
        
        while current_date <= today and col_idx < num_cols:
            day_of_week_idx = current_date.weekday() # Monday=0, Sunday=6
            
            # GitHub contribution graph usually displays Sunday as the first row (index 0)
            # So, map Mon(0) to row 1, Tue(1) to row 2, ..., Sat(5) to row 6, Sun(6) to row 0.
            row_idx = (day_of_week_idx + 1) % 7
            
            # Only populate the grid for dates within our desired display window
            if current_date >= earliest_date_window:
                count = commit_counts.get(current_date, 0)
                grid_data[row_idx][col_idx] = get_voxel_char(count)
            
            current_date += datetime.timedelta(days=1)
            # Move to next column (next week) if it's Monday
            if current_date.weekday() == 0:
                col_idx += 1

        # Print the grid with month headers and day labels
        print("\n")
        # Month header - approximate positioning
        month_line = "      "
        current_month = start_of_viz_week.month
        for c in range(num_cols):
            date_at_col_start = start_of_viz_week + datetime.timedelta(weeks=c)
            if date_at_col_start.month != current_month:
                month_line += datetime.date(1, date_at_col_start.month, 1).strftime("%b") + "  "
                current_month = date_at_col_start.month
            else:
                month_line += "   "
        print(month_line[:num_cols*3 + 6]) # Trim to fit

        day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, row in enumerate(grid_data):
            print(f"{day_labels[i]:<5} {''.join(row[:num_cols])}") # Ensure row is also trimmed if num_cols was adjusted
        
        print("\nINFO: Voxel 잔디 현황판 출력 완료.")
        
    except Exception as e:
        print(f"ERROR: Failed to visualize grass. Please ensure your Git history is accessible and GITHUB_EMAIL is correct. Error: {e}")

# --- Main execution ---
def main():
    print("\n--- [단계 1/3] 오또의 잔디GroK: AI 스텔스 잔디 파수꾼 시작 ---")

    # 1. Load and validate environment variables
    load_environment_variables()

    try:
        # 2. Setup Git user configuration
        setup_git_config()

        # 3. Clone or pull the dummy repository
        clone_or_pull_repo(DUMMY_REPO_URL, LOCAL_REPO_PATH)

        # 4. Analyze and fill missing commits for the last 90 days
        analyze_and_fill_grass(days_to_check=90) 

        # 5. Visualize the contribution graph for the last 365 days
        visualize_grass(days_to_display=365) 

        print("\n--- [작업 완료] 오또의 잔디GroK 작업 완료! 당신은 이제 성실 개발자! ---\n")
    except Exception as e:
        print(f"\nFATAL ERROR: Ottos_GrassGroK encountered a critical error: {e}")
        print("FATAL ERROR: Please review the log messages above, ensure your environment variables are correctly set, and your Git setup is valid.")
        sys.exit(1)

if __name__ == "__main__":
    main()
