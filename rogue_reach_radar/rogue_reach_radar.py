# [환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
# UnicodeEncodeError로 인해 프로그램이 비정상 종료되는 것을 방지합니다. 삭제하지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import csv
import argparse
import os
import datetime
import statistics
import requests

# --- 전역 설정 상수 ---
# 이전 게시물 평균 대비 도달/참여율이 이 비율 이하로 떨어지면 이상 징후로 간주합니다.
DEFAULT_THRESHOLD_PERCENTAGE = 0.60
# 이동 평균을 계산할 때 고려할 이전 게시물의 수입니다.
LOOKBACK_WINDOW = 5
# Slack/Discord 웹훅 URL 환경 변수입니다. 실제 알림을 받으려면 설정하세요.
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "YOUR_SLACK_WEBHOOK_URL_HERE")
# 이상 징후 보고서를 저장할 디렉토리입니다.
REPORT_DIR = "reports"
# Slack/Discord 알림에 사용될 서비스명 (선택 사항)
SERVICE_NAME = "Rogue Reach Radar"

def load_data(filepath: str) -> list | None:
    """지정된 CSV 파일에서 게시물 데이터를 로드합니다.

    Args:
        filepath: CSV 파일의 경로.

    Returns:
        게시물 데이터 딕셔너리 리스트 또는 오류 발생 시 None.
    """
    posts = []
    print(f"[INFO] 데이터 파일 '{filepath}' 로드를 시작합니다.")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2): # 헤더 제외하고 2번째 줄부터 계산
                try:
                    row['reach'] = int(row.get('reach', 0))
                    row['likes'] = int(row.get('likes', 0))
                    row['comments'] = int(row.get('comments', 0))
                    # 필수 필드 검증 (예: post_id, timestamp) - 필요 시 추가
                    if not all(k in row for k in ['post_id', 'timestamp', 'platform']):
                        print(f"[WARNING] {filepath}:{row_num} 줄: 필수 필드 누락 (post_id, timestamp, platform). 이 행을 건너뜁니다: {row}")
                        continue
                    posts.append(row)
                except (ValueError, TypeError) as e:
                    print(f"[WARNING] {filepath}:{row_num} 줄: 데이터 변환 오류 발생. 이 행을 건너뜁니다: {row} - {e}")
                except Exception as e:
                    print(f"[WARNING] {filepath}:{row_num} 줄: 알 수 없는 오류 발생. 이 행을 건너뜁니다: {row} - {e}")
        print(f"[INFO] '{filepath}' 파일에서 총 {len(posts)}개의 게시물을 성공적으로 로드했습니다.")
        return posts
    except FileNotFoundError:
        print(f"[ERROR] 파일을 찾을 수 없습니다: '{filepath}'. 경로를 확인해주세요.")
        return None
    except Exception as e:
        print(f"[ERROR] 데이터 로드 중 예상치 못한 오류가 발생했습니다: {e}")
        return None

def generate_mock_data() -> list:
    """데모 목적을 위한 샘플 데이터를 생성합니다.

    Returns:
        샘플 게시물 데이터 딕셔너리 리스트.
    """
    print("[INFO] CSV 파일이 제공되지 않았습니다. 데모를 위한 샘플 데이터를 생성합니다.")
    print("      자신의 데이터를 사용하려면: 'python rogue_reach_radar.py --file your_data.csv'\n")
    return [
        {"post_id": "p001", "timestamp": "2023-10-01 10:00:00", "platform": "Instagram", "reach": 1200, "likes": 150, "comments": 20},
        {"post_id": "p002", "timestamp": "2023-10-02 11:00:00", "platform": "Instagram", "reach": 1150, "likes": 145, "comments": 22},
        {"post_id": "p003", "timestamp": "2023-10-03 12:00:00", "platform": "Instagram", "reach": 1300, "likes": 160, "comments": 25},
        {"post_id": "p004", "timestamp": "2023-10-04 13:00:00", "platform": "Instagram", "reach": 1250, "likes": 155, "comments": 23},
        {"post_id": "p005", "timestamp": "2023-10-05 14:00:00", "platform": "Instagram", "reach": 1100, "likes": 140, "comments": 21},
        {"post_id": "p006", "timestamp": "2023-10-06 15:00:00", "platform": "Instagram", "reach": 300, "likes": 50, "comments": 5}, # 이상 징후
        {"post_id": "p007", "timestamp": "2023-10-07 16:00:00", "platform": "Instagram", "reach": 1200, "likes": 140, "comments": 20},
        {"post_id": "p008", "timestamp": "2023-10-08 17:00:00", "platform": "Instagram", "reach": 1180, "likes": 138, "comments": 19},
        {"post_id": "p009", "timestamp": "2023-10-09 18:00:00", "platform": "Instagram", "reach": 400, "likes": 30, "comments": 2}  # 또 다른 이상 징후
    ]

def detect_anomalies(posts: list, threshold_percentage: float, lookback_window: int) -> list:
    """게시물의 도달률 및 참여도에서 이상 징후를 감지합니다.

    Args:
        posts: 게시물 데이터 딕셔너리 리스트.
        threshold_percentage: 평균 대비 이상 징후로 간주할 하락 비율 (예: 0.60).
        lookback_window: 이동 평균을 계산할 이전 게시물의 수.

    Returns:
        감지된 이상 징후 딕셔너리 리스트.
    """
    anomalies = []
    if len(posts) < lookback_window:
        print(f"[INFO] 이동 평균 계산을 위한 데이터가 충분하지 않습니다 (현재 {len(posts)}개, 최소 {lookback_window}개 필요). 이상 징후 감지를 건너뜁니다.")
        return anomalies

    print(f"[INFO] {LOOKBACK_WINDOW}개의 게시물 이동 평균 기준으로 이상 징후를 감지합니다 (임계값: {threshold_percentage*100:.0f}%).")
    for i in range(lookback_window, len(posts)):
        current_post = posts[i]
        recent_posts = posts[i-lookback_window:i]

        try:
            avg_reach = statistics.mean([p['reach'] for p in recent_posts])
            avg_likes = statistics.mean([p['likes'] for p in recent_posts])
            avg_comments = statistics.mean([p['comments'] for p in recent_posts])
        except statistics.StatisticsError:
            print(f"[WARNING] {current_post.get('post_id', 'Unknown')} 게시물 주변에서 통계 계산 오류 발생. 해당 게시물 건너뜁니다.")
            continue

        is_reach_anomaly = current_post['reach'] < avg_reach * threshold_percentage
        is_likes_anomaly = current_post['likes'] < avg_likes * threshold_percentage
        is_comments_anomaly = current_post['comments'] < avg_comments * threshold_percentage

        if is_reach_anomaly or is_likes_anomaly or is_comments_anomaly:
            potential_causes = []
            if is_reach_anomaly: potential_causes.append("도달률 급락")
            if is_likes_anomaly: potential_causes.append("좋아요 급락")
            if is_comments_anomaly: potential_causes.append("댓글 급락")
            potential_causes_str = "; ".join(potential_causes) + ". (가능성: 섀도우밴, 알고리즘 변경, 플랫폼 일시적 문제, 콘텐츠 매력도 하락)"
            
            anomalies.append({
                "post_id": current_post['post_id'],
                "timestamp": current_post['timestamp'],
                "platform": current_post['platform'],
                "current_reach": current_post['reach'],
                "avg_reach_prev": round(avg_reach, 2),
                "current_likes": current_post['likes'],
                "avg_likes_prev": round(avg_likes, 2),
                "current_comments": current_post['comments'],
                "avg_comments_prev": round(avg_comments, 2),
                "reason": potential_causes_str
            })
            print(f"[ALERT] 이상 징후 감지! Post ID: {current_post['post_id']} - 이유: {potential_causes_str.split('.')[0]}")
    print(f"[INFO] 총 {len(anomalies)}개의 이상 징후가 감지되었습니다.")
    return anomalies

def send_notification(message: str) -> None:
    """Slack/Discord 웹훅 URL이 설정된 경우 알림을 전송합니다.

    Args:
        message: 전송할 알림 메시지 문자열.
    """
    if SLACK_WEBHOOK_URL and SLACK_WEBHOOK_URL != "YOUR_SLACK_WEBHOOK_URL_HERE":
        try:
            headers = {'Content-type': 'application/json'}
            payload = {'text': message}
            response = requests.post(SLACK_WEBHOOK_URL, json=payload, headers=headers, timeout=10)
            response.raise_for_status() # HTTP 오류가 발생하면 예외 발생
            print("[INFO] 이상 징후 알림을 웹훅으로 성공적으로 전송했습니다.")
        except requests.exceptions.Timeout:
            print(f"[ERROR] 웹훅 알림 전송 시간 초과 (10초).")
        except requests.exceptions.ConnectionError as e:
            print(f"[ERROR] 웹훅 서버 연결 오류 발생: {e}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 웹훅으로 알림 전송 실패: {e}")
    else:
        print("[INFO] 웹훅 URL이 설정되지 않았습니다. 알림이 전송되지 않습니다.")

def generate_report(anomalies: list, report_filepath: str) -> None:
    """감지된 이상 징후에 대한 텍스트 보고서를 생성합니다.

    Args:
        anomalies: 감지된 이상 징후 딕셔너리 리스트.
        report_filepath: 보고서를 저장할 파일 경로.
    """
    try:
        os.makedirs(REPORT_DIR, exist_ok=True)
        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write(f"{SERVICE_NAME} 이상 징후 보고서 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("--------------------------------------------------------------------------------\n\n")
            if not anomalies:
                f.write("이번 실행에서는 중요한 이상 징후가 감지되지 않았습니다.\n")
            else:
                for anomaly in anomalies:
                    f.write(f"[이상 징후] 게시물 ID: {anomaly['post_id']} (플랫폼: {anomaly['platform']})\n")
                    f.write(f"  시간: {anomaly['timestamp']}\n")
                    f.write(f"  현재 도달률: {anomaly['current_reach']} (이전 평균: {anomaly['avg_reach_prev']})\n")
                    f.write(f"  현재 좋아요: {anomaly['current_likes']} (이전 평균: {anomaly['avg_likes_prev']})\n")
                    f.write(f"  현재 댓글: {anomaly['current_comments']} (이전 평균: {anomaly['avg_comments_prev']})\n")
                    f.write(f"  잠재적 원인: {anomaly['reason']}\n\n")
        print(f"[INFO] 이상 징후 보고서가 '{report_filepath}'에 성공적으로 저장되었습니다.")
    except IOError as e:
        print(f"[ERROR] 보고서 파일 생성 또는 쓰기 오류 발생: {e}")
    except Exception as e:
        print(f"[ERROR] 보고서 생성 중 예상치 못한 오류 발생: {e}")

def main():
    """스크립트의 메인 실행 함수입니다."""
    parser = argparse.ArgumentParser(
        description=f"{SERVICE_NAME}: 소셜 미디어 게시물의 도달률 및 참여도 비정상적인 하락을 감지합니다."
    )
    parser.add_argument(
        '--file', type=str, help="소셜 미디어 게시물 데이터가 포함된 CSV 파일의 경로입니다."
    )
    args = parser.parse_args()

    print(f"\n--- {SERVICE_NAME} 시작 ---")
    posts = []
    if args.file:
        posts = load_data(args.file)
        if not posts:
            print("[ERROR] 데이터 로드 실패. 스크립트를 종료합니다.")
            return # 파일 로드 실패 시 즉시 종료
    else:
        posts = generate_mock_data()
    
    if not posts:
        print("[ERROR] 처리할 데이터가 없습니다. 스크립트를 종료합니다.")
        return

    print("[INFO] 이상 징후 감지 분석을 시작합니다...")
    anomalies = detect_anomalies(posts, DEFAULT_THRESHOLD_PERCENTAGE, LOOKBACK_WINDOW)

    current_time_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"anomaly_report_{current_time_str}.txt"
    report_filepath = os.path.join(REPORT_DIR, report_filename)
    generate_report(anomalies, report_filepath)

    if anomalies:
        print("\n[ALERT] 이상 징후가 감지되었습니다! 보고서와 알림을 확인해주세요.\n")
        alert_message = f"{SERVICE_NAME}: 총 {len(anomalies)}개의 이상 징후가 감지되었습니다. 보고서: {report_filename}\n"
        for anomaly in anomalies:
            alert_message += (
                f"- Post ID: {anomaly['post_id']} ({anomaly['platform']}) - "
                f"도달률: {anomaly['current_reach']}/{anomaly['avg_reach_prev']} - "
                f"주요 원인: {anomaly['reason'].split('.')[0].strip()}\n"
            )
        send_notification(alert_message.strip())
    else:
        print("[INFO] 이번 실행에서는 이상 징후가 감지되지 않았습니다.")

    print("\n[INFO] 스크립트가 완료되었습니다. 매일 실행하려면 cron (Linux/macOS) 또는 작업 스케줄러 (Windows)에 등록하세요.\n       예시: '0 9 * * * python /path/to/rogue_reach_radar.py --file /path/to/your_data.csv' (매일 오전 9시 실행)")
    print(f"--- {SERVICE_NAME} 종료 ---\n")

if __name__ == '__main__':
    main()