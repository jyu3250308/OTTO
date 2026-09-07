# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서 UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import requests
import time
import os
from datetime import datetime
import csv

# --- 전역 상수 및 설정 --- #
SATURATION_THRESHOLD = 50       # 키워드 출현 빈도 포화 임계치. 이 값 이상이면 포화로 간주.
DECREASE_FACTOR_THRESHOLD = 0.8 # 관심도 감소 임계치. 이전 평균 대비 80% 미만일 경우 감소로 간주.
OUTPUT_REPORT_FILE = "niche_pulse_sentinel_report.csv" # 분석 보고서 파일명
HISTORY_FILE = "niche_pulse_history.csv"             # 키워드 출현 이력 저장 파일명
REQUEST_TIMEOUT = 10                                 # HTTP 요청 타임아웃 (초)

def _log_message(message: str):
    """타임스탬프와 함께 콘솔에 메시지를 출력합니다."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def fetch_content_for_keywords(keywords: list[str], source_url: str = None, source_file: str = None) -> dict:
    """지정된 키워드에 대해 웹 페이지 또는 로컬 파일에서 콘텐츠를 가져와 키워드 빈도를 계산합니다.
    데이터 소스가 없거나 실패할 경우, 데모용 샘플 데이터를 사용합니다."""
    _log_message(f"🔍 '{', '.join(keywords)}' 키워드에 대한 콘텐츠를 가져오는 중...")
    text_content = ""
    source_type = ""

    if source_url:
        source_type = "URL"
        _log_message(f"🌐 URL '{source_url}'에서 콘텐츠 요청 시도...")
        try:
            response = requests.get(source_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status() # HTTP 오류 발생 시 예외 발생 (4xx, 5xx)
            text_content = response.text.lower()
            _log_message(f"✅ URL '{source_url}'에서 콘텐츠를 성공적으로 가져왔습니다.")
        except requests.exceptions.Timeout:
            _log_message(f"❌ 오류: URL '{source_url}' 요청 시간 초과. 샘플 데이터로 대체합니다.")
        except requests.exceptions.RequestException as e:
            _log_message(f"❌ 오류: URL '{source_url}'에서 콘텐츠를 가져오는 중 문제가 발생했습니다: {e}. 샘플 데이터로 대체합니다.")
    elif source_file:
        source_type = "File"
        _log_message(f"📄 로컬 파일 '{source_file}'에서 콘텐츠 읽기 시도...")
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                text_content = f.read().lower()
            _log_message(f"✅ 로컬 파일 '{source_file}'에서 콘텐츠를 성공적으로 읽었습니다.")
        except FileNotFoundError:
            _log_message(f"❌ 오류: 파일 '{source_file}'을(를) 찾을 수 없습니다. 샘플 데이터로 대체합니다.")
        except IOError as e:
            _log_message(f"❌ 오류: 파일 '{source_file}'을(를) 읽는 중 문제가 발생했습니다: {e}. 샘플 데이터로 대체합니다.")

    if not text_content: # 데이터 소스가 없거나 실패한 경우, 데모 데이터를 사용
        source_type = "Mock Data"
        _log_message("⚠️ 데이터 소스(URL/파일)가 없거나 실패하여 데모용 샘플 데이터를 사용합니다. 본인 데이터를 사용하려면 `--url <URL>` 또는 `--file <경로>` 인자를 지정하세요.")
        # 실제와 유사한 샘플 데이터
        text_content = "the latest trend is ai art, everyone is talking about ai. ai is everywhere. but now, crypto is back! crypto trading, crypto news, crypto updates! blockchain technology is also seeing a resurgence. ai and blockchain will dominate. metaverse is quiet, but vr technology is still growing. ai art is getting saturated, too much ai art. people are tired of ai art. the new wave is green tech solutions. sustainable energy is the future. quantum computing is still a niche but growing rapidly."

    content_counts = {keyword.lower(): text_content.count(keyword.lower()) for keyword in keywords}
    _log_message(f"✅ 키워드 빈도 계산 완료 (데이터 소스: {source_type}).")
    return content_counts

def load_history() -> dict[str, list[dict]]:
    """이력 파일에서 키워드별 과거 데이터를 로드합니다."""
    history = {}
    if not os.path.exists(HISTORY_FILE):
        _log_message(f"ℹ️ 이력 파일 '{HISTORY_FILE}'이(가) 존재하지 않습니다. 새로 생성합니다.")
        return history

    _log_message(f"📂 이력 파일 '{HISTORY_FILE}' 로드 시도...")
    try:
        with open(HISTORY_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 필요한 필드가 모두 있는지 확인
                if 'keyword' in row and 'timestamp' in row and 'count' in row:
                    keyword = row['keyword'].lower()
                    history.setdefault(keyword, []).append({'timestamp': row['timestamp'], 'count': int(row['count'])})
                else:
                    _log_message(f"⚠️ 이력 파일 '{HISTORY_FILE}'의 한 행이 유효하지 않습니다. 스킵: {row}")
        _log_message(f"✅ 이력 파일 '{HISTORY_FILE}'에서 데이터를 성공적으로 로드했습니다.")
    except (FileNotFoundError, IOError, ValueError, KeyError) as e:
        _log_message(f"❌ 경고: 이력 파일 '{HISTORY_FILE}' 로드 중 오류 발생: {e}. 기존 이력은 무시하고 새로 시작합니다.")
        history = {} # 오류 발생 시 이력을 초기화하여 새롭게 시작
    return history

def save_history(history: dict[str, list[dict]], current_data: dict[str, int]):
    """현재 키워드 빈도를 이력에 추가하고 파일에 저장합니다."""
    _log_message(f"💾 이력 파일 '{HISTORY_FILE}'에 현재 데이터를 저장하는 중...")
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for keyword, count in current_data.items():
        history.setdefault(keyword, []).append({'timestamp': current_timestamp, 'count': count})

    try:
        with open(HISTORY_FILE, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['timestamp', 'keyword', 'count']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for keyword, data_list in history.items():
                for data_entry in data_list:
                    # 데이터 무결성 검증: 필요한 키가 모두 있는지 확인
                    if all(k in data_entry for k in ['timestamp', 'count']):
                        writer.writerow({'timestamp': data_entry['timestamp'], 'keyword': keyword, 'count': data_entry['count']})
                    else:
                        _log_message(f"⚠️ 이력 데이터 '{keyword}'의 한 항목이 유효하지 않습니다. 스킵: {data_entry}")
        _log_message(f"✅ 이력 파일 '{HISTORY_FILE}'에 데이터 저장을 완료했습니다.")
    except IOError as e:
        _log_message(f"❌ 오류: 이력 파일 '{HISTORY_FILE}' 저장 중 문제가 발생했습니다: {e}.")

def analyze_niche_pulse(current_counts: dict[str, int], history: dict[str, list[dict]]) -> list[dict]:
    """키워드별 틈새시장(niche)의 동향(pulse)을 분석합니다."""
    _log_message("📊 키워드 틈새시장 동향 분석 시작...")
    analysis_results = []
    for keyword, current_count in current_counts.items():
        status = "안정 (Stable)"
        # 해당 키워드의 과거 출현 횟수만 필터링
        historical_counts = [entry['count'] for entry in history.get(keyword, []) if 'count' in entry]
        # 과거 데이터가 있는 경우 평균 계산, 없는 경우 0
        avg_historical_count = sum(historical_counts) / len(historical_counts) if historical_counts else 0

        if current_count >= SATURATION_THRESHOLD:
            status = "포화 (Saturated)"
            _log_message(f"  -> '{keyword}': 현재 {current_count}회 (포화 임계치 {SATURATION_THRESHOLD}회 이상)")
        elif avg_historical_count > 0 and current_count < avg_historical_count * DECREASE_FACTOR_THRESHOLD:
            status = "관심도 감소 (Decreasing)"
            _log_message(f"  -> '{keyword}': 현재 {current_count}회 (이전 평균 {avg_historical_count:.2f}회 대비 {DECREASE_FACTOR_THRESHOLD*100:.0f}% 미만)")
        elif current_count > avg_historical_count:
            status = "관심도 상승 (Rising)"
            _log_message(f"  -> '{keyword}': 현재 {current_count}회 (이전 평균 {avg_historical_count:.2f}회 대비 상승)")
        else:
             _log_message(f"  -> '{keyword}': 현재 {current_count}회 (이전 평균 {avg_historical_count:.2f}회)")

        analysis_results.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'keyword': keyword,
            'current_count': current_count,
            'historical_average': round(avg_historical_count, 2),
            'status': status
        })
    _log_message("✅ 키워드 틈새시장 동향 분석 완료.")
    return analysis_results

def generate_report(results: list[dict]):
    """분석 결과를 CSV 보고서 파일로 생성합니다."""
    _log_message(f"📄 분석 보고서 '{OUTPUT_REPORT_FILE}' 생성 중...")
    if not results:
        _log_message("ℹ️ 보고서로 작성할 분석 결과가 없습니다.")
        return

    try:
        with open(OUTPUT_REPORT_FILE, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['timestamp', 'keyword', 'current_count', 'historical_average', 'status']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        _log_message(f"✅ 보고서 '{OUTPUT_REPORT_FILE}'를 성공적으로 생성했습니다.")
    except IOError as e:
        _log_message(f"❌ 오류: 보고서 파일 '{OUTPUT_REPORT_FILE}' 저장 중 문제가 발생했습니다: {e}.")

def main():
    """Niche Pulse Sentinel 프로그램의 메인 함수."""
    _log_message("🚀 Niche Pulse Sentinel 프로그램 시작.")
    parser = argparse.ArgumentParser(description="키워드 트렌드를 분석하여 틈새시장 동향을 감지합니다.")
    parser.add_argument('-k', '--keywords', type=str, required=True,
                        help="분석할 키워드를 쉼표로 구분하여 입력하세요 (예: 'AI art,crypto,blockchain').")
    parser.add_argument('-u', '--url', type=str, default=None,
                        help="콘텐츠를 가져올 웹 페이지 URL.")
    parser.add_argument('-f', '--file', type=str, default=None,
                        help="콘텐츠를 가져올 로컬 파일 경로.")
    
    args = parser.parse_args()

    keywords_list = [k.strip() for k in args.keywords.split(',') if k.strip()]
    if not keywords_list:
        _log_message("❌ 오류: 분석할 키워드가 제공되지 않았습니다. -k 또는 --keywords 옵션을 사용하세요.")
        _sys.exit(1) # 치명적 오류로 프로그램 종료

    _log_message(f"🎯 분석 대상 키워드: {', '.join(keywords_list)}")

    # 1. 콘텐츠 가져오기 및 키워드 빈도 계산
    current_keyword_counts = fetch_content_for_keywords(keywords_list, args.url, args.file)
    if not current_keyword_counts:
        _log_message("❌ 오류: 키워드 빈도를 계산할 콘텐츠를 가져오지 못했습니다. 프로그램을 종료합니다.")
        _sys.exit(1)

    # 2. 이력 데이터 로드 및 현재 데이터 저장
    history_data = load_history()
    save_history(history_data, current_keyword_counts)

    # 3. 틈새시장 동향 분석
    analysis_results = analyze_niche_pulse(current_keyword_counts, history_data)

    # 4. 보고서 생성
    generate_report(analysis_results)

    _log_message("👋 Niche Pulse Sentinel 프로그램 종료.")

if __name__ == '__main__':
    main()
