import json
import time
import random
import os
from datetime import datetime
from typing import List, Dict, Any # Added for more precise type hinting

# --- Configuration ---
class Config:
    """
    Centralized configuration for the ReddAI Radar bot.
    It's recommended to load sensitive data from environment variables in production.
    """
    # Slack Webhook URL for sending notifications.
    # In a real scenario, this MUST be retrieved from environment variables
    # for security and flexibility (e.g., os.getenv("SLACK_WEBHOOK_URL")).
    # For this mock, we'll keep it as a placeholder or load a default.
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "YOUR_SLACK_WEBHOOK_URL_HERE")

    # List of Reddit subreddits to monitor for popular memes.
    REDDIT_SUBREDDITS: List[str] = ["memes", "dankmemes", "funny", "wholesomememes", "ProgrammerHumor"]

    # Keywords to filter content in post titles or text content.
    # Posts containing any of these keywords will be considered relevant.
    KEYWORDS_TO_FILTER: List[str] = ["meme", "funny", "joke", "lol", "reaction", "relatable", "code", "programming", "developer", "bug", "epic fail"]

    # Flairs to prioritize or filter by.
    # Posts with these flairs will be given higher consideration.
    FLAIRS_TO_FILTER: List[str] = ["Humor", "Meme", "Funny", "Image", "Video", "Programming Humor", "Tech", "Animals", "Cooking Fails"]

    # Interval in seconds between consecutive scans for new memes.
    # Set to 3600 for 1 hour in production, lower for testing (e.g., 60 seconds).
    SCAN_INTERVAL_SECONDS: int = int(os.getenv("SCAN_INTERVAL_SECONDS", "60"))

    # Maximum number of posts to summarize and send to Slack per scan run.
    MAX_POSTS_PER_RUN: int = int(os.getenv("MAX_POSTS_PER_RUN", "3"))

    # Time format for logging messages.
    LOG_TIMESTAMP_FORMAT: str = '%Y-%m-%d %H:%M:%S'

# --- Utility Functions ---
def get_current_timestamp() -> str:
    """Returns the current formatted timestamp for logging."""
    return datetime.now().strftime(Config.LOG_TIMESTAMP_FORMAT)

# --- Mocking Functions ---

def get_mock_reddit_posts(subreddits: List[str], keywords: List[str], flairs: List[str]) -> List[Dict[str, Any]]:
    """
    Mocks fetching popular meme posts from specified subreddits.
    In a real scenario, this would use a library like PRAW (Python Reddit API Wrapper)
    or custom web scraping.

    Args:
        subreddits: A list of subreddit names to search within.
        keywords: A list of keywords to match in post titles or text content.
        flairs: A list of flairs to match posts by.

    Returns:
        A list of dictionaries, where each dictionary represents a filtered mock Reddit post.
        The number of returned posts is limited by Config.MAX_POSTS_PER_RUN.
    """
    print(f"[{get_current_timestamp()}] INFO: Mocking Reddit API call to fetch posts from {subreddits}...")
    
    # Comprehensive mock data to simulate various post types and scenarios.
    mock_posts_data = [
        {
            "id": "post1_boomer_boss",
            "subreddit": "memes",
            "title": "When you try to explain a meme to your boomer boss",
            "url": "https://i.imgur.com/example1.jpg", # Mock image URL
            "permalink": "https://reddit.com/r/memes/comments/post1_boomer_boss",
            "text_content": "Boss: What's a 'dank meme'? Me: It's like, you know, a really good inside joke that only people online get. Boss: So, like an office joke from the 90s? This situation is truly relatable and always funny.",
            "flair": "Humor",
            "comments": [
                "This is too real! Happens every single time.",
                "My boss asked if 'yeet' was a new type of yogurt, I swear.",
                "Classic boomer moment, absolutely hilarious.",
                "Totally relatable, I just nod and smile now."
            ]
        },
        {
            "id": "post2_code_compiles",
            "subreddit": "dankmemes",
            "title": "My face when my code finally compiles after 3 hours (reaction meme)",
            "url": "https://i.imgur.com/example2.png", # Mock image URL
            "permalink": "https://reddit.com/r/dankmemes/comments/post2_code_compiles",
            "text_content": "Just spent half my day debugging a semicolon. The relief is immense. Feels like winning the lottery, or finding a hidden treasure. Programming humor at its finest.",
            "flair": "Programming Humor",
            "comments": [
                "Happens every time, the struggle is real.",
                "The best feeling ever, pure euphoria!",
                "Compile-time errors are the worst, but the victory is sweet.",
                "This needs more upvotes! Every developer knows this pain and joy."
            ]
        },
        {
            "id": "post3_burnt_toast",
            "subreddit": "funny",
            "title": "Tried to cook a fancy meal, ended up with burnt toast (epic fail)",
            "url": "https://i.imgur.com/example3.gif", # Mock image URL
            "permalink": "https://reddit.com/r/funny/comments/post3_burnt_toast",
            "text_content": "Followed a recipe precisely. Or so I thought. Kitchen is now a smoke-filled disaster zone. Send help (and pizza). Culinary adventure gone wrong.",
            "flair": "Cooking Fails",
            "comments": [
                "Been there, done that. My kitchen still smells.",
                "Just order takeout next time, save yourself the trouble!",
                "At least you tried! That's what matters... mostly.",
                "F for effort, and for your toast."
            ]
        },
        {
            "id": "post4_doggo_pets",
            "subreddit": "wholesomememes",
            "title": "Doggo patiently waiting for pets (very cute)",
            "url": "https://i.imgur.com/example4.jpg", # Mock image URL
            "permalink": "https://reddit.com/r/wholesomememes/comments/post4_doggo_pets",
            "text_content": "My dog just sat there looking at me with those big puppy eyes until I gave him belly rubs. Couldn't resist! Pure innocent love.",
            "flair": "Animals",
            "comments": [
                "So adorable! I'd give all the pets.",
                "Give that good boy all the pets, he deserves them!",
                "Made my day, thank you for sharing this wholesomeness.",
                "The purest thing on the internet today."
            ]
        },
         {
            "id": "post5_monday_meme",
            "subreddit": "memes",
            "title": "Another meme about Mondays, because why not? (relatable)",
            "url": "https://i.imgur.com/example5.jpg",
            "permalink": "https://reddit.com/r/memes/comments/post5_monday_meme",
            "text_content": "Mondays always hit different. Send coffee and good vibes. (This is a reaction image post). The struggle is real on Monday mornings.",
            "flair": "Meme",
            "comments": [
                "Mood. Every single Monday.",
                "I hate Mondays, send help.",
                "Can confirm, this is my spirit animal today.",
                "Need more coffee, and maybe a time machine."
            ]
        },
        {
            "id": "post6_general_lol",
            "subreddit": "funny",
            "title": "Just a funny cat being a cat",
            "url": "https://i.imgur.com/example6.jpg",
            "permalink": "https://reddit.com/r/funny/comments/post6_general_lol",
            "text_content": "My cat just knocked over a plant for no reason. Classic cat behavior, always making me laugh.",
            "flair": "Animals",
            "comments": [
                "Cats are the best!",
                "Typical cat things.",
                "Made my day, thanks!",
                "This is hilarious."
            ]
        },
        {
            "id": "post7_dev_joke",
            "subreddit": "ProgrammerHumor",
            "title": "Why programmers prefer dark mode (a programming joke)",
            "url": "https://i.imgur.com/example7.jpg",
            "permalink": "https://reddit.com/r/ProgrammerHumor/comments/post7_dev_joke",
            "text_content": "Because light attracts bugs! LOL. Get it? A classic developer joke.",
            "flair": "Programming Humor",
            "comments": [
                "Good one!",
                "Haha, so true.",
                "Dark mode for life.",
                "I needed this laugh."
            ]
        }
    ]

    filtered_posts: List[Dict[str, Any]] = []
    # Normalize inputs for case-insensitive matching and efficient lookups
    normalized_subreddits = {s.lower() for s in subreddits}
    normalized_keywords = {k.lower() for k in keywords}
    normalized_flairs = {f.lower() for f in flairs}

    for post in mock_posts_data:
        # Step 1: Check subreddit membership (case-insensitive)
        if post["subreddit"].lower() not in normalized_subreddits:
            print(f"[{get_current_timestamp()}] DEBUG: Skipping post '{post.get('title', 'N/A')}' - Subreddit '{post['subreddit']}' not in configured list.")
            continue

        # Step 2: Check for keyword match in title or text content (case-insensitive)
        post_content = (post.get("title", "") + " " + post.get("text_content", "")).lower()
        keyword_match = any(k in post_content for k in normalized_keywords)
        if not keyword_match:
            print(f"[{get_current_timestamp()}] DEBUG: Skipping post '{post.get('title', 'N/A')}' - No matching keywords found.")
            continue

        # Step 3: Check for flair match (case-insensitive)
        post_flair_lower = post.get("flair", "").lower()
        flair_match = any(f in post_flair_lower for f in normalized_flairs)
        if not flair_match:
            print(f"[{get_current_timestamp()}] DEBUG: Skipping post '{post.get('title', 'N/A')}' - No matching flairs found.")
            continue
        
        filtered_posts.append(post)
        print(f"[{get_current_timestamp()}] DEBUG: Matched post '{post.get('title', 'N/A')}' - Added to filtered list.")

    print(f"[{get_current_timestamp()}] INFO: Found {len(filtered_posts)} mock posts after applying all filters.")
    
    # Randomly select a subset of filtered posts, up to MAX_POSTS_PER_RUN.
    # This prevents sending too many notifications at once and simulates variability.
    num_posts_to_return = min(len(filtered_posts), Config.MAX_POSTS_PER_RUN)
    if num_posts_to_return == 0:
        print(f"[{get_current_timestamp()}] INFO: No posts to return after random selection.")
        return [] # No posts to return
    
    selected_posts = random.sample(filtered_posts, num_posts_to_return)
    print(f"[{get_current_timestamp()}] INFO: Selected {len(selected_posts)} posts for processing this run.")
    return selected_posts

def summarize_meme_with_mock_llm(post_title: str, post_text_content: str, comments: List[str]) -> str:
    """
    Mocks an LLM's ability to summarize a meme and its reactions.
    In a real scenario, this would integrate with an actual LLM API
    (e.g., OpenAI GPT-3.5/4, Google Gemini, Anthropic Claude).

    Args:
        post_title: The title of the Reddit post.
        post_text_content: The self-text content of the post (if any).
        comments: A list of top comments on the post.

    Returns:
        A concise summary string of the meme and its general sentiment.
    """
    print(f"[{get_current_timestamp()}] INFO: Mocking LLM summary for post: '{post_title}'")
    
    summary_parts: List[str] = []
    summary_parts.append(f"이 밈은 '{post_title}'에 대한 내용입니다.")
    
    # Rule-based summarization for mocking purposes.
    # This logic simulates understanding common meme themes.
    post_content_lower = (post_title + " " + post_text_content).lower()

    if "boomer boss" in post_content_lower:
        summary_parts.append("디지털 밈 문화를 이해하지 못하는 상사에게 밈을 설명하려는 상황의 어려움을 유머러스하게 표현합니다.")
        summary_parts.append("주요 반응: '너무 현실적이다', '내 상사도 그랬다'며 공감하는 의견이 많습니다.")
    elif "code finally compiles" in post_content_lower or "programming" in post_content_lower or "developer" in post_content_lower:
        summary_parts.append("오랜 디버깅 끝에 코드가 성공적으로 컴파일되었을 때의 극심한 안도감을 다루는 개발자 유머입니다.")
        summary_parts.append("주요 반응: 개발자들이 '매번 겪는 일', '최고의 기분'이라며 격하게 공감합니다.")
    elif "burnt toast" in post_content_lower or "cooking fail" in post_content_lower or "epic fail" in post_content_lower:
        summary_parts.append("요리 시도 실패로 인해 결국 토스트를 태워버리고 엉망이 된 상황을 우스꽝스럽게 묘사합니다.")
        summary_parts.append("주요 반응: '나도 해봤다', '다음엔 배달 시켜라' 등의 유쾌한 실패 공감 댓글이 많습니다.")
    elif "doggo patiently waiting" in post_content_lower or "animal" in post_content_lower or "cute" in post_content_lower:
        summary_parts.append("사랑스러운 강아지가 인내심 있게 쓰다듬어 주기를 기다리는 훈훈한 장면입니다. 보는 이들에게 따뜻함을 전달합니다.")
        summary_parts.append("주요 반응: '너무 귀엽다', '이 세상에서 가장 순수하다'며 강아지에 대한 애정을 표현합니다.")
    elif "mondays" in post_content_lower:
        summary_parts.append("월요일의 피곤함과 스트레스를 표현하는 일반적인 밈입니다. 커피와 긍정적인 에너지를 요구하는 내용입니다.")
        summary_parts.append("주요 반응: '격하게 공감한다', '커피가 필요하다'는 등 월요일에 대한 보편적인 불평을 나눕니다.")
    else:
        # Generic summary if no specific rule matches.
        brief_text = post_text_content[:100].strip() + "..." if len(post_text_content) > 100 else post_text_content
        sample_comments = ", ".join(comments[:2]) if comments else "댓글 없음."
        summary_parts.append(f"주요 내용: {brief_text if brief_text else '본문 내용 없음.'}")
        summary_parts.append(f"주요 반응: {sample_comments} 등.")
    
    final_summary = " ".join(summary_parts)
    print(f"[{get_current_timestamp()}] DEBUG: Generated mock summary (first 50 chars): '{final_summary[:50]}...'")
    return final_summary

def post_to_mock_slack(summary_text: str, image_url: str, original_link: str):
    """
    Mocks sending a formatted message to Slack.
    In a real scenario, this would use the `requests` library to post to a Slack webhook URL.

    Args:
        summary_text: The summarized content of the meme.
        image_url: The URL of the meme image/video.
        original_link: The permalink to the original Reddit post.
    """
    print(f"[{get_current_timestamp()}] INFO: --- MOCK SLACK POST START ---")
    print(f"[{get_current_timestamp()}] DEBUG: Attempting to simulate sending message to Slack webhook: {Config.SLACK_WEBHOOK_URL}")

    # The actual Slack message payload structure, as it would be sent via `requests`.
    # Emojis are represented using their Unicode escape sequences or raw characters in Python.
    # The `json.dumps` function handles the final JSON escaping when the payload is serialized.
    slack_payload: Dict[str, Any] = {
        "text": f"\ud83d\udd25 ReddAI Radar: 발롱봇이 새로운 바이럴 밈을 발견했습니다! \ud83d\udd25",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{summary_text}*"
                }
            },
            {
                "type": "image",
                "image_url": image_url,
                "alt_text": "Meme Image"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"원본 밈 보기: <{original_link}|클릭하세요>"
                    }
                ]
            }
        ]
    }

    # For demonstration, we'll just print the structured payload to console.
    # ensure_ascii=False makes sure Korean characters are printed as-is to console,
    # but when this entire code string is put into JSON, they will be \uXXXX escaped.
    print(f"Slack Message Payload (simulated):\n{json.dumps(slack_payload, indent=2, ensure_ascii=False)}")
    print(f"[{get_current_timestamp()}] INFO: --- MOCK SLACK POST END ---")

# --- Main Bot Logic ---

def run_redd_ai_radar():
    """
    Main function to run the ReddAI Radar bot.
    This bot continuously scans specified subreddits for popular memes,
    summarizes them using a mock LLM, and then mock-posts them to Slack.
    """
    print(f"[{get_current_timestamp()}] INFO: ReddAI Radar bot initializing...")
    print(f"[{get_current_timestamp()}] CONFIG: Subreddits: {', '.join(Config.REDDIT_SUBREDDITS)}")
    print(f"[{get_current_timestamp()}] CONFIG: Keywords: {', '.join(Config.KEYWORDS_TO_FILTER)}")
    print(f"[{get_current_timestamp()}] CONFIG: Flairs: {', '.join(Config.FLAIRS_TO_FILTER)}")
    print(f"[{get_current_timestamp()}] CONFIG: Scan Interval: {Config.SCAN_INTERVAL_SECONDS} seconds")
    print(f"[{get_current_timestamp()}] CONFIG: Max Posts per Run: {Config.MAX_POSTS_PER_RUN}")
    print(f"[{get_current_timestamp()}] INFO: ReddAI Radar bot started. Entering main loop. Press Ctrl+C to stop.")
    
    while True:
        try:
            print(f"\n[{get_current_timestamp()}] === STARTING NEW SCAN CYCLE ===")
            
            # Step 1: Real-time Reddit Meme Scan & Filtering (Mocked)
            print(f"[{get_current_timestamp()}] INFO: Calling mock Reddit post fetching function...")
            meme_posts = get_mock_reddit_posts(
                Config.REDDIT_SUBREDDITS,
                Config.KEYWORDS_TO_FILTER,
                Config.FLAIRS_TO_FILTER
            )
            
            if not meme_posts:
                print(f"[{get_current_timestamp()}] INFO: No new filtered memes found in this scan cycle. Waiting for next cycle.")
            else:
                print(f"[{get_current_timestamp()}] INFO: Processing {len(meme_posts)} selected meme(s) for summarization and delivery.")
                for i, post in enumerate(meme_posts):
                    post_id = post.get("id", "N/A")
                    post_title = post.get("title", "No Title")
                    
                    print(f"[{get_current_timestamp()}] INFO: [{i+1}/{len(meme_posts)}] Attempting to process post ID '{post_id}': '{post_title}'")
                    
                    try:
                        # Safely retrieve post data with defaults
                        post_text_content = post.get("text_content", "")
                        post_comments = post.get("comments", [])
                        post_url = post.get("url", "")
                        post_permalink = post.get("permalink", "")

                        if not post_url or not post_permalink:
                            print(f"[{get_current_timestamp()}] WARNING: Post '{post_id}' is missing a valid URL or permalink. Skipping processing for this post.")
                            continue

                        # Step 2: AI Humor Core Summary & Interpretation (Mocked)
                        print(f"[{get_current_timestamp()}] INFO: Summarizing post '{post_id}' ('{post_title}') using mock LLM...")
                        summary = summarize_meme_with_mock_llm(
                            post_title,
                            post_text_content,
                            post_comments
                        )
                        
                        # Step 3: Slack Channel Automatic Delivery & Sharing (Mocked)
                        print(f"[{get_current_timestamp()}] INFO: Mock-posting summary for '{post_id}' ('{post_title}') to Slack...")
                        post_to_mock_slack(summary, post_url, post_permalink)
                        
                        print(f"[{get_current_timestamp()}] SUCCESS: Successfully processed and mocked posting for post ID '{post_id}'.")
                    
                    except KeyError as ke:
                        print(f"[{get_current_timestamp()}] ERROR: Data integrity issue for post '{post_id}'. Missing expected key: {ke}. Skipping this post.")
                    except Exception as inner_e:
                        print(f"[{get_current_timestamp()}] ERROR: An unexpected error occurred while processing post '{post_id}' ('{post_title}'): {inner_e}")
                        # Log the full traceback for debugging in a real scenario: traceback.print_exc()
                        print(f"[{get_current_timestamp()}] ERROR: Skipping this post due to an error during processing.")
                        
        except KeyboardInterrupt:
            print(f"\n[{get_current_timestamp()}] INFO: KeyboardInterrupt detected. Shutting down ReddAI Radar bot gracefully.")
            break # Exit the infinite loop
        except Exception as e:
            print(f"[{get_current_timestamp()}] CRITICAL ERROR: An unexpected error occurred during main bot execution cycle: {e}")
            # In a real application, implement more robust logging (e.g., Sentry, email alerts)
            # and potentially exponential backoff for retries to prevent continuous failures.
            print(f"[{get_current_timestamp()}] CRITICAL ERROR: Bot will attempt to restart the scan cycle after the configured interval.")
            
        finally:
            print(f"[{get_current_timestamp()}] === SCAN CYCLE COMPLETE === Waiting for {Config.SCAN_INTERVAL_SECONDS} seconds until next scan.")
            time.sleep(Config.SCAN_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_redd_ai_radar()