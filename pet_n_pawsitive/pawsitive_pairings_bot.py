# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서 UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import datetime
import os
import csv

# --- 전역 상수 --- 
RECOMMENDATION_LOG_FILE = "recommendations_history.txt"
USER_QUERY_LOG_FILE = "user_queries_log.txt"
MARKET_INSIGHTS_FILE = "market_insights.csv"

# --- Mocking 데이터 & AI 로직 --- (실제 API 연동 대신 가상 데이터로 동작)
# 가상 제품 및 서비스 데이터
PRODUCTS = {
    "알러지프리 강아지 사료": {"type": "dog", "allergens": ["chicken", "beef"], "age_range": "all", "description": "특정 알러지 성분이 없는 사료.", "price": 25},
    "고양이 장난감 세트": {"type": "cat", "allergens": [], "age_range": "all", "description": "다양한 종류의 고양이 장난감.", "price": 15},
    "유기농 아기 세탁세제": {"type": "baby", "allergens": [], "age_range": "0-36", "description": "아기 피부에 안전한 세탁세제.", "price": 12},
    "프리미엄 아기 기저귀": {"type": "baby", "allergens": [], "age_range": "0-24", "description": "민감한 아기 피부를 위한 고품질 기저귀.", "price": 30},
    "강아지 교육 바우처": {"type": "dog", "allergens": [], "age_range": "all", "description": "전문가 훈련 서비스.", "location": "seoul", "price": 50},
    "아기 돌봄 베이비시터": {"type": "baby", "allergens": [], "age_range": "0-60", "description": "인증된 베이비시터 서비스.", "location": "busan", "price": 40}
}

# --- 핵심 봇 기능 --- 

def parse_age_to_months(age_str: str) -> int:
    """
    사용자 입력 연령 문자열에서 월(month)을 추출하여 정수로 반환합니다.
    예: "6 months" -> 6, "1 year" -> 12. 파싱 실패 시 0을 반환합니다.
    """
    if not age_str:
        return 0
    age_str_lower = age_str.lower()
    try:
        if "month" in age_str_lower:
            return int(age_str_lower.split()[0])
        elif "year" in age_str_lower:
            return int(age_str_lower.split()[0]) * 12
    except (ValueError, IndexError):
        print(f"[경고] 연령 '{age_str}' 파싱에 실패했습니다. 유효하지 않은 형식입니다.")
    return 0

def recommend_items(user_input: dict) -> tuple[list[str], list[str]]:
    """
    사용자 입력에 기반하여 맞춤형 아이템을 추천하고, 잠재적 경고 목록을 반환합니다.
    Args:
        user_input (dict): 사용자의 선호 및 조건 (type, pet_type, allergy, age, location 등).
    Returns:
        tuple[list[str], list[str]]: 추천 아이템 목록과 경고 메시지 목록.
    """
    print("[추천] 추천 아이템 분석을 시작합니다.")
    recommendations = []
    warnings = []

    target_type = user_input.get("type", "").lower()  # pet (dog/cat) or baby
    user_pet_type = user_input.get("pet_type", "").lower()
    user_allergy = user_input.get("allergy", "").lower()
    user_age_months = parse_age_to_months(user_input.get("age", ""))
    user_location = user_input.get("location", "").lower()

    if not target_type: # 기본 대상 타입 유효성 검사
        warnings.append("유효한 추천 대상을 입력해주세요 (예: baby, dog, cat).")
        return [], warnings

    for item_name, data in PRODUCTS.items():
        is_suitable = True

        # 1. 타입 필터링
        item_category = data.get("type", "")
        if target_type == "pet":
            if item_category not in ["dog", "cat"] or (user_pet_type and item_category != user_pet_type):
                is_suitable = False
        elif target_type == "baby":
            if item_category != "baby":
                is_suitable = False
        else: # 알 수 없는 타입 입력 시 해당 타입이 아닌 모든 아이템 제외
            if item_category not in ["dog", "cat", "baby"]:
                 is_suitable = False

        if not is_suitable: continue # 다음 아이템으로 이동

        # 2. 알레르기 필터링
        if user_allergy and user_allergy in data.get("allergens", []):
            warnings.append(f"경고: '{item_name}'은(는) 사용자의 알레르기 유발 가능성(성분: {user_allergy})이 있습니다.")
            is_suitable = False

        # 3. 연령 필터링
        if user_age_months > 0 and item_category == "baby" and data.get("age_range") and data["age_range"] != "all":
            try:
                min_age, max_age = map(int, data["age_range"].split('-'))
                if not (min_age <= user_age_months <= max_age):
                    warnings.append(f"경고: '{item_name}'은(는) 사용자의 연령({user_age_months}개월)에 부적합할 수 있습니다 (적정 연령: {data['age_range']}개월).")
                    is_suitable = False
            except (ValueError, KeyError):
                print(f"[경고] '{item_name}'의 연령 범위('{data.get('age_range', 'N/A')}') 파싱 오류. 필터링을 건너뜁니다.")

        # 4. 위치 필터링 (서비스에만 적용)
        if user_location and data.get("location"):
            if user_location not in data["location"].lower(): # 아이템의 location이 더 구체적일 수 있음
                is_suitable = False

        if is_suitable:
            recommendations.append(f"{item_name} (설명: {data['description']})")
            print(f"[추천 진행] '{item_name}'이(가) 조건에 부합하여 추천 목록에 추가되었습니다.")
        else:
            print(f"[필터링] '{item_name}'이(가) 현재 조건에 부합하지 않습니다.")

    if not recommendations:
        recommendations.append("죄송합니다. 현재 조건에 맞는 추천 아이템을 찾을 수 없습니다.")
        print("[추천] 일치하는 아이템이 없어 기본 메시지를 추가합니다.")
    
    print("[추천] 추천 분석이 완료되었습니다.")
    return recommendations, warnings

def generate_market_insights(query_log_file: str, insights_file: str):
    """
    사용자 쿼리 로그를 분석하여 시장 수요 패턴을 도출하고 CSV 파일로 저장합니다.
    Args:
        query_log_file (str): 사용자 쿼리 로그 파일 경로.
        insights_file (str): 시장 인사이트를 저장할 CSV 파일 경로.
    """
    print(f"[인사이트 분석] 로그 파일 '{query_log_file}' 분석을 시작합니다.")
    query_counts = {}
    total_queries = 0

    if not os.path.exists(query_log_file):
        print(f"[인사이트 분석] 경고: 로그 파일 '{query_log_file}'이 존재하지 않습니다. 분석을 건너뜝니다.")
        with open(insights_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["패턴", "수요빈도", "점유율(%)"])
            writer.writerow(["데이터 부족", 0, 0.00])
        print(f"[인사이트 분석] 빈 인사이트가 '{insights_file}'에 저장되었습니다.")
        return

    try:
        with open(query_log_file, 'r', encoding='utf-8') as f:
            for line in f:
                total_queries += 1
                # 간단한 패턴 분석: 쉼표로 구분된 키워드 빈도수 계산
                keywords = [kw.strip().lower() for kw in line.strip().split(',') if kw.strip()]
                for kw in keywords:
                    query_counts[kw] = query_counts.get(kw, 0) + 1
        print(f"[인사이트 분석] 총 {total_queries}개의 쿼리 로그를 성공적으로 읽었습니다.")
    except IOError as e:
        print(f"[인사이트 분석] 오류: 로그 파일 '{query_log_file}' 읽기 실패: {e}")
        return

    sorted_insights = sorted(query_counts.items(), key=lambda item: item[1], reverse=True)

    print(f"\n--- 시장 수요 인사이트 분석 결과 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
    if not sorted_insights:
        print("[인사이트 분석] 분석할 데이터가 부족합니다.")
        with open(insights_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["패턴", "수요빈도", "점유율(%)"])
            writer.writerow(["데이터 부족", 0, 0.00])
        print(f"[인사이트 분석] 빈 인사이트가 '{insights_file}'에 저장되었습니다.")
        return

    print(f"총 {total_queries}개의 쿼리 분석.")
    print("수요가 높은 패턴:")

    try:
        with open(insights_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["패턴", "수요빈도", "점유율(%)"])
            for i, (pattern, count) in enumerate(sorted_insights):
                share = (count / total_queries) * 100 if total_queries > 0 else 0
                print(f"  {i+1}. '{pattern}': {count}회 (점유율: {share:.2f}%) ")
                writer.writerow([pattern, count, f"{share:.2f}"])
        print(f"[인사이트 분석] 상세 인사이트가 '{insights_file}' 파일로 성공적으로 저장되었습니다.\n")
    except IOError as e:
        print(f"[인사이트 분석] 오류: 인사이트 파일 '{insights_file}' 쓰기 실패: {e}")

# --- 메인 봇 루프 --- 
if __name__ == "__main__":
    print("--- Pet/Paws-itive Pairings Bot --- (반려 맞춤템 오또피아)")
    print("반려동물/아기 돌봄, '뭘 사야 할지' 고민인가요? 오또가 도와드립니다.\n")

    while True:
        print("\n--- 새 추천을 위해 정보를 입력해주세요. (종료: 'q', 시장 분석: 'a') ---")
        user_type_input = input("추천 대상 (예: baby, dog, cat): ").strip().lower()

        if user_type_input == 'q':
            print("[종료] 봇을 종료합니다.")
            break
        if user_type_input == 'a':
            generate_market_insights(USER_QUERY_LOG_FILE, MARKET_INSIGHTS_FILE)
            continue

        # 사용자 입력 정규화 및 데이터 모델 구성
        current_user_input = {
            "type": "",
            "pet_type": "",
            "allergy": "",
            "age": "",
            "location": ""
        }

        if user_type_input in ["dog", "cat"]:
            current_user_input["type"] = "pet"
            current_user_input["pet_type"] = user_type_input
        elif user_type_input == "baby":
            current_user_input["type"] = "baby"
        else:
            print("[입력 오류] 유효하지 않은 추천 대상입니다. 다시 입력해주세요.")
            continue

        current_user_input["allergy"] = input("알레르기가 있다면 입력해주세요 (예: chicken, beef, 없음): ").strip().lower()
        if current_user_input["allergy"] == '없음':
            current_user_input["allergy"] = ''

        current_user_input["age"] = input("연령 (아기: 6개월, 반려동물: 상관 없음): ").strip()

        current_user_input["location"] = input("선호하는 지역 (서비스에 해당, 예: seoul, busan, 전국): ").strip().lower()
        if current_user_input["location"] == '전국':
            current_user_input["location"] = ''
        
        # 사용자 쿼리 로그 저장 (시장 분석용)
        try:
            with open(USER_QUERY_LOG_FILE, 'a', encoding='utf-8') as f:
                query_str = f"{current_user_input['type']},{current_user_input['pet_type']},{current_user_input['allergy']},{current_user_input['age']},{current_user_input['location']}"
                f.write(query_str + "\n")
            print(f"[로그 저장] 사용자 쿼리가 '{USER_QUERY_LOG_FILE}'에 기록되었습니다.")
        except IOError as e:
            print(f"[로그 저장 오류] 사용자 쿼리 로그 파일 쓰기 실패: {e}")

        recommendations, warnings = recommend_items(current_user_input)

        print("\n--- 오또의 맞춤 추천 결과 ---")
        if warnings:
            for warning in warnings:
                print(f"[주의] {warning}")
        if recommendations:
            for i, rec in enumerate(recommendations):
                print(f"  {i+1}. {rec}")
        
        # 추천 결과 로그 저장 (이력 관리용)
        try:
            with open(RECOMMENDATION_LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"\n--- {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                f.write(f"[입력] 대상: {current_user_input['type']}{' ('+current_user_input['pet_type']+')' if current_user_input['pet_type'] else ''}, 알러지: {current_user_input['allergy'] if current_user_input['allergy'] else '없음'}, 연령: {current_user_input['age'] if current_user_input['age'] else '상관 없음'}, 지역: {current_user_input['location'] if current_user_input['location'] else '전국'}\n")
                if warnings:
                    for warning in warnings:
                        f.write(f"[주의] {warning}\n")
                if recommendations:
                    for rec in recommendations:
                        f.write(f"- {rec}\n")
                f.write("--------------------\n")
            print(f"[로그 저장] 추천 결과가 '{RECOMMENDATION_LOG_FILE}'에 기록되었습니다.")
        except IOError as e:
            print(f"[로그 저장 오류] 추천 결과 로그 파일 쓰기 실패: {e}")

    print("\n오또피아 봇을 종료합니다. 다음에 또 이용해주세요!")
    # TIP: 이 스크립트를 Crontab (Linux/macOS) 또는 작업 스케줄러 (Windows)에 등록하여
    #      정기적으로 'a' 옵션을 실행하면 최신 시장 인사이트 파일을 자동 생성할 수 있습니다.
