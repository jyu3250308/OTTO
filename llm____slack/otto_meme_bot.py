import time
import random
import json

# --- Configuration (Mocked for testing) ---
SLACK_BOT_TOKEN = "xoxb-YOUR-SLACK-BOT-TOKEN"  # Placeholder for mocking
SLACK_CHANNEL = "#general-memes"               # Target Slack channel
REDDIT_BASE_URL = "https://www.reddit.com"     # Mocked Reddit API endpoint

# --- Mocking External APIs ---

class MockRequests:
    """Mocks the 'requests' library for Reddit API calls."""
    def get(self, url, headers=None, params=None):
        print(f"[MOCK] Simulating GET request to {url} with params: {params}")
        if "reddit" in url:
            # Simulate Reddit Hot/Trending posts
            mock_reddit_data = {
                "data": {
                    "children": [
                        {
                            "data": {
                                "title": "Me trying to understand recursive functions",
                                "selftext": "It's like looking at a mirror in a mirror, indefinitely.",
                                "url": "https://i.redd.it/recursive_meme.png",
                                "score": 1234,
                                "permalink": "/r/ProgrammerHumor/comments/xyz/recursive_functions/"
                            }
                        },
                        {
                            "data": {
                                "title": "When your code works on the first try (impossible)",
                                "selftext": "A rare sight, indeed. Might need to check for cosmic rays.",
                                "url": "https://i.redd.it/first_try_code.gif",
                                "score": 987,
                                "permalink": "/r/funny/comments/abc/code_works_first_try/"
                            }
                        },
                        {
                            "data": {
                                "title": "My cat's reaction when I try to work from home",
                                "selftext": "Demands attention, always.",
                                "url": "https://i.redd.it/cat_wfh.jpg",
                                "score": 567,
                                "permalink": "/r/aww/comments/def/cat_wfh/"
                            }
                        }
                    ]
                }
            }
            class MockResponse:
                def json(self):
                    return mock_reddit_data
                @property
                def status_code(self):
                    return 200
                @property
                def ok(self):
                    return True
            return MockResponse()
        else:
            print("[MOCK ERROR] Unexpected URL for MockRequests.")
            raise ValueError("Unknown mock URL")

class MockWebClient:
    """Mocks the Slack WebClient."""
    def __init__(self, token):
        self.token = token
        print(f"[MOCK] Slack WebClient initialized with token: {token[:5]}...")

    def chat_postMessage(self, channel, text):
        print(f"--- [MOCK SLACK] Message to {channel} ---")
        print(f"Content: {text}")
        print("------------------------------------------")
        return {"ok": True, "message": {"text": text}}

# Replace actual libraries with mocks for testing
# In a real scenario, you'd import requests and slack_sdk.WebClient
# For this exercise, we directly use our mock objects.
requests = MockRequests()
slack_client = MockWebClient(SLACK_BOT_TOKEN)

# --- Bot Core Logic ---

def fetch_reddit_posts(subreddit="all", limit=5):
    """
    Mocks fetching hot/trending posts from Reddit.
    Returns a list of dictionaries, each representing a post.
    """
    print(f"[INFO] Fetching {limit} posts from r/{subreddit}...")
    try:
        # Using mocked requests object
        response = requests.get(f"{REDDIT_BASE_URL}/r/{subreddit}/hot.json", params={"limit": limit})
        if response.ok:
            data = response.json()
            posts = []
            for item in data.get("data", {}).get("children", []):
                post_data = item.get("data", {})
                if post_data and (post_data.get("selftext") or post_data.get("url")):
                    posts.append({
                        "title": post_data.get("title", "No title"),
                        "content": post_data.get("selftext", post_data.get("url", "No content")),
                        "url": f"{REDDIT_BASE_URL}{post_data.get('permalink', '')}",
                        "score": post_data.get("score", 0)
                    })
            print(f"[INFO] Successfully fetched {len(posts)} mocked Reddit posts.")
            return posts
        else:
            print(f"[ERROR] Failed to fetch Reddit posts: Status {response.status_code}")
            return []
    except Exception as e:
        print(f"[ERROR] An error occurred while fetching Reddit posts: {e}")
        return []

def analyze_and_summarize_with_llm(post_title, post_content):
    """
    Mocks LLM analysis to create a humorous summary.
    """
    print(f"[INFO] Analyzing post with LLM: '{post_title[:50]}...'"
)
    # Simulate LLM processing delay
    time.sleep(0.5)

    mock_llm_responses = [
        f"🚨 Meme Alert! '{post_title}' - AI says: This is basically a digital equivalent of a cat video, but for your brain. Expect maximum chuckle output!",
        f"🔮 Otto's Oracle says: '{post_title}' is a certified laughter-inducer. My circuits are tingling! Summary: {post_content[:70]}...",
        f"✨ Cosmic Joke Detected: '{post_title}'! Prepare for quantum giggles. The universe confirms its humor: {post_content[:80]}",
        f"😂 Your daily dose of digital absurdity: '{post_title}'. My humor detection algorithms rated this 9/10 on the 'spit-take' scale!",
        f"🚀 Blast off to Laughter Land! '{post_title}' is trending in the meme-iverse. AI's take: {post_content[:90]}... Now go forth and conquer your day!"
    ]
    return random.choice(mock_llm_responses)

def post_to_slack(channel, message):
    """
    Mocks posting a message to Slack.
    """
    print(f"[INFO] Attempting to post to Slack channel '{channel}'...")
    try:
        # Using mocked slack_client object
        response = slack_client.chat_postMessage(channel=channel, text=message)
        if response.get("ok"):
            print("[INFO] Message successfully mocked to Slack.")
            return True
        else:
            print(f"[ERROR] Failed to post to Slack: {response.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"[ERROR] An error occurred while posting to Slack: {e}")
        return False

def run_bot(interval_seconds=600):
    """
    Main bot loop. Fetches posts periodically and can also be triggered on demand.
    """
    print("[INFO] Otto's Meme Cosmogony Bot started!")
    print("--- (Mocking external API calls for Reddit, LLM, and Slack) ---")

    # Simulate an "on-demand" request for testing purposes
    # In a real bot, this would come from a Slack event listener
    mock_on_demand_trigger = False # Set to True to simulate an immediate trigger

    while True:
        try:
            if mock_on_demand_trigger:
                print("\n[INFO] Simulating an on-demand request!")
                mock_on_demand_trigger = False # Reset for next cycle
                on_demand_posts = fetch_reddit_posts(limit=1) # Fetch just one for demand
                if on_demand_posts:
                    post = on_demand_posts[0]
                    summary = analyze_and_summarize_with_llm(post["title"], post["content"])
                    full_message = f"🌟 ON-DEMAND JOKE! 🌟\n{summary}\nRead more: {post['url']}"
                    post_to_slack(SLACK_CHANNEL, full_message)
                else:
                    post_to_slack(SLACK_CHANNEL, "Otto couldn't find any fresh jokes on demand today. Try again later!")
            else:
                print(f"\n[INFO] Running scheduled fetch. Next check in {interval_seconds} seconds.")
                posts = fetch_reddit_posts(limit=3) # Fetch more for scheduled run

                if posts:
                    for post in posts:
                        summary = analyze_and_summarize_with_llm(post["title"], post["content"])
                        full_message = f"🌌 Otto's Daily Cosmic Chuckle! 🌌\n{summary}\nReddit Score: {post['score']}\nRead more: {post['url']}"
                        post_to_slack(SLACK_CHANNEL, full_message)
                        time.sleep(2) # Simulate delay between posts
                else:
                    post_to_slack(SLACK_CHANNEL, "Otto ventured into the Reddit depths but found no new cosmic humor today. The universe is quiet.")

            print(f"\n[INFO] Scheduled run complete. Waiting for {interval_seconds} seconds...")
            # For quick testing, reduce the actual sleep time
            time.sleep(min(interval_seconds, 10)) # sleep for max 10s for test purposes
            
            # Simulate turning on on-demand trigger occasionally for testing
            if random.random() < 0.3: # 30% chance to simulate on-demand next cycle
                mock_on_demand_trigger = True

        except KeyboardInterrupt:
            print("\n[INFO] Bot stopped by user.")
            break
        except Exception as e:
            print(f"[CRITICAL ERROR] Bot encountered a critical issue: {e}")
            post_to_slack(SLACK_CHANNEL, f"🤖 Otto encountered an internal error: {e}. Please check logs!")
            time.sleep(60) # Wait before retrying after an error

if __name__ == "__main__":
    run_bot(interval_seconds=30) # Reduced interval for testing purposes