
# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import datetime
import random
import os

def get_tomorrow_weather_mock():
    """내일 날씨 데이터를 가상으로 생성합니다."""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    
    # 온도 (섭씨)
    temp = random.randint(5, 30) # 5도에서 30도 사이
    
    # 날씨 상태
    conditions = ["맑음", "흐림", "구름 많음", "비", "소나기", "눈"]
    condition = random.choice(conditions)
    
    print(f"[모의 날씨 API] 내일({tomorrow.strftime('%Y-%m-%d')}) 날씨 예측: {condition}, 기온: {temp}°C")
    
    return {
        "date": tomorrow.strftime("%Y-%m-%d"),
        "temperature": temp,
        "condition": condition
    }

def recommend_outfit(weather_data):
    """날씨 데이터에 기반하여 옷차림을 추천합니다."""
    temperature = weather_data["temperature"]
    condition = weather_data["condition"]
    
    outfit = ""
    if temperature < 10:
        outfit = "두꺼운 코트, 목도리, 장갑 등 따뜻한 옷차림"
    elif 10 <= temperature < 18:
        outfit = "자켓, 가디건, 긴팔 티셔츠 등 쌀쌀함에 대비한 옷차림"
    elif 18 <= temperature < 25:
        outfit = "얇은 가디건, 긴팔/반팔 티셔츠, 청바지 등 일교차에 대비한 옷차림"
    else: # temperature >= 25
        outfit = "반팔, 반바지, 시원한 소재의 옷차림"
        
    if "비" in condition or "소나기" in condition:
        outfit += ", 우산 필수!"
    elif "눈" in condition:
        outfit += ", 방수되는 따뜻한 신발 추천!"
        
    return outfit

def send_notification_and_save(phone_number, weather_info, outfit_recommendation):
    """SMS 알림을 가상으로 전송하고, 내용을 파일로 저장합니다."""
    message = (
        f"[AI 옷차림 알리미]\n"+
        f"내일({weather_info['date']}) 날씨는 {weather_info['condition']}, "+
        f"기온은 {weather_info['temperature']}°C 입니다.\n"+
        f"추천 옷차림: {outfit_recommendation}\n"+
        f"즐거운 하루 되세요!"
    )
    
    print(f"\n[모의 SMS 전송] 수신: {phone_number}\n내용:\n{message}")
    
    # 결과를 파일로 저장
    output_dir = "notifications"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.join(output_dir, f"notification_{datetime.date.today().strftime('%Y%m%d')}.txt")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(message)
        print(f"[파일 저장 완료] 알림 내용이 '{filename}' 파일로 저장되었습니다.")
    except IOError as e:
        print(f"[에러 발생] 파일 저장 중 오류가 발생했습니다: {e}")

def main():
    print("====== AI 내일 날씨 맞춤형 옷차림 알리미 시작 ======")
    
    # 사용자 휴대폰 번호 (가상)
    user_phone_number = "010-1234-5678"
    
    try:
        # 1. 내일 날씨 데이터 가져오기 (모의)
        weather_data = get_tomorrow_weather_mock()
        
        # 2. 옷차림 추천
        outfit = recommend_outfit(weather_data)
        print(f"[AI 추천] 추천 옷차림: {outfit}")
        
        # 3. 알림 전송 및 파일 저장 (모의)
        send_notification_and_save(user_phone_number, weather_data, outfit)
        
    except Exception as e:
        print(f"[오류] 봇 실행 중 예기치 않은 오류가 발생했습니다: {e}")
    finally:
        print("\n====== AI 내일 날씨 맞춤형 옷차림 알리미 종료 ======")
        print("TIP: 이 스크립트를 매일 자동으로 실행하려면, 'cron' (Linux/macOS) 또는 '작업 스케줄러' (Windows)에 등록하세요.")

if __name__ == "__main__":
    main()
