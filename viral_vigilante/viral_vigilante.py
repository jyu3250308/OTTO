import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import os
import csv
import random
from datetime import datetime
import json
import requests

# --- 전역 상수 및 설정 --- #
SLACK_WEBHOOK_ENV_VAR = "SLACK_WEBHOOK_URL"
REPORT_FILENAME_PREFIX = "viral_vigilante_report_"

# 조기 사망 징후 감지 규칙 임계값
ENGAGEMENT_RATE_THRESHOLD = 0.01
NEGATIVE_COMMENT_RATIO_THRESHOLD = 0.3
SHARE_RATE_THRESHOLD = 0.001 # views 대비 공유율

def fetch_content_data(content_id: str) -> dict:
    """콘텐츠의 실시간 반응 데이터를 시뮬레이션하여 가져옵니다."""
    print(f"[INFO] 데이터 모니터링 시작: 콘텐츠 ID '{content_id}'")
    if content_id == "sample_content_123": # 데모용 폴백 데이터
        print(f"[INFO] 콘텐츠 ID '{content_id}': 샘플 데이터를 반환합니다.")
        return {
            "likes": 150, "comments": 10, "shares": 3, "views": 1200,
            "negative_comments": 4, "engagement_rate": 0.0125
        }
    else: # 실제 데이터처럼 무작위 값 시뮬레이션
        metrics = {
            "likes": random.randint(50, 500),
            "comments": random.randint(5, 50),
            "shares": random.randint(1, 15),
            "views": random.randint(1000, 10000),
            "negative_comments": random.randint(0, 10),
            "engagement_rate": round(random.uniform(0.005, 0.03), 4)
        }
        print(f"[INFO] 콘텐츠 ID '{content_id}': 시뮬레이션된 라이브 데이터를 반환합니다.")
        return metrics

def detect_early_death_signs(metrics: dict) -> tuple[bool, str]:
    """주어진 콘텐츠 지표를 분석하여 '조기 사망 징후'를 감지합니다."""
    reasons = []
    if metrics["engagement_rate"] < ENGAGEMENT_RATE_THRESHOLD:
        reasons.append(f"낮은 참여율 ({metrics['engagement_rate']:.4f} < {ENGAGEMENT_RATE_THRESHOLD})")
    
    # 댓글이 0인 경우 ZeroDivisionError 방지
    total_comments = metrics["comments"]
    if total_comments > 0 and metrics["negative_comments"] / total_comments > NEGATIVE_COMMENT_RATIO_THRESHOLD:
        reasons.append(f"부정적 댓글 비율 높음 ({metrics['negative_comments']}/{total_comments})")
    elif total_comments == 0 and metrics["negative_comments"] > 0: # 댓글은 없는데 부정적 댓글만 있는 특이 케이스
        reasons.append(f"부정적 댓글만 존재 ({metrics['negative_comments']}/{total_comments})")

    if metrics["views"] > 0 and metrics["shares"] < metrics["views"] * SHARE_RATE_THRESHOLD:
        reasons.append(f"매우 낮은 공유율 ({metrics['shares']}/{metrics['views']})")

    if reasons:
        print(f"[WARN] 조기 사망 징후 감지됨: {', '.join(reasons)}")
        return True, ", ".join(reasons)
    print("[INFO] 특별한 조기 사망 징후 감지되지 않음.")
    return False, ""

def send_alert(content_id: str, reason: str):
    """콘솔에 경고 메시지를 출력하고, 설정된 경우 Slack으로 알림을 전송합니다."""
    alert_message = f"[🚨 조기 사망 경고] 콘텐츠 ID: {content_id}. 감지된 징후: {reason}"
    print(alert_message)

    slack_webhook_url = os.getenv(SLACK_WEBHOOK_ENV_VAR)
    if slack_webhook_url and slack_webhook_url != "YOUR_SLACK_WEBHOOK_URL":
        try:
            headers = {'Content-type': 'application/json'}
            payload = {'text': alert_message}
            response = requests.post(slack_webhook_url, data=json.dumps(payload), headers=headers, timeout=5)
            response.raise_for_status() # 200번대 응답이 아니면 예외 발생
            print(f"[INFO] Slack 알림 전송 성공 (상태 코드: {response.status_code})")
        except requests.exceptions.Timeout:
            print(f"[ERROR] Slack 알림 전송 실패: 요청 시간 초과. 웹훅 URL을 확인해 주세요.")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Slack 알림 전송 실패: {e}. 웹훅 URL이나 네트워크 상태를 확인해 주세요.")
    elif slack_webhook_url == "YOUR_SLACK_WEBHOOK_URL":
        print(f"[WARN] '{SLACK_WEBHOOK_ENV_VAR}' 환경 변수가 플레이스홀더로 설정되어 Slack 알림을 보내지 않습니다. 실제 URL로 변경해 주세요.")
    else:
        print(f"[INFO] '{SLACK_WEBHOOK_ENV_VAR}' 환경 변수가 설정되지 않아 Slack 알림을 보내지 않습니다.")

def save_report(alerts: list, filename: str):
    """감지된 경고를 CSV 파일로 저장합니다."""
    file_exists = os.path.isfile(filename)
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists or os.stat(filename).st_size == 0:
                writer.writerow(["timestamp", "content_id", "is_dead", "reason"])
            for alert in alerts:
                writer.writerow(alert)
        print(f"[INFO] 분석 결과가 '{filename}'에 성공적으로 저장되었습니다.")
    except IOError as e:
        print(f"[ERROR] 보고서 파일 저장 실패 '{filename}': {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Viral Vigilante: 콘텐츠 조기 사망 경고 시스템. 소셜 콘텐츠의 초기 반응을 모니터링하여 '조기 사망' 징후를 감지합니다."
    )
    parser.add_argument(
        "--content_ids",
        nargs='*',
        default=[],
        help="모니터링할 콘텐츠 ID 목록 (공백으로 구분). 예: --content_ids video1 blogpost2"
    )
    args = parser.parse_args()

    content_ids_to_monitor = args.content_ids
    if not content_ids_to_monitor:
        content_ids_to_monitor = ["sample_content_123", "trending_video_456", "new_blog_post_789"]
        print("[INFO] 모니터링할 콘텐츠 ID가 제공되지 않아 샘플 데이터로 시연합니다.")
        print("       본인 콘텐츠를 모니터링하려면 'python viral_vigilante.py --content_ids content1 content2' 처럼 실행하세요.")
    else:
        print(f"[INFO] 총 {len(content_ids_to_monitor)}개의 콘텐츠 ID를 모니터링합니다: {', '.join(content_ids_to_monitor)}")

    detected_alerts = []
    for i, cid in enumerate(content_ids_to_monitor):
        print(f"\n[INFO] --- [{i+1}/{len(content_ids_to_monitor)}] 콘텐츠 ID '{cid}' 분석 중 ---")
        metrics = fetch_content_data(cid)
        is_dead, reason = detect_early_death_signs(metrics)
        
        timestamp = datetime.now().isoformat()
        if is_dead:
            send_alert(cid, reason)
            detected_alerts.append([timestamp, cid, "True", reason])
        else:
            print(f"[INFO] 콘텐츠 ID '{cid}'은(는) 현재까지 양호합니다.")
            detected_alerts.append([timestamp, cid, "False", ""])
    
    print("\n[INFO] 모든 콘텐츠 분석 완료. 보고서를 저장합니다.")
    report_filename = f"{REPORT_FILENAME_PREFIX}{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    save_report(detected_alerts, report_filename)
    
    print("\n[INFO] Viral Vigilante 시스템이 성공적으로 작업을 완료했습니다.")
    print("       이 봇은 매일 또는 주기적으로 실행하여 콘텐츠 반응을 지속적으로 모니터링할 수 있습니다.")
    print("       (예: Linux/macOS의 'cron' 또는 Windows의 '작업 스케줄러' 사용)")

if __name__ == "__main__":
    main()