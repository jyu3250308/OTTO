# -*- coding: utf-8 -*-
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
import random
import time
from datetime import datetime
import requests # Real-time data fetching (simulated for demo)

# --- Constants ---
DEMO_CONTENT_FILE = "demo_content.json"
DEFAULT_REPORT_FILE = "resurge_report.csv"

# --- Simulation Functions ---
def _simulate_historical_interactions(content_id, base_daily_avg=10, recent_spike_chance=0.1, spike_multiplier=5):
    """
    콘텐츠에 대한 7일간의 일일 상호작용 수를 시뮬레이션합니다.
    최근 스파이크 발생 가능성을 포함하여 데이터를 반환합니다.
    """
    interactions = []
    for i in range(7):
        # 평균 주변의 기본 노이즈 추가
        current_day_interactions = max(1, int(random.gauss(base_daily_avg, base_daily_avg * 0.2)))
        interactions.append(current_day_interactions)

    # 지난 2일 중 하나에 특정 확률로 스파이크 발생
    if random.random() < recent_spike_chance:
        spike_day_index = random.randint(5, 6) # 지난 이틀 중 하루
        interactions[spike_day_index] = int(interactions[spike_day_index] * spike_multiplier)
        print(f"  [SIMULATION] '{content_id}'에 대해 {spike_day_index + 1}일차에 잠재적인 스파이크를 시뮬레이션했습니다.")
    
    return interactions

def fetch_platform_mentions(content_id, platform_type="generic", api_key=None):
    """
    콘텐츠에 대한 실시간 멘션 데이터를 가져오는 것을 시뮬레이션합니다.
    실제 시나리오에서는 Reddit, Twitter 또는 뉴스 애그리게이터와 같은 API를 호출할 수 있습니다.
    데모를 위해 API 키가 제공되지 않거나 호출이 실패하면 시뮬레이션된 데이터를 사용합니다.
    """
    print(f"[INFO] '{content_id}'에 대한 '{platform_type}' 플랫폼 멘션 데이터를 가져오는 중... (API 키: {'사용' if api_key else '미사용'})")
    
    if api_key: # 실제 API 호출 시뮬레이션
        try:
            # 여기에 실제 API 호출 로직을 구현합니다.
            # 예시: response = requests.get(f"https://api.someplatform.com/mentions?q={content_id}&api_key={api_key}", timeout=5)
            #      response.raise_for_status() # HTTP 오류 발생 시 예외 발생
            #      return response.json()['data'] # 실제 데이터 반환
            print(f"[INFO] API 키가 제공되었지만, 실제 API 호출은 시뮬레이션으로 대체됩니다.")
            time.sleep(0.5) # 네트워크 지연 시뮬레이션
            return _simulate_historical_interactions(content_id, base_daily_avg=20) # API 사용 시 더 높은 기본값 시뮬레이션
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] '{content_id}'에 대한 API 호출 중 오류 발생: {e}. 시뮬레이션 데이터로 대체합니다.")
        except json.JSONDecodeError:
            print(f"[ERROR] API 응답 디코딩 실패. 시뮬레이션 데이터로 대체합니다.")
        except Exception as e:
            print(f"[ERROR] 알 수 없는 API 처리 오류: {e}. 시뮬레이션 데이터로 대체합니다.")
            
    # API 키가 없거나 API 호출 실패 시 시뮬레이션 데이터 사용
    time.sleep(0.5) # 네트워크 지연 시뮬레이션
    return _simulate_historical_interactions(content_id)

# --- Core Logic ---
def analyze_resurgence(content_info, platform_data, threshold_multiplier=2.0):
    """
    주어진 콘텐츠에 대한 플랫폼 데이터를 분석하여 재유행 패턴을 감지합니다.
    재유행이 감지되면 상세 정보를 담은 딕셔너리를 반환하고, 그렇지 않으면 None을 반환합니다.
    """
    content_id = content_info['id']
    content_title = content_info.get('title', content_id)
    keywords = content_info.get('keywords', [])

    if not platform_data or len(platform_data) < 7: # 주간 평균을 위해 최소 7일 데이터 필요
        print(f"  [WARN] '{content_title}'에 대한 데이터 부족 ({len(platform_data)}일). 분석을 건너뜀.")
        return None

    recent_interaction = platform_data[-1] # 가장 최근 날짜의 상호작용
    # 지난 날짜들의 평균 계산 (최근 하루 제외)
    past_interactions = platform_data[:-1]
    if not past_interactions:
        print(f"  [WARN] '{content_title}'의 과거 상호작용 데이터가 없어 평균을 계산할 수 없습니다. 분석을 건너뜀.")
        return None

    past_average = sum(past_interactions) / len(past_interactions)

    print(f"  - '{content_title}' 분석: 최근 일 상호작용: {recent_interaction}, 과거 평균: {past_average:.2f}")

    # 스파이크 감지 조건: 최근 상호작용이 과거 평균의 임계값 배수보다 높고, 최소 원시 상호작용 수보다 많을 때
    if recent_interaction > (past_average * threshold_multiplier) and recent_interaction > 5:
        spike_factor = recent_interaction / past_average
        print(f"[ALERT] '{content_title}' 재유행 감지! 상호작용이 평균 {past_average:.2f}에서 {recent_interaction}으로 급증 ({spike_factor:.2f}배).")
        return {
            "timestamp": datetime.now().isoformat(),
            "content_id": content_id,
            "content_title": content_title,
            "past_average_interactions": f"{past_average:.2f}",
            "current_interactions": recent_interaction,
            "spike_multiplier": f"{spike_factor:.2f}x",
            "triggering_keywords": ", ".join(keywords) if keywords else "N/A",
            "trend_analysis_note": "시뮬레이션 분석: 관련 이벤트/커뮤니티를 확인하십시오."
        }
    return None

# --- Report Generation ---
def generate_report(detected_surges, report_filepath):
    """
    감지된 재유행 이벤트를 CSV 보고서 파일에 생성하거나 추가합니다.
    """
    if not detected_surges:
        print("[INFO] 새로 보고할 재유행 이벤트가 없습니다.")
        return

    file_exists = os.path.exists(report_filepath)
    mode = 'a' if file_exists else 'w'

    try:
        with open(report_filepath, mode, encoding='utf-8', newline='') as f: # newline=''로 CSV 줄바꿈 문제 방지
            if not file_exists:
                f.write("Timestamp,Content ID,Content Title,Past Average Interactions,Current Interactions,Spike Multiplier,Triggering Keywords,Trend Analysis Note\n")

            for surge in detected_surges:
                # CSV 인코딩을 위해 필드의 콤마, 따옴표 등을 적절히 처리할 수 있지만, 여기서는 단순 문자열로 처리
                f.write(f"{surge['timestamp']},{surge['content_id']},{surge['content_title']},{surge['past_average_interactions']},{surge['current_interactions']},{surge['spike_multiplier']},{surge['triggering_keywords']},{surge['trend_analysis_note']}\n")
        print(f"[SUCCESS] '{report_filepath}'에 {len(detected_surges)}개의 새로운 재유행 이벤트를 추가하여 보고서를 업데이트했습니다.")
    except IOError as e:
        print(f"[ERROR] 보고서 파일 '{report_filepath}' 작성 중 오류 발생: {e}")
    except Exception as e:
        print(f"[ERROR] 보고서 생성 중 알 수 없는 오류 발생: {e}")

# --- Main Execution ---
def main():
    parser = argparse.ArgumentParser(
        description="Re:Surge Sentinel - 과거 콘텐츠 참여의 재유행을 감지합니다."
    )
    parser.add_argument(
        "--content-file", 
        type=str, 
        default=DEMO_CONTENT_FILE,
        help=f"과거 콘텐츠 목록이 있는 JSON 파일 경로. 기본값: {DEMO_CONTENT_FILE} (데모 데이터)."
    )
    parser.add_argument(
        "--report-file", 
        type=str, 
        default=DEFAULT_REPORT_FILE,
        help=f"재유행 보고서 CSV를 저장할 경로. 기본값: {DEFAULT_REPORT_FILE}."
    )
    parser.add_argument(
        "--threshold", 
        type=float, 
        default=2.0,
        help="경고를 트리거하는 상호작용 스파이크 배율 (예: 2.0은 200%% 증가). 기본값: 2.0."
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=os.getenv('RESURGE_API_KEY'),
        help="실제 플랫폼 통합을 위한 선택적 API 키 (예: 소셜 미디어 분석). 환경 변수 RESURGE_API_KEY 사용 가능."
    )
    args = parser.parse_args()

    print("\n--- Re:Surge Sentinel 시작 ---")
    content_list = []
    loaded_from_file = False

    # 콘텐츠 목록 로드
    if args.content_file and os.path.exists(args.content_file): # 파일이 지정되었고 존재하는 경우
        print(f"[INFO] '{args.content_file}'에서 콘텐츠 목록을 로드하는 중...")
        try:
            with open(args.content_file, 'r', encoding='utf-8') as f:
                content_list = json.load(f)
            print(f"[INFO] '{args.content_file}'에서 {len(content_list)}개의 콘텐츠 항목을 성공적으로 로드했습니다.")
            loaded_from_file = True
        except json.JSONDecodeError:
            print(f"[ERROR] '{args.content_file}' 파일에 유효하지 않은 JSON 형식이 있습니다. 샘플 데이터로 대체합니다.")
        except FileNotFoundError: # os.path.exists 체크로 대부분 방지되나, 경합 조건 대비
            print(f"[ERROR] '{args.content_file}' 파일을 찾을 수 없습니다. 샘플 데이터로 대체합니다.")
        except Exception as e:
            print(f"[ERROR] '{args.content_file}' 파일을 읽을 수 없습니다: {e}. 샘플 데이터로 대체합니다.")
    
    if not loaded_from_file or not content_list: # 파일에서 로드 실패 또는 비어있는 경우, 하드코딩된 샘플 데이터 사용
        print(f"[INFO] 유효한 콘텐츠 파일이 제공되지 않았거나 로드에 실패했습니다. 샘플 데이터로 실행합니다.\n       자신만의 데이터를 사용하려면 '{DEMO_CONTENT_FILE}' (또는 --content-file 경로 지정)를 다음과 같이 만드십시오:\n       [{{\"id\": \"my_old_post_1\", \"title\": \"나의 첫 블로그 게시물\", \"keywords\": [\"블로그\", \"스타트업\"]}}, ...].")
        content_list = [
            {"id": "article_2020_ai_future", "title": "AI가 세상을 바꿀 것 (2020년 비전)", "keywords": ["AI", "미래 기술", "예측"]},
            {"id": "video_2021_cat_vids", "title": "귀여운 고양이 영상 모음", "keywords": ["고양이", "웃긴", "바이럴"]},
            {"id": "guide_2022_diy_home", "title": "궁극의 DIY 주택 리노베이션 가이드", "keywords": ["DIY", "주택 개선", "가이드"]},
            {"id": "podcast_2019_market_trends", "title": "잊혀진 2019년 주식 시장 트렌드", "keywords": ["금융", "투자", "경제"]}
        ]
        # 사용자 참조를 위한 더미 demo_content.json 파일 생성
        if not os.path.exists(DEMO_CONTENT_FILE):
            try:
                with open(DEMO_CONTENT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(content_list, f, indent=2, ensure_ascii=False) # 한글 인코딩
                print(f"[INFO] 예제 콘텐츠 파일 '{DEMO_CONTENT_FILE}'을 생성했습니다.")
            except Exception as e:
                print(f"[WARN] 데모 콘텐츠 파일을 생성할 수 없습니다: {e}")

    detected_surges = []

    if not content_list:
        print("[ERROR] 모니터링할 콘텐츠 항목이 없습니다. 종료합니다.")
        return

    print(f"[INFO] {len(content_list)}개의 콘텐츠 항목에 대한 모니터링을 시작합니다...")
    for i, content in enumerate(content_list):
        content_title = content.get('title', content['id'])
        print(f"\n[{i+1}/{len(content_list)}] 모니터링 시작: '{content_title}' (ID: {content['id']})")
        try:
            platform_data = fetch_platform_mentions(content['id'], api_key=args.api_key)
            
            surge_event = analyze_resurgence(content, platform_data, args.threshold)
            if surge_event:
                detected_surges.append(surge_event)
        except Exception as e:
            print(f"[ERROR] '{content_title}' 분석 중 예기치 않은 오류 발생: {e}. 이 항목을 건너뜁니다.")

    generate_report(detected_surges, args.report_file)

    print("\n--- Re:Surge Sentinel 종료 ---")
    print("이 모니터를 반복적으로 (예: 매일) 실행하려면 cron (Linux/macOS) 또는 작업 스케줄러 (Windows)로 예약하는 것을 고려하십시오.")
    print(f"예시 (Linux): 0 9 * * * python3 {os.path.basename(__file__)} --report-file daily_resurge_report.csv")

if __name__ == "__main__":
    main()
