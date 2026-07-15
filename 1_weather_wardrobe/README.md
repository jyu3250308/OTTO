# 💸 오또의 1달러 Weather Wardrobe: 내일 뭐 입을지 AI SMS로! 💸

## 🎯 프로젝트 목적
매일 아침 '오늘 뭐 입지?' 고민에 시간을 낭비하시나요? 이제 천재 개발자 에이전트 오또 AI가 실시간 날씨 데이터와 독자적인 'Grok My Wardrobe' 알고리즘으로 당신의 $1 가치 패션 센스를 강제 주입해 드립니다! 유료 SMS 콘셉트로 매일 아침 옷차림 추천을 받으세요. (물론 과금은 농담입니다... 😉)

## ✨ 주요 기능
*   **AI 기반 날씨 파싱 & 패션 분석:** OpenWeatherMap API를 통해 내일의 최저/최고 기온, 강수 확률을 실시간으로 분석합니다. 이 데이터를 기반으로 가장 적합하고 유쾌한 옷차림을 추천합니다.
*   **$1 과금형 SMS 전송 (시뮬레이션):** 사용자에게 '선택의 자유'를 강탈하는 유료 SMS 콘셉트로 아침마다 옷차림 추천 메시지를 푸시합니다. 실제 SMS 전송은 Twilio 서비스를 활용합니다.
*   **'Grok-ish' 패션 트렌드 반영:** 단순 날씨 정보를 넘어, AI가 밈 트렌드까지 읽어 쇼츠용 코믹 드립이 섞인 패션 추천 메시지를 생성합니다. 당신의 하루를 유쾌하게 시작해 보세요!

## ⚙️ 작동 방식
1.  Python 스크립트가 실행되면, `.env` 파일에 설정된 도시에 대해 OpenWeatherMap API에서 내일의 날씨 예보를 안전하게 가져옵니다.
2.  가져온 날씨 데이터(최저/최고 기온, 강수 확률, 날씨 설명)를 기반으로 내장된 'Grok My Wardrobe' 알고리즘이 최적의 옷차림 추천을 생성합니다.
3.  여기에 랜덤으로 선정된 'Grok-ish' 패션 드립을 추가하여 최종 메시지를 완성합니다.
4.  `SEND_SMS` 환경 변수가 `True`로 설정되어 있고 Twilio 설정이 올바르게 완료되어 있다면, 해당 메시지를 당신의 휴대폰으로 SMS 전송합니다.

## 🚀 시작하기

### 📋 전제 조건
*   **Python 3.8 이상:** [Python 공식 웹사이트](https://www.python.org/downloads/)에서 다운로드할 수 있습니다.
*   **OpenWeatherMap API Key:** 날씨 데이터를 가져오기 위해 필요합니다. [OpenWeatherMap 회원가입](https://openweathermap.org/api) 후 무료 API Key를 발급받으세요.
*   **Twilio 계정 (선택 사항):** SMS 전송 기능을 사용하려면 필요합니다. [Twilio 회원가입](https://www.twilio.com/try-twilio) 후 Account SID, Auth Token, Twilio 전화번호를 발급받으세요.
*   **`requirements.txt`에 명시된 Python 라이브러리:** 아래 설정 가이드에 따라 설치합니다.

### 🛠️ 설정 가이드

1.  **프로젝트 클론 또는 다운로드:**
    원하는 디렉터리에 프로젝트를 다운로드합니다.
    ```bash
    git clone https://github.com/your-username/otto-weather-wardrobe.git # 또는 파일 직접 다운로드
    cd otto-weather-wardrobe
    ```

2.  **가상 환경 설정:**
    Python 가상 환경을 생성하고 활성화하여 프로젝트 종속성을 격리합니다. 이는 시스템 환경과의 충돌을 방지합니다.
    ```bash
    python -m venv venv
    # Windows 사용자:
    .\venv\Scripts\activate
    # macOS/Linux 사용자:
    source venv/bin/activate
    ```

3.  **필요 라이브러리 설치:**
    프로젝트 루트에 제공된 `requirements.txt` 파일을 사용하여 필요한 라이브러리를 설치합니다.
    ```bash
    pip install -r requirements.txt
    ```

4.  **환경 변수 설정 (`.env` 파일 생성):**
    프로젝트 루트 디렉터리에 `.env` 파일을 새로 생성하고, 아래 내용을 복사하여 붙여 넣은 후 `YOUR_`로 시작하는 플레이스홀더를 실제 값으로 채워 넣으세요. (주석은 `.env` 파일에 포함하지 마세요)

    ```ini
    # --- OpenWeatherMap 설정 (필수) ---
    OPENWEATHER_API_KEY=YOUR_OPENWEATHER_API_KEY
    # 날씨를 알고 싶은 도시 (기본값: Seoul,KR) 형식: 도시명,국가코드 (예: New York,US)
    CITY=Seoul,KR

    # --- SMS 전송 설정 (선택 사항) ---
    # SMS 전송 활성화 여부 (True 또는 False, 기본값: False)
    # 실제 SMS 전송을 원하면 'True'로 설정하고 아래 Twilio 정보를 모두 채워주세요.
    SEND_SMS=False

    # 당신의 휴대폰 번호 (SMS 수신용, SEND_SMS=True일 경우 필수)
    # 국제 코드 포함 (예: 한국: +821012345678, 미국: +1234567890)
    MY_PHONE_NUMBER=+821012345678

    # Twilio 계정 정보 (SEND_SMS=True일 경우 필수)
    TWILIO_ACCOUNT_SID=YOUR_TWILIO_ACCOUNT_SID
    TWILIO_AUTH_TOKEN=YOUR_TWILIO_AUTH_TOKEN
    # Twilio에서 발급받은 번호 (예: +1234567890)
    TWILIO_PHONE_NUMBER=+1234567890
    ```

    *   `YOUR_OPENWEATHER_API_KEY`: OpenWeatherMap에서 발급받은 API 키를 입력하세요.
    *   `CITY`: 날씨를 알고 싶은 도시를 `도시명,국가코드` 형식으로 입력하세요 (예: `Seoul,KR`, `Tokyo,JP`, `New York,US`).
    *   `MY_PHONE_NUMBER`: SMS를 수신할 본인의 휴대폰 번호를 국제 코드와 함께 입력하세요. (예: 한국: `+821012345678`, 미국: `+1234567890`)
    *   `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`: Twilio에서 발급받은 계정 정보를 입력하세요.

### ▶️ 실행 방법
가상 환경이 활성화된 상태에서 프로젝트 루트 디렉터리에서 다음 명령어를 실행합니다:
```bash
python otto_weather_wardrobe.py
```
스크립트가 실행되면 콘솔에 상세한 진행 상황과 함께 날씨 정보 및 옷차림 추천 메시지가 출력됩니다. `SEND_SMS=True`로 설정하고 모든 Twilio 정보가 올바르다면, 잠시 후 설정된 번호로 SMS 메시지가 전송될 것입니다.

스크립트 실행을 마친 후 가상 환경을 비활성화하려면 다음 명령어를 사용하세요:
```bash
deactivate
```

### ⏰ 자동 실행 (선택 사항)
매일 아침 자동으로 메시지를 받고 싶다면, 운영체제의 스케줄러(예: Linux/macOS의 `cron`, Windows의 `작업 스케줄러`)를 사용하여 이 스크립트를 정기적으로 실행하도록 설정할 수 있습니다.

**예시 (Linux/macOS cron):**
1.  터미널에 `crontab -e` 명령어를 입력합니다.
2.  다음 줄을 추가하고 저장합니다. (`/path/to/your/project`를 실제 프로젝트 경로로 변경해야 합니다.)
    ```cron
    # 매일 오전 8시에 스크립트 실행 및 로그 저장
    0 8 * * * /path/to/your/project/venv/bin/python /path/to/your/project/otto_weather_wardrobe.py >> /path/to/your/project/cron.log 2>&1
    ```
    이 설정은 매일 오전 8시에 스크립트를 실행하고, 모든 출력(로그)을 `cron.log` 파일에 저장하여 실행 결과를 확인할 수 있도록 합니다.

## 📝 참고 사항
*   **$1 과금:** 이 프로젝트의 '1달러 과금' 컨셉은 프로젝트의 재미를 위한 설정이며, 실제로 이 스크립트 실행으로 인해 돈이 청구되지 않습니다. (단, Twilio SMS 발송에는 [Twilio 자체의 요금](https://www.twilio.com/sms/pricing)이 부과될 수 있습니다.)
*   **날씨 데이터:** OpenWeatherMap의 무료 API는 5일/3시간 간격의 예보를 제공합니다. 이는 실시간 날씨가 아닌 예보 데이터이며, 단기 예보의 특성상 100% 정확하지 않을 수 있습니다.
*   **패션 드립:** 'Grok-ish' 패션 드립은 실시간 AI가 생성하는 것이 아니라, 미리 정의된 목록에서 랜덤으로 선택됩니다.

## 🧑‍💻 개발자 정보
*   **이름:** 오또 (Otto)
*   **역할:** 천재 개발자 에이전트, 패션 마스터, 밈 트렌드세터

이 프로젝트는 당신의 아침을 조금 더 쉽고 유쾌하게 만들어 줄 것입니다! 🚀
