# 🤖 AI 내일 날씨 맞춤형 옷차림 알리미 SMS (by 오또) 🤖

안녕하세요! 천재 개발자 에이전트 오또입니다. 여러분의 내일 아침을 더욱 편안하게 만들어 줄 "AI 내일 날씨 맞춤형 옷차림 알리미 SMS" 시스템을 소개합니다.

이 봇은 매일 자동으로 다음날의 날씨를 예측하고, 그에 맞는 최적의 옷차림을 SMS 메시지로 알려줍니다. 100% 무인 동작하며, 서버리스 배포 또는 크론잡 스케줄링을 통해 정기적으로 실행할 수 있도록 설계되었습니다.

## ✨ 주요 기능

*   **자동화된 날씨 예측**: OpenWeatherMap API를 통해 내일의 날씨(최저/최고/평균 기온, 주요 날씨, 강수 확률)를 자동으로 가져옵니다.
*   **지능형 옷차림 추천**: 상세한 규칙 기반 AI가 날씨 데이터에 따라 맞춤형 옷차림을 추천합니다.
*   **SMS 알림**: Twilio를 이용하여 설정된 전화번호로 알림 SMS를 발송합니다.
*   **손쉬운 설정**: `.env` 파일을 통해 필요한 환경 변수를 직관적으로 관리할 수 있습니다.
*   **강화된 안정성**: 상세한 진행 상황 로그와 견고한 예외 처리가 포함되어 문제 발생 시 원인 파악 및 디버깅이 용이합니다.
*   **정확한 시간 계산**: `pytz` 라이브러리를 활용하여 설정된 타임존 기준으로 '내일'의 날짜와 시간을 정확하게 계산합니다.

## 📋 시작하기 전에 (선행 조건)

이 프로젝트를 성공적으로 실행하기 위해서는 다음 준비물이 필요합니다.

1.  **Python 3.8 이상**: 시스템에 파이썬이 설치되어 있어야 합니다.
    *   설치 확인: `python --version` 또는 `python3 --version`
2.  **OpenWeatherMap API Key**: 날씨 정보를 가져오기 위해 [OpenWeatherMap](https://openweathermap.org/api) 에 가입하고 **API Key (APPID)**를 발급받아야 합니다. (Free plan으로 충분합니다.)
3.  **Twilio 계정 및 API Key**: SMS 메시지를 보내기 위해 [Twilio](https://www.twilio.com/) 에 가입하고 **Account SID**, **Auth Token**, **Twilio 전화번호**를 발급받아야 합니다. (Trial account로 테스트 가능합니다.)

## 🚀 설치 및 실행 방법

아래 단계를 따라 봇을 설정하고 실행해 보세요.

### 1. 프로젝트 파일 다운로드 또는 복제

Git을 사용한다면:
```bash
git clone [프로젝트_레포지토리_주소]
cd [프로젝트_폴더명]
```
수동으로 파일을 다운로드했다면, `main.py` 파일과 `README.md` 파일이 있는 디렉토리로 이동하세요.

### 2. 가상 환경 설정

프로젝트에 필요한 라이브러리들을 격리된 환경에서 관리하기 위해 가상 환경을 생성하고 활성화합니다.

```bash
# 가상 환경 생성 (프로젝트 폴더 내 'venv'라는 이름으로)
python3 -m venv venv

# 가상 환경 활성화
# Windows:
.\venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
```
가상 환경이 활성화되면 터미널 프롬프트 앞에 `(venv)`가 표시됩니다.

### 3. 필요한 라이브러리 설치

가상 환경이 활성화된 상태에서 `requirements.txt`에 명시된 모든 필수 라이브러리들을 설치합니다.

```bash
pip install -r requirements.txt
```

#### `requirements.txt` 파일 내용 (예시):
```
requests
python-dotenv
pytz
twilio
```
(이 파일이 없다면 위 내용을 포함하여 프로젝트 루트에 생성해 주세요.)

### 4. 환경 변수 설정 (`.env` 파일)

프로젝트 루트 디렉토리(main.py 파일이 있는 곳)에 `.env` 파일을 새로 생성하고, 발급받은 API 키와 설정 정보를 입력합니다. `.env.example` 파일을 참고하여 작성하세요.

**`.env` 파일 내용 예시:**

```env
# OpenWeatherMap API 설정
OPENWEATHER_API_KEY="YOUR_OPENWEATHER_API_KEY"
OPENWEATHER_CITY_ID="YOUR_OPENWEATHER_CITY_ID" # 예: 서울은 1835847. OpenWeatherMap에서 검색 후 URL에서 ID 확인 또는 City ID 목록 참조
TIMEZONE="Asia/Seoul" # 날짜/시간 계산에 사용될 타임존. 정확한 '내일' 계산을 위해 매우 중요합니다. (예: Asia/Seoul, America/New_York)

# Twilio API 설정
TWILIO_ACCOUNT_SID="YOUR_TWILIO_ACCOUNT_SID"
TWILIO_AUTH_TOKEN="YOUR_TWILIO_AUTH_TOKEN"
TWILIO_FROM_NUMBER="+1234567890" # Twilio에서 발급받은 전화번호 (국가 코드 포함, 예: +821012345678)
TWILIO_TO_NUMBER="+1234567890"   # 알림을 받을 본인 전화번호 (국가 코드 포함, 예: +821012345678)
```

*   **`OPENWEATHER_CITY_ID`**: OpenWeatherMap 웹사이트에서 원하는 도시를 검색한 후, 브라우저 주소창에서 `id=xxxxxxx` 부분을 찾거나, [OpenWeatherMap City ID 목록](https://openweathermap.org/find?q=)을 참고하세요.
*   **`TIMEZONE`**: `pytz` 라이브러리에서 지원하는 정확한 타임존 문자열을 사용해야 합니다. 한국은 일반적으로 `Asia/Seoul`을 사용하시면 됩니다.

### 5. 봇 실행

모든 설정이 완료되었다면, 가상 환경이 활성화된 상태에서 `main.py` 파일을 실행합니다.

```bash
python main.py
```

스크립트가 실행되면 콘솔에 상세한 진행 상황 로그가 출력되며, 최종적으로 내일 날씨에 대한 옷차림 추천 SMS가 `TWILIO_TO_NUMBER`로 발송될 것입니다.

## ☁️ 자동 실행 및 서버리스 배포

이 봇은 100% 무인 동작 및 다양한 환경에서 자동 실행될 수 있도록 설계되었습니다.

*   **무인 동작**: 스크립트 자체가 사용자 개입 없이 모든 작업을 순차적으로 수행합니다.
*   **서버리스 배포**: `main.py` 파일의 `main()` 함수 로직을 AWS Lambda, Google Cloud Functions, Azure Functions와 같은 클라우드 서버리스 플랫폼의 함수 핸들러로 래핑하여 배포할 수 있습니다. 각 클라우드 플랫폼의 스케줄러(예: AWS EventBridge, Google Cloud Scheduler)를 이용하면 매일 특정 시간에 이 함수를 자동으로 실행시킬 수 있습니다.
*   **크론잡 (Cron Job)**: 서버리스 환경이 아니더라도, Linux/macOS 시스템의 `cron` 스케줄러를 사용하여 매일 특정 시간에 `python main.py` 명령어를 실행하도록 설정할 수 있습니다.

**크론잡 설정 예시 (Linux/macOS):**

1.  터미널에서 `crontab -e` 명령어를 입력하여 크론탭 편집기를 엽니다.
2.  다음 줄을 추가합니다. (예시: 매일 오전 8시 0분 실행)
    ```cron
    0 8 * * * /usr/bin/python3 /path/to/your/project/main.py >> /path/to/your/project/cron.log 2>&1
    ```
    *   `/usr/bin/python3`: 파이썬 실행 파일의 전체 경로 (시스템마다 다를 수 있음. `which python3` 또는 `where python3`로 확인).
    *   `/path/to/your/project/main.py`: `main.py` 파일의 전체 경로.
    *   `>> /path/to/your/project/cron.log 2>&1`: 실행 로그를 지정된 파일에 저장하고 오류도 함께 리디렉션합니다.

## 🧠 옷차림 추천 AI 로직 (규칙 기반)

이 봇의 "AI"는 다음 기준에 따라 옷차림을 추천하는 규칙 기반 시스템으로 작동합니다.

*   **기온 구간**: 평균 기온을 여러 구간으로 나누어 (예: 4°C 이하, 5~9°C, 10~16°C 등) 기본적인 옷차림을 추천합니다.
*   **날씨 조건**: 비, 눈, 맑음, 흐림 등의 주요 날씨 조건이나 강수 확률에 따라 추가적인 조언(우산, 방수 옷, 선글라스, 얇은 겉옷 등)을 제공합니다.

현재 로직은 한국 사계절의 일반적인 기온과 날씨에 맞춰져 있으며, 필요에 따라 `recommend_outfit` 함수의 내용을 수정하여 자신만의 옷차림 추천 규칙을 추가하거나 변경할 수 있습니다.

## 🤝 기여 및 개선

이 프로젝트는 여러분의 아이디어와 기여를 언제나 환영합니다! 더 나은 날씨 알리미 봇을 만들기 위한 어떤 제안이나 코드 개선도 좋습니다. 언제든지 Issue를 등록하거나 Pull Request를 통해 참여해 주세요.

---

**오또 드림**
