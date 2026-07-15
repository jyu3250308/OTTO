import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException # Import specific Twilio exception
import logging

# --- Logging Configuration ---
# Configure logging to display INFO level messages and above, with a clear format.
# This helps in tracking the execution flow and debugging.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Global Constants for Outfit Suggestions (Gemma AI's Wardrobe) ---
# This dictionary defines clothing items based on various temperature categories and weather conditions.
# It acts as a simple rule-based "AI" for outfit recommendations.
WARDROBE = {
    "상의": {
        "매우 추움": ["두꺼운 패딩 안에 울 스웨터", "기모 맨투맨"], # -5 이하
        "추움": ["니트 스웨터", "후드티", "두꺼운 맨투맨"], # -5 ~ 5
        "쌀쌀함": ["가디건", "맨투맨", "얇은 니트"], # 5 ~ 12
        "선선함": ["긴팔 티셔츠", "셔츠"], # 12 ~ 20
        "따뜻함": ["반팔 티셔츠"], # 20 ~ 27
        "더움": ["얇은 반팔 티셔츠", "민소매"] # 27 초과
    },
    "하의": {
        "매우 추움": ["기모 바지", "두꺼운 청바지", "융털 레깅스"],
        "추움": ["울 바지", "기모 레깅스+치마", "두꺼운 청바지"],
        "쌀쌀함": ["면 바지", "슬랙스", "청바지"],
        "선선함": ["슬랙스", "면 바지", "얇은 청바지"],
        "따뜻함": ["청바지", "면 반바지"],
        "더움": ["린넨 반바지", "통기성 좋은 바지"]
    },
    "외투": {
        "매우 추움": ["롱패딩", "두꺼운 코트"],
        "추움": ["숏패딩", "울 코트", "두꺼운 자켓"],
        "쌀쌀함": ["트렌치 코트", "블레이저", "얇은 자켓", "플리스"],
        "선선함": ["가벼운 바람막이", "가디건"],
        "따뜻함": [], # 겉옷 불필요
        "더움": [] # 겉옷 불필요
    },
    "액세서리": {
        "비": ["우산", "레인 부츠 (선택)"],
        "눈": ["장갑", "목도리", "방수 부츠", "귀마개"],
        "맑음": [],
        "흐림": [], # "구름 많음" 포함
        "매우 추움": ["목도리", "장갑", "털모자"],
        "추움": ["목도리", "장갑"],
        "더움": ["선글라스", "양산 (선택)"]
    }
}

def load_environment_variables() -> dict:
    """
    Loads environment variables from a .env file and validates their presence.
    Ensures all necessary API keys and credentials are set before proceeding.
    
    Raises:
        ValueError: If any required environment variable is not found.
    
    Returns:
        dict: A dictionary containing all loaded environment variables.
    """
    logging.info("환경 변수 로드를 시도합니다...")
    print("⚙️ 환경 변수를 로드하는 중...")
    load_dotenv() # Load variables from .env file

    # Define a list of all required environment variables.
    required_vars = [
        "OWM_API_KEY",
        "CITY_NAME",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "RECIPIENT_PHONE_NUMBER"
    ]
    env_vars = {}

    # Iterate through the required variables, get their values, and validate.
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            # Log an error and raise an exception if a variable is missing.
            logging.error(f"환경 변수 '{var}'가 설정되지 않았습니다. .env 파일을 확인하거나 환경 변수를 직접 설정해주세요.")
            raise ValueError(f"필수 환경 변수 누락: {var}")
        env_vars[var] = value
        logging.debug(f"환경 변수 '{var}' 로드 완료.") # Use debug for sensitive info if needed, or info for confirmation.
    
    logging.info("모든 환경 변수가 성공적으로 로드되었습니다.")
    print("✅ 환경 변수 로드 완료!")
    return env_vars

def get_tomorrow_weather(api_key: str, city_name: str) -> dict:
    """
    Fetches tomorrow's weather forecast (minimum/maximum temperature, overall condition) 
    for a given city using the OpenWeatherMap 5-day / 3-hour forecast API.
    
    Args:
        api_key (str): Your OpenWeatherMap API key.
        city_name (str): The name of the city to get the forecast for.
        
    Returns:
        dict: A dictionary containing tomorrow's weather information (date, min/max temp, condition, description).
              Returns an empty dictionary if fetching or parsing fails.
    """
    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city_name,         # City name for the forecast
        "appid": api_key,       # Your OpenWeatherMap API key
        "units": "metric",      # Temperature in Celsius
        "lang": "kr"            # Weather description in Korean
    }
    
    logging.info(f"'{city_name}'의 내일 날씨 정보를 조회합니다...")
    print(f"☁️ '{city_name}'의 내일 날씨 정보를 가져오는 중...")

    try:
        # Make an HTTP GET request to the OpenWeatherMap API with a timeout.
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status() # Raise an exception for bad HTTP status codes (4xx or 5xx).
        data = response.json()

        # Check for API-specific error codes in the response body.
        if data.get("cod") != "200":
            error_message = data.get('message', '알 수 없는 OpenWeatherMap API 오류')
            logging.error(f"OpenWeatherMap API 오류 발생 (Code: {data.get('cod')}): {error_message}")
            print(f"❌ 날씨 API에서 오류가 발생했습니다: {error_message}")
            return {}

        # Calculate tomorrow's date for filtering the forecast.
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        
        # Filter the forecast list to include only entries for tomorrow.
        tomorrow_forecasts = [
            item for item in data.get("list", [])
            if datetime.fromtimestamp(item["dt"]).date() == tomorrow
        ]

        if not tomorrow_forecasts:
            logging.warning(f"'{city_name}'에 대한 내일 날씨 데이터를 찾을 수 없습니다. API 응답을 다시 확인하세요.")
            print("⚠️ 내일 날씨 데이터를 찾을 수 없습니다. API 응답을 확인해주세요.")
            return {}

        min_temp = float('inf')  # Initialize with positive infinity for minimum comparison
        max_temp = float('-inf') # Initialize with negative infinity for maximum comparison
        weather_conditions = set() # Use a set to store unique weather conditions (e.g., 'rain', 'clear')

        # Iterate through tomorrow's forecasts to find min/max temperatures and aggregate conditions.
        for forecast in tomorrow_forecasts:
            temp = forecast["main"]["temp"]
            min_temp = min(min_temp, temp)
            max_temp = max(max_temp, temp)
            # Add the main weather condition (e.g., 'Rain', 'Clouds') in lowercase.
            weather_conditions.add(forecast["weather"][0]["main"].lower())

        # Determine the primary weather condition for the day based on aggregated conditions.
        main_condition = "맑음" # Default condition
        if "rain" in weather_conditions:
            main_condition = "비"
        elif "snow" in weather_conditions:
            main_condition = "눈"
        elif "thunderstorm" in weather_conditions: # Add thunderstorm
            main_condition = "천둥번개"
        elif "drizzle" in weather_conditions: # Add drizzle
            main_condition = "이슬비"
        elif "fog" in weather_conditions or "mist" in weather_conditions or "haze" in weather_conditions:
            main_condition = "안개"
        elif "clouds" in weather_conditions and "clear" in weather_conditions:
            main_condition = "구름 많음" # Mixed clouds and clear
        elif "clouds" in weather_conditions:
            main_condition = "흐림" # Only clouds

        weather_info = {
            "date": tomorrow.strftime("%Y-%m-%d"),
            "min_temp": round(min_temp), # Round temperatures to nearest integer
            "max_temp": round(max_temp),
            "condition": main_condition,
            # Use the description from the first available forecast entry for a general sense.
            "description": tomorrow_forecasts[0]["weather"][0]["description"]
        }
        logging.info(f"내일 날씨 정보 조회 성공: {weather_info}")
        print("✅ 날씨 정보 조회 완료!")
        return weather_info

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP 오류 발생 (날씨 정보 조회 중): {http_err}. 응답 코드: {http_err.response.status_code}")
        print(f"❌ HTTP 오류: 날씨 정보를 가져오는 데 실패했습니다. ({http_err.response.status_code})")
    except requests.exceptions.ConnectionError as conn_err:
        logging.error(f"네트워크 연결 오류 발생 (날씨 정보 조회 중): {conn_err}. 인터넷 연결을 확인하세요.")
        print(f"❌ 연결 오류: 인터넷 연결을 확인해주세요.")
    except requests.exceptions.Timeout as timeout_err:
        logging.error(f"요청 시간 초과 오류 발생 (날씨 정보 조회 중): {timeout_err}. API 서버가 응답하지 않거나 네트워크가 불안정합니다.")
        print(f"❌ 시간 초과: 날씨 API 응답이 너무 오래 걸립니다. 다시 시도해주세요.")
    except requests.exceptions.RequestException as req_err:
        logging.error(f"예상치 못한 요청 오류 발생 (날씨 정보 조회 중): {req_err}")
        print(f"❌ 요청 오류: 날씨 정보를 가져오는 중 예상치 못한 문제가 발생했습니다.")
    except KeyError as key_err:
        logging.error(f"날씨 API 응답에서 예상치 못한 키 오류 발생: {key_err}. API 응답 구조가 변경되었을 수 있습니다.")
        print(f"❌ 데이터 오류: 날씨 API 응답 형식이 예상과 다릅니다. (키 '{key_err}' 누락)")
    except Exception as e:
        logging.error(f"get_tomorrow_weather 함수에서 예상치 못한 오류 발생: {e}", exc_info=True)
        print(f"❌ 알 수 없는 오류: 날씨 정보 조회 중 문제가 발생했습니다. 로그를 확인하세요.")
    return {}

def get_temperature_category(temp: int) -> str:
    """
    Classifies a given temperature into predefined categories for outfit suggestions.
    
    Args:
        temp (int): The temperature in Celsius.
        
    Returns:
        str: The temperature category (e.g., "매우 추움", "추움", "따뜻함").
    """
    if temp <= -5:
        return "매우 추움"
    elif -5 < temp <= 5:
        return "추움"
    elif 5 < temp <= 12:
        return "쌀쌀함"
    elif 12 < temp <= 20:
        return "선선함"
    elif 20 < temp <= 27:
        return "따뜻함"
    else: # temp > 27
        return "더움"

def generate_outfit_suggestion(weather_info: dict) -> str:
    """
    Generates an outfit suggestion based on the provided weather information.
    This function simulates Gemma's fashion advice using a rule-based system.
    
    Args:
        weather_info (dict): A dictionary containing tomorrow's weather forecast.
                              Expected keys: "min_temp", "max_temp", "condition", "date", "description".
                                
    Returns:
        str: A formatted string containing the outfit suggestion and weather summary.
             Returns an error message if weather information is missing.
    """
    logging.info("날씨 정보 기반으로 코디 제안을 생성합니다...")
    print("👕 코디를 제안하는 중...")

    if not weather_info:
        logging.warning("날씨 정보가 없어 코디를 제안할 수 없습니다.")
        return "날씨 정보를 가져오는 데 실패하여 코디를 제안할 수 없습니다."

    min_temp = weather_info["min_temp"]
    max_temp = weather_info["max_temp"]
    condition = weather_info["condition"]

    logging.info(f"코디 생성 조건: 최저={min_temp}°C, 최고={max_temp}°C, 날씨='{condition}'")

    # Determine temperature categories for clothing layers.
    # We use max_temp for general daily wear comfort (상의, 하의)
    # and min_temp for outer layers or accessories that protect against colder conditions (외투, 일부 액세서리).
    main_temp_category = get_temperature_category(max_temp)
    min_temp_category = get_temperature_category(min_temp)

    suggestions = []

    # 1. Outerwear (외투): Based on the minimum temperature to ensure protection against the coldest part of the day.
    outerwear_options = WARDROBE["외투"].get(min_temp_category, [])
    if outerwear_options:
        suggestions.append(f"외투: {', '.join(outerwear_options)}")

    # 2. Tops (상의): Based on the maximum temperature for comfort during the warmest part of the day.
    top_options = WARDROBE["상의"].get(main_temp_category, [])
    if top_options:
        suggestions.append(f"상의: {', '.join(top_options)}")

    # 3. Bottoms (하의): Based on the maximum temperature for daily comfort.
    bottom_options = WARDROBE["하의"].get(main_temp_category, [])
    if bottom_options:
        suggestions.append(f"하의: {', '.join(bottom_options)}")

    # 4. Accessories (액세서리):
    # Start with condition-specific accessories (rain, snow).
    current_accessories = set()
    accessory_weather_key = condition
    
    # Map "구름 많음" to "흐림" for accessory lookup if specific accessories are not defined for it.
    if condition == "구름 많음" or condition == "이슬비" or condition == "안개" or condition == "천둥번개":
        # For these conditions, we might default to '흐림' or just specific conditions
        # '비' and '눈' are handled first.
        # Let's map "이슬비", "안개", "천둥번개" to "비" if that makes sense for accessories
        if condition in ["이슬비", "천둥번개"]:
            accessory_weather_key = "비"
        elif condition == "안개" or condition == "흐림" or condition == "구름 많음":
            accessory_weather_key = "흐림"

    if accessory_weather_key in WARDROBE["액세서리"]:
        current_accessories.update(WARDROBE["액세서리"][accessory_weather_key])
    
    # Add temperature-specific accessories (cold, hot) based on the min/max temp category.
    # Use min_temp_category for '매우 추움', '추움' as these are critical for warmth.
    if min_temp_category in ["매우 추움", "추움"]:
        current_accessories.update(WARDROBE["액세서리"].get(min_temp_category, []))
    
    # Use main_temp_category (based on max_temp) for '더움'.
    if main_temp_category == "더움":
        current_accessories.update(WARDROBE["액세서리"].get("더움", []))
    
    # Remove duplicates and add to suggestions if any.
    if current_accessories:
        suggestions.append(f"액세서리: {', '.join(sorted(list(current_accessories)))}")

    if not suggestions:
        logging.warning(f"내일 날씨 ({min_temp}~{max_temp}°C, {condition})에 맞는 코디 제안을 찾을 수 없습니다.")
        return f"내일 날씨 ({min_temp}~{max_temp}°C, {condition})에 맞는 코디를 찾기 어렵네요. 기본 복장을 준비해주세요!"

    # Construct the final message.
    base_message = (
        f"🌟 내일({weather_info['date']}) {weather_info['description']} 날씨 예보 "
        f"({min_temp}°C / {max_temp}°C) 룩북!\n"
    )
    outfit_message = "\n".join(suggestions)
    
    final_suggestion = base_message + outfit_message + "\n\n" + "💰 당신의 1달러를 위한 초저가 패션 예보입니다!"
    logging.info("코디 제안 생성 완료.")
    return final_suggestion


def send_sms(to_number: str, from_number: str, message_body: str, account_sid: str, auth_token: str) -> bool:
    """
    Sends an SMS message using the Twilio API.
    
    Args:
        to_number (str): The recipient's phone number (e.g., "+821012345678").
        from_number (str): Your Twilio phone number (e.g., "+1234567890").
        message_body (str): The content of the SMS message.
        account_sid (str): Your Twilio Account SID.
        auth_token (str): Your Twilio Auth Token.
        
    Returns:
        bool: True if the SMS was sent successfully, False otherwise.
    """
    logging.info(f"SMS 발송을 시도합니다. 수신자: {to_number}")
    print(f"📱 SMS를 {to_number} 번호로 발송하는 중...")
    try:
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            to=to_number,
            from_=from_number,
            body=message_body
        )
        logging.info(f"SMS가 성공적으로 발송되었습니다. 메시지 SID: {message.sid}")
        return True
    except TwilioRestException as twilio_err:
        logging.error(f"Twilio API 오류로 SMS 발송에 실패했습니다: {twilio_err}")
        print(f"❌ SMS 발송 실패: Twilio 오류 ({twilio_err})")
    except Exception as e:
        logging.error(f"SMS 발송 중 예상치 못한 오류 발생: {e}", exc_info=True)
        print(f"❌ SMS 발송 실패: 예상치 못한 오류 ({e})")
    return False

def main():
    """
    Main function to run the Gemma-on-Xeon's 1달러 룩북 SMS service.
    It orchestrates loading environment variables, fetching weather, generating outfits, and sending SMS.
    """
    logging.info("--- Gemma-on-Xeon's 1달러 룩북 SMS 서비스 시작 ---")
    print("\n--- 💰 Gemma-on-Xeon's 1달러 룩북 SMS 서비스 시작 💰 ---")
    
    try:
        # 1. Load environment variables
        env_vars = load_environment_variables()
        owm_api_key = env_vars["OWM_API_KEY"]
        city_name = env_vars["CITY_NAME"]
        twilio_sid = env_vars["TWILIO_ACCOUNT_SID"]
        twilio_token = env_vars["TWILIO_AUTH_TOKEN"]
        twilio_phone_number = env_vars["TWILIO_PHONE_NUMBER"]
        recipient_phone_number = env_vars["RECIPIENT_PHONE_NUMBER"]

        # 2. Get tomorrow's weather forecast
        weather_data = get_tomorrow_weather(owm_api_key, city_name)
        if not weather_data:
            logging.error("날씨 정보를 가져오는 데 실패하여 서비스를 중단합니다.")
            print("❌ 오류: 날씨 정보를 가져오는 데 실패했습니다. 로그를 확인하세요.")
            return # Exit if weather data is not available

        # 3. Generate outfit suggestion
        outfit_suggestion = generate_outfit_suggestion(weather_data)
        logging.info(f"생성된 코디 제안:\n{outfit_suggestion.strip()}") # strip to clean up logs if extra newlines

        print("\n--- 오늘의 Gemma-on-Xeon 룩북 SMS 내용 미리보기 ---")
        print(outfit_suggestion)
        print("--------------------------------------------------\n")

        # 4. Send SMS
        if send_sms(recipient_phone_number, twilio_phone_number, outfit_suggestion, twilio_sid, twilio_token):
            print(f"✅ SMS가 성공적으로 {recipient_phone_number} 번호로 발송되었습니다!")
        else:
            print(f"❌ 오류: SMS 발송에 실패했습니다. 로그를 확인하세요.")

    except ValueError as ve:
        # Catches errors from load_environment_variables if a variable is missing.
        logging.critical(f"초기화 오류: {ve}. 프로그램 실행을 중단합니다.", exc_info=True)
        print(f"❌ 치명적인 오류: 서비스 초기화에 실패했습니다. {ve}. .env 파일을 확인해주세요.")
    except Exception as e:
        # Catches any other unexpected errors during the main execution flow.
        logging.critical(f"예상치 못한 치명적인 오류가 발생했습니다: {e}", exc_info=True)
        print(f"❌ 예상치 못한 치명적인 오류 발생: {e}. 자세한 내용은 로그를 확인하세요.")

    logging.info("--- Gemma-on-Xeon's 1달러 룩북 SMS 서비스 종료 ---")
    print("\n--- 💰 Gemma-on-Xeon's 1달러 룩북 SMS 서비스 종료 💰 ---")

if __name__ == "__main__":
    main()
