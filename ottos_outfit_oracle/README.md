# 👕 옷또입지? (Otto's Outfit Oracle)

> 🆕 **v2 UPDATE (2026-07-23)**: 유료 API 키(OpenWeather·Twilio) 의존을 전부 제거했습니다!
> 이제 **가입도 키도 필요 없는 무료 날씨 API(open-meteo)**로 내일 날씨를 실측 조회하고,
> SNS 공유 가능한 **코디 카드 이미지(PNG)**를 저장합니다. `python main.py` 한 줄이면 끝!

안녕하세요! 저는 천재 개발자 에이전트 '오또'입니다. 매일 아침 '오늘은 뭐 입지?' 고민에 빠져 계신가요? 이제 걱정하지 마세요! '옷또입지?' 프로젝트가 당신의 패션 고민을 해결해 드립니다.

매일 밤, '오또'가 내일 날씨의 'uni-context' (온도, 습도, 강수량 등)를 꼼꼼히 분석하여 당신에게 가장 적합한 '시그니처 룩'을 제안해 드립니다. 이 모든 정보는 당신의 휴대폰으로 SMS 메시지로 도착합니다. 이제 날씨 맞춤형 코디를 '오또'에게 맡기고, 당신의 소중한 시간을 절약하세요!

## ✨ 주요 기능

1.  **자동 날씨 데이터 분석**: 지정된 지역의 내일 날씨(최저/최고 온도, 습도, 강수확률 등)를 OpenWeatherMap API를 통해 매일 자동으로 가져와 분석합니다.
2.  **AI 기반 옷차림 추천**: 분석된 날씨 데이터를 기반으로 '오또'만의 룰(rule-based AI)에 따라 최적의 옷차림을 추천합니다.
3.  **SMS 알림 서비스**: 개인 휴대폰으로 매일 전날 저녁 또는 아침, 추천된 옷차림 정보 SMS를 발송합니다 (Twilio API 사용).

## 🚀 시작하기

이 프로젝트를 실행하기 위한 단계별 가이드입니다.

### 📝 전제 조건

*   **Python 3.8 이상**: [Python 공식 웹사이트](https://www.python.org/downloads/)에서 다운로드 및 설치할 수 있습니다.
*   **OpenWeatherMap API Key**: [OpenWeatherMap](https://openweathermap.org/api) 웹사이트에서 계정을 생성하고 API Key를 발급받으세요. `One Call API 3.0`을 사용합니다.
*   **Twilio 계정 및 정보**: [Twilio](https://www.twilio.com/) 웹사이트에서 계정을 생성하고 다음 정보를 준비하세요:
    *   `ACCOUNT_SID`
    *   `AUTH_TOKEN`
    *   `Twilio Phone Number` (SMS 발송용으로 구매해야 합니다.)
*   **수신할 휴대폰 번호**: SMS 메시지를 받을 당신의 휴대폰 번호.

### 💻 개발 환경 설정

1.  **프로젝트 클론 (선택 사항)** 또는 파일 다운로드:
    ```bash
    git clone [repository_url]
    cd [project_directory]
    ```
    (이 프로젝트는 단일 파일이므로 파일을 직접 생성해도 무방합니다.)

2.  **가상 환경 생성 및 활성화**: 프로젝트 의존성을 격리하기 위해 가상 환경을 사용하는 것이 좋습니다.

    ```bash
    python3 -m venv venv
    # macOS/Linux
    source venv/bin/activate
    # Windows
    .\venv\Scripts\activate
    ```

3.  **필요한 라이브러리 설치**: `requirements.txt` 파일에 명시된 라이브러리를 설치합니다.

    ```bash
    pip install -r requirements.txt
    ```

### 🔑 환경 변수 설정 (.env 파일)

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 정보를 입력하세요. (값은 실제 당신의 정보로 대체해야 합니다.)

```env
# OpenWeatherMap API 설정
OPENWEATHER_API_KEY="YOUR_OPENWEATHER_API_KEY"
CITY_NAME="Seoul"       # 날씨 정보를 얻을 도시 이름 (예: Seoul, New York)
COUNTRY_CODE="KR"       # 도시가 속한 국가 코드 (ISO 3166 코드, 예: KR, US)

# Twilio SMS 설정
TWILIO_ACCOUNT_SID="YOUR_TWILIO_ACCOUNT_SID"
TWILIO_AUTH_TOKEN="YOUR_TWILIO_AUTH_TOKEN"
TWILIO_PHONE_NUMBER="+1234567890" # Twilio에서 발급받은 전화번호 (반드시 '+'로 시작)
RECIPIENT_PHONE_NUMBER="+1987654321" # SMS를 받을 휴대폰 번호 (반드시 '+'로 시작)
```

> **중요**: `TWILIO_PHONE_NUMBER`와 `RECIPIENT_PHONE_NUMBER`는 반드시 국가 코드와 함께 `+`로 시작하는 E.164 형식이어야 합니다. (예: 한국 번호는 `+8210xxxxxxxx`)

### ▶️ 프로젝트 실행 방법

**수동 실행 (테스트용)**

가상 환경이 활성화된 상태에서 `main.py` 파일을 직접 실행합니다.

```bash
python main.py
```

콘솔에 날씨 조회 및 옷차림 추천 로그가 출력되며, Twilio를 통해 SMS가 발송됩니다.

**자동 실행 (매일 알림)**

이 스크립트는 매일 특정 시간에 자동으로 실행되도록 스케줄링할 수 있습니다. `cron` (Linux/macOS) 또는 Windows 작업 스케줄러를 사용하는 것을 권장합니다.

**cron (Linux/macOS) 예시:**

1.  `crontab` 편집기를 엽니다:
    ```bash
    crontab -e
    ```

2.  파일의 마지막에 다음 줄을 추가합니다. (예시는 매일 오전 8시에 실행하는 설정이며, 경로를 실제 경로로 변경해야 합니다.)

    ```cron
    # 매일 오전 8시에 '옷또입지?' 실행
    0 8 * * * /usr/bin/python3 /path/to/your/project/venv/bin/python /path/to/your/project/main.py >> /path/to/your/project/otto_outfit_log.log 2>&1
    ```

    *   `/usr/bin/python3`: 당신의 시스템에 설치된 Python 실행 경로. `which python3` 또는 `where python3`로 확인할 수 있습니다.
    *   `/path/to/your/project/venv/bin/python`: 가상 환경 내의 Python 인터프리터 경로.
    *   `/path/to/your/project/main.py`: `main.py` 파일의 전체 경로.
    *   `>> /path/to/your/project/otto_outfit_log.log 2>&1`: 실행 로그를 파일에 기록하고, 에러도 함께 기록합니다.

3.  저장하고 종료합니다.

**Windows 작업 스케줄러:**

Windows의 경우, '작업 스케줄러'를 이용하여 `main.py` 스크립트를 매일 특정 시간에 실행하도록 설정할 수 있습니다. 자세한 설정 방법은 [Microsoft 문서](https://docs.microsoft.com/ko-kr/windows/win32/taskschd/creating-tasks)를 참고하세요.

## 🎨 커스터마이징

*   **도시 변경**: `.env` 파일의 `CITY_NAME`과 `COUNTRY_CODE` 값을 변경하여 다른 지역의 날씨를 받아볼 수 있습니다.
*   **옷차림 추천 로직 변경**: `recommend_outfit` 함수 내부의 온도별/날씨별 옷차림 추천 룰을 수정하여 당신의 취향에 맞는 코디를 만들 수 있습니다.
*   **SMS 발송 시간**: `cron` 또는 작업 스케줄러 설정을 변경하여 SMS를 받는 시간을 조절할 수 있습니다.

## ❓ 문제 해결

*   **SMS가 오지 않아요**: 
    *   `.env` 파일에 모든 Twilio 관련 정보(SID, Auth Token, Twilio 전화번호, 수신자 전화번호)가 올바르게 설정되었는지 확인하세요.
    *   전화번호가 `+국가코드전화번호` 형식(예: `+821012345678`)으로 되어 있는지 확인하세요.
    *   Twilio 계정에 잔액이 충분한지, 발신 가능한 번호인지 확인하세요.
    *   스크립트 실행 시 콘솔에 Twilio 오류 메시지가 출력되는지 확인하세요.
*   **날씨 정보를 가져올 수 없어요**: 
    *   `.env` 파일의 `OPENWEATHER_API_KEY`가 올바른지 확인하세요.
    *   `CITY_NAME`과 `COUNTRY_CODE`가 올바른지, OpenWeatherMap에서 지원하는 이름인지 확인하세요.
    *   인터넷 연결이 정상적인지 확인하세요.
    *   OpenWeatherMap One Call API 3.0은 유료일 수 있습니다. 계정의 플랜을 확인하거나, 무료 Plan에서 사용하는 API가 맞는지 확인해야 합니다. (이 코드에서는 Free Tier에서 사용 가능한 `GeoCoding API`와 `One Call API 3.0`을 사용합니다. `One Call API 3.0`은 일부 무료 사용 제한이 있을 수 있으니, 요금 정책을 확인하는 것이 좋습니다.)

오또와 함께 스마트한 패션 생활을 즐기세요! 🤖👗👔