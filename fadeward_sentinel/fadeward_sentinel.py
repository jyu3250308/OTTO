# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import os
import json
import datetime
import csv

try:
    import requests
except ImportError:
    print("경고: 'requests' 라이브러리가 설치되지 않았습니다. 알림 기능이 제한됩니다.")
    print("       pip install requests 명령어로 설치할 수 있습니다.", file=_sys.stderr)
    requests = None

def load_trend_data(filepath: str = None) -> list:
    """트렌드 데이터를 지정된 파일에서 로드하거나, 파일이 없거나 오류 발생 시 샘플 데이터를 생성합니다.

    Args:
        filepath (str, optional): 트렌드 데이터가 포함된 JSON 파일 경로. Defaults to None.

    Returns:
        list: 로드되거나 생성된 트렌드 데이터 목록.
    """
    if filepath and os.path.exists(filepath):
        print(f"[INFO] 트렌드 데이터 로드 시도: '{filepath}'")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 'history' 키가 있고 그 값이 리스트인 경우, 모든 요소를 float로 변환합니다.
            for trend in data:
                if 'history' in trend and isinstance(trend['history'], list):
                    trend['history'] = [float(x) for x in trend['history']]
                else:
                    print(f"[경고] 트렌드 '{trend.get('name', '이름 없음')}'에 유효한 'history' 데이터가 없어 건너뜁니다.", file=_sys.stderr)
            print(f"[INFO] '{filepath}'에서 {len(data)}개의 트렌드 데이터를 성공적으로 로드했습니다.")
            return data
        except FileNotFoundError:
            print(f"[오류] 지정된 트렌드 파일 '{filepath}'을 찾을 수 없습니다. 샘플 데이터로 대체합니다.", file=_sys.stderr)
        except json.JSONDecodeError as e:
            print(f"[오류] 트렌드 파일 '{filepath}'이 유효한 JSON 형식이 아닙니다: {e}. 샘플 데이터로 대체합니다.", file=_sys.stderr)
        except Exception as e:
            print(f"[오류] 트렌드 파일 로드 중 예기치 않은 오류 발생 ({filepath}): {e}. 샘플 데이터로 대체합니다.", file=_sys.stderr)

    print("[안내] 트렌드 데이터 파일을 찾을 수 없거나 로드에 실패했습니다. 샘플 데이터로 시연합니다.")
    print("       본인 파일을 사용하려면 'python fadeward_sentinel.py --trends 내트렌드.json' 명령어를 사용하세요.")
    # 샘플 데이터: 이름, 플랫폼, 최근 5일간의 참여도 점수 (0-100)
    sample_trends = [
        {"name": "AI Art Trends", "platform": "YouTube", "history": [85.0, 83.0, 80.0, 75.0, 70.0]}, # Cooling
        {"name": "Vintage Fashion", "platform": "TikTok", "history": [90.0, 92.0, 91.0, 93.0, 94.0]}, # Growing
        {"name": "Remote Work Setup", "platform": "X", "history": [70.0, 68.0, 65.0, 62.0, 58.0]}, # Cooling
        {"name": "Gaming Metaverse", "platform": "YouTube", "history": [75.0, 74.0, 73.0, 72.0, 71.0]}, # Slightly Cooling
        {"name": "Sustainable Living", "platform": "Instagram", "history": [60.0, 61.0, 62.0, 63.0, 64.0]}  # Growing
    ]
    return sample_trends

def detect_cooling_pattern(trend_history: list, lookback_days: int = 3, drop_percentage: float = 10.0) -> tuple[bool, float]:
    """
    트렌드 관심도 하락 패턴을 감지합니다.
    주어진 과거 데이터에서 최근 점수와 이전 N일 평균 점수를 비교하여 하락률을 계산합니다.

    Args:
        trend_history (list): 트렌드의 시간별 관심도 점수 목록.
        lookback_days (int): 평균을 계산할 이전 일수.
        drop_percentage (float): 냉각으로 간주할 최소 하락률 (백분율).

    Returns:
        tuple[bool, float]: 냉각 패턴 감지 여부 (True/False)와 실제 하락률.
    """
    if len(trend_history) < lookback_days + 1:
        # 충분한 과거 데이터가 없으면 감지 불가
        return False, 0.0

    current_score = trend_history[-1]
    # 현재 점수 바로 직전의 lookback_days 동안의 점수들을 가져옵니다.
    previous_scores = trend_history[-(lookback_days + 1):-1]

    # 이전 점수들의 평균을 계산합니다. 빈 리스트일 경우 0으로 나누는 오류 방지.
    if not previous_scores:
        return False, 0.0
    avg_previous_score = sum(previous_scores) / len(previous_scores)

    if avg_previous_score == 0: # 0으로 나누기 방지
        return False, 0.0

    percentage_drop = ((avg_previous_score - current_score) / avg_previous_score) * 100

    if percentage_drop >= drop_percentage:
        return True, percentage_drop
    return False, percentage_drop

def send_notification(message: str, webhook_url: str = None) -> bool:
    """콘텐츠 제작자에게 알림을 보냅니다 (Slack 또는 콘솔).

    Args:
        message (str): 전송할 알림 메시지.
        webhook_url (str, optional): Slack 웹훅 URL. 제공되지 않으면 콘솔에 출력됩니다.

    Returns:
        bool: 알림 전송 성공 여부.
    """
    if webhook_url and requests: # requests 라이브러리가 설치되어 있고 URL이 제공된 경우
        print(f"[INFO] Slack 알림 전송 시도: {message[:70]}...")
        try:
            response = requests.post(webhook_url, json={'text': message}, timeout=5)
            response.raise_for_status() # HTTP 오류 발생 시 예외 발생
            print("[알림] Slack으로 알림 전송 완료.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"[오류] Slack 알림 전송 실패: {e}", file=_sys.stderr)
            print(f"[알림] (콘솔) {message}") # Slack 실패 시 콘솔로 대체
            return False
    else:
        print("[안내] Slack 웹훅 URL이 없거나 'requests' 라이브러리가 없어 콘솔에 출력합니다.")
        print(f"[알림] (콘솔) {message}")
        return False

def save_report(filename: str, data: list, header: list) -> None:
    """감지된 냉각 트렌드 데이터를 CSV 파일로 저장합니다.

    Args:
        filename (str): 저장할 CSV 파일명.
        data (list): CSV에 기록할 한 줄의 데이터.
        header (list): CSV 파일의 헤더 (파일이 새로 생성될 때만 기록).
    """
    try:
        file_exists = os.path.exists(filename)
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists: # 파일이 없었다면 헤더를 먼저 작성
                writer.writerow(header)
            writer.writerow(data)
        print(f"[INFO] 냉각 트렌드 보고서 저장 완료: '{filename}'")
    except IOError as e:
        print(f"[오류] 보고서 파일 저장 실패 ({filename}): 입출력 오류 발생 - {e}", file=_sys.stderr)
    except Exception as e:
        print(f"[오류] 보고서 파일 저장 실패 ({filename}): 예기치 않은 오류 발생 - {e}", file=_sys.stderr)

def save_alert_log(filename: str, message: str) -> None:
    """전송된 알림 메시지를 텍스트 파일로 기록합니다.

    Args:
        filename (str): 알림 로그를 저장할 파일명.
        message (str): 기록할 알림 메시지.
    """
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] {message}\n")
        print(f"[INFO] 알림 로그 기록 완료: '{filename}'")
    except IOError as e:
        print(f"[오류] 알림 로그 저장 실패 ({filename}): 입출력 오류 발생 - {e}", file=_sys.stderr)
    except Exception as e:
        print(f"[오류] 알림 로그 저장 실패 ({filename}): 예기치 않은 오류 발생 - {e}", file=_sys.stderr)

def main():
    """Fadeward Sentinel의 메인 실행 함수. 트렌드 감지 및 알림/보고서 생성을 담당합니다."""
    parser = argparse.ArgumentParser(description="Fadeward Sentinel: 트렌드 냉각 신호 감지 및 알림.")
    parser.add_argument('--trends', type=str, help='트렌드 데이터가 포함된 JSON 파일 경로.')
    parser.add_argument('--webhook', type=str, default=os.getenv('SLACK_WEBHOOK_URL'),
                        help='알림을 보낼 Slack 웹훅 URL (환경변수 SLACK_WEBHOOK_URL 대체 가능).')
    args = parser.parse_args()

    print("─" * 40)
    print("Fadeward Sentinel (트렌드 파수꾼) 시작")
    print("─" * 40)

    trends = load_trend_data(args.trends)
    cooling_trends_detected = []
    report_header = ["Timestamp", "Trend Name", "Platform", "Last Score", "Avg Previous Score", "Drop Percentage"]
    report_filename = 'cooling_trends_report.csv'
    alert_log_filename = 'fadeward_sentinel_alerts.txt'

    if not trends:
        print("[경고] 처리할 트렌드 데이터가 없습니다. 프로그램을 종료합니다.")
        return

    print(f"[INFO] 총 {len(trends)}개의 트렌드를 모니터링합니다.")
    for i, trend in enumerate(trends, 1):
        trend_name = trend.get('name', 'Unknown Trend')
        platform = trend.get('platform', 'N/A')
        history = trend.get('history', [])

        print(f"\n[{i}/{len(trends)}] 모니터링 중: '{trend_name}' ({platform}) - 최근 관심도: {history[-1] if history else 'N/A'}")

        is_cooling, drop_percent = detect_cooling_pattern(history)

        if is_cooling:
            # 냉각 트렌드 감지 시 알림 메시지 구성 및 전송
            alert_message = (
                f"[🚨 트렌드 냉각 감지 🚨] '{trend_name}' ({platform}) 트렌드의 관심도가 식고 있습니다! "
                f"최근 {len(history) - 1}일간 평균 대비 {drop_percent:.2f}% 하락했습니다. "
                f"콘텐츠 전략 재고를 권장합니다."
            )
            print(f"[감지] {alert_message}")
            # 웹훅 URL이 없는 경우를 대비하여 플레이스홀더 사용
            send_notification(alert_message, args.webhook or 'YOUR_SLACK_WEBHOOK_URL_PLACEHOLDER')
            save_alert_log(alert_log_filename, alert_message)

            # 보고서 저장을 위한 데이터 준비
            avg_prev = sum(history[:-1]) / len(history[:-1]) if len(history) > 1 else history[-1] if history else 0.0
            cooling_trends_detected.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "name": trend_name,
                "platform": platform,
                "last_score": history[-1] if history else 0.0,
                "avg_previous_score": avg_prev,
                "drop_percentage": drop_percent
            })
        else:
            print(f"[정상] '{trend_name}' 트렌드는 안정적입니다. (하락률: {drop_percent:.2f}%)")

    if cooling_trends_detected:
        print(f"\n[결과] 총 {len(cooling_trends_detected)}개의 냉각 트렌드를 감지했습니다. 보고서에 기록합니다.")
        for ct in cooling_trends_detected:
            report_data = [
                ct['timestamp'], ct['name'], ct['platform'],
                f"{ct['last_score']:.2f}", f"{ct['avg_previous_score']:.2f}", f"{ct['drop_percentage']:.2f}"
            ]
            save_report(report_filename, report_data, report_header)
    else:
        print("\n[결과] 현재 감지된 냉각 트렌드는 없습니다.")

    print("─" * 40)
    print("Fadeward Sentinel 작업 완료.")
    print("이 봇은 매일 실행되도록 스케줄러(예: Cron)에 등록하여 사용할 수 있습니다.")
    print("─" * 40)

if __name__ == "__main__":
    main()
