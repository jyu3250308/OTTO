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
from datetime import datetime

# --- Constants and Default Values ---
DEFAULT_GROWTH_THRESHOLD = 20  # Percentage increase required for 'rapid growth'
DEFAULT_DECLINE_THRESHOLD = 20 # Absolute percentage decrease required for 'sudden decline'
OUTPUT_REPORT_PREFIX = "trend_report_"

# --- Helper Functions ---
def load_trend_data(filepath: str) -> list:
    """지정된 CSV 파일에서 트렌드 데이터를 로드합니다.

    CSV는 'Topic', 'Current Mentions', 'Previous Mentions' 컬럼을 포함해야 합니다.
    잘못된 형식의 행은 건너뛰고 오류를 로깅합니다.
    """
    topics = []
    print(f"[INFO] 데이터 파일 로딩 중: '{filepath}'")
    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            line_num = 1
            for row in reader:
                line_num += 1
                try:
                    topic = row['Topic']
                    current_mentions = int(row['Current Mentions'])
                    previous_mentions = int(row['Previous Mentions'])
                    topics.append({"topic": topic, "current": current_mentions, "previous": previous_mentions})
                except (ValueError, KeyError) as e:
                    print(f"[WARNING] {filepath} 파일의 {line_num}번째 행 처리 중 오류 발생: {row}. 오류: {e}. 해당 행을 건너뜁니다.")
    except FileNotFoundError:
        print(f"[ERROR] 데이터 파일을 찾을 수 없습니다: '{filepath}'. 경로를 확인해 주세요.")
        return []
    except Exception as e:
        print(f"[ERROR] 데이터 파일 '{filepath}'을(를) 읽는 데 실패했습니다: {e}")
        return []
    print(f"[INFO] '{filepath}'에서 총 {len(topics)}개의 데이터 항목을 성공적으로 로드했습니다.")
    return topics

def generate_synthetic_data() -> list:
    """데모를 위해 합성(가상) 트렌드 데이터를 생성합니다."""
    print("[INFO] 데이터 파일이 제공되지 않거나 유효하지 않아 샘플 데이터를 생성합니다.")
    print("[INFO] 본인 파일을 사용하려면: python trend_tide_sentinel.py --data-file your_data.csv")
    return [
        {"topic": "AI Ethics", "current": 1200, "previous": 1000}, # 성장 20%
        {"topic": "Quantum Computing", "current": 550, "previous": 600}, # 감소 ~8.3%
        {"topic": "Metaverse", "current": 300, "previous": 1500}, # 감소 80%
        {"topic": "Web3 Gaming", "current": 800, "previous": 600}, # 성장 33.3%
        {"topic": "Sustainable Tech", "current": 720, "previous": 700} # 성장 ~2.8%
    ]

def analyze_trends(trend_data: list, growth_threshold: int, decline_threshold: int) -> list:
    """트렌드를 분석하고 급격한 성장 또는 갑작스러운 감소를 감지합니다."""
    alerts = []
    print(f"[INFO] 총 {len(trend_data)}개 항목에 대해 트렌드 분석을 시작합니다.")
    for item in trend_data:
        topic = item["topic"]
        current = item["current"]
        previous = item["previous"]

        change_percent = 0.0
        if previous == 0:
            if current > 0:
                change_percent = float('inf') # 이전 언급이 0에서 증가 시 무한 성장
            # current도 0이면 change_percent는 0으로 유지
        else:
            change_percent = ((current - previous) / previous) * 100

        if change_percent >= growth_threshold:
            alert_msg = f"[ALERT: 급격한 성장] '{topic}' 관심도가 {previous}에서 {current}로 {change_percent:.2f}% 급증했습니다."
            alerts.append(alert_msg)
            print(alert_msg)
        elif change_percent <= -decline_threshold:
            alert_msg = f"[ALERT: 갑작스러운 감소] '{topic}' 관심도가 {previous}에서 {current}로 {-change_percent:.2f}% 급감했습니다."
            alerts.append(alert_msg)
            print(alert_msg)
        else:
            print(f"[INFO] '{topic}': 변화율 {change_percent:.2f}% (정상 범위). 현재: {current}, 이전: {previous}")
    print(f"[INFO] 트렌드 분석 완료. 총 {len(alerts)}개의 경고가 감지되었습니다.")
    return alerts

def save_report(alerts: list, filename: str):
    """트렌드 분석 보고서를 텍스트 파일로 저장합니다."""
    print(f"[INFO] 분석 보고서를 '{filename}'에 저장 중입니다.")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"TrendTide Sentinel Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            if alerts:
                for alert in alerts:
                    f.write(alert + "\n")
            else:
                f.write("중요한 트렌드 변화가 감지되지 않았습니다.\n")
            f.write("\n" + "=" * 60 + "\n")
            f.write("TrendTide Sentinel에 의해 생성된 보고서.\n")
        print(f"[SUCCESS] 트렌드 보고서가 '{filename}'에 성공적으로 저장되었습니다.")
    except IOError as e:
        print(f"[ERROR] 보고서 '{filename}' 저장에 실패했습니다: {e}")
    except Exception as e:
        print(f"[ERROR] 알 수 없는 오류로 보고서 저장에 실패했습니다: {e}")

# --- Main Function ---
def main():
    parser = argparse.ArgumentParser(
        description="TrendTide Sentinel: 토픽 관심도의 급격한 성장 또는 갑작스러운 감소를 감지합니다."
    )
    parser.add_argument(
        "--data-file",
        type=str,
        help="트렌드 데이터를 포함하는 CSV 파일 경로 (예: topic,current_mentions,previous_mentions)."
    )
    parser.add_argument(
        "--growth-threshold",
        type=int,
        default=DEFAULT_GROWTH_THRESHOLD,
        help=f"'급격한 성장'으로 플래그 지정할 백분율 증가 (기본값: {DEFAULT_GROWTH_THRESHOLD}%)."
    )
    parser.add_argument(
        "--decline-threshold",
        type=int,
        default=DEFAULT_DECLINE_THRESHOLD,
        help=f"'갑작스러운 감소'로 플래그 지정할 백분율 감소 (절대값) (기본값: {DEFAULT_DECLINE_THRESHOLD}%)."
    )

    args = parser.parse_args()

    print("\n--- TrendTide Sentinel 시작 ---")
    print(f"[설정] 성장 임계값: {args.growth_threshold}% | 감소 임계값: {args.decline_threshold}%")

    trend_data = []
    if args.data_file:
        if os.path.exists(args.data_file):
            trend_data = load_trend_data(args.data_file)
            if not trend_data:
                print("[INFO] 파일에서 유효한 데이터를 로드하지 못했습니다. 샘플 데이터를 사용합니다.")
                trend_data = generate_synthetic_data()
        else:
            print(f"[ERROR] 지정된 데이터 파일 '{args.data_file}'을(를) 찾을 수 없습니다.")
            trend_data = generate_synthetic_data()
    else:
        trend_data = generate_synthetic_data()

    if not trend_data:
        print("[CRITICAL] 분석할 데이터가 없습니다. 프로그램을 종료합니다.")
        return

    print("\n--- 트렌드 분석 실행 ---")
    alerts = analyze_trends(trend_data, args.growth_threshold, args.decline_threshold)

    output_filename = f"{OUTPUT_REPORT_PREFIX}{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    save_report(alerts, output_filename)

    print("\n--- TrendTide Sentinel 완료 ---")
    print("일상적인 모니터링을 위해 이 스크립트를 스케줄링하는 것을 고려해 보세요 (예: Linux/macOS의 cron 또는 Windows의 작업 스케줄러). ")

if __name__ == "__main__":
    main()
