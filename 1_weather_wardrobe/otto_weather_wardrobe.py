#!/usr/bin/env python3

import os
import requests
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

# --- Conditional Twilio Import ---
# Twilio is optional. It's imported only if 'twilio' library is installed,
# preventing errors if SMS functionality is not desired or installed.
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
    print("✅ Twilio library found. SMS functionality can be enabled.")
except ImportError:
    TwilioClient = None # Placeholder if Twilio is not installed
    TWILIO_AVAILABLE = False
    print("💡 Twilio library not found. SMS sending will be disabled unless 'pip install twilio' is run.")

# Load environment variables from .env file
print("⚙️ 환경 변수 로드 중...")
load_dotenv()

# --- Configuration Constants ---
# Retrieve API keys and other configurations from environment variables.
# Sensible defaults are provided where appropriate.
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = os.getenv("CITY", "Seoul,KR")  # Default to Seoul,KR if not set
MY_PHONE_NUMBER = os.getenv("MY_PHONE_NUMBER")  # Your phone number (e.g., +821012345678 or +1234567890)

# Determine if SMS sending is enabled. Case-insensitive check.
SEND_SMS = os.getenv("SEND_SMS", "False").lower() == "true"

# Twilio specific environment variables, only needed if SEND_SMS is True
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")  # Your Twilio phone number (e.g., +15017122661)

# OpenWeatherMap API endpoint for 5-day / 3-hour forecast
OPENWEATHER_FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

# --- Helper Function for Environment Variable Validation ---
def _validate_env_variables():
    """Validates essential environment variables and prints warnings/errors."""
    print("🔍 필수 환경 변수 검증 중...")
    if not OPENWEATHER_API_KEY:
        print("❌ 에러: OPENWEATHER_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return False

    if SEND_SMS:
        if not TWILIO_AVAILABLE:
            print("❌ 에러: SMS 전송이 활성화되었으나 Twilio 라이브러리가 설치되지 않았습니다. `pip install twilio`를 실행해주세요.")
            return False
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, MY_PHONE_NUMBER]):
            print("❌ 에러: SMS 전송을 위해 Twilio 관련 환경 변수(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, MY_PHONE_NUMBER)가 모두 설정되어야 합니다.")
            return False
        print("✅ SMS 전송 환경 변수 설정 확인 완료.")
    else:
        print("💡 SMS 전송은 비활성화되어 있습니다. `SEND_SMS=True`로 설정하여 활성화할 수 있습니다.")
    
    print("✅ 환경 변수 검증 완료.")
    return True


# --- Weather Data Fetching ---
def get_tomorrow_weather(city: str, api_key: str) -> dict or None:
    """
    Fetches weather forecast for tomorrow for a given city.
    Aggregates min/max temperature, average probability of precipitation, and a representative description.
    """
    print(f"🔄 내일의 {city} 날씨 예보를 가져오는 중...")
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",  # For Celsius temperatures
    }

    try:
        print(f"📡 OpenWeatherMap API에 요청 전송: {OPENWEATHER_FORECAST_URL} (도시: {city})")
        response = requests.get(OPENWEATHER_FORECAST_URL, params=params, timeout=10) # Added timeout
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        print("✅ 날씨 데이터 요청 성공.")
        
        print("📊 JSON 응답 파싱 중...")
        data = response.json()
        print("✅ JSON 데이터 파싱 완료.")

    except requests.exceptions.Timeout:
        print(f"❌ 오류: OpenWeatherMap API 요청 시간 초과. 네트워크 상태를 확인해주세요.")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 오류: OpenWeatherMap API 연결 실패. 인터넷 연결을 확인해주세요: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"❌ 오류: HTTP 요청 실패 (상태 코드: {response.status_code}). API 키 또는 도시 이름을 확인해주세요: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ 오류: 날씨 데이터를 가져오는 중 예상치 못한 요청 에러 발생: {e}")
        return None
    except ValueError as e:  # Catch JSON decoding error specifically for response.json()
        print(f"❌ 오류: 날씨 데이터 JSON 디코딩 실패. 응답 형식이 올바르지 않습니다: {e}")
        return None
    except Exception as e:
        print(f"❌ 오류: 날씨 데이터를 가져오는 중 알 수 없는 에러 발생: {e}")
        return None

    # Calculate tomorrow's date for filtering forecasts
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    tomorrow_forecasts = []

    print(f"📅 내일 ({tomorrow})의 예보 데이터 필터링 중...")
    if not data.get('list'):
        print("⚠️ 예보 데이터 ('list' 키)가 API 응답에 없습니다.")
        return None

    for forecast in data['list']:
        # Convert Unix timestamp to datetime object
        forecast_dt = datetime.fromtimestamp(forecast['dt'])
        if forecast_dt.date() == tomorrow:
            tomorrow_forecasts.append(forecast)

    if not tomorrow_forecasts:
        print(f"⚠️ {city}에 대한 내일 ({tomorrow}) 예보 데이터가 발견되지 않았습니다. API 응답을 확인하세요.")
        return None
    
    print(f"✅ 내일의 예보 데이터 {len(tomorrow_forecasts)}개 발견.")

    # Initialize aggregation variables
    min_temp = float('inf')
    max_temp = float('-inf')
    total_pop = 0.0 # Use float for precision
    
    # Variables to determine the most representative weather description
    representative_description = "알 수 없는 날씨" # Default fallback
    min_time_diff_to_noon = timedelta(days=999) # A large timedelta for comparison
    all_unique_descriptions = set() # To gather all distinct descriptions
    
    midday_tomorrow = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12, 0, 0) # Tomorrow's noon

    print("📈 기온 및 강수 확률 계산, 대표 날씨 설명 추출 중...")
    for forecast in tomorrow_forecasts:
        try:
            temp = forecast['main']['temp']
            min_temp = min(min_temp, temp)
            max_temp = max(max_temp, temp)
            total_pop += forecast.get('pop', 0.0) # 'pop' might not always be present, default to 0.0

            # Extract description and add to set
            if forecast.get('weather') and forecast['weather']:
                current_description = forecast['weather'][0]['description']
                all_unique_descriptions.add(current_description)

            # Find forecast closest to tomorrow's noon for the representative description
            forecast_dt_obj = datetime.fromtimestamp(forecast['dt'])
            time_diff = abs(forecast_dt_obj - midday_tomorrow)

            if time_diff < min_time_diff_to_noon:
                min_time_diff_to_noon = time_diff
                if forecast.get('weather') and forecast['weather']:
                    representative_description = forecast['weather'][0]['description']
        except KeyError as e:
            print(f"⚠️ 경고: 예보 데이터에서 필수 키를 찾을 수 없습니다 ({e}). 이 항목은 건너뜁니다.")
            continue

    # Calculate average probability of precipitation
    avg_pop = (total_pop / len(tomorrow_forecasts)) * 100 if tomorrow_forecasts else 0.0

    # If no specific representative description was found, use all collected unique descriptions
    if representative_description == "알 수 없는 날씨" and all_unique_descriptions:
        representative_description = ", ".join(sorted(list(all_unique_descriptions)))

    print(f"✅ 내일 ({city})의 날씨 예측 최종 요약: \n"\
          f"   최저 기온: {min_temp:.1f}°C, 최고 기온: {max_temp:.1f}°C, \n"\
          f"   강수 확률: {avg_pop:.0f}%, 날씨 설명: {representative_description}.")

    return {
        "city": city,
        "min_temp": min_temp,
        "max_temp": max_temp,
        "description": representative_description,
        "rain_prob": avg_pop,
    }


# --- Wardrobe Advice Generation ---
def get_wardrobe_advice(weather_data: dict) -> str:
    """Generates fashion advice based on processed weather data."""
    print("👗 옷차림 추천 알고리즘 실행 중...")
    if not weather_data:
        print("❌ 날씨 데이터가 유효하지 않아 옷차림 추천을 할 수 없습니다.")
        return "날씨 데이터를 찾을 수 없어 옷차림 추천을 할 수 없습니다. 오또의 AI가 잠시 밈 창조 중인가 봅니다."

    max_temp = weather_data['max_temp']
    min_temp = weather_data['min_temp']
    rain_prob = weather_data['rain_prob']
    description = weather_data['description']
    city = weather_data['city']

    advice_parts = []
    
    advice_parts.append(f"🔮 내일 {city} 날씨 예측: 최저 {min_temp:.1f}°C ~ 최고 {max_temp:.1f}°C, {description}.")

    print("🌡️ 기온에 따른 옷차림 분석 중...")
    if max_temp > 28:
        advice_parts.append("☀️ 완전 여름! 가벼운 린넨, 반팔, 반바지로 시원하게! 선글라스는 필수!")
    elif max_temp > 22:
        advice_parts.append("👕 활동하기 좋은 쾌적한 날씨! 티셔츠나 얇은 셔츠, 청바지/스커트 추천.")
    elif max_temp > 15:
        advice_parts.append("🍂 쌀쌀할 수 있는 가을 날씨! 긴팔 셔츠, 가디건이나 얇은 재킷 하나 걸쳐주세요.")
    elif max_temp > 8:
        advice_parts.append("🧥 점점 추워지는 날씨! 스웨터, 재킷, 긴 바지로 따뜻하게. 아침저녁으로는 쌀쌀할 수 있어요.")
    else:  # max_temp <= 8
        advice_parts.append("🥶 겨울 한파! 두꺼운 코트, 목도리, 장갑, 내복으로 무장하세요. 따뜻함이 최고!")

    print("☔ 강수 확률에 따른 우산 소지 여부 분석 중...")
    if rain_prob > 60:
        advice_parts.append(f"☔️ 비 올 확률 {rain_prob:.0f}%! 우산과 방수 신발은 선택이 아닌 필수! 빗물에 $1 짜리 신발이 젖을 순 없죠.")
    elif rain_prob > 30:
        advice_parts.append(f"☁️ 비 올 확률 {rain_prob:.0f}%! 혹시 모르니 작은 우산 하나 챙겨두면 좋아요. (AI 오또가 미리 경고했습니다!)")
    
    print("✨ 패션 분석 완료!")
    return " ".join(advice_parts)


# --- Grok-ish Drip Code Generation ---
def generate_grok_drip() -> str:
    """Generates a random 'Grok-ish' meme phrase for added humor."""
    grok_phrases = [
        "오또의 알고리즘이 당신의 패션 센스를 1달러의 가치로 격상시켜 드립니다.",
        "Grok My Wardrobe: 내일 당신은 분명 옷 잘 입는다는 말을 들을 겁니다. (아님 말고)",
        "밈 트렌드를 읽어 당신의 옷차림에 AI 유머 한 스푼! #오또패션",
        "경고: 이 패션 조언은 당신의 $1 가치 자존감을 폭등시킬 수 있습니다.",
        "내일, 당신의 옷차림은 단순한 의상이 아닌... '스테이트먼트'가 될 것입니다. 😎",
        "오또의 '유료' 패션 드립! 당신의 아침을 책임지는 (강제) 코디 서비스.",
        "선택의 자유는 없습니다. 오또가 시키는 대로 입으세요. 🤖"
    ]
    print("😂 Grok-ish 드립 생성 완료!")
    return random.choice(grok_phrases)


# --- SMS Sending ---
def send_sms(to_number: str, message_body: str) -> bool:
    """Sends an SMS message using Twilio if configured and available."""
    print("✉️ SMS 전송 기능 확인 중...")
    if not TWILIO_AVAILABLE:
        print("❌ Twilio 라이브러리가 없어 SMS 전송을 건너뜀. `pip install twilio`를 확인하세요.")
        return False
    
    # Ensure all required Twilio credentials are set
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, to_number]):
        print("❌ Twilio SMS 전송을 위한 필수 환경 변수 중 일부가 설정되지 않았습니다.")
        print("   (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, MY_PHONE_NUMBER 확인 필요)")
        return False

    print(f"✉️ SMS 전송 시도 중: '{message_body[:50]}...' (수신: {to_number})")
    try:
        client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            to=to_number,
            from_=TWILIO_PHONE_NUMBER,
            body=message_body
        )
        print(f"✅ SMS 전송 성공! Message SID: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ SMS 전송 실패: {e}")
        return False


# --- Main Logic ---
def main():
    """Main function to orchestrate weather fetching, advice generation, and SMS sending."""
    print("\n--- 🚀 오또의 1달러 Weather Wardrobe 시작! ---")

    # 1. Validate environment variables
    if not _validate_env_variables():
        print("❌ 환경 변수 검증 실패로 프로젝트를 종료합니다.")
        return

    # 2. Fetch tomorrow's weather data
    weather_data = get_tomorrow_weather(CITY, OPENWEATHER_API_KEY)
    if not weather_data:
        print("❌ 날씨 데이터를 가져오는데 실패했습니다. 프로젝트를 종료합니다.")
        return

    # 3. Generate wardrobe advice based on weather
    wardrobe_advice = get_wardrobe_advice(weather_data)

    # 4. Generate a Grok-ish meme phrase
    grok_drip = generate_grok_drip()

    # 5. Assemble the final message
    final_message = f"[오또의 Weather Wardrobe]\n{wardrobe_advice}\n\n{grok_drip}\n\n(오늘도 $1 과금 성공! 🤑)"
    
    print("\n--- 📝 최종 옷차림 추천 메시지 미리보기 ---")
    print(final_message)
    print("------------------------------------------\n")

    # 6. Optionally send SMS
    if SEND_SMS:
        print("📲 SMS 전송이 활성화되어 있습니다...")
        if MY_PHONE_NUMBER:
            send_sms(MY_PHONE_NUMBER, final_message)
        else:
            print("❌ MY_PHONE_NUMBER가 설정되지 않아 SMS를 보낼 수 없습니다.")
    else:
        print("💡 SMS 전송은 비활성화되어 있습니다. '.env' 파일에서 `SEND_SMS=True`로 설정하여 활성화할 수 있습니다.")
    
    print("\n--- 🎉 오또의 1달러 Weather Wardrobe 종료! ---")

# Entry point of the script
if __name__ == "__main__":
    main()
