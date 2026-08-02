# -*- coding: utf-8 -*-

# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import datetime

# --- CalorieCraft 설정 데이터 (Mock Data) ---
# 운동 종류별 분당 소모 칼로리 (kcal/min)
EXERCISE_CALORIES_PER_MINUTE = {
    "러닝": 10, "수영": 8, "사이클": 7, "요가": 3, "걷기": 5, "줄넘기": 12, "웨이트트레이닝": 6
}

# 식단 항목별 칼로리 수준 (AI 예측용)
DIET_CALORIE_LEVELS = {
    "피자": "high", "치킨": "high", "햄버거": "high", "콜라": "high",
    "파스타": "medium", "김치찌개": "medium", "돈까스": "medium",
    "샐러드": "low", "닭가슴살": "low", "과일": "low", "채소": "low",
    "물": "low"
}

# --- 핵심 기능 모듈 (AI Mocking Logic) ---
def calculate_exercise_time(target_kcal: int, exercise_type: str) -> float:
    """목표 칼로리 소모를 위한 특정 운동의 소요 시간을 계산합니다.
    
    Args:
        target_kcal (int): 소모해야 할 목표 칼로리.
        exercise_type (str): 계산할 운동 종류.

    Returns:
        float: 목표 칼로리 소모에 필요한 운동 시간 (분 단위). 
               유효하지 않은 입력 시 0.0 반환.
    """
    if not isinstance(target_kcal, int) or target_kcal <= 0:
        print(f"[경고] 유효하지 않은 목표 칼로리 입력 ({target_kcal}). 0.0분 반환.")
        return 0.0
    
    kcal_per_min = EXERCISE_CALORIES_PER_MINUTE.get(exercise_type)
    if kcal_per_min is None or kcal_per_min <= 0:
        print(f"[경고] 알 수 없거나 칼로리 소모가 없는 운동 종류 '{exercise_type}'. 0.0분 반환.")
        return 0.0
    
    time_needed = target_kcal / kcal_per_min
    return round(time_needed, 1)

def recommend_exercise_combination(target_kcal: int, preferred_exercises: list) -> dict:
    """선호하는 운동 종류를 바탕으로 최적의 운동 조합을 추천합니다.
    
    Args:
        target_kcal (int): 소모해야 할 총 목표 칼로리.
        preferred_exercises (list): 사용자가 선호하는 운동 종류 리스트.

    Returns:
        dict: 운동 종류별 소모 칼로리 및 소요 시간.
              예: {"러닝": {"kcal": 250, "time_minutes": 25.0}}
    """
    print(f"[진행] {target_kcal}kcal 소모를 위한 운동 조합 추천을 시작합니다...")
    if not isinstance(target_kcal, int) or target_kcal <= 0 or not preferred_exercises:
        print("[정보] 유효한 목표 칼로리 또는 선호 운동이 없어 조합 추천을 건너뜁니다.")
        return {}

    combination_plan = {}
    num_exercises = len(preferred_exercises)
    
    # 칼로리를 선호 운동에 최대한 균등하게 분배
    kcal_per_exercise_base = target_kcal // num_exercises 
    remaining_kcal_dist = target_kcal % num_exercises

    for i, exercise in enumerate(preferred_exercises):
        current_kcal_target = kcal_per_exercise_base
        if i < remaining_kcal_dist: # 남은 칼로리를 앞에서부터 하나씩 분배
            current_kcal_target += 1
        
        if current_kcal_target <= 0: # 0 이하의 칼로리는 계산하지 않음
            continue

        time_needed = calculate_exercise_time(current_kcal_target, exercise)
        if time_needed > 0:
            combination_plan[exercise] = {"kcal": current_kcal_target, "time_minutes": time_needed}
        else:
            print(f"[정보] '{exercise}' 운동은 칼로리 소모 계산이 불가능하여 조합에서 제외됩니다.")

    print(f"[완료] 총 {len(combination_plan)}가지 운동으로 조합 추천 완료.")
    return combination_plan

def predict_exercise_difficulty(diet_input: str) -> str:
    """섭취한 식단 텍스트를 바탕으로 필요한 운동 난이도를 예측합니다.
    
    Args:
        diet_input (str): 사용자가 입력한 식단 정보 문자열.

    Returns:
        str: 예측된 운동 난이도 ("상", "중", "하" 또는 정보 부족).
    """
    print(f"[진행] 식단 '{diet_input}' 분석을 통한 운동 난이도 예측 중...")
    diet_input_lower = diet_input.lower()
    total_level_score = 0
    matched_keywords_count = 0
    
    for keyword, level_str in DIET_CALORIE_LEVELS.items():
        if keyword in diet_input_lower:
            matched_keywords_count += 1
            if level_str == "high": total_level_score += 3
            elif level_str == "medium": total_level_score += 2
            else: total_level_score += 1 # low
    
    if matched_keywords_count == 0: 
        print("[정보] 식단 분석에 매칭되는 키워드가 없습니다.")
        return "보통 (식단 정보 부족)"

    avg_level_score = total_level_score / matched_keywords_count
    
    if avg_level_score >= 2.5: 
        difficulty = "상 (강도 높은 운동 권장)"
    elif avg_level_score >= 1.5: 
        difficulty = "중 (적당한 강도 운동 권장)"
    else: 
        difficulty = "하 (가벼운 운동으로 충분)"
    
    print(f"[완료] 예측된 운동 난이도: {difficulty}")
    return difficulty

# --- 메인 구동 루프 ---
def run_calorie_craft():
    print("\n=======================================================")
    print("⚙️ CalorieCraft ⚙️ 칼로리 변환 공작소에 오신 것을 환영합니다!")
    print("AI가 당신의 운동 목표를 최적의 '운동 시간 + 종류 조합'으로 변환해 드립니다.")
    print("=======================================================\n")

    # 1. 목표 칼로리 입력
    print("[단계 1/3] 오늘 소모하고 싶은 목표 칼로리를 입력해주세요.")
    while True:
        target_kcal_input = input("➡️ 목표 칼로리 (예: 500): ")
        try:
            target_kcal = int(target_kcal_input)
            if target_kcal <= 0:
                print("⚠️ 목표 칼로리는 1 이상의 양수여야 합니다. 다시 입력해주세요.")
            else:
                print(f"[확인] 목표 칼로리: {target_kcal}kcal")
                break
        except ValueError:
            print("⚠️ 유효하지 않은 입력입니다. 숫자를 입력해주세요.")

    # 2. 선호하는 운동 종류 입력
    print("\n[단계 2/3] 선호하는 운동 종류를 선택해주세요.")
    available_exercises = ", ".join(EXERCISE_CALORIES_PER_MINUTE.keys())
    print(f"💡 선택 가능한 운동: [{available_exercises}]")
    preferred_exercises_input = input("➡️ 선호하는 운동 종류를 쉼표(,)로 구분하여 입력 (예: 러닝,수영): ")
    
    # 입력된 운동 목록 필터링 및 유효성 검사
    preferred_exercises_list = [
        e.strip() for e in preferred_exercises_input.split(',') 
        if e.strip() in EXERCISE_CALORIES_PER_MINUTE
    ]

    if not preferred_exercises_list:
        print("[정보] 유효한 선호 운동이 선택되지 않아 기본 운동(러닝, 걷기)으로 진행합니다.")
        preferred_exercises_list = ["러닝", "걷기"]
    else:
        print(f"[확인] 선택된 선호 운동: {', '.join(preferred_exercises_list)}")
    
    # 3. 식단 입력
    print("\n[단계 3/3] 오늘 섭취한 식단을 간단히 입력해주세요.")
    diet_input = input("➡️ 오늘 섭취한 식단 (예: 피자 한 조각, 콜라): ")
    if not diet_input.strip():
        print("[정보] 식단 정보가 입력되지 않았습니다. 분석이 제한될 수 있습니다.")
        diet_input = "" # 빈 문자열로 처리하여 정보 부족 상태 유도
    else:
        print(f"[확인] 입력된 식단: {diet_input}")

    # --- 결과 생성 및 보고 --- 
    print("\n[진행] AI 맞춤 운동 레시피를 생성 중입니다...")
    report_lines = []
    report_lines.append(f"--- CalorieCraft AI 맞춤 운동 레시피 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
    report_lines.append(f"\n[목표]: 오늘 {target_kcal}kcal 소모하기")

    # 단일 운동 제안
    report_lines.append("\n[1. 칼로리 소모를 위한 단일 운동 제안]")
    for exercise, kcal_per_min in EXERCISE_CALORIES_PER_MINUTE.items():
        time_needed = calculate_exercise_time(target_kcal, exercise)
        if time_needed > 0:
            report_lines.append(f"  - {exercise}: 약 {time_needed}분")

    # 개인 맞춤 운동 조합 추천
    report_lines.append("\n[2. 개인 맞춤 운동 조합 추천 (선호 운동 기반)]")
    combination_plan = recommend_exercise_combination(target_kcal, preferred_exercises_list)
    if combination_plan:
        for exercise, data in combination_plan.items():
            report_lines.append(f"  - {exercise}: {data['kcal']}kcal 소모를 위해 약 {data['time_minutes']}분")
    else:
        report_lines.append("  - 선호하는 운동으로 유효한 조합을 생성할 수 없습니다.")

    # 식단-운동 균형 예측
    report_lines.append("\n[3. 식단-운동 균형 예측]")
    difficulty = predict_exercise_difficulty(diet_input)
    report_lines.append(f"  - 오늘 섭취한 식단({diet_input if diet_input else '입력 없음'}) 기준, 필요한 운동 난이도: {difficulty}")

    report_content = "\n".join(report_lines)
    print(f"\n{report_content}")

    # --- 결과 파일 저장 (눈에 보이는 산출물) ---
    print("\n[진행] AI 맞춤 운동 레시피를 파일로 저장 중입니다...")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"calorie_craft_report_{timestamp}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"✅ AI 맞춤 운동 레시피가 '{filename}' 파일로 성공적으로 저장되었습니다.")
        print("\n--- [팁] 이 봇을 매일 자동 실행하려면 OS 스케줄러에 등록하세요 (예: Windows 작업 스케줄러, Linux/macOS cron) ---")
        print(f"  (예시: '0 8 * * * python3 {__file__}' 입력 시 매일 오전 8시 실행)\n")
    except IOError as e:
        print(f"⚠️ 파일 저장 중 오류가 발생했습니다: {e}")
    except Exception as e:
        print(f"⚠️ 예기치 않은 오류로 파일 저장에 실패했습니다: {e}")

if __name__ == "__main__":
    run_calorie_craft()
