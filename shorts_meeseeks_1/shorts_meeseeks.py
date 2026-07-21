import os
import time
import re
import sys # For sys.exit()
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openai import OpenAI, APIError, RateLimitError
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# --- Environment Variables Loading ---
load_dotenv()

# --- Configuration from Environment Variables ---
# Google API Key for YouTube Data API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# OpenAI API Key for GPT model access
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Slack Bot Token (starts with 'xoxb-')
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
# Slack Channel ID where messages will be posted
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

# --- Constants ---
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
# Keywords to search for trending shorts
TRENDING_SHORT_KEYWORDS = [
    "shorts", "meme", "viral", "funny", "유튜브쇼츠", "밈", "웃긴영상"
]
# Maximum number of videos to fetch per keyword from YouTube Search API
MAX_RESULTS_PER_KEYWORD = 10
# Minimum duration for a video to be considered a 'short' (in seconds)
MIN_VIDEO_DURATION_SECONDS = 5
# Maximum duration for a video to be considered a 'short' (in seconds)
MAX_VIDEO_DURATION_SECONDS = 60
# AI Model to use for humor analysis
OPENAI_MODEL = "gpt-3.5-turbo" # Consider "gpt-4-turbo" for better quality (higher cost)
# Limit for processing videos in a single run (for demo purposes)
PROCESSED_VIDEO_LIMIT = 3
# Delay before completing and deleting a Slack mission message (in seconds)
SLACK_MISSION_COMPLETION_DELAY = 15
# Delay before deleting the final mission complete message (in seconds)
SLACK_MISSION_DELETION_DELAY = 5
# Brief pause between processing each video to avoid rate limits (in seconds)
INTER_VIDEO_PROCESSING_PAUSE = 5

# --- Global Client Instances ---
youtube_client = None
openai_client = None
s_client = None # Renamed to s_client to avoid conflict with slack_sdk

# --- Logging Helper --- (for consistent output formatting)
def log_message(level, component, message):
    """Prints a formatted log message."""
    print(f"[{level}][{component}] {message}")

def parse_iso8601_duration_to_seconds(duration_str):
    """
    Parses an ISO 8601 duration string (e.g., "PT1M30S", "PT30S") to total seconds.
    Assumes standard YouTube API duration format (PT...H...M...S).
    """
    total_seconds = 0
    # Use regex to find H, M, S components. Handle 'PT' prefix.
    duration_str_clean = duration_str.replace('PT', '')
    
    hours = re.search(r'(\d+)H', duration_str_clean)
    minutes = re.search(r'(\d+)M', duration_str_clean)
    seconds = re.search(r'(\d+)S', duration_str_clean)

    if hours:
        total_seconds += int(hours.group(1)) * 3600
    if minutes:
        total_seconds += int(minutes.group(1)) * 60
    if seconds:
        total_seconds += int(seconds.group(1))

    return total_seconds

def initialize_clients():
    """Initializes YouTube, OpenAI, and Slack API clients and sets them as global variables."""
    global youtube_client, openai_client, s_client

    log_message("INFO", "SYSTEM", "클라이언트 초기화를 시작합니다...")

    # Initialize YouTube Client
    if not GOOGLE_API_KEY:
        log_message("ERROR", "YOUTUBE", "GOOGLE_API_KEY가 설정되지 않았습니다. YouTube 클라이언트를 초기화할 수 없습니다.")
    else:
        try:
            youtube_client = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=GOOGLE_API_KEY)
            log_message("INFO", "YOUTUBE", "YouTube 클라이언트가 성공적으로 초기화되었습니다.")
        except Exception as e:
            log_message("ERROR", "YOUTUBE", f"YouTube 클라이언트 초기화 중 오류 발생: {e}")

    # Initialize OpenAI Client
    if not OPENAI_API_KEY:
        log_message("ERROR", "OPENAI", "OPENAI_API_KEY가 설정되지 않았습니다. OpenAI 클라이언트를 초기화할 수 없습니다.")
    else:
        try:
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            log_message("INFO", "OPENAI", "OpenAI 클라이언트가 성공적으로 초기화되었습니다.")
        except Exception as e:
            log_message("ERROR", "OPENAI", f"OpenAI 클라이언트 초기화 중 오류 발생: {e}")

    # Initialize Slack Client
    if not SLACK_BOT_TOKEN:
        log_message("ERROR", "SLACK", "SLACK_BOT_TOKEN이 설정되지 않았습니다. Slack 클라이언트를 초기화할 수 없습니다.")
    elif not SLACK_CHANNEL_ID:
        log_message("ERROR", "SLACK", "SLACK_CHANNEL_ID가 설정되지 않았습니다. Slack 클라이언트를 초기화할 수 없습니다.")
    else:
        try:
            s_client = WebClient(token=SLACK_BOT_TOKEN)
            # Test Slack connectivity by fetching channel info
            s_client.conversations_info(channel=SLACK_CHANNEL_ID) 
            log_message("INFO", "SLACK", "Slack 클라이언트가 성공적으로 초기화되었습니다.")
        except SlackApiError as e:
            log_message("ERROR", "SLACK", f"Slack API 오류 발생 (클라이언트 초기화/채널 확인): {e.response['error']}")
            s_client = None # Reset client if it fails to connect or verify channel
        except Exception as e:
            log_message("ERROR", "SLACK", f"Slack 클라이언트 초기화 중 예상치 못한 오류 발생: {e}")
            s_client = None

    # Check if all essential clients are initialized
    if not (youtube_client and openai_client and s_client):
        log_message("ERROR", "SYSTEM", "모든 필수 클라이언트가 초기화되지 않았습니다. 프로그램을 종료합니다.")
        sys.exit(1)
    log_message("INFO", "SYSTEM", "모든 클라이언트 초기화 완료.")

def get_trending_shorts():
    """
    Searches YouTube for trending shorts based on predefined keywords and duration filters.
    Returns a list of dictionaries, each representing a short video with its details.
    """
    log_message("INFO", "YOUTUBE", f"핫 키워드 '{', '.join(TRENDING_SHORT_KEYWORDS)}'를 이용해 쇼츠를 검색합니다.")
    unique_video_ids = set()

    for keyword in TRENDING_SHORT_KEYWORDS:
        try:
            log_message("INFO", "YOUTUBE", f"키워드 '{keyword}'로 쇼츠 후보를 검색 중입니다...")
            search_response = youtube_client.search().list(
                q=keyword,
                type="video",
                videoDuration="short", # Filters for videos under 4 minutes
                order="viewCount",     # Most popular videos for the keyword
                part="id,snippet",
                maxResults=MAX_RESULTS_PER_KEYWORD
            ).execute()

            items_found = search_response.get("items", [])
            for item in items_found:
                video_id = item["id"].get("videoId") # Safely get videoId
                if video_id:
                    unique_video_ids.add(video_id)
            log_message("INFO", "YOUTUBE", f"키워드 '{keyword}'로 {len(items_found)}개의 쇼츠 후보를 찾았습니다. 현재 총 {len(unique_video_ids)}개.")

        except HttpError as e:
            log_message("ERROR", "YOUTUBE", f"YouTube API 호출 중 오류 발생 (키워드: {keyword}): {e}")
            continue
        except Exception as e:
            log_message("ERROR", "YOUTUBE", f"YouTube 영상 검색 중 예상치 못한 오류 발생 (키워드: {keyword}): {e}")
            continue

    if not unique_video_ids:
        log_message("INFO", "YOUTUBE", "검색된 쇼츠 후보가 없습니다.")
        return []

    log_message("INFO", "YOUTUBE", f"총 {len(unique_video_ids)}개의 고유한 쇼츠 후보를 찾았습니다. 상세 정보를 가져옵니다.")

    final_shorts = []
    video_ids_list = list(unique_video_ids)

    # Fetch full video details in batches to get actual duration and filter for true shorts
    # YouTube API allows up to 50 video IDs per request for videos().list
    for i in range(0, len(video_ids_list), 50):
        batch_ids = video_ids_list[i : i + 50]
        log_message("INFO", "YOUTUBE", f"영상 상세 정보 배치 요청 ({i+1}~{min(i+50, len(video_ids_list))} / {len(video_ids_list)})... ID: {', '.join(batch_ids[:3])}...")
        try:
            videos_response = youtube_client.videos().list(
                part="snippet,contentDetails",
                id=",".join(batch_ids)
            ).execute()

            for item in videos_response.get("items", []):
                video_id = item.get("id")
                snippet = item.get("snippet", {})
                content_details = item.get("contentDetails", {})
                
                duration_str = content_details.get("duration") # e.g., "PT1M30S"

                if not duration_str:
                    log_message("WARNING", "YOUTUBE", f"영상 ID {video_id}의 Duration 정보가 없습니다. 스킵합니다.")
                    continue

                total_seconds = parse_iso8601_duration_to_seconds(duration_str)

                # Filter for videos within the desired Shorts duration range
                if MIN_VIDEO_DURATION_SECONDS <= total_seconds <= MAX_VIDEO_DURATION_SECONDS:
                    final_shorts.append({
                        "id": video_id,
                        "title": snippet.get("title", "제목 없음"),
                        "description": snippet.get("description", "설명 없음"),
                        "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", "")
                    })
                    log_message("DEBUG", "YOUTUBE", f"'{snippet.get('title')}' ({video_id}) - {total_seconds}초. 유효한 쇼츠로 추가.")
                else:
                    log_message("DEBUG", "YOUTUBE", f"'{snippet.get('title')}' ({video_id}) - {total_seconds}초. 쇼츠 길이 기준에 부합하지 않아 스킵합니다.")

        except HttpError as e:
            log_message("ERROR", "YOUTUBE", f"YouTube API (videos.list) 호출 중 오류 발생 (배치: {','.join(batch_ids[:5])}...): {e}")
            continue
        except Exception as e:
            log_message("ERROR", "YOUTUBE", f"YouTube 영상 상세 정보 가져오는 중 예상치 못한 오류 발생: {e}")
            continue

    log_message("INFO", "YOUTUBE", f"최종적으로 {len(final_shorts)}개의 유효한 쇼츠를 필터링했습니다.")
    return final_shorts

def analyze_humor_with_ai(video_title, video_description):
    """
    Analyzes the humor points of a video title and description using OpenAI's GPT model.
    Returns a 3-line summary of humor or an error message.
    """
    log_message("INFO", "OPENAI", f"'{video_title}' 영상의 유머 포인트를 AI로 분석합니다...")
    try:
        prompt = (
            f"다음 YouTube 비디오의 제목과 설명을 분석하여 핵심 유머 포인트를 찾아 3줄로 요약해 주세요. "
            f"만약 명확한 유머가 감지되지 않는다면, '명확한 유머 포인트 없음.'이라고 답하세요.\n\n"
            f"제목: {video_title}\n"
            f"설명: {video_description}\n\n"
            f"유머 포인트 요약 (3줄):"
        )
        chat_completion = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that specializes in identifying and summarizing humor in short video content."}, 
                {"role": "user", "content": prompt}
            ],
            temperature=0.0, # Zero for more deterministic output
            max_tokens=150   # Enough tokens for 3 sentences
        )
        summary = chat_completion.choices[0].message.content.strip()
        log_message("INFO", "OPENAI", f"유머 분석 완료: {summary[:70]}...")
        return summary
    except RateLimitError as e:
        log_message("ERROR", "OPENAI", f"OpenAI API Rate Limit 초과 오류 발생: {e}")
        return "AI 분석 중 Rate Limit 초과 오류가 발생했습니다."
    except APIError as e:
        log_message("ERROR", "OPENAI", f"OpenAI API 호출 중 오류 발생: {e}")
        return "AI 분석 중 오류가 발생했습니다. (OpenAI API Error)"
    except Exception as e:
        log_message("ERROR", "OPENAI", f"OpenAI 유머 분석 중 예상치 못한 오류 발생: {e}")
        return "AI 분석 중 예상치 못한 오류가 발생했습니다."

def post_to_slack(video, humor_summary):
    """
    Posts the video information and AI humor summary to the configured Slack channel.
    Returns the timestamp (ts) of the posted message if successful, otherwise None.
    """
    log_message("INFO", "SLACK", f"'{video['title']}' 영상을 Slack에 게시합니다.")
    try:
        message_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"👀 Shorts Meeseeks 미션 시작! 웃음 배달!"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{video['title']}*\n<https://www.youtube.com/watch?v={video['id']}|영상 보러가기>"
                },
                "accessory": {
                    "type": "image",
                    "image_url": video.get('thumbnail_url', 'https://via.placeholder.com/128'), # Provide fallback image
                    "alt_text": "Video thumbnail"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*핵심 웃음 포인트 (AI 요약):*\n" + humor_summary
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": ":meeseeks: 저의 1달러짜리 웃음 미션이 곧 완료될 예정입니다..."
                    }
                ]
            }
        ]

        response = s_client.chat_postMessage(
            channel=SLACK_CHANNEL_ID,
            blocks=message_blocks,
            text=f"새로운 Shorts Meeseeks 미션: {video['title']}" # Fallback text for notifications
        )
        log_message("INFO", "SLACK", f"Slack 메시지 게시 성공. Message TS: {response['ts']}")
        return response["ts"]
    except SlackApiError as e:
        log_message("ERROR", "SLACK", f"Slack API 오류 발생 (메시지 게시): {e.response['error']}")
        return None
    except Exception as e:
        log_message("ERROR", "SLACK", f"Slack 메시지 게시 중 예상치 못한 오류 발생: {e}")
        return None

def complete_slack_mission(ts):
    """
    Updates the Slack message to 'mission complete' and then deletes it after a short delay.
    """
    log_message("INFO", "SLACK", f"Slack 메시지 '{ts}'를 '미션 완료' 상태로 업데이트합니다.")
    try:
        updated_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "✅ Shorts Meeseeks 미션 완료!"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*푸른 요정 오또의 1달러짜리 웃음 미션이 성공적으로 완료되었습니다!* :sparkles:\n\n"
                            "저는 이제 할 일을 다 했으니... 사라지겠습니다! :meeseeks_disappear:\n"
                            "다음에 또 다른 웃음 미션으로 찾아올게요! Goodbye!"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "이 메시지는 잠시 후 자동으로 삭제됩니다."
                    }
                ]
            }
        ]
        s_client.chat_update(
            channel=SLACK_CHANNEL_ID,
            ts=ts,
            blocks=updated_blocks,
            text="Shorts Meeseeks 미션 완료!"
        )
        log_message("INFO", "SLACK", f"Slack 메시지 '{ts}' 업데이트 성공. {SLACK_MISSION_DELETION_DELAY}초 후 삭제합니다...")
        time.sleep(SLACK_MISSION_DELETION_DELAY) # Give users a moment to see the completion message
        
        s_client.chat_delete(
            channel=SLACK_CHANNEL_ID,
            ts=ts
        )
        log_message("INFO", "SLACK", f"Slack 메시지 '{ts}'가 성공적으로 삭제되었습니다.")

    except SlackApiError as e:
        log_message("ERROR", "SLACK", f"Slack API 오류 발생 (메시지 업데이트/삭제): {e.response['error']}")
    except Exception as e:
        log_message("ERROR", "SLACK", f"Slack 메시지 완료 처리 중 예상치 못한 오류 발생: {e}")

def run_meeseeks_mission():
    """
    Main function to run the Shorts Meeseeks mission: 
    initialize clients, get shorts, analyze humor, post to Slack, and clean up.
    """
    log_message("INFO", "MISSION", "--- Shorts Meeseeks: 1달러 웃음 미션 시작! ---")
    initialize_clients() # This will exit if any client fails to initialize

    shorts_to_process = get_trending_shorts()

    if not shorts_to_process:
        log_message("INFO", "MISSION", "처리할 쇼츠가 없습니다. 미션을 종료합니다.")
        return

    processed_count = 0
    for video in shorts_to_process:
        if processed_count >= PROCESSED_VIDEO_LIMIT: # Limit processing for demo
            log_message("INFO", "MISSION", f"데모를 위해 {PROCESSED_VIDEO_LIMIT}개의 영상만 처리했습니다. 더 많은 영상을 처리하려면 'PROCESSED_VIDEO_LIMIT'를 조정하세요.")
            break

        log_message("INFO", "MISSION", f"\n[MISSION] 새로운 쇼츠 미션 시작: '{video['title']}' (ID: {video['id']})")
        
        humor_summary = analyze_humor_with_ai(video["title"], video["description"])

        if "명확한 유머 포인트 없음." in humor_summary or "오류" in humor_summary:
            log_message("WARNING", "MISSION", f"'{video['title']}' 영상에서 유머 포인트를 찾지 못했거나 AI 분석에 실패했습니다. 다음으로 넘어갑니다.")
            continue

        message_ts = post_to_slack(video, humor_summary)

        if message_ts:
            log_message("INFO", "MISSION", f"Slack 메시지가 게시되었습니다. {SLACK_MISSION_COMPLETION_DELAY}초 후 미션 완료 처리합니다...")
            time.sleep(SLACK_MISSION_COMPLETION_DELAY) # Wait for a moment before completing the mission
            complete_slack_mission(message_ts)
            processed_count += 1
        else:
            log_message("ERROR", "MISSION", f"Slack 메시지 게시 실패로 '{video['title']}' 미션을 완료할 수 없습니다.")
        
        time.sleep(INTER_VIDEO_PROCESSING_PAUSE) # Brief pause before processing the next video to avoid rate limits

    log_message("INFO", "MISSION", f"--- Shorts Meeseeks: {processed_count}개의 웃음 미션 완료! ---")

if __name__ == "__main__":
    run_meeseeks_mission()
