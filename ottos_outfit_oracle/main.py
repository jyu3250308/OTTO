import os
import requests
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables from .env file
load_dotenv()

# --- Configuration from Environment Variables ---
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY_NAME = os.getenv("CITY_NAME", "Seoul") # Default to Seoul if not set
COUNTRY_CODE = os.getenv("COUNTRY_CODE", "KR") # Default to KR
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
RECIPIENT_PHONE_NUMBER = os.getenv("RECIPIENT_PHONE_NUMBER")

def get_weather_data(city: str, country_code: str, api_key: str) -> dict | None:
    """
    OpenWeatherMap API를 사용하여 특정 도시의 내일 날씨 데이터를 가져옵니다.
    위도/경도 조회 후 One Call API를 사용합니다.
    """
    print(f"[날씨 조회] '{city}, {country_code}' 날씨 정보를 가져오는 중...")
    
    # 1. 도시 이름으로 위도/경도 조회
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{country_code}&limit=1&appid={api_key}"
    try:
        geo_response = requests.get(geo_url)
        geo_response.raise_for_status() # HTTP 오류 발생 시 예외 발생
        geo_data = geo_response.json()

        if not geo_data:
            print(f"[에러] '{city}, {country_code}'에 대한 지리 정보를 찾을 수 없습니다. 도시 이름과 국가 코드를 확인해주세요.")
            return None
        
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        print(f"[날씨 조회] '{city}'의 위도: {lat}, 경도: {lon} 확인.")

    except requests.exceptions.RequestException as e:
        print(f"[에러] 지리 정보 조회 중 네트워크 오류 발생: {e}")
        return None
    except Exception as e:
        print(f"[에러] 지리 정보 처리 중 예상치 못한 오류 발생: {e}")
        return None

    # 2. 위도/경도로 내일의 날씨 예보 조회 (One Call API)
    # exclude=current,minutely,hourly,alerts -> daily만 필요
    # units=metric -> 섭씨
    weather_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&units=metric&appid={api_key}"
    try:
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status() # HTTP 오류 발생 시 예외 발생
        weather_data = weather_response.json()

        # 내일 날씨 (daily 배열의 두 번째 요소, 오늘이 첫 번째 0번 인덱스)
        if weather_data and 'daily' in weather_data and len(weather_data['daily']) > 1:
            tomorrow_weather = weather_data['daily'][1]
            print("[날씨 조회] 내일 날씨 데이터 가져오기 성공.")
            return {
                "temp_min": tomorrow_weather['temp']['min'],
                "temp_max": tomorrow_weather['temp']['max'],
                "humidity": tomorrow_weather['humidity'],
                "pop": tomorrow_weather['pop'] * 100, # Probability of precipitation (0-1, convert to %)
                "weather_desc": tomorrow_weather['weather'][0]['description']
            }
        else:
            print("[에러] 내일 날씨 데이터를 찾을 수 없습니다. API 응답 구조를 확인하세요.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"[에러] 날씨 예보 조회 중 네트워크 오류 발생: {e}")
        return None
    except Exception as e:
        print(f"[에러] 날씨 예보 처리 중 예상치 못한 오류 발생: {e}")
        return None

def recommend_outfit(weather: dict) -> str:
    """
    날씨 데이터를 기반으로 '오또'만의 시그니처 룩을 추천합니다.
    """
    if not weather:
        return "날씨 정보를 가져올 수 없어 옷차림 추천이 어렵습니다. 잠시 후 다시 시도해주세요."

    temp_min = weather['temp_min']
    temp_max = weather['temp_max']
    humidity = weather['humidity']
    pop = weather['pop'] # Probability of precipitation in %
    weather_desc = weather['weather_desc']

    print(f"[옷차림 추천] 내일 날씨: 최저 {temp_min:.1f}°C, 최고 {temp_max:.1f}°C, 습도 {humidity}%, 강수확률 {pop:.1f}% ({weather_desc})")

    outfit = []
    accessories = []
    
    avg_temp = (temp_min + temp_max) / 2

    # --- Temperature-based recommendations ---
    if avg_temp < 5:
        outfit.append("롱패딩, 두꺼운 코트")
        outfit.append("히트텍, 울 스웨터, 기모 바지")
        accessories.append("목도리, 장갑, 털모자")
        main_rec = "아주 추운 날씨예요. 단단히 무장하세요!"
    elif 5 <= avg_temp < 10:
        outfit.append("겨울 코트, 경량 패딩")
        outfit.append("니트, 기모 맨투맨, 청바지")
        accessories.append("얇은 목도리, 장갑")
        main_rec = "쌀쌀한 날씨입니다. 따뜻하게 입으세요."
    elif 10 <= avg_temp < 15:
        outfit.append("트렌치코트, 자켓, 가디건")
        outfit.append("맨투맨, 후드티, 얇은 니트, 청바지/면바지")
        main_rec = "일교차가 클 수 있어요. 겉옷을 꼭 챙기세요."
    elif 15 <= avg_temp < 20:
        outfit.append("얇은 가디건, 바람막이, 맨투맨")
        outfit.append("긴팔 티셔츠, 청바지/슬랙스")
        main_rec = "활동하기 좋은 쾌적한 날씨입니다. 가벼운 겉옷도 좋아요."
    elif 20 <= avg_temp < 25:
        outfit.append("반팔 티셔츠, 얇은 셔츠")
        outfit.append("반바지, 면바지, 얇은 긴팔")
        main_rec = "초여름 날씨예요. 시원하고 가볍게 입으세요."
    else: # avg_temp >= 25
        outfit.append("민소매, 반팔 티셔츠")
        outfit.append("반바지, 시원한 소재의 하의")
        main_rec = "무더운 한여름 날씨입니다. 자외선 차단에 신경 쓰고, 통풍이 잘 되는 옷을 추천해요."

    # --- Precipitation considerations ---
    if pop > 80:
        accessories.append("강한 비가 예상되니 우산과 방수 외투는 필수!")
        main_rec += " (🌧️ 폭우 대비 필수!)"
    elif pop > 50:
        accessories.append("비 올 확률이 높아요. 우산이나 가벼운 방수 자켓을 챙기세요.")
        main_rec += " (☔ 비 대비!)"
    elif pop > 20:
        accessories.append("혹시 모를 비에 대비해 작은 우산을 챙기면 좋아요.")
        main_rec += " (💧 소나기 주의!)"

    # --- Humidity considerations ---
    if humidity > 80 and avg_temp > 20:
        main_rec += " 습도가 높아 끈적하게 느껴질 수 있어요. 통풍 잘 되는 소재의 옷이 좋아요."
    elif humidity < 40 and avg_temp < 15:
        main_rec += " 공기가 건조할 수 있으니 보습에 신경 써주세요."
        
    final_recommendation = f"✨ 오또의 내일 코디 ✨\n\n"
    final_recommendation += f"🌡️ 예상 온도: 최저 {temp_min:.1f}°C, 최고 {temp_max:.1f}°C\n"
    final_recommendation += f"💧 강수 확률: {pop:.1f}%\n"
    final_recommendation += f"💨 습도: {humidity}%\n\n"
    final_recommendation += f"👉 추천 옷차림: {', '.join(outfit)}\n"
    if accessories:
        final_recommendation += f"➕ 기타: {', '.join(accessories)}\n"
    final_recommendation += f"\n💡 오또의 한마디: {main_rec}"
    final_recommendation += "\n\n#옷또입지 #날씨코디 #오또의선택"
    
    return final_recommendation

def send_sms(to_number: str, message: str) -> bool:
    """
    Twilio를 사용하여 SMS 메시지를 전송합니다.
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, to_number]):
        print("[에러] Twilio SMS 발송에 필요한 환경 변수 (SID, TOKEN, 발신 번호, 수신 번호) 중 일부가 설정되지 않았습니다.")
        return False

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            to=to_number,
            from_=TWILIO_PHONE_NUMBER,
            body=message
        )
        print(f"[SMS 발송] 메시지 성공적으로 전송! SID: {message.sid}")
        return True
    except Exception as e:
        print(f"[에러] SMS 발송 실패: {e}")
        print(f"Twilio 설정 확인: ACCOUNT_SID={TWILIO_ACCOUNT_SID}, FROM_NUMBER={TWILIO_PHONE_NUMBER}, TO_NUMBER={to_number}")
        return False

def main():
    """
    '옷또입지?' 프로젝트의 메인 실행 함수.
    날씨를 분석하고 옷차림을 추천하여 SMS로 전송합니다.
    """
    print("--- 🤖 오또의 옷또입지? 프로젝트 시작 ---")

    # 1. 환경 변수 확인
    if not OPENWEATHER_API_KEY:
        print("[오류] OPENWEATHER_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER or not RECIPIENT_PHONE_NUMBER:
        print("[오류] Twilio 관련 환경 변수 (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, RECIPIENT_PHONE_NUMBER) 중 일부가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return
    if not CITY_NAME or not COUNTRY_CODE:
        print("[경고] CITY_NAME 또는 COUNTRY_CODE가 설정되지 않아 기본값 (Seoul, KR)을 사용합니다.")


    # 2. 내일 날씨 데이터 가져오기
    weather_data = get_weather_data(CITY_NAME, COUNTRY_CODE, OPENWEATHER_API_KEY)
    if not weather_data:
        print("[실패] 날씨 정보를 가져오지 못했습니다. 프로그램 종료.")
        return

    # 3. AI 기반 옷차림 추천 생성
    outfit_recommendation = recommend_outfit(weather_data)
    print("\n--- 오또의 옷차림 추천 내용 ---")
    print(outfit_recommendation)
    print("-----------------------------\n")

    # 4. SMS 알림 서비스 전송
    print(f"[SMS 발송] 수신자: {RECIPIENT_PHONE_NUMBER} 에게 SMS 전송 시도...")
    if send_sms(RECIPIENT_PHONE_NUMBER, outfit_recommendation):
        print("[성공] '옷또입지?' 알림이 성공적으로 전송되었습니다.")
    else:
        print("[실패] '옷또입지?' 알림 SMS 전송에 실패했습니다. 로그를 확인해주세요.")
    
    print("--- 🤖 오또의 옷또입지? 프로젝트 종료 ---")

if __name__ == "__main__":
    main()