# tastetrail_guru.py

# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        # 이 부분은 환경 방어 코드이므로, 실패해도 프로그램 동작에 직접적인 영향 없음
        pass

import json
import random
import os

# --- Mock Data and Configuration ---
# 퀴즈 데이터셋: 카테고리, 질문, 정답, 해설을 포함합니다.
QUIZ_DATA = [
    {
        "category": "Basic Principles",
        "question": "튀김 온도가 너무 낮으면 음식이 어떻게 되나요?",
        "answer": "기름을 많이 흡수하고 눅눅해집니다.",
        "explanation": "낮은 온도에서는 음식 표면이 빠르게 굳지 않아 기름이 침투하기 쉽고, 바삭함이 줄어들어 눅눅해집니다. 적정 온도를 유지하는 것이 중요해요!"
    },
    {
        "category": "Ingredient Characteristics",
        "question": "숙성된 소고기를 건조 숙성(Dry Aging)하는 주요 이유가 뭔가요?",
        "answer": "수분이 증발하며 풍미가 응축되고, 효소 작용으로 육질이 부드러워집니다.",
        "explanation": "건조 숙성은 고기의 수분을 날려 맛을 응축시키고, 자연 효소가 단백질을 분해하여 부드러운 식감과 독특한 풍미를 만들어냅니다. 시간과 기술이 필요한 과정이죠."
    },
    {
        "category": "Culinary Terminology",
        "question": "블렌딩(Blending)의 정확한 의미는 무엇인가요?",
        "answer": "여러 재료를 섞어 균일하고 부드러운 혼합물을 만드는 조리 과정입니다.",
        "explanation": "블렌딩은 단순히 섞는 것을 넘어, 재료들을 완전히 통합하여 새로운 질감과 맛의 조화를 이루는 과정입니다. 믹서기나 블렌더를 주로 사용해요."
    }
]

# 사용자 진행 상황을 저장할 파일 경로
USER_DATA_FILE = "user_progress.json"
# 맞춤형 학습 경로를 저장할 파일 경로
LEARNING_PATH_FILE = "personalized_learning_path.txt"
# 생성된 광고 문구를 저장할 파일 경로
AD_COPY_FILE = "generated_ad_copy.txt"

# --- Core Functions ---

def load_user_progress():
    """
    사용자 진행 상황을 파일에서 로드합니다.
    파일이 없거나 손상되었을 경우 초기 데이터를 반환합니다.
    """
    print(f"\n🔄 사용자 진행 상황을 '{USER_DATA_FILE}'에서 로드 중...")
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            print("✅ 사용자 진행 상황 로드 완료.")
            return user_data
        except json.JSONDecodeError:
            print(f"⚠️ '{USER_DATA_FILE}' 파일이 손상되었거나 유효한 JSON 형식이 아닙니다. 새 프로필을 생성합니다.")
        except IOError as e:
            print(f"❌ '{USER_DATA_FILE}' 파일을 읽는 중 오류 발생: {e}. 새 프로필을 생성합니다.")
    else:
        print(f"ℹ️ '{USER_DATA_FILE}' 파일이 존재하지 않습니다. 새로운 사용자 프로필을 생성합니다.")
    return {"quiz_stats": {}}

def save_user_progress(data):
    """
    사용자 진행 상황 데이터를 파일에 저장합니다.
    저장 중 오류가 발생할 경우 사용자에게 알립니다.
    """
    print(f"🔄 사용자 진행 상황을 '{USER_DATA_FILE}'에 저장 중...")
    try:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ 사용자 진행 상황 저장 완료.")
    except IOError as e:
        print(f"❌ '{USER_DATA_FILE}' 파일을 쓰는 중 오류 발생: {e}. 진행 상황이 저장되지 않을 수 있습니다.")

def run_quiz(user_data):
    """
    퀴즈를 실행하고 사용자 답변을 처리하여 진행 상황을 업데이트합니다.
    """
    print("\n--- TasteTrail Guru 퀴즈 시작! ---\n")
    print("새로운 미식 퀴즈를 풀어보세요!")

    if not QUIZ_DATA:
        print("⚠️ 퀴즈 데이터가 없습니다. 퀴즈를 실행할 수 없습니다.")
        return user_data

    question_data = random.choice(QUIZ_DATA)
    category = question_data['category']
    question = question_data['question']
    answer = question_data['answer']
    explanation = question_data['explanation']

    print(f"[문제: {category}] {question}")
    user_answer = input("👩‍🍳 당신의 답변은? (최대한 정확한 문장으로 입력해주세요): ")

    # 답변 비교 (대소문자 무시, 공백 제거)
    is_correct = user_answer.strip().lower() == answer.strip().lower()

    # 사용자 통계 업데이트 준비
    category_stats = user_data["quiz_stats"].get(category, {"correct": 0, "wrong": 0})

    if is_correct:
        print("\n✅ 정답입니다! 축하해요! 미식 지수가 한 단계 상승했습니다.\n")
        category_stats["correct"] += 1
    else:
        print("\n❌ 오답입니다. 괜찮아요, 같이 배워봐요! 틀려야 성장하죠!\n")
        print(f"💡 정답: {answer}")
        print(f"✨ 해설: {explanation}\n")
        category_stats["wrong"] += 1

    user_data["quiz_stats"][category] = category_stats
    save_user_progress(user_data) # 퀴즈 결과 후 즉시 저장
    return user_data

def analyze_and_generate_output(user_data):
    """
    사용자의 퀴즈 오답 패턴을 분석하여 맞춤형 학습 경로 제안 및 광고 문구를 생성합니다.
    """
    print("\n--- TasteTrail Guru AI 분석 및 맞춤 제안 시작! ---\n")
    most_wrong_category = None
    max_wrong_count = -1

    # 오답이 가장 많은 카테고리 분석
    if user_data["quiz_stats"]:
        for category, stats in user_data["quiz_stats"].items():
            if stats["wrong"] > max_wrong_count:
                max_wrong_count = stats["wrong"]
                most_wrong_category = category
        print(f"🔍 분석 결과: 현재 '{most_wrong_category}' 카테고리가 가장 보강이 필요해 보입니다.")
    else:
        print("ℹ️ 아직 충분한 퀴즈 기록이 없어 분석하기 어렵습니다. 퀴즈를 더 풀어보세요!")

    # 1. 맞춤형 학습 경로 제안 생성 및 저장
    learning_path_message = "TasteTrail Guru님의 맞춤 학습 가이드\n-----------------------------------"
    if most_wrong_category:
        learning_path_message += f"\n현재까지의 퀴즈 결과를 바탕으로, '[{most_wrong_category}]' 분야가 가장 보강이 필요한 분야로 보입니다.\n\n해당 분야의 추가 학습 자료를 찾아보시거나, 관련 요리 프로그램을 시청해 보시면 큰 도움이 될 것입니다.\n지속적인 학습으로 미식의 길을 정복해 보세요!"
    else:
        learning_path_message += "\n아직 퀴즈 결과가 충분하지 않습니다. 퀴즈를 더 풀어보고 맞춤형 가이드를 받아보세요!\n"
    learning_path_message += "\n-----------------------------------"

    try:
        with open(LEARNING_PATH_FILE, 'w', encoding='utf-8') as f:
            f.write(learning_path_message)
        print(f"✅ '맞춤형 학습 경로'가 '{LEARNING_PATH_FILE}' 파일로 성공적으로 저장되었습니다.")
    except IOError as e:
        print(f"❌ '맞춤형 학습 경로' 파일 저장 중 오류 발생: {e}")

    # 2. 사용자 오답 패턴 기반 광고 문구 생성 (MOCK 시뮬레이션)
    ad_copy_content = "\n--- TasteTrail Guru 프리미엄 광고 (판매가: $1) ---\n"
    if most_wrong_category == "Basic Principles":
        ad_copy_content += "더 이상 요리 실패는 그만! '완벽한 튀김 온도계'로 당신의 요리를 한 단계 업그레이드하세요! 지금 구매하고 미식의 마법을 경험하세요!"
    elif most_wrong_category == "Ingredient Characteristics":
        ad_copy_content += "미식가들이 선택한 비밀! '프리미엄 숙성 한우 세트'로 가정에서 최상의 풍미를 즐기세요! 특별 할인 중!"
    elif most_wrong_category == "Culinary Terminology":
        ad_copy_content += "요리 용어 마스터의 지름길! '쉐프의 블렌더'로 어떤 재료든 부드럽고 완벽하게! 지금 바로 경험해보세요!"
    else:
        ad_copy_content += "당신의 잠재력을 깨울 다양한 요리 도구들이 기다립니다. 지금 바로 확인하세요! 미식의 여정, TasteTrail Guru와 함께!"

    try:
        with open(AD_COPY_FILE, 'w', encoding='utf-8') as f:
            f.write(ad_copy_content)
        print(f"✅ '맞춤형 광고 문구'가 '{AD_COPY_FILE}' 파일로 성공적으로 생성 및 저장되었습니다.")
        print(f"💰 이 광고 문구는 ${1}에 판매될 수 있습니다. (시뮬레이션)")
    except IOError as e:
        print(f"❌ '맞춤형 광고 문구' 파일 저장 중 오류 발생: {e}")

    print("\n--- AI 분석 및 맞춤 제안 완료 ---\n")

def main():
    """
    TasteTrail Guru 프로그램의 메인 실행 함수입니다.
    사용자 진행 상황 로드, 퀴즈 실행, 결과 분석 및 제안 생성을 순차적으로 수행합니다.
    """
    print("✨ TasteTrail Guru에 오신 것을 환영합니다! 미식의 세계로 떠나볼까요? ✨\n")
    print("---------------------------------------------------")

    user_data = load_user_progress()

    # 퀴즈 실행 및 진행 상황 업데이트
    print("\n--- 퀴즈 진행 ---")
    user_data = run_quiz(user_data)

    # 결과 분석 및 맞춤형 파일 생성
    print("\n--- 결과 분석 및 맞춤 제안 생성 ---")
    analyze_and_generate_output(user_data)

    print("\n---------------------------------------------------")
    print("🎉 TasteTrail Guru 세션이 성공적으로 종료되었습니다!\n")
    print(f"✅ 현재까지의 모든 진행 상황은 '{USER_DATA_FILE}'에 안전하게 저장됩니다.")
    print("🚀 매일 새로운 퀴즈를 풀고, 요리 실력을 꾸준히 향상시켜 보세요!")
    print("팁: 이 스크립트를 시스템 스케줄러(예: Windows 작업 스케줄러, Linux cron)에 등록하여 정기적으로 학습할 수 있습니다.")

if __name__ == "__main__":
    main()
