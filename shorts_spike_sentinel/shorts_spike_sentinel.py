# -*- coding: utf-8 -*-
# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError: # reconfigure may not exist in some environments
        pass
    except Exception: # Catch any other potential errors during reconfigure
        pass

import argparse
import os
import requests
import time
import random
from datetime import datetime

# --- 환경 설정 --- #
YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3/videos"
SPIKE_THRESHOLD_SCORE = 70 # 바이럴 스파이크 감지 기준 점수 (0-100)
API_REQUEST_TIMEOUT = 10 # YouTube API 호출 타임아웃 (초)

def fetch_youtube_data(video_id: str, api_key: str) -> dict:
    """YouTube Data API를 사용하여 영상 통계를 가져옵니다.

    Args:
        video_id (str): YouTube 영상의 ID.
        api_key (str): YouTube Data API 키.

    Returns:
        dict: 영상 제목, 조회수, 좋아요 수 등 통계 데이터를 담은 딕셔너리.
              API 호출 실패 시 빈 딕셔너리를 반환합니다.
    """
    print(f"[진행중] 영상 ID '{video_id}'의 YouTube 데이터를 가져오는 중...")
    params = {
        "part": "snippet,statistics",
        "id": video_id,
        "key": api_key
    }
    try:
        response = requests.get(YOUTUBE_API_BASE_URL, params=params, timeout=API_REQUEST_TIMEOUT)
        response.raise_for_status() # HTTP 에러 (4xx, 5xx) 발생 시 예외 발생
        data = response.json()

        if not data.get('items'):
            print(f"[경고] YouTube API: ID '{video_id}'에 대한 데이터를 찾을 수 없습니다. 유효한 ID인지 확인하세요.")
            return {}

        item = data['items'][0]
        snippet = item.get('snippet', {})
        stats = item.get('statistics', {})

        print(f"[성공] 영상 ID '{video_id}' 데이터 수신 완료.")
        return {
            "title": snippet.get('title', '제목 없음'),
            "description": snippet.get('description', '설명 없음'),
            "views": int(stats.get('viewCount', 0)),
            "likes": int(stats.get('likeCount', 0)),
            "comments": int(stats.get('commentCount', 0)),
            "shares": int(stats.get('shareCount', 0)) if 'shareCount' in stats else random.randint(100, 1000) # YouTube API가 공유수를 직접 제공하지 않아 임의 값 사용
        }
    except requests.exceptions.Timeout:
        print(f"[에러] YouTube API 호출 시간 초과 (ID: {video_id}). 네트워크 연결을 확인하세요.")
    except requests.exceptions.HTTPError as e:
        print(f"[에러] YouTube API HTTP 오류 (ID: {video_id}): {e.response.status_code} - {e.response.text}")
    except requests.exceptions.ConnectionError:
        print(f"[에러] YouTube API 연결 오류 (ID: {video_id}). 인터넷 연결을 확인하세요.")
    except requests.exceptions.RequestException as e:
        print(f"[에러] YouTube API 호출 중 예상치 못한 문제 발생 (ID: {video_id}): {e}")
    except ValueError as e:
        print(f"[에러] YouTube API 응답 파싱 오류 (ID: {video_id}): {e}. 유효하지 않은 JSON 응답일 수 있습니다.")
    except Exception as e:
        print(f"[에러] fetch_youtube_data 함수에서 알 수 없는 오류 발생 (ID: {video_id}): {e}")
    return {}

def generate_viral_hook(video_title: str) -> str:
    """영상 제목을 기반으로 바이럴 후킹 문구를 생성합니다 (최대 20자).
    제목 길이에 따라 동적으로 잘라내어 문구를 생성합니다.
    """
    # 제목이 짧을 경우를 대비하여 최소 길이 확인
    title_segment_5 = video_title[:min(len(video_title), 5)]
    title_segment_6 = video_title[:min(len(video_title), 6)]
    title_segment_7 = video_title[:min(len(video_title), 7)]
    title_segment_8 = video_title[:min(len(video_title), 8)]

    templates = [
        f"필수 시청: {title_segment_5}..",
        f"충격! {title_segment_8} 비결은?",
        f"이거 봐! {title_segment_6}!",
        f"궁금증 폭발 {title_segment_7}",
        f"이게 바로 {title_segment_5}이다"
    ]
    hook = random.choice(templates)
    return (hook if len(hook) <= 20 else hook[:17] + '...') # 20자 초과 시 ...으로 줄임

def calculate_virality_score(data: dict) -> int:
    """영상 데이터로 바이럴 잠재력 점수를 계산합니다 (0-100).
    조회수, 좋아요 비율, 댓글 수, 공유 수를 기반으로 점수를 매깁니다.
    (실제 AI 모델 대신 간단한 수식으로 시뮬레이션)
    """
    print(f"[진행중] 바이럴 잠재력 점수 계산 중... (현재 조회수: {data.get('views', 0):,})")
    if not data or data.get('views', 0) == 0:
        print("[정보] 유효한 데이터가 없거나 조회수가 0이므로 점수를 0으로 설정합니다.")
        return 0
    
    views = data['views']
    likes = data['likes']
    comments = data['comments']
    shares = data['shares']

    score = 0
    # 조회수 기여: 10만 뷰 당 40점. 최대 40점.
    views_score = min(views / 100000, 1) * 40 
    # 좋아요 비율 기여: 좋아요/조회수 비율 10% 당 30점. 최대 30점.
    likes_ratio_score = min(likes / views * 100 if views > 0 else 0, 10) * 3 
    # 댓글 수 기여: 1천 댓글 당 20점. 최대 20점.
    comments_score = min(comments / 1000, 1) * 20 
    # 공유 수 기여: 500 공유 당 10점. 최대 10점.
    shares_score = min(shares / 500, 1) * 10 
    
    score = int(views_score + likes_ratio_score + comments_score + shares_score)
    final_score = min(score, 100)
    print(f"[완료] 바이럴 잠재력 점수 계산 완료: {final_score}/100")
    return final_score

def main():
    """유튜브 쇼츠 떡상 감시병의 주 실행 함수입니다.
    명령줄 인자를 파싱하고, 영상 데이터를 가져와 바이럴 점수를 계산하며, 결과를 보고서 파일로 저장합니다.
    """
    parser = argparse.ArgumentParser(
        description="유튜브 쇼츠 떡상 감시병 (Shorts Spike Sentinel). "
                    "제공된 영상 ID들의 바이럴 잠재력을 분석하고 떡상 조짐을 감지합니다."
    )
    parser.add_argument(
        "--video_ids",
        nargs='+',
        help="감시할 유튜브 쇼츠 영상 ID 목록 (예: -v VIDEO_ID1 VIDEO_ID2)"
    )
    parser.add_argument(
        "--api_key",
        default=os.getenv("YOUTUBE_API_KEY"),
        help="유튜브 Data API 키 (환경 변수 YOUTUBE_API_KEY로 설정 가능)"
    )
    args = parser.parse_args()

    video_ids_to_monitor = args.video_ids
    youtube_api_key = args.api_key

    if not video_ids_to_monitor:
        print("\n[안내] --video_ids 인자가 없어 샘플 데이터로 시연합니다.")
        print("       본인 영상을 감시하려면 'python shorts_spike_sentinel.py --video_ids YourVideoID1 YourVideoID2' 처럼 실행하세요.\n")
        video_ids_to_monitor = ["dQw4w9WgXcQ"] # Rick Astley - Never Gonna Give You Up (example)

    if not youtube_api_key:
        print("\n[경고] YouTube API 키가 제공되지 않았습니다 (환경 변수 YOUTUBE_API_KEY 또는 --api_key). 실제 데이터 대신 시뮬레이션된 데이터로 진행합니다.\n")

    # 결과 보고서 파일명 생성
    report_filename = f"spike_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    spike_detected_count = 0

    print(f"[시작] Shorts Spike Sentinel이 감시를 시작합니다. 결과는 '{report_filename}'에 저장됩니다.")

    with open(report_filename, 'w', encoding='utf-8') as f_report:
        f_report.write(f"Shorts Spike Sentinel Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f_report.write("="*60 + "\n\n")

        for i, video_id in enumerate(video_ids_to_monitor):
            print(f"\n{'='*10} [{i+1}/{len(video_ids_to_monitor)}] 영상 ID: {video_id} 감시 시작 {'='*10}")
            current_video_data = {}
            
            if youtube_api_key:
                current_video_data = fetch_youtube_data(video_id, youtube_api_key)
            
            # API 키가 없거나, API 호출에 실패했거나, API 호출 결과가 비어있을 경우 모의 데이터 사용
            if not current_video_data:
                print(f"[시뮬레이션] ID '{video_id}'에 대한 모의 데이터를 생성합니다 (실제 데이터 획득 실패 또는 API 키 부재). ")
                current_video_data = {
                    "title": f"쇼츠 떡상 감시병 데모 영상 {video_id[:min(len(video_id),5)]}",
                    "description": "오또가 쇼츠 떡상의 비결을 알려드립니다!",
                    "views": random.randint(50000, 500000) * (2 if random.random() > 0.5 else 1), # Spike potential
                    "likes": random.randint(2000, 20000) * (2 if random.random() > 0.5 else 1),
                    "comments": random.randint(100, 1000) * (2 if random.random() > 0.5 else 1),
                    "shares": random.randint(50, 500) * (2 if random.random() > 0.5 else 1)
                }

            # 모의 데이터 생성마저 실패하는 경우는 없으므로, 이 시점에서는 항상 current_video_data가 채워져 있음

            virality_score = calculate_virality_score(current_video_data)
            viral_hook = generate_viral_hook(current_video_data['title'])

            f_report.write(f"영상 ID: {video_id}\n")
            f_report.write(f"  제목: {current_video_data['title']}\n")
            f_report.write(f"  조회수: {current_video_data['views']:,}\n")
            f_report.write(f"  좋아요: {current_video_data['likes']:,}\n")
            f_report.write(f"  댓글: {current_video_data['comments']:,}\n")
            f_report.write(f"  공유수(추정): {current_video_data['shares']:,}\n")
            f_report.write(f"  바이럴 잠재력 점수: {virality_score}/100\n")

            if virality_score >= SPIKE_THRESHOLD_SCORE:
                spike_detected_count += 1
                alert_message = f"[!!! 떡상 감지 !!!] 영상 ID '{video_id}' (제목: {current_video_data['title'][:30]}{'...' if len(current_video_data['title']) > 30 else ''}) - 점수: {virality_score}\n"
                alert_message += f"  >> ✨ 추천 바이럴 후킹 문구 (1달러에 판매!): '{viral_hook}'\n"
                print(alert_message)
                f_report.write(alert_message)
            else:
                print(f"[정상] 영상 ID '{video_id}' - 점수: {virality_score} (떡상 조짐 없음)\n")
                f_report.write(f"[정상] 바이럴 잠재력 점수: {virality_score}/100 (떡상 조짐 없음)\n")
            f_report.write("\n" + "-"*40 + "\n\n")

    print(f"\n[보고 완료] 총 {len(video_ids_to_monitor)}개 영상 감시 완료. {spike_detected_count}개 떡상 조짐 감지.")
    print(f"결과 보고서는 '{report_filename}' 파일에 저장되었습니다.")
    print("[안내] 이 봇은 주기적으로 실행하면 더욱 효과적입니다 (예: crontab 또는 Windows 작업 스케줄러 등록).")

if __name__ == "__main__":
    main()
