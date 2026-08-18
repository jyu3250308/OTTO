# -*- coding: utf-8 -*-
# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 이 코드는 시스템의 기본 인코딩 설정을
#   'utf-8'로 재구성하여 문자 인코딩 오류를 방지합니다. 지우지 마세요!
import sys as _sys
import io

for _s in (_sys.stdout, _sys.stderr):
    if isinstance(_s, io.TextIOWrapper): # TextIOWrapper일 경우에만 reconfigure 적용
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass # 이미 설정되어 있거나 reconfigure를 지원하지 않는 경우 오류 무시

import argparse
import csv
import datetime
import random
import time
import os

# =============================================================================
#   [핵심 기능 1] 트렌드 데이터 수집 (실제 데이터 또는 시뮬레이션)
# =============================================================================
def fetch_trend_data(keyword: str, input_file_path: str = None) -> list:
    """지정된 키워드에 대한 트렌드 데이터를 수집합니다.
    
    인풋 파일 경로가 제공되면 해당 파일에서 키워드를 읽어 처리하고,
    없으면 주어진 단일 키워드로 시뮬레이션 데이터를 생성합니다.
    
    Args:
        keyword (str): 트렌드 데이터를 감시할 핵심 키워드.
        input_file_path (str, optional): 키워드 목록이 담긴 CSV 파일 경로.
                                        파일은 'keyword'라는 헤더를 가져야 합니다.

    Returns:
        list: 각 트렌드의 이름, 언급량, 성장률, 긍정 감성 지표를 포함하는 딕셔너리 목록.
    """
    print(f"[오또] 🔍 '{keyword}' 키워드(또는 파일로부터) 미세 트렌드 데이터를 감시 중입니다...")
    time.sleep(random.uniform(0.5, 1.5)) # API 호출 또는 데이터 처리 지연 시뮬레이션

    trends_data = []

    if input_file_path: # CSV 파일에서 키워드 목록 읽기
        try:
            with open(input_file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if 'keyword' not in reader.fieldnames:
                    print(f"[오또] ⚠️ 오류: '{input_file_path}' 파일에 'keyword' 컬럼이 없습니다. 처리 건너뜀.")
                    return []
                
                for row in reader:
                    file_keyword = row['keyword'].strip()
                    if file_keyword:
                        print(f"[오또] 📝 파일에서 '{file_keyword}' 키워드를 읽어 분석합니다.")
                        base_mentions = random.randint(300, 2000)
                        trends_data.append({
                            "name": f"파일 키워드: {file_keyword} ({random.choice(['AI 분석', '데이터 트렌드', '기술 혁신'])})",
                            "mentions": base_mentions + random.randint(-200, 200),
                            "growth_rate": random.uniform(0.05, 0.25),
                            "sentiment": random.uniform(0.6, 0.95)
                        })
            print(f"[오또] ✅ '{input_file_path}' 파일의 키워드 분석을 완료했습니다.")
            return trends_data
        except FileNotFoundError:
            print(f"[오또] ❌ 오류: '{input_file_path}' 파일을 찾을 수 없습니다. 기본 키워드로 진행합니다.")
        except Exception as e:
            print(f"[오또] ❌ 오류: '{input_file_path}' 파일 처리 중 예외 발생: {e}. 기본 키워드로 진행합니다.")
    
    # 인풋 파일이 없거나 오류 발생 시, 단일 키워드 또는 데모 데이터를 사용
    if keyword == "_DEMO_DEFAULT_": # 내부 데모 모드용 특별 키워드
        print("[오또] ✨ 데모 모드: 샘플 데이터를 사용하여 트렌드를 감지합니다.")
        trends_data = [
            {"name": "AI Chatbots for Pets", "mentions": 1200, "growth_rate": 0.15, "sentiment": 0.8},
            {"name": "Eco-friendly Home Decor", "mentions": 850, "growth_rate": 0.08, "sentiment": 0.7},
            {"name": "Virtual Reality Fitness", "mentions": 1500, "growth_rate": 0.22, "sentiment": 0.9}
        ]
    else: # 사용자 지정 키워드 시뮬레이션
        print(f"[오또] ⚙️ '{keyword}' 키워드에 대한 시뮬레이션 데이터를 생성합니다.")
        base_mentions = random.randint(300, 2000)
        trends_data = [
            {
                "name": f"신규 {keyword} 트렌드: {random.choice(['AI 아트 스타일', '에코-테크', '미래 식량'])} 예측",
                "mentions": base_mentions + random.randint(-200, 200),
                "growth_rate": random.uniform(0.05, 0.25),
                "sentiment": random.uniform(0.6, 0.95)
            }
        ]
    return trends_data

# =============================================================================
#   [핵심 기능 2] 트렌드 데이터 분석 및 예측
# =============================================================================
def analyze_trend(trend: dict) -> dict:
    """단일 트렌드를 분석하여 잠재적 영향력, 골든 타임 및 소멸 시점을 예측합니다.
    
    Args:
        trend (dict): 'name', 'mentions', 'growth_rate', 'sentiment'를 포함하는 트렌드 데이터.

    Returns:
        dict: 잠재적 파급력 점수, 골든 타임(ISO 형식), 예상 소멸 시점(ISO 형식) 정보.
    """
    print(f"[오또] 🧠 트렌드 '{trend['name']}' 상세 분석 중... (현재 언급량: {trend['mentions']})")
    
    # 잠재적 파급력 점수 계산: 언급량, 성장률, 긍정 감성 지표를 복합적으로 고려
    # 점수가 높을수록 트렌드의 영향력이 크다고 판단합니다.
    potential_score = int(trend['mentions'] * trend['growth_rate'] * trend['sentiment'] * 10)
    potential_score = max(10, min(potential_score, 10000)) # 최소 10, 최대 10000점 범위로 조정
    
    # 콘텐츠 제작 골든 타임 예측: 빠른 성장률과 높은 언급량일수록 골든 타임이 빨리 도래
    # 최소 1일 후, 최대 10일 후로 가정 (성장률에 따라 조정)
    golden_days = random.randint(3, 10) - int(trend['growth_rate'] * 10) # 성장률이 높으면 골든 타임이 더 빨리 옴
    golden_time = (datetime.date.today() + datetime.timedelta(days=max(1, golden_days)))

    # 예상 소멸 시점 예측: 트렌드의 강도(언급량)가 높으면 소멸 시점이 늦어짐
    # 골든 타임 이후 최소 7일~30일 후, 최대 90일 후로 가정
    decline_days = random.randint(30, 90) + int(trend['mentions'] / 100) # 언급량이 많으면 소멸 시점이 더 늦어짐
    decline_time = (datetime.date.today() + datetime.timedelta(days=max(golden_days + 7, decline_days)))

    print(f"[오또] ✨ '{trend['name']}' 예측 완료: 파급력 {potential_score}점, 골든 타임 {golden_time}, 소멸 시점 {decline_time}")

    return {
        "potential_score": potential_score,
        "golden_time": golden_time.isoformat(), # 국제 표준 ISO 8601 형식으로 변환
        "decline_time": decline_time.isoformat()
    }

# =============================================================================
#   [핵심 기능 3] 분석 결과 알림 메시지 생성
# =============================================================================
def send_alert(trend_name: str, analysis_result: dict) -> str:
    """분석된 트렌드 정보를 바탕으로 콘텐츠 제작자에게 보낼 알림 메시지를 생성합니다.
    
    Args:
        trend_name (str): 분석된 트렌드의 이름.
        analysis_result (dict): analyze_trend 함수에서 반환된 분석 결과.

    Returns:
        str: 포맷팅된 알림 메시지 문자열.
    """
    alert_message = (
        f"🔔 트렌드 알림: '{trend_name}'\n"
        f"   잠재적 파급력: {analysis_result['potential_score']}점 (높을수록 좋습니다!)\n"
        f"   콘텐츠 제작 골든 타임: {analysis_result['golden_time']}부터 시작!\n"
        f"   예상 소멸 시점: {analysis_result['decline_time']}쯤 꺾일 수 있으니 서두르세요.\n"
        f"   💡 오또가 예측하는 다음 대세 트렌드입니다. 지금 바로 선점하여 성공적인 콘텐츠를 만드세요!"
    )
    print("\n" + "="*50 + "\n" + alert_message + "\n" + "="*50 + "\n")
    return alert_message

# =============================================================================
#   [메인 실행 로직] 프로그램의 진입점
# =============================================================================
def main():
    """오또의 트렌드 예측 레이더를 실행하는 메인 함수입니다."""
    parser = argparse.ArgumentParser(
        description="오또의 트렌드 예측 레이더: 소셜 미디어 미세 트렌드를 감시하고 예측합니다."
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default="", # 기본값은 빈 문자열로 설정하여 input_file 없을 때만 데모 또는 키워드 사용 유도
        help="감시할 특정 트렌드 키워드를 입력하세요 (예: '숏폼 챌린지' 또는 'AI 펫'). --input-file과 함께 사용할 수 없습니다."
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default="",
        help="키워드 목록이 담긴 CSV 파일 경로 (예: 'keywords.csv'). 파일은 'keyword'라는 헤더를 가져야 합니다. --keyword보다 우선순위가 높습니다."
    )
    args = parser.parse_args()

    target_keyword = args.keyword
    target_input_file = args.input_file

    # 입력 방식 우선순위 결정: input-file > keyword > _DEMO_DEFAULT_
    if target_input_file:
        print(f"[오또] 📂 CSV 파일 '{target_input_file}'을(를) 통해 트렌드 키워드를 불러옵니다.")
        # fetch_trend_data 내부에서 파일 처리 및 에러 핸들링 수행
    elif not target_keyword:
        target_keyword = "_DEMO_DEFAULT_" # 키워드도 파일도 없으면 데모 모드 진입
        print("--- 🌟 키워드나 파일이 지정되지 않아 샘플 데이터로 시연 중입니다. 🌟 ---")
        print("본인만의 트렌드를 분석하려면 `python trend_whisper.py --keyword '내키워드'` 또는")
        print("`python trend_whisper.py --input-file '내파일.csv'` 처럼 실행하세요.\n")
    else:
        print(f"[오또] 📝 단일 키워드 '{target_keyword}'로 트렌드를 감시합니다.")

    print(f"[오또] 🚀 트렌드 예측 시스템 가동! 현재 시각: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_alerts = []
    try:
        # 키워드와 파일 경로를 fetch_trend_data로 전달하여 내부에서 로직 분기
        trends_to_analyze = fetch_trend_data(target_keyword, target_input_file)
        
        if not trends_to_analyze:
            print("[오또] ⚠️ 현재 감지된 미세 트렌드가 없거나 처리할 키워드가 없습니다. 다음에 다시 시도해주세요.")
            return

        print(f"[오또] 총 {len(trends_to_analyze)}개의 트렌드에 대한 분석을 시작합니다.\n")
        for i, trend in enumerate(trends_to_analyze):
            print(f"[오또] ===== 트렌드 분석 진행 중: {i+1}/{len(trends_to_analyze)} =====")
            analysis = analyze_trend(trend)
            alert = send_alert(trend['name'], analysis)
            all_alerts.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "trend_name": trend['name'],
                "current_mentions": trend['mentions'],
                "growth_rate": trend['growth_rate'],
                "sentiment": trend['sentiment'],
                "potential_score": analysis['potential_score'],
                "golden_time": analysis['golden_time'],
                "decline_time": analysis['decline_time'],
                "alert_message": alert.replace('\n', ' ') # CSV 저장을 위해 개행 문자 제거
            })
            time.sleep(0.3) # 각 트렌드 분석 후 약간의 딜레이

        # 모든 알림 데이터를 CSV 파일로 저장
        output_filename = "trend_whisper_alerts.csv"
        file_exists = os.path.exists(output_filename)
        
        try:
            with open(output_filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=all_alerts[0].keys())
                if not file_exists: # 파일이 새로 생성되는 경우에만 헤더를 씁니다.
                    writer.writeheader()
                writer.writerows(all_alerts)
            print(f"[오또] ✅ 모든 트렌드 알림 데이터가 '{output_filename}' 에 성공적으로 저장되었습니다.\n")
        except IOError as e:
            print(f"[오또] ❌ 오류: '{output_filename}' 파일 저장 중 문제가 발생했습니다: {e}")
        except Exception as e:
            print(f"[오또] ❌ 예기치 않은 오류로 파일 저장에 실패했습니다: {e}")

    except Exception as e:
        print(f"[오또] ❌ 치명적인 오류 발생! 트렌드 예측 시스템이 중단되었습니다: {e}")
        # 상세한 오류 추적을 위해 스택 트레이스를 출력할 수도 있습니다.
        # import traceback
        # traceback.print_exc()

    print("--- 🌟 오또의 트렌드 예측 레이더 임무 완료! 🌟 ---")
    print("💡 팁: 이 스크립트를 스케줄러(예: cron, Windows 작업 스케줄러)에 등록하여")
    print("      매일 실행하면 최신 트렌드를 지속적으로 감시하고 변화에 빠르게 대응할 수 있습니다!")

if __name__ == "__main__":
    main()
