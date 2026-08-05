# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import random
import csv
import os
from datetime import datetime

# --- 전역 상수 설정 ---
DATA_FILE = "travel_play_data.csv"
CITIES_MISSIONS = [
    {"city": "Paris, France", "themes": ["culture", "romance", "food"], "mission_templates": ["에펠탑 아래에서 가장 로맨틱한 순간을 포착하세요!", "몽마르뜨 언덕에서 즉흥 버스킹에 참여하세요!", "파리의 숨겨진 골목 맛집을 찾아 미식 투어를 떠나세요!"]},
    {"city": "Tokyo, Japan", "themes": ["modern", "culture", "food"], "mission_templates": ["시부야 스크램블 교차로에서 가장 특이한 패션 피플을 찾아 사진을 찍으세요!", "로봇 레스토랑에서 잊지 못할 경험을 하세요!", "츠키지 시장에서 새벽부터 신선한 해산물을 맛보세요!"]},
    {"city": "Rio de Janeiro, Brazil", "themes": ["adventure", "party", "nature"], "mission_templates": ["코파카바나 해변에서 현지인들과 축구 경기에 참여하세요!", "슈가로프 산 정상에서 일몰을 감상하며 춤을 추세요!", "파벨라 투어를 통해 리오의 또 다른 얼굴을 만나보세요!"]},
    {"city": "Cairo, Egypt", "themes": ["history", "mystery", "culture"], "mission_templates": ["기자의 피라미드 앞에서 고대 이집트 복장을 하고 사진을 찍으세요!", "칸 엘 칼릴리 시장에서 보물을 찾아 흥정하세요!", "나일강 펠루카 투어를 하며 석양을 즐기세요!"]},
    {"city": "Kyoto, Japan", "themes": ["history", "culture", "nature"], "mission_templates": ["기온 거리에서 게이샤를 만나 전통 차를 마시는 경험을 하세요!", "후시미 이나리 신사의 천 개 토리이 길을 완주하세요!", "아라시야마 대나무 숲에서 명상하며 평온을 찾으세요!"]},
    {"city": "New York City, USA", "themes": ["urban", "culture", "entertainment"], "mission_templates": ["타임스퀘어 한복판에서 K-POP 랜덤 플레이 댄스에 참여하세요!", "브루클린 브릿지를 걸어 건너며 멋진 스카이라인을 촬영하세요!", "현지 길거리 음식 투어를 하며 뉴욕의 맛을 탐험하세요!"]},
    {"city": "Seoul, South Korea", "themes": ["modern", "culture", "food"], "mission_templates": ["광장시장에서 빈대떡과 막걸리를 맛보고, 현지인처럼 흥정하세요!", "N서울타워에서 서울 야경을 배경으로 최고의 '인생샷'을 남기세요!", "홍대 거리에서 버스킹 공연에 참여하거나 관객들과 함께 춤추세요!"]},
    {"city": "Rome, Italy", "themes": ["history", "culture", "food"], "mission_templates": ["콜로세움 앞에서 글래디에이터 분장을 하고 사진을 찍으세요!", "트레비 분수에 동전을 던지며 소원을 빌고, 가장 맛있는 젤라또를 찾으세요!", "로마의 숨겨진 골목길을 탐험하며 진정한 로컬 푸드를 경험하세요!"]},
    {"city": "Cape Town, South Africa", "themes": ["nature", "adventure", "culture"], "mission_templates": ["테이블 마운틴 정상에서 케이프타운 전경을 감상하고, 야생 다람쥐와 셀카를 찍으세요!", "볼더스 비치에서 펭귄들과 함께 수영하는 대담한 도전을 하세요!", "보캅 지역의 알록달록한 집들 사이에서 가장 아름다운 색의 집을 찾아 기념 사진을 찍으세요!"]},
    {"city": "Sydney, Australia", "themes": ["nature", "urban", "adventure"], "mission_templates": ["시드니 오페라 하우스를 배경으로 가장 멋진 점프샷을 찍으세요!", "본다이 비치에서 서핑 강습을 받고 파도를 타세요!", "달링 하버 주변을 산책하며 현지 해산물 요리를 맛보세요!"]}
]

# --- 함수 정의 ---
def save_play_data(round_num: int, chosen_city: str, mission: str, score: int) -> None:
    """사용자의 플레이 데이터를 CSV 파일에 안전하게 저장합니다."""
    print(f"[INFO] 데이터 저장 준비: 라운드 {round_num}, 도시 '{chosen_city}', 미션: '{mission}'")
    file_exists = os.path.isfile(DATA_FILE)
    try:
        with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'Round', 'Chosen_City', 'Mission', 'Score'])
                print(f"[LOG] 새로운 데이터 파일 '{DATA_FILE}'을 생성하고 헤더를 작성했습니다.")
            writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), round_num, chosen_city, mission, score])
        print(f"[SUCCESS] 플레이 데이터가 '{DATA_FILE}'에 성공적으로 저장되었습니다.")
    except IOError as e:
        print(f"[ERROR] 데이터 파일 '{DATA_FILE}' 쓰기 중 오류 발생: {e}")
    except Exception as e:
        print(f"[ERROR] 알 수 없는 오류로 플레이 데이터 저장 실패: {e}")

def analyze_play_data() -> str:
    """누적된 플레이 데이터를 분석하여 사용자 맞춤형 여행 테마를 도출합니다."""
    print("[INFO] 누적된 플레이 데이터를 분석합니다...")
    if not os.path.isfile(DATA_FILE):
        print(f"[WARN] 데이터 파일 '{DATA_FILE}'을 찾을 수 없습니다. 분석을 건너뜝니다.")
        return "아직 플레이 데이터가 충분하지 않습니다. 게임을 더 플레이해주세요!"

    city_counts = {}
    theme_counts = {}
    total_plays = 0

    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader) # 헤더 건너뛰기
            if not header:
                print("[WARN] 데이터 파일이 비어 있거나 헤더가 유효하지 않습니다.")
                return "플레이 데이터를 분석할 수 없습니다. 데이터가 유효한지 확인해주세요."

            for i, row in enumerate(reader, start=1):
                if len(row) >= 3:
                    chosen_city = row[2]
                    city_counts[chosen_city] = city_counts.get(chosen_city, 0) + 1
                    total_plays += 1
                    
                    # 선택된 도시에 해당하는 테마를 찾아서 카운트
                    city_info = next((item for item in CITIES_MISSIONS if item["city"] == chosen_city), None)
                    if city_info:
                        for theme in city_info["themes"]:
                            theme_counts[theme] = theme_counts.get(theme, 0) + 1
                else:
                    print(f"[WARN] {DATA_FILE} 파일의 {i+1}번째 줄 데이터 형식이 올바르지 않습니다: {row}")

    except FileNotFoundError:
        print(f"[ERROR] 분석 중 데이터 파일 '{DATA_FILE}'을 찾을 수 없습니다.")
        return "플레이 데이터를 분석할 수 없습니다. 파일을 찾을 수 없습니다."
    except StopIteration:
        print("[WARN] 데이터 파일에 내용이 없습니다. 헤더만 존재합니다.")
        return "플레이 데이터를 분석할 수 없습니다. 데이터가 유효한지 확인해주세요."
    except IOError as e:
        print(f"[ERROR] 데이터 파일 '{DATA_FILE}' 읽기 중 오류 발생: {e}")
        return f"데이터 분석 중 오류 발생: {e}"
    except Exception as e:
        print(f"[ERROR] 알 수 없는 오류로 플레이 데이터 분석 실패: {e}")
        return f"데이터 분석 중 알 수 없는 오류 발생: {e}"

    if not total_plays:
        print("[WARN] 유효한 플레이 데이터가 없어 분석을 진행할 수 없습니다.")
        return "플레이 데이터를 분석할 수 없습니다. 데이터가 유효한지 확인해주세요."

    # 가장 자주 등장하는 테마 찾기
    most_frequent_theme = max(theme_counts, key=theme_counts.get) if theme_counts else "다양한"

    result = f"\n[✨ 분석 결과 ✨] 총 {total_plays}회의 플레이 데이터를 기반으로 볼 때, 당신은 " \
             f"'{most_frequent_theme}' 테마의 즉흥 여행을 선호하는 경향이 있습니다!\n"
    result += f"[💡 추천] 다음 즉흥 여행 시 '{most_frequent_theme}' 테마를 중심으로 계획해보세요!"
    print("[SUCCESS] 플레이 데이터 분석이 완료되었습니다.")
    return result

def main():
    """Global Gamble Guild 게임의 메인 로직을 실행합니다."""
    print("\n✨ Global Gamble Guild: AI 즉흥 여행 룰렛에 오신 것을 환영합니다! ✨")
    print("AI가 제시하는 3개의 도시 중 하나를 선택하고 미션을 수행하여 점수를 얻으세요!")
    print("누적된 데이터를 바탕으로 당신만을 위한 즉흥 여행 테마를 도출해드립니다.")
    print("------------------------------------------------------------------")

    round_num = 1
    while True:
        print(f"\n--- 라운드 {round_num} 시작: AI가 새로운 여행지를 추천합니다! ---")
        # 무작위로 3개의 도시와 각 도시별 미션 하나를 선택
        # 사용자에게 제시된 특정 미션을 저장하여 나중에 활용
        selected_options = []
        unique_choices = random.sample(CITIES_MISSIONS, 3)
        
        for i, choice in enumerate(unique_choices):
            city = choice["city"]
            mission = random.choice(choice["mission_templates"])
            selected_options.append({"city": city, "mission": mission, "themes": choice["themes"]})
            print(f"  {i+1}. 도시: {city}, 미션: {mission}")
        
        user_choice_idx = -1
        while user_choice_idx not in [0, 1, 2]: # 인덱스 0, 1, 2 에 해당
            try:
                user_input = input("어떤 도시와 미션을 선택하시겠습니까? (1, 2, 3 입력): ")
                user_choice_idx = int(user_input) - 1 # 사용자는 1, 2, 3 입력, 인덱스는 0, 1, 2
                if user_choice_idx not in [0, 1, 2]:
                    print("🚫 유효하지 않은 선택입니다. 1, 2, 3 중 하나를 숫자로 입력해주세요.")
            except ValueError:
                print("🚫 잘못된 입력입니다. 숫자를 입력해주세요.")
            except Exception as e:
                print(f"[ERROR] 입력 처리 중 알 수 없는 오류 발생: {e}")
        
        chosen_info = selected_options[user_choice_idx]
        chosen_city = chosen_info["city"]
        chosen_mission = chosen_info["mission"]
        score = random.randint(5, 15) # 미션 수행에 따른 점수 시뮬레이션
        
        print(f"\n🎉 당신은 '{chosen_city}'(으)로 떠나 '{chosen_mission}' 미션을 수행하기로 선택했습니다!")
        print(f"👏 미션을 성공적으로 수행하여 {score}점을 획득했습니다! (AI 시뮬레이션)")
        
        save_play_data(round_num, chosen_city, chosen_mission, score)

        round_num += 1

        play_again = input("\n계속 플레이하시겠습니까? (y/n 입력): ").lower()
        if play_again != 'y':
            print("------------------------------------------------------------------")
            break

    # 게임 종료 후 분석 및 테마 판매 시뮬레이션
    print("\n--- 게임 종료 ---\n")
    analysis_result = analyze_play_data()
    print(analysis_result)
    
    # 분석 결과에 따라 AI의 진화 및 테마 판매 시뮬레이션
    if "아직 플레이 데이터가" not in analysis_result and "분석할 수 없습니다" not in analysis_result:
        print("\n💡 AI는 당신의 맞춤형 여행 테마를 여행 상품 기획자에게 1달러에 판매했습니다!")
        print("오또의 뇌가 진화했습니다! 감사합니다. 🧠")
    else:
        print("\n[INFO] 플레이 데이터가 부족하여 AI의 테마 판매가 보류되었습니다.")
    
    print(f"\n[참고] 이 프로그램은 반복 사용 시 데이터가 누적되어 더욱 정교한 분석을 제공합니다.\n       매일 실행하여 당신의 여행 취향 변화를 추적하거나 새로운 테마를 발견해보세요.\n       (Tip: `python global_gamble_guild.py` 명령어를 스케줄러에 등록하여 자동 실행할 수 있습니다.)")
    print("\n✨ Global Gamble Guild를 이용해주셔서 감사합니다! ✨")

# --- 프로그램 시작 지점 ---
if __name__ == "__main__":
    main()
