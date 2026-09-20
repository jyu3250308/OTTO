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
import csv
import datetime
import random
from collections import defaultdict

# --- Constants ---
ALERT_THRESHOLD_MULTIPLIER_REACTIONS = 2.5 # 급작스러운 인기 감지 임계치 (평균 대비 몇 배)
ALERT_THRESHOLD_MULTIPLIER_COMMENTS = 3.0  # 논쟁의 조짐 감지 임계치 (평균 대비 몇 배)
HISTORICAL_WINDOW_SIZE = 5               # 과거 데이터 비교 윈도우 크기: 최근 N개 데이터 사용

# --- Helper Functions ---
def _log(level, message):
    """일관된 로깅 형식을 위한 헬퍼 함수."""
    print(f"[{level}] {message}")

def generate_sample_data(num_entries=10, num_content_ids=3):
    """
    데모용 샘플 데이터를 생성합니다. 실제 파일이 없을 경우 사용됩니다.
    """
    _log("INFO", "샘플 데이터로 시연 중입니다.")
    _log("INFO", "본인 파일을 사용하려면 'python buzzpulse_ai.py --file 내파일.csv' 처럼 실행하세요.")
    data = []
    content_ids = [f"content_{i+1}" for i in range(num_content_ids)]
    base_reactions = {cid: random.randint(50, 200) for cid in content_ids}
    base_comments = {cid: random.randint(5, 30) for cid in content_ids}

    for i in range(num_entries):
        cid = random.choice(content_ids)
        timestamp = (datetime.datetime.now() - datetime.timedelta(hours=num_entries - i)).isoformat(timespec='minutes')
        reactions = max(1, base_reactions[cid] + random.randint(-20, 50))
        comments = max(0, base_comments[cid] + random.randint(-5, 15))

        # 가끔 급격한 변화를 넣어 시연 효과 높이기
        if i == num_entries // 2 and random.random() < 0.7:
            reactions *= random.uniform(ALERT_THRESHOLD_MULTIPLIER_REACTIONS * 0.8, ALERT_THRESHOLD_MULTIPLIER_REACTIONS * 1.5)
            comments *= random.uniform(ALERT_THRESHOLD_MULTIPLIER_COMMENTS * 0.8, ALERT_THRESHOLD_MULTIPLIER_COMMENTS * 1.5)
            _log("DEBUG", f"샘플 데이터에 {cid}의 인위적인 급증을 추가했습니다.")

        data.append({
            'content_id': cid,
            'timestamp': timestamp,
            'reactions': int(reactions),
            'comments': int(comments)
        })
    return data

def load_data_from_csv(filepath):
    """
    주어진 CSV 파일 경로에서 콘텐츠 데이터를 로드합니다.
    """
    if not os.path.exists(filepath):
        _log("ERROR", f"파일 경로를 찾을 수 없습니다: {filepath}")
        return None

    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # CSV 헤더 검증
            required_headers = ['content_id', 'timestamp', 'reactions', 'comments']
            if not all(header in reader.fieldnames for header in required_headers):
                _log("ERROR", f"CSV 파일({filepath})에 필수 헤더({', '.join(required_headers)})가 누락되었습니다.")
                return None

            for i, row in enumerate(reader):
                try:
                    data.append({
                        'content_id': row['content_id'],
                        'timestamp': row['timestamp'],
                        'reactions': int(row['reactions']),
                        'comments': int(row['comments'])
                    })
                except ValueError as ve:
                    _log("ERROR", f"CSV 파일({filepath})의 {i+2}번째 줄에서 숫자 변환 오류 발생: {ve}. 해당 줄은 건너뜁니다.")
                except KeyError as ke:
                    _log("ERROR", f"CSV 파일({filepath})의 {i+2}번째 줄에서 필수 컬럼({ke}) 누락. 해당 줄은 건너뜁니다.")

        _log("INFO", f"{len(data)}개의 콘텐츠 데이터를 {filepath}에서 로드했습니다.")
    except Exception as e:
        _log("ERROR", f"CSV 파일을 읽는 중 예상치 못한 오류 발생: {e}")
        return None
    return data

def calculate_average(values):
    """
    리스트의 평균을 계산합니다. 빈 리스트의 경우 0을 반환합니다.
    """
    if not values: 
        return 0
    return sum(values) / len(values)

# --- Main Anomaly Detection Logic ---
def detect_anomalies(current_data, historical_metrics_prev_run):
    """
    현재 데이터를 기반으로 이상 징후를 감지하고 알림을 생성합니다.
    이전 실행의 이력 데이터를 활용하여 비교합니다.
    """
    alerts = []
    historical_metrics_current_run = defaultdict(lambda: {'reactions': [], 'comments': []})

    _log("INFO", f"{len(current_data)}개 콘텐츠 데이터에 대한 이상 징후 분석을 시작합니다.")

    for item in current_data:
        content_id = item['content_id']
        current_reactions = item['reactions']
        current_comments = item['comments']
        timestamp = item['timestamp']

        # 현재 데이터를 금번 실행의 기록에 추가
        historical_metrics_current_run[content_id]['reactions'].append(current_reactions)
        historical_metrics_current_run[content_id]['comments'].append(current_comments)

        # 과거 데이터 가져오기 (이전 실행에서 축적된 데이터)
        past_reactions = historical_metrics_prev_run[content_id]['reactions'][-HISTORICAL_WINDOW_SIZE:]
        past_comments = historical_metrics_prev_run[content_id]['comments'][-HISTORICAL_WINDOW_SIZE:]

        if past_reactions and past_comments: # 충분한 과거 데이터가 있을 때만 분석
            avg_reactions = calculate_average(past_reactions)
            avg_comments = calculate_average(past_comments)

            # 급작스러운 인기 감지
            if current_reactions > avg_reactions * ALERT_THRESHOLD_MULTIPLIER_REACTIONS:
                alerts.append(f"[⭐ 인기 급증 - {content_id}] {timestamp}: 반응 {current_reactions} (평균 {avg_reactions:.1f} 대비 {current_reactions/avg_reactions:.1f}배!)")
            
            # 논쟁 조짐 감지 (댓글 급증)
            if current_comments > avg_comments * ALERT_THRESHOLD_MULTIPLIER_COMMENTS:
                alerts.append(f"[⚠️ 논쟁 조짐 - {content_id}] {timestamp}: 댓글 {current_comments} (평균 {avg_comments:.1f} 대비 {current_comments/avg_comments:.1f}배!)")

    # 다음 실행을 위해 금번 실행 데이터를 이전 데이터에 병합 (윈도우 크기 유지)
    updated_historical_metrics = defaultdict(lambda: {'reactions': [], 'comments': []}, historical_metrics_prev_run)
    for cid, metrics in historical_metrics_current_run.items():
        updated_historical_metrics[cid]['reactions'].extend(metrics['reactions'])
        updated_historical_metrics[cid]['comments'].extend(metrics['comments'])
        # 윈도우 크기를 유지하도록 오래된 데이터 제거
        updated_historical_metrics[cid]['reactions'] = updated_historical_metrics[cid]['reactions'][-HISTORICAL_WINDOW_SIZE:]
        updated_historical_metrics[cid]['comments'] = updated_historical_metrics[cid]['comments'][-HISTORICAL_WINDOW_SIZE:]
    
    return alerts, updated_historical_metrics

# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(description='BuzzPulse AI: 소셜 미디어 콘텐츠 반응 심박 감시기')
    parser.add_argument('--file', type=str, help='분석할 소셜 미디어 데이터 CSV 파일 경로 (예: data.csv)')
    args = parser.parse_args()

    _log("INFO", "🚀 BuzzPulse AI를 시작합니다...")

    # 1. 데이터 로드 (CSV 또는 샘플 데이터)
    content_data = None
    if args.file:
        _log("INFO", f"CSV 파일 '{args.file}'에서 데이터를 로드 중입니다...")
        content_data = load_data_from_csv(args.file)
        if content_data is None or not content_data:
            _log("WARNING", f"CSV 파일 로드 실패 또는 데이터 없음. 샘플 데이터를 사용합니다.")
            content_data = generate_sample_data()
    else:
        content_data = generate_sample_data()
    
    if not content_data:
        _log("ERROR", "처리할 데이터가 없습니다. 프로그램을 종료합니다.")
        return

    # 2. 과거 이력 데이터 로드 또는 초기화
    historical_data = defaultdict(lambda: {'reactions': [], 'comments': []})
    history_filepath = 'buzzpulse_history.csv'
    if os.path.exists(history_filepath):
        try:
            with open(history_filepath, 'r', encoding='utf-8') as f_hist:
                reader = csv.DictReader(f_hist)
                for i, row in enumerate(reader):
                    try:
                        cid = row['content_id']
                        historical_data[cid]['reactions'].append(int(row['reactions']))
                        historical_data[cid]['comments'].append(int(row['comments']))
                    except ValueError as ve:
                        _log("WARNING", f"이력 파일({history_filepath})의 {i+2}번째 줄에서 숫자 변환 오류: {ve}. 해당 줄 건너뜀.")
                    except KeyError as ke:
                        _log("WARNING", f"이력 파일({history_filepath})의 {i+2}번째 줄에서 필수 컬럼({ke}) 누락. 해당 줄 건너뜀.")
            _log("INFO", f"이전 이력 데이터({len(historical_data)}개 콘텐츠)를 {history_filepath}에서 로드했습니다.")
            
            # 로드된 이력 데이터도 윈도우 크기에 맞게 유지
            for cid in historical_data:
                historical_data[cid]['reactions'] = historical_data[cid]['reactions'][-HISTORICAL_WINDOW_SIZE:]
                historical_data[cid]['comments'] = historical_data[cid]['comments'][-HISTORICAL_WINDOW_SIZE:]

        except Exception as e:
            _log("WARNING", f"이력 데이터 로드 중 오류 발생: {e}. 새로운 이력으로 시작합니다.")
            historical_data = defaultdict(lambda: {'reactions': [], 'comments': []})

    # 3. 이상 감지 및 알림 생성
    _log("INFO", "🔍 콘텐츠 패턴 변화를 분석 중입니다...")
    alerts, updated_historical_data = detect_anomalies(content_data, historical_data)

    # 4. 결과 출력 및 저장
    output_filepath = 'buzzpulse_alerts.txt'
    with open(output_filepath, 'a', encoding='utf-8') as f_out:
        if alerts:
            _log("INFO", "--- 🚨 새로운 알림 감지! ---")
            for alert in alerts:
                _log("ALERT", alert)
                f_out.write(alert + '\n')
            f_out.write(f"[END] {datetime.datetime.now().isoformat()}\n\n")
            _log("INFO", f"총 {len(alerts)}개의 알림이 '{output_filepath}'에 추가되었습니다.")
        else:
            _log("INFO", "✅ 특이한 변화를 감지하지 못했습니다. 모든 것이 정상입니다.")

    # 5. 현재 데이터를 이력으로 저장 (다음 실행을 위해)
    try:
        with open(history_filepath, 'w', encoding='utf-8', newline='') as f_hist:
            writer = csv.writer(f_hist)
            writer.writerow(['content_id', 'reactions', 'comments'])
            for cid, metrics in updated_historical_data.items():
                # 윈도우 크기에 맞는 최신 데이터만 저장
                for i in range(len(metrics['reactions'])):
                    writer.writerow([cid, metrics['reactions'][i], metrics['comments'][i]])
        _log("INFO", f"현재 처리된 데이터를 '{history_filepath}'에 이력으로 저장했습니다.")
    except Exception as e:
        _log("ERROR", f"이력 데이터를 '{history_filepath}'에 저장하는 중 오류 발생: {e}")

    _log("INFO", "✨ BuzzPulse AI 분석 완료.\n")
    _log("INFO", "--- 반복 사용 가치 안내 ---")
    _log("INFO", "이 스크립트를 Crontab (Linux/macOS) 또는 작업 스케줄러 (Windows)에 등록하여 주기적으로 실행하면,")
    _log("INFO", "지속적으로 소셜 미디어 콘텐츠의 반응을 감시하고 변화를 즉시 알림 받을 수 있습니다.")
    _log("INFO", "예시 (매시간 실행): `0 * * * * /usr/bin/python3 /path/to/buzzpulse_ai.py --file /path/to/your_data.csv`")

if __name__ == '__main__':
    main()