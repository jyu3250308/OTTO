
# ─────────────────────────────────────────────────────────────────────────────
# [실행 환경 방어] 한글 윈도우에서 출력을 파일로 저장하거나 다른 프로그램에 넘길 때
#   (예: python bot.py > log.txt / 작업 스케줄러 등록 / 주피터 / VS Code 일부 설정)
#   파이썬이 콘솔 기본 인코딩(cp949)을 쓰게 되어 이모지 출력 순간 UnicodeEncodeError로 죽습니다.
#   아래 3줄이 그걸 막아줍니다. 지우지 마세요!
# ─────────────────────────────────────────────────────────────────────────────
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


import datetime
import os

def get_tomorrow_weather(location="서울"):
    """
    내일 날씨 데이터를 모의로 가져옵니다. 실제 시나리오에서는 외부 API를 호출합니다.
    """
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    print(f"[INFO] {location}의 {tomorrow.strftime('%Y-%m-%d')} 날씨 정보를 가져오는 중 (모의)...")

    # 테스트를 위해 날마다 다른 날씨 데이터가 나오도록 모의 데이터를 설정합니다.
    mock_weathers = [
        {"temp_min": 15, "temp_max": 22, "condition": "맑음", "precipitation_chance": 10},
        {"temp_min": 10, "temp_max": 16, "condition": "흐림", "precipitation_chance": 30},
        {"temp_min": 5, "temp_max": 10, "condition": "비", "precipitation_chance": 80},
        {"temp_min": 20, "temp_max": 28, "condition": "구름 많음", "precipitation_chance": 20},
        {"temp_min": -3, "temp_max": 3, "condition": "눈", "precipitation_chance": 60}
    ]
    index = tomorrow.day % len(mock_weathers)
    weather_data = mock_weathers[index]
    weather_data["date"] = tomorrow.strftime("%Y년 %m월 %d일")
    weather_data["location"] = location

    print(f"[INFO] 모의 날씨 데이터: {weather_data}")
    return weather_data

def recommend_outfit(weather_data):
    """
    날씨 데이터에 기반하여 옷차림을 추천합니다. AI 의사결정을 시뮬레이션합니다.
    """
    temp_min = weather_data["temp_min"]
    temp_max = weather_data["temp_max"]
    condition = weather_data["condition"]
    recommendations = []

    if temp_max >= 25:
        recommendations.append("반팔 티셔츠, 반바지 또는 얇은 원피스")
    elif temp_max >= 20:
        recommendations.append("얇은 긴팔, 면바지, 가벼운 가디건")
    elif temp_max >= 15:
        recommendations.append("긴팔 티셔츠, 청바지, 자켓 또는 트렌치코트")
    elif temp_max >= 10:
        recommendations.append("니트, 맨투맨, 두꺼운 자켓 또는 코트")
    elif temp_max >= 5:
        recommendations.append("두꺼운 니트, 코트, 히트텍, 목도리")
    else: # temp_max < 5
        recommendations.append("두꺼운 패딩/코트, 목도리, 장갑, 방한용품")

    if "비" in condition or weather_data["precipitation_chance"] >= 50:
        recommendations.append("우산 또는 우비, 방수 신발")
    if "눈" in condition or ("눈" in condition and weather_data["precipitation_chance"] >= 50):
        recommendations.append("방한 부츠, 두꺼운 양말")

    outfit = ", ".join(recommendations) + "를 추천합니다." if recommendations else "오늘 날씨에 맞는 적절한 옷차림을 준비하세요."
    print(f"[INFO] 옷차림 추천: {outfit}")
    return outfit

def generate_sms_content(weather_data, outfit_recommendation):
    """
    SMS 메시지 내용을 생성합니다.
    """
    date = weather_data["date"]
    location = weather_data["location"]
    temp_range = f"{weather_data['temp_min']}°C ~ {weather_data['temp_max']}°C"
    condition = weather_data["condition"]
    precipitation = f"{weather_data['precipitation_chance']}%"

    sms_message = (
        f"[{date} {location} 날씨 알림]\n"
        f"최저/최고 기온: {temp_range}\n"
        f"날씨: {condition} (강수확률: {precipitation})\n"
        f"오또의 추천 옷차림: {outfit_recommendation}\n"
        f"즐거운 하루 되세요!"
    )
    print(f"[INFO] 생성된 SMS 내용:\n{sms_message}")
    return sms_message

def send_sms_mock(phone_number, message_content):
    """
    SMS 발송을 모의하고, 내용을 텍스트 파일로 저장합니다. (실물 파일 출력)
    """
    today_str = datetime.date.today().strftime("%Y%m%d")
    filename = f"daily_outfit_sms_{today_str}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(message_content)
        print(f"[SUCCESS] SMS 내용이 '{filename}' 파일로 성공적으로 저장되었습니다. (수신번호: {phone_number} 모의)")
        print(f"[INFO] 이 파일을 친구나 가족에게 공유해 보세요!")
    except IOError as e:
        print(f"[ERROR] 파일 저장 중 오류 발생: {e}")

def main():
    print("\n=== AI 내일 날씨 맞춤형 옷차림 알리미 SMS 시스템 시작 ===")
    target_phone_number = "010-1234-5678" # 사용자 정의 가능 (모의 발송)

    try:
        # 1. 내일 날씨 데이터 가져오기 (모의)
        weather = get_tomorrow_weather()
        if not weather:
            print("[ERROR] 날씨 데이터를 가져오는 데 실패했습니다.")
            return

        # 2. 옷차림 추천 생성
        outfit = recommend_outfit(weather)

        # 3. SMS 메시지 내용 생성
        sms_message = generate_sms_content(weather, outfit)

        # 4. SMS 발송 (파일로 모의 저장)
        send_sms_mock(target_phone_number, sms_message)

    except Exception as e:
        print(f"[CRITICAL ERROR] 시스템 실행 중 예외 발생: {e}")
    finally:
        print("\n=== AI 내일 날씨 맞춤형 옷차림 알리미 SMS 시스템 종료 ===")

if __name__ == "__main__":
    main()
    # [반복 사용 가치] 이 스크립트를 매일 자동으로 실행하려면, 운영체제의 스케줄러(예: Windows 작업 스케줄러, Linux/macOS Cron)에 등록하세요.
    # 예시 (Linux/macOS Cron): 0 8 * * * python3 /path/to/weather_outfit_notifier.py