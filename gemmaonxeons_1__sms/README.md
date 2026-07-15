# 💰 Gemma-on-Xeon's 1달러 룩북 SMS 💰

"13년 묵은 Xeon 위 AI Gemma가 당신의 1달러를 위해 내일 날씨를 잽싸게 분석! 옷장 속 아이템과 매칭해 '오늘의 최저가 패션 예보'를 SMS로 쏴줍니다. 이제 아침마다 "뭐 입지?" 고민 대신, 침대에서 바로 '오또' AI 스타일리스트의 메시지만 확인하세요!"

이 프로젝트는 오래된 서버에서도 가볍게 작동하도록 설계된 "AI" 스타일리스트가 내일 날씨에 맞춰 최적의 의상을 추천하고, 이를 SMS로 받아볼 수 있도록 돕는 유틸리티 알림 서비스입니다.

## ✨ 주요 기능

*   **실시간 날씨 API 연동**: OpenWeatherMap API를 사용하여 지정된 도시의 내일 날씨(최저/최고 기온, 날씨 상태)를 정확하게 예측합니다.
*   **"AI" 기반 맞춤 코디 제안**: 간단한 규칙 기반 시스템을 통해 날씨 정보에 따라 옷장 속 아이템을 조합하여 오늘의 최저가 패션 예보를 제공합니다. (여기서 'Gemma'는 가상의 AI 페르소나입니다!)
*   **초저가 SMS 게이트웨이**: Twilio와 같은 SMS 서비스를 통해 개인화된 패션 예보를 직접 휴대폰으로 받아볼 수 있습니다. (Twilio 무료 평가판 사용 시 발신 메시지에 'Sent from your Twilio trial account' 문구가 추가될 수 있습니다.)

## 🚀 시작하기

이 프로젝트를 로컬 환경에서 실행하기 위한 단계별 지침입니다.

### 📋 전제 조건

*   Python 3.8 이상 버전
*   `pip` (Python 패키지 관리자)

### 📦 설치 및 설정

1.  **프로젝트 클론 및 이동**

    ```bash
    # 이 프로젝트가 Git 리포지토리라면
    # git clone [프로젝트_URL]
    # cd [프로젝트_폴더명]
    # 만약 파일만 받았다면 해당 디렉토리로 이동하세요.
    ```

2.  **가상 환경 설정 (권장)**

    프로젝트의 종속성을 격리하기 위해 가상 환경을 생성하고 활성화합니다.

    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **의존성 라이브러리 설치**

    `requirements.txt` 파일을 생성하고, 필요한 라이브러리를 설치합니다.

    ```bash
    # requirements.txt 파일 생성
    pip freeze > requirements.txt
    # (또는 직접 파일에 다음 내용을 추가)
    # requests
    # python-dotenv
    # twilio

    # 라이브러리 설치
    pip install -r requirements.txt
    ```

4.  **API 키 및 환경 변수 설정**

    프로젝트의 루트 디렉토리에 `.env` 파일을 생성하고, 아래 예시와 같이 필수 환경 변수들을 추가합니다. **반드시 `YOUR_..._HERE` 부분과 예시 값을 자신의 실제 값으로 대체해야 합니다.**

    ```dotenv
    # OpenWeatherMap API Key
    # 1. OpenWeatherMap (https://openweathermap.org/) 에 가입합니다.
    # 2. 로그인 후, "API keys" 섹션에서 API Key를 발급받습니다.
    OWM_API_KEY="YOUR_OPENWEATHERMAP_API_KEY_HERE"

    # 날씨 정보를 가져올 도시 이름 (영문으로 입력하세요, 예: Seoul, Tokyo, New York)
    CITY_NAME="Seoul" 

    # Twilio API Credentials
    # 1. Twilio (https://www.twilio.com/try-twilio) 에 가입하여 무료 평가판 계정을 만듭니다.
    # 2. Twilio Console (https://www.twilio.com/console) 에서 Account SID와 Auth Token을 확인합니다.
    TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # YOUR_TWILIO_ACCOUNT_SID_HERE
    TWILIO_AUTH_TOKEN="your_auth_token_here" # YOUR_TWILIO_AUTH_TOKEN_HERE

    # Twilio에서 발급받은 Twilio 전화번호 (예: +1234567890)
    # 무료 평가판 계정에서는 자동으로 하나의 번호가 할당됩니다.
    TWILIO_PHONE_NUMBER="+1234567890" # YOUR_TWILIO_PHONE_NUMBER_HERE

    # SMS를 받아볼 본인의 휴대폰 번호 (반드시 국제 전화 형식으로 입력하세요, 예: +821012345678)
    RECIPIENT_PHONE_NUMBER="+8210xxxxxxxx" # YOUR_RECIPIENT_PHONE_NUMBER_HERE
    ```

    *   **OpenWeatherMap 설정 가이드**:
        *   `OWM_API_KEY`: [OpenWeatherMap API keys 페이지](https://openweathermap.org/api) 에서 계정을 생성하거나 로그인하여 발급받으세요.
        *   `CITY_NAME`: 날씨 정보를 받을 도시의 **영문 이름**을 정확하게 입력해야 합니다.
    *   **Twilio 설정 가이드**:
        *   [Twilio 가입 페이지](https://www.twilio.com/try-twilio) 에서 무료 계정을 생성합니다.
        *   대시보드에서 `Account SID`와 `Auth Token`을 복사하여 `.env` 파일에 붙여넣습니다.
        *   `TWILIO_PHONE_NUMBER`: Twilio에서 제공하는 발신용 전화번호입니다. 이 번호는 Twilio 콘솔에서 확인할 수 있습니다.
        *   `RECIPIENT_PHONE_NUMBER`: SMS를 수신할 **본인의 휴대폰 번호**입니다. 반드시 `+국가코드전화번호` 형식(예: 한국은 `+821012345678`)으로 입력해야 합니다. Twilio 무료 평가판은 검증된 전화번호로만 SMS를 보낼 수 있으므로, 해당 번호를 Twilio 계정에 미리 등록해야 합니다.

### 🏃 실행 방법

모든 설정이 완료되었다면, 다음 명령어를 사용하여 스크립트를 실행합니다.

```bash
python main.py
```

스크립트가 실행되면 콘솔에 다음과 같은 진행 상황이 출력됩니다:
1.  환경 변수 로드 여부
2.  OpenWeatherMap API를 통한 내일 날씨 정보 조회 진행 상황
3.  Gemma-on-Xeon의 코디 제안 생성 진행 상황
4.  발송될 SMS 메시지의 내용 미리보기
5.  Twilio를 통한 SMS 발송 진행 상황 및 최종 성공/실패 여부

### ⚠️ 에러 핸들링 및 로깅

코드에는 초보자도 쉽게 문제 해결을 할 수 있도록 다음과 같은 기능이 강화되었습니다:

*   **상세한 콘솔 출력 (`print`)**: 스크립트의 각 주요 단계와 그 결과를 사용자가 명확히 이해할 수 있도록 콘솔에 알기 쉬운 메시지를 출력합니다. (예: "⚙️ 환경 변수를 로드하는 중...", "✅ 날씨 정보 조회 완료!")
*   **통합 로깅 (`logging`)**: `logging` 모듈을 사용하여 실행 시간, 로그 레벨 (INFO, ERROR 등), 상세 메시지를 표준 출력(콘솔)으로 기록합니다. 이를 통해 문제가 발생했을 때 어떤 단계에서 어떤 오류가 발생했는지 더욱 쉽게 추적하고 디버깅할 수 있습니다.
*   **견고한 예외 처리**: API 호출 실패(HTTP 오류, 연결 오류, 시간 초과), 환경 변수 누락, API 응답 데이터 구조 오류 등 발생 가능한 대부분의 문제에 대해 구체적인 예외 처리가 포함되어 있습니다. 이는 프로그램이 예상치 못하게 종료되는 것을 방지하고, 사용자에게 문제 해결에 유용한 오류 메시지를 제공합니다.

## 🤝 기여

이 프로젝트는 간단한 토이 프로젝트로 기획되었지만, 아이디어를 확장하거나 기능을 개선하는 어떤 기여도 환영합니다. 예를 들어, 날씨 조건에 따른 코디 규칙을 더욱 세분화하거나, 다른 날씨 API 또는 SMS 게이트웨이를 통합하는 등의 개선이 가능합니다.
(현재는 "오또"가 직접 코드를 작성했습니다.)
