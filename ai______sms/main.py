import requests
import os
from datetime import datetime, timedelta
import pytz # For timezone handling, crucial for accurate "tomorrow" calculation
from dotenv import load_dotenv
from twilio.rest import Client
import json # To pretty print weather data if needed for debugging
from typing import Dict, Any, Optional

# --- 1. 환경 변수 로드 ---
def load_environment_variables() -> Optional[Dict[str, str]]:
    """
    .env 파일에서 환경 변수를 로드하고 필요한 변수들이 설정되었는지 확인합니다.
    모든 필수 변수가 로드되면 딕셔너리를 반환하고, 누락된 변수가 있으면 프로그램을 종료합니다.
    """
    print("[환경 설정] .env 파일에서 환경 변수를 로드합니다.")
    load_dotenv()
    
    required_vars = [
        "OPENWEATHER_API_KEY", "OPENWEATHER_CITY_ID", "TIMEZONE",
        "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", 
        "TWILIO_FROM_NUMBER", "TWILIO_TO_NUMBER"
    ]
    
    env_vars: Dict[str, str] = {}
    missing_vars = []

    for var in required_vars:
        value = os.getenv(var)
        if value is None:
            missing_vars.append(var)
        env_vars[var] = value # None 값도 일단 저장하여 누락 여부와 관계없이 딕셔너리에 추가

    if missing_vars:
        print(f"[오류] 다음 필수 환경 변수가 .env 파일에 없거나 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("[환경 설정] 프로그램을 종료합니다. .env 파일을 확인하고 다시 시도해주세요.")
        return None # main 함수에서 이 반환값을 체크하여 종료
    
    print("[환경 설정] 모든 필수 환경 변수가 성공적으로 로드되었습니다.")
    # 민감 정보는 로그로 출력하지 않도록 주의
    print(f"[환경 설정] OpenWeather City ID: {env_vars['OPENWEATHER_CITY_ID']}")
    print(f"[환경 설정] Timezone: {env_vars['TIMEZONE']}")
    print(f"[환경 설정] Twilio From Number: {env_vars['TWILIO_FROM_NUMBER']}")
    print(f"[환경 설정] Twilio To Number: {env_vars['TWILIO_TO_NUMBER']}")

    return env_vars

# --- 2. 날씨 데이터 가져오기 ---
def get_weather_data(city_id: str, api_key: str) -> Optional[Dict[str, Any]]:
    """
    OpenWeatherMap 5일 / 3시간 예보 데이터를 가져옵니다.
    API 요청에 실패하거나 데이터를 파싱할 수 없을 경우 None을 반환합니다.
    """
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "id": city_id,
        "appid": api_key,
        "units": "metric", # 섭씨 온도로 받음
        "lang": "kr"       # 한국어 날씨 설명
    }
    
    print(f"[날씨 정보] OpenWeatherMap API에서 도시 ID '{city_id}'의 5일/3시간 날씨 데이터를 요청합니다.")
    print(f"[날씨 정보] 요청 URL: {base_url}?id={city_id}&appid=***&units=metric&lang=kr") # API Key 숨김

    try:
        response = requests.get(base_url, params=params, timeout=15) # 15초 타임아웃 설정 (기존 10초에서 조금 늘림)
        response.raise_for_status() # 4xx 또는 5xx HTTP 응답 코드에 대해 예외 발생

        data = response.json()
        print(f"[날씨 정보] 날씨 데이터를 성공적으로 가져왔습니다. 총 {len(data.get('list', []))}개의 예보 항목 포함.")
        return data
    except requests.exceptions.HTTPError as e:
        print(f"[오류] OpenWeatherMap API HTTP 오류 발생: {e.response.status_code} - {e.response.reason}")
        print(f"[오류] 응답 본문: {e.response.text}")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"[오류] OpenWeatherMap API 연결 오류 발생. 네트워크 상태를 확인하세요: {e}")
        return None
    except requests.exceptions.Timeout as e:
        print(f"[오류] OpenWeatherMap API 요청 시간 초과 (15초). 서버 응답이 지연되거나 네트워크 문제일 수 있습니다: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[오류] OpenWeatherMap API 요청 중 알 수 없는 오류 발생: {type(e).__name__} - {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"[오류] OpenWeatherMap API 응답을 JSON으로 파싱하는 데 실패했습니다: {e}")
        print(f"[오류] 수신된 텍스트: {response.text}")
        return None

# --- 3. 내일 날씨 예보 추출 및 분석 ---
def get_tomorrow_forecast(weather_data: Dict[str, Any], timezone_str: str) -> Optional[Dict[str, Any]]:
    """
    가져온 날씨 데이터에서 내일의 최소/최대 기온, 평균 기온, 주요 날씨 조건, 강수 확률을 추출하고 분석합니다.
    타임존을 정확히 반영하여 '내일'을 정의하고 해당 시간대의 예보만 필터링합니다.
    """
    if not weather_data or 'list' not in weather_data:
        print("[날씨 분석] 유효한 날씨 데이터가 없거나 'list' 키가 누락되었습니다. 분석을 건너뜝니다.")
        return None

    try:
        # 1. 타임존 설정 및 내일 날짜 범위 계산
        tz = pytz.timezone(timezone_str)
        print(f"[날씨 분석] 타임존 '{timezone_str}'을(를) 사용하여 내일 날짜 범위를 계산합니다.")
        
        # 현재 로컬 시간 기준으로 내일 날짜를 얻음
        now_local = datetime.now(tz)
        tomorrow_local = now_local + timedelta(days=1)
        
        # 내일 00:00:00부터 23:59:59까지의 예보를 필터링하기 위한 범위 설정
        tomorrow_start = tomorrow_local.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_end = tomorrow_local.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        print(f"[날씨 분석] 내일 날짜 범위: {tomorrow_start.strftime('%Y-%m-%d %H:%M:%S %Z%z')} ~ {tomorrow_end.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")

        # 2. 내일 예보 항목 필터링
        tomorrow_forecasts = []
        for item in weather_data['list']:
            dt_txt = item['dt_txt'] # 예: '2023-10-27 12:00:00' (UTC 시간으로 가정)
            # OpenWeatherMap API는 dt_txt를 UTC로 제공하며, 실제 예보 시간은 해당 UTC 시간을 기준으로 함.
            # 이를 지정된 로컬 타임존으로 변환하여 내일 범위에 속하는지 확인
            forecast_time_utc = datetime.strptime(dt_txt, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)
            forecast_time_local = forecast_time_utc.astimezone(tz)
            
            if tomorrow_start <= forecast_time_local <= tomorrow_end:
                tomorrow_forecasts.append(item)
                # print(f"[날씨 분석] 내일 예보 포함: {forecast_time_local.strftime('%Y-%m-%d %H:%M:%S')}, 기온: {item['main']['temp']:.1f}°C")

        if not tomorrow_forecasts:
            print(f"[날씨 분석] 내일 ({tomorrow_local.strftime('%Y-%m-%d')}) 날짜에 해당하는 예보 데이터를 찾을 수 없습니다. (총 {len(weather_data['list'])}개 예보 중)")
            print("[날씨 분석] OpenWeatherMap 5일 예보는 약 3시간 간격이므로, 내일 데이터가 없을 경우도 있습니다. 프로그램을 종료합니다.")
            return None
        
        print(f"[날씨 분석] 내일 ({tomorrow_local.strftime('%Y-%m-%d')}) 예보 항목 {len(tomorrow_forecasts)}개를 찾았습니다. 데이터 분석을 시작합니다.")

        # 3. 내일의 기온, 날씨 조건 등 집계
        min_temp = float('inf')
        max_temp = float('-inf')
        total_temp = 0.0
        weather_conditions: Dict[str, int] = {} # { "Clouds": count, "Rain": count }
        pop_sum = 0.0 # 강수 확률 (Probability of Precipitation) 합계 (0.0 ~ 1.0 사이 값)

        for item in tomorrow_forecasts:
            temp = item['main']['temp']
            min_temp = min(min_temp, item['main']['temp_min'])
            max_temp = max(max_temp, item['main']['temp_max'])
            total_temp += temp
            
            main_weather = item['weather'][0]['main'] # 'Clouds', 'Rain', 'Clear' 등
            weather_conditions[main_weather] = weather_conditions.get(main_weather, 0) + 1
            
            # OpenWeatherMap의 'pop' (Probability of Precipitation)은 0.0에서 1.0 사이의 값
            pop_sum += item.get('pop', 0.0) 

        # 4. 집계된 데이터로 최종 값 계산
        avg_temp = total_temp / len(tomorrow_forecasts)
        
        # 가장 빈번한 날씨 조건 선택
        most_common_weather = max(weather_conditions, key=weather_conditions.get) if weather_conditions else "날씨 정보 없음"
        
        # 전체 강수 확률 평균 (0-100% 스케일로 변환)
        avg_pop = (pop_sum / len(tomorrow_forecasts)) * 100 if tomorrow_forecasts else 0.0

        print(f"[날씨 분석] 내일 ({tomorrow_local.strftime('%Y-%m-%d')}) 예보 요약 결과:")
        print(f"  - 최저 기온: {min_temp:.1f}°C")
        print(f"  - 최고 기온: {max_temp:.1f}°C")
        print(f"  - 평균 기온: {avg_temp:.1f}°C")
        print(f"  - 주요 날씨: {most_common_weather}")
        print(f"  - 강수 확률: {avg_pop:.1f}%")

        return {
            "min_temp": min_temp,
            "max_temp": max_temp,
            "avg_temp": avg_temp,
            "weather_condition": most_common_weather,
            "precipitation_chance": avg_pop
        }
    except pytz.exceptions.UnknownTimeZoneError:
        print(f"[오류] 유효하지 않은 타임존 '{timezone_str}'이(가) 설정되었습니다.")
        print("[오류] pytz 라이브러리에서 인식하는 타임존 이름을 사용하세요 (예: 'Asia/Seoul', 'America/New_York').")
        return None
    except KeyError as e:
        print(f"[오류] 날씨 데이터 구조에 예상치 못한 키가 누락되었습니다: {e}. OpenWeatherMap API 응답 형식을 확인하세요.")
        # print(f"[디버그] 전체 날씨 데이터: {json.dumps(weather_data, indent=2)}") # 디버깅 시 유용
        return None
    except TypeError as e:
        print(f"[오류] 날씨 데이터 처리 중 타입 오류 발생: {e}. 데이터 형식이 예상과 다를 수 있습니다.")
        return None
    except Exception as e:
        print(f"[오류] 내일 날씨 예보 추출 및 분석 중 예기치 않은 오류 발생: {type(e).__name__} - {e}")
        return None

# --- 4. 옷차림 추천 AI (규칙 기반) ---
def recommend_outfit(min_temp: float, max_temp: float, avg_temp: float, weather_condition: str, precipitation_chance: float) -> str:
    """
    기온과 날씨 조건에 따라 옷차림을 추천합니다.
    보다 상세하고 사용자 친화적인 메시지를 생성합니다.
    """
    outfit_parts = []
    
    print(f"[옷차림 추천] 분석 시작 - 기온: (최저 {min_temp:.1f}°C, 최고 {max_temp:.1f}°C, 평균 {avg_temp:.1f}°C), 날씨: '{weather_condition}', 강수 확률: {precipitation_chance:.1f}%")

    # 4.1. 기온 기반 추천
    print("[옷차림 추천] 기온에 따른 기본 옷차림을 결정합니다.")
    if avg_temp <= 4:
        outfit_parts.append("❄️ 아주 추워요! 두꺼운 패딩, 롱 코트, 목도리, 장갑, 모자 등으로 최대한 따뜻하게 무장하세요.")
        print("[옷차림 추천] - '매우 추움' 규칙 적용 (평균 4°C 이하)")
    elif 5 <= avg_temp <= 9:
        outfit_parts.append("🧥 쌀쌀한 날씨입니다. 코트, 가죽 재킷, 히트텍, 두꺼운 니트, 경량 패딩 등으로 체온 유지에 신경 쓰세요.")
        print("[옷차림 추천] - '쌀쌀함' 규칙 적용 (평균 5°C ~ 9°C)")
    elif 10 <= avg_temp <= 16:
        outfit_parts.append("🍁 선선한 가을/봄 날씨입니다. 트렌치코트, 재킷, 가디건, 니트, 맨투맨이 적당해요.")
        print("[옷차림 추천] - '선선함' 규칙 적용 (평균 10°C ~ 16°C)")
    elif 17 <= avg_temp <= 22:
        outfit_parts.append("👕 활동하기 좋은 쾌적한 날씨입니다. 얇은 가디건, 긴팔 티셔츠, 면바지, 청바지 등을 추천합니다.")
        print("[옷차림 추천] - '쾌적함' 규칙 적용 (평균 17°C ~ 22°C)")
    elif 23 <= avg_temp <= 27:
        outfit_parts.append("🌞 조금 더운 날씨입니다. 반팔 티셔츠, 얇은 셔츠, 반바지, 치마 등 가벼운 옷차림이 좋아요.")
        print("[옷차림 추천] - '조금 더움' 규칙 적용 (평균 23°C ~ 27°C)")
    else: # avg_temp >= 28
        outfit_parts.append("🔥 매우 더운 날씨입니다. 민소매, 반팔 티셔츠, 반바지 등 시원한 소재의 옷을 입고 양산이나 모자를 챙겨 햇볕을 피하세요.")
        print("[옷차림 추천] - '매우 더움' 규칙 적용 (평균 28°C 이상)")

    # 4.2. 날씨 조건 기반 추가 추천
    print("[옷차림 추천] 날씨 조건에 따른 추가 조언을 확인합니다.")
    if "Rain" in weather_condition or precipitation_chance >= 40:
        outfit_parts.append("🌧️ 비 소식이 있거나 강수 확률이 높습니다. 우산이나 레인코트를 꼭 챙기세요!")
        print(f"[옷차림 추천] - '비/높은 강수 확률' 규칙 적용 (날씨: {weather_condition}, 강수확률: {precipitation_chance:.1f}%)")
        if avg_temp < 10:
            outfit_parts.append("💧 기온이 낮으니 방수 기능이 있는 따뜻한 아우터를 입는 것도 좋은 선택입니다.")
            print("[옷차림 추천] - '저온 비' 추가 규칙 적용")
    elif "Snow" in weather_condition:
        outfit_parts.append("🌨️ 눈이 올 가능성이 있습니다. 미끄럼 방지 기능이 있는 신발과 따뜻한 방한복을 챙겨주세요.")
        print(f"[옷차림 추천] - '눈' 규칙 적용 (날씨: {weather_condition})")
    elif "Clear" in weather_condition and avg_temp > 20:
        outfit_parts.append("☀️ 화창한 날씨가 예상됩니다. 자외선 차단제를 바르고 선글라스를 착용하여 눈과 피부를 보호하세요.")
        print(f"[옷차림 추천] - '맑고 더움' 규칙 적용 (날씨: {weather_condition}, 평균: {avg_temp:.1f}°C)")
    elif "Clouds" in weather_condition and avg_temp < 15:
         outfit_parts.append("☁️ 구름이 많아 다소 흐리고 쌀쌀하게 느껴질 수 있습니다. 얇은 겉옷을 준비하면 좋아요.")
         print(f"[옷차림 추천] - '흐리고 쌀쌀함' 규칙 적용 (날씨: {weather_condition}, 평균: {avg_temp:.1f}°C)")
    elif "Mist" in weather_condition or "Fog" in weather_condition:
        outfit_parts.append("🌫️ 안개나 박무가 예상됩니다. 시야 확보에 유의하시고, 운전 시에는 안전 운전하세요.")
        print(f"[옷차림 추천] - '안개' 규칙 적용 (날씨: {weather_condition})")

    recommendation = " ".join(outfit_parts)
    print(f"[옷차림 추천] 최종 옷차림 추천 메시지가 생성되었습니다.")
    return recommendation

# --- 5. SMS 알림 보내기 ---
def send_sms(to_number: str, from_number: str, message_body: str, account_sid: str, auth_token: str) -> bool:
    """
    Twilio API를 사용하여 SMS 메시지를 보냅니다.
    메시지 전송 성공 여부를 True/False로 반환합니다.
    """
    print(f"[SMS 알림] SMS 메시지를 수신자 {to_number} (발신: {from_number}) 로 보낼 준비 중입니다.")
    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            to=to_number,
            from_=from_number,
            body=message_body
        )
        print(f"[SMS 알림] SMS 메시지 전송 성공! 메시지 SID: {message.sid}")
        return True
    except Exception as e:
        print(f"[오류] SMS 메시지 전송 실패: {type(e).__name__} - {e}")
        print(f"[오류] Twilio 계정 SID, 인증 토큰, 발신/수신 번호가 정확한지 확인해 주세요.")
        return False

# --- 메인 실행 로직 ---
def main():
    """
    AI 내일 날씨 맞춤형 옷차림 알리미 SMS 시스템의 주요 실행 로직입니다.
    단계별로 환경 변수 로드, 날씨 데이터 획득, 예보 분석, 옷차림 추천, SMS 발송을 수행합니다.
    """
    print("======================================================================")
    print("              🤖 AI 내일 날씨 맞춤형 옷차림 알리미 SMS 시스템 시작 🤖")
    print("======================================================================")

    # 1. 환경 변수 로드
    print("\n[메인 프로세스] 1단계: 환경 변수를 로드합니다.")
    env_vars = load_environment_variables()
    if env_vars is None:
        print("[메인 프로세스] 환경 변수 로드 실패. 프로그램을 종료합니다.")
        return # load_environment_variables에서 이미 오류 메시지 출력됨

    OPENWEATHER_API_KEY = env_vars["OPENWEATHER_API_KEY"]
    OPENWEATHER_CITY_ID = env_vars["OPENWEATHER_CITY_ID"]
    TIMEZONE = env_vars["TIMEZONE"]
    TWILIO_ACCOUNT_SID = env_vars["TWILIO_ACCOUNT_SID"]
    TWILIO_AUTH_TOKEN = env_vars["TWILIO_AUTH_TOKEN"]
    TWILIO_FROM_NUMBER = env_vars["TWILIO_FROM_NUMBER"]
    TWILIO_TO_NUMBER = env_vars["TWILIO_TO_NUMBER"]

    # 2. 날씨 데이터 가져오기
    print("\n[메인 프로세스] 2단계: OpenWeatherMap API에서 날씨 데이터를 가져옵니다.")
    weather_data = get_weather_data(OPENWEATHER_CITY_ID, OPENWEATHER_API_KEY)
    if weather_data is None:
        print("[메인 프로세스] 날씨 데이터를 가져오는 데 실패했습니다. 프로그램을 종료합니다.")
        return

    # 3. 내일 날씨 예보 추출 및 분석
    print("\n[메인 프로세스] 3단계: 가져온 날씨 데이터에서 내일 예보를 추출하고 분석합니다.")
    tomorrow_forecast = get_tomorrow_forecast(weather_data, TIMEZONE)
    if tomorrow_forecast is None:
        print("[메인 프로세스] 내일 날씨 예보를 분석하는 데 실패했습니다. 프로그램을 종료합니다.")
        return

    # 4. 옷차림 추천 AI
    print("\n[메인 프로세스] 4단계: 분석된 내일 날씨를 기반으로 옷차림을 추천합니다.")
    outfit_recommendation = recommend_outfit(
        tomorrow_forecast["min_temp"],
        tomorrow_forecast["max_temp"],
        tomorrow_forecast["avg_temp"],
        tomorrow_forecast["weather_condition"],
        tomorrow_forecast["precipitation_chance"]
    )
    
    # 5. SMS 메시지 생성
    print("\n[메인 프로세스] 5단계: 전송할 SMS 메시지 내용을 구성합니다.")
    try:
        tz = pytz.timezone(TIMEZONE)
        tomorrow_local = (datetime.now(tz) + timedelta(days=1)).strftime('%Y년 %m월 %d일')
    except pytz.exceptions.UnknownTimeZoneError:
        print(f"[오류] SMS 메시지 생성 중 타임존 '{TIMEZONE}' 오류 발생. 기본 날짜 형식으로 진행합니다.")
        tomorrow_local = (datetime.now() + timedelta(days=1)).strftime('%Y년 %m월 %d일') # Fallback to naive datetime
    except Exception as e:
        print(f"[오류] SMS 메시지 날짜 형식화 중 오류 발생: {e}. 기본 날짜 형식으로 진행합니다.")
        tomorrow_local = (datetime.now() + timedelta(days=1)).strftime('%Y년 %m월 %d일')

    sms_message = (
        f"🤖 오또의 내일({tomorrow_local}) 날씨 알림 🤖\n\n"
        f"✅ 기온: 최저 {tomorrow_forecast['min_temp']:.1f}°C / 최고 {tomorrow_forecast['max_temp']:.1f}°C (평균 {tomorrow_forecast['avg_temp']:.1f}°C)\n"
        f"✅ 날씨: {tomorrow_forecast['weather_condition']}\n"
        f"✅ 강수확률: {tomorrow_forecast['precipitation_chance']:.1f}%\n\n"
        f"✨ 오또의 추천 옷차림 ✨\n"
        f"{outfit_recommendation}\n\n"
        f"오늘도 좋은 하루 보내세요! 😊"
    )
    print("\n--- 전송될 SMS 메시지 내용 미리보기 ---")
    print(sms_message)
    print("--------------------------------------\n")

    # 6. SMS 알림 보내기
    print("\n[메인 프로세스] 6단계: Twilio를 통해 SMS 알림을 보냅니다.")
    send_success = send_sms(TWILIO_TO_NUMBER, TWILIO_FROM_NUMBER, sms_message, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    if send_success:
        print("[메인 프로세스] SMS 알림 전송 프로세스가 성공적으로 완료되었습니다.")
    else:
        print("[메인 프로세스] SMS 알림 전송에 실패했습니다. Twilio 설정을 다시 확인해 주세요.")

    print("\n======================================================================")
    print("              ✅ AI 내일 날씨 맞춤형 옷차림 알리미 SMS 시스템 종료 ✅")
    print("======================================================================")

if __name__ == "__main__":
    main()
