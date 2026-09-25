# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import csv
import os
import random
import time
from datetime import datetime
import requests

# --- Configuration --- 상수 설정 ---
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "YOUR_SLACK_WEBHOOK_URL") # Slack 알림을 위한 웹훅 URL (환경 변수 또는 직접 설정)
FLAME_THRESHOLD_MULTIPLIER = 1.8  # '불꽃' 반응으로 간주하기 위한 평균 대비 성능 배율 (예: 1.8배)
FLAME_CHANCE = 0.15               # '불꽃' 영상이 발생할 확률 (예: 15%)
FLAME_DATA_FILE = "reelrush_flame_data.csv" # 불꽃 영상 데이터 저장 파일

# --- Helper Functions 보조 함수 ---
def send_slack_notification(message):
    """Slack으로 알림 메시지를 보냅니다."""
    if SLACK_WEBHOOK_URL == "YOUR_SLACK_WEBHOOK_URL" or not SLACK_WEBHOOK_URL:
        print(f"[DEBUG] Slack 웹훅 URL이 설정되지 않았습니다. 알림을 보내지 않습니다: {message}")
        return
    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json={"text": f"\ud83d\udd25 ReelRush Radar Alert! {message}"},
            timeout=5
        )
        response.raise_for_status()  # 200 이외의 응답 코드에 대해 예외 발생
        print(f"[INFO] Slack 알림이 성공적으로 전송되었습니다: {message}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Slack 알림 전송 중 오류 발생: {e}")

def load_channels_data(filepath=None):
    """
    CSV 파일에서 채널의 과거 데이터를 로드하거나, 파일이 없으면 샘플 데이터를 반환합니다.
    CSV 형식: channel_name,avg_views,avg_likes,avg_comments
    """
    channels = {}
    if filepath and os.path.exists(filepath):
        print(f"[PROGRESS] 채널 데이터를 '{filepath}'에서 로드 중...")
        try:
            with open(filepath, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 필요한 모든 필드가 있는지 확인합니다.
                    if all(key in row for key in ['channel_name', 'avg_views', 'avg_likes', 'avg_comments']):
                        channel_name = row['channel_name']
                        channels[channel_name] = {
                            'avg_views': int(row['avg_views']),
                            'avg_likes': int(row['avg_likes']),
                            'avg_comments': int(row['avg_comments'])
                        }
                    else:
                        print(f"[WARNING] CSV 줄 스킵됨 (필드 누락): {row}")
            print(f"[SUCCESS] '{filepath}'에서 {len(channels)}개의 채널을 성공적으로 로드했습니다.")
        except (IOError, ValueError, csv.Error) as e:
            print(f"[ERROR] 채널 데이터 로드 실패 ('{filepath}'): {e}. 샘플 데이터를 사용합니다.")
            channels = get_sample_channels_data()
    else:
        if filepath:
            print(f"[WARNING] 채널 데이터 파일 '{filepath}'을 찾을 수 없습니다. 샘플 데이터를 사용합니다.")
        print("[INFO] 지금은 샘플 데이터로 실행됩니다. 본인 파일을 쓰려면 'python reels_radar.py --channels your_channels.csv'를 실행하세요.")
        channels = get_sample_channels_data()
    return channels

def get_sample_channels_data():
    """데모를 위한 샘플 채널 과거 데이터를 제공합니다."""
    return {
        "AI Innovators": {'avg_views': 50000, 'avg_likes': 3000, 'avg_comments': 150},
        "Tech Insights Daily": {'avg_views': 120000, 'avg_likes': 7000, 'avg_comments': 300},
        "Coding Master": {'avg_views': 80000, 'avg_likes': 5000, 'avg_comments': 200}
    }

def simulate_new_video_performance(channel_name, avg_data):
    """새로운 숏폼/릴 영상의 초기 1시간 성능을 시뮬레이션하고 '불꽃' 여부를 판단합니다."""
    base_views = avg_data['avg_views']
    base_likes = avg_data['avg_likes']
    base_comments = avg_data['avg_comments']

    # 일반적인 성능 변동 시뮬레이션 (평균의 80% ~ 120%)
    views = int(base_views * random.uniform(0.8, 1.2))
    likes = int(base_likes * random.uniform(0.8, 1.2))
    comments = int(base_comments * random.uniform(0.8, 1.2))

    is_flame = False
    if random.random() < FLAME_CHANCE: # 무작위로 '불꽃' 영상 발생 기회
        is_flame = True
        # '불꽃'일 경우, 기준치 대비 성능을 크게 증가시킵니다.
        views = int(views * random.uniform(FLAME_THRESHOLD_MULTIPLIER, FLAME_THRESHOLD_MULTIPLIER + 0.5)) # 최소 임계치 이상
        likes = int(likes * random.uniform(FLAME_THRESHOLD_MULTIPLIER, FLAME_THRESHOLD_MULTIPLIER + 0.5))
        comments = int(comments * random.uniform(FLAME_THRESHOLD_MULTIPLIER, FLAME_THRESHOLD_MULTIPLIER + 0.5))
        print(f"[SIMULATION] 채널 '{channel_name}'에서 \ud83d\udd25 불꽃 영상 발생 확률! \ud83d\udd25")

    return views, likes, comments, is_flame

def save_flame_data(data):
    """'불꽃' 영상 데이터를 CSV 파일에 추가합니다."""
    file_exists = os.path.exists(FLAME_DATA_FILE)
    try:
        with open(FLAME_DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
            fieldnames = [
                'timestamp', 'channel_name', 'simulated_views', 'simulated_likes', 'simulated_comments',
                'avg_views', 'avg_likes', 'avg_comments'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists: # 파일이 없으면 헤더를 작성합니다.
                writer.writeheader()

            writer.writerow(data)
        print(f"[INFO] 불꽃 영상 데이터가 '{FLAME_DATA_FILE}'에 기록되었습니다.")
    except IOError as e:
        print(f"[ERROR] 불꽃 영상 데이터 저장 실패 ('{FLAME_DATA_FILE}'): {e}")

# --- Main Execution Script 메인 실행 스크립트 ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ReelRush Radar: 숏폼/릴 영상의 초기 성능을 시뮬레이션하고 '불꽃' 영상을 감지합니다."
    )
    parser.add_argument(
        "--channels", 
        type=str,
        help="과거 채널 데이터가 포함된 CSV 파일의 경로. 예: your_channels.csv"
    )
    args = parser.parse_args()

    print(f"\n--- ReelRush Radar 시뮬레이션 시작 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")

    # 채널 데이터 로드
    channels_data = load_channels_data(args.channels)

    if not channels_data:
        print("[CRITICAL] 시뮬레이션할 채널 데이터가 없습니다. 프로그램을 종료합니다.")
        _sys.exit(1)

    print("\n[PROGRESS] 각 채널의 새 영상 성능을 시뮬레이션합니다...")
    for channel_name, avg_data in channels_data.items():
        print(f"\n--- 채널: {channel_name} ---")
        print(f"  평균 성능: 조회수 {avg_data['avg_views']:,}, 좋아요 {avg_data['avg_likes']:,}, 댓글 {avg_data['avg_comments']:,}")

        sim_views, sim_likes, sim_comments, is_flame = simulate_new_video_performance(channel_name, avg_data)

        if is_flame:
            alert_message = (
                f"채널 '{channel_name}'에서 \ud83d\udd25 불꽃 영상 감지! \ud83d\udd25\n" +
                f"초기 예상 성능: 조회수 {sim_views:,}, 좋아요 {sim_likes:,}, 댓글 {sim_comments:,}\n" +
                f"평균 대비 {FLAME_THRESHOLD_MULTIPLIER:.1f}배 이상 달성!"
            )
            print(f"[ALERT] {alert_message}")
            send_slack_notification(alert_message)

            # 불꽃 영상 데이터를 기록합니다.
            flame_record = {
                'timestamp': datetime.now().isoformat(),
                'channel_name': channel_name,
                'simulated_views': sim_views,
                'simulated_likes': sim_likes,
                'simulated_comments': sim_comments,
                'avg_views': avg_data['avg_views'],
                'avg_likes': avg_data['avg_likes'],
                'avg_comments': avg_data['avg_comments']
            }
            save_flame_data(flame_record)
        else:
            print(
                f"[SIMULATION] 채널 '{channel_name}'의 새 영상 (일반):\n" +
                f"  초기 예상 성능: 조회수 {sim_views:,}, 좋아요 {sim_likes:,}, 댓글 {sim_comments:,}"
            )
        time.sleep(0.5) # 시뮬레이션 진행 상황을 보기 위한 짧은 지연

    print(f"\n--- ReelRush Radar 시뮬레이션 완료 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")

