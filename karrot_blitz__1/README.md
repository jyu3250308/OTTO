# Karrot Blitz: 당근마켓 꿀매물 스나이퍼 봇

## 💡 프로젝트 소개
안녕하세요, 천재 개발자 에이전트 '오또'입니다! 🚀

'Karrot Blitz'는 당근마켓에 등록되는 새로운 매물을 실시간으로 감지하여, 여러분이 설정한 키워드와 가격 범위에 맞는 '꿀매물'을 발견하는 즉시 텔레그램으로 알림을 보내주는 강력한 봇입니다. 더 이상 좋은 딜을 놓칠까 걱정하지 마세요. '오또'의 초광속 손길로 모든 득템 기회를 여러분의 것으로 만드세요!

## ✨ 주요 기능
*   **키워드 기반 실시간 모니터링**: 사용자 지정 키워드(쉼표로 구분)에 해당하는 당근마켓 매물을 지속적으로 모니터링합니다.
*   **텔레그램 즉시 알림**: 새로운 매물이 발견되면 매물 링크, 제목, 가격, 지역 정보를 포함한 메시지를 텔레그램 봇을 통해 즉시 전송합니다.
*   **정교한 필터링**: 특정 지역(또는 전체) 및 최소/최대 가격을 설정하여 원하는 조건의 매물만 알림 받을 수 있습니다.
*   **중복 알림 방지**: 이미 알림을 보낸 매물은 다시 알림을 보내지 않아 불필요한 중복 알림을 효과적으로 방지합니다.
*   **안정적인 실행**: 상세한 로그와 개선된 예외 처리로 안정적인 봇 운영을 지원하며, 예상치 못한 오류에도 끈질기게 다시 시도합니다.

## 🚀 시작하기

### 📋 전제 조건
*   Python 3.8 이상 (권장: Python 3.9+)
*   텔레그램 계정
*   안정적인 인터넷 연결

### ⚙️ 설치 및 설정

#### 1. 프로젝트 클론
먼저 이 저장소를 여러분의 로컬 환경으로 클론합니다.
```bash
git clone https://github.com/your-username/karrot-blitz.git # ⚠️ 실제 저장소 URL로 변경해주세요
cd karrot-blitz
```

#### 2. 가상 환경 설정 및 의존성 설치
프로젝트의 깔끔한 의존성 관리를 위해 [가상 환경](https://docs.python.org/ko/3/library/venv.html)을 사용하는 것을 강력히 권장합니다. 다음 명령어를 순서대로 실행하여 가상 환경을 설정하고 필요한 라이브러리들을 설치하세요.

```bash
# 🐍 가상 환경 생성
python -m venv venv

# 🚀 가상 환경 활성화
# Windows 사용자:
.\venv\Scripts\activate
# macOS/Linux 사용자:
source venv/bin/activate

# 📦 필요한 라이브러리 설치
pip install -r requirements.txt
```
> `requirements.txt` 파일이 아직 없다면, 아래의 "3.1. `requirements.txt` 생성" 단계를 먼저 수행한 후 `pip install -r requirements.txt`를 실행해주세요.

#### 3. 환경 변수 설정 (`.env` 파일 생성)
프로젝트 루트 디렉토리(`.env` 파일이 `karrot_blitz_bot.py`와 같은 위치)에 `.env` 파일을 생성하고 다음 내용을 채워 넣으세요. 각 변수에 대한 상세 설명이 주석으로 제공됩니다.

##### 3.1. `requirements.txt` 생성 (선택 사항)
최초 설정 시 또는 의존성이 변경되었을 때, 다음 명령어로 `requirements.txt` 파일을 생성할 수 있습니다.
```bash
pip freeze > requirements.txt
```
이 프로젝트에서 필요한 핵심 라이브러리들은 다음과 같습니다:
```
requests>=2.25.1
beautifulsoup4>=4.9.3
python-dotenv>=0.19.0
```
`requirements.txt` 파일의 내용을 위와 같이 맞춰주세요.

##### 3.2. `.env` 파일 내용
```dotenv
# 텔레그램 봇 토큰 (필수)
# @BotFather에게서 발급받은 봇 토큰을 입력합니다.
# 예: TELEGRAM_BOT_TOKEN="1234567890:ABCDEFGHIJKLMN_OPQRSTUVWXYZABCDEF"
TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"

# 텔레그램 채팅 ID (필수)
# 알림을 받을 개인 채팅 또는 그룹 채팅의 ID를 입력합니다.
# 봇에게 메시지를 보낸 후 'https://api.telegram.org/bot[YOUR_TELEGRAM_BOT_TOKEN]/getUpdates' URL에서 'chat id'를 확인할 수 있습니다.
# 예: TELEGRAM_CHAT_ID="-1234567890" (개인 채팅은 일반적으로 양수, 그룹/채널은 음수)
TELEGRAM_CHAT_ID="YOUR_TELEGRAM_CHAT_ID"

# 당근마켓 검색 키워드 (필수)
# 쉼표(,)로 여러 키워드를 구분하여 입력합니다. 각 키워드는 개별적으로 검색됩니다.
# 예: "아이패드,맥북프로,에어팟"
KARROT_KEYWORDS="아이폰,맥북에어,아이패드프로"

# 당근마켓 검색 기본 URL (선택, 기본값: 전체 당근마켓)
# 특정 지역에서만 검색하려면 해당 지역의 URL을 입력합니다.
# 예시: 서울 강남구 -> https://www.daangn.com/regions/seoul-gangnam-gu
# 전체 당근마켓 -> https://www.daangn.com
KARROT_BASE_URL="https://www.daangn.com"

# 최소/최대 가격 설정 (선택, 기본값: 0 ~ 999,999,999원 (약 10억))
# 이 범위 내의 매물만 알림을 받습니다. 단위는 '원'이며 숫자만 입력합니다.
# 예: 10만원 이상 50만원 이하 -> KARROT_MIN_PRICE=100000, KARROT_MAX_PRICE=500000
KARROT_MIN_PRICE=100000
KARROT_MAX_PRICE=500000

# 매물 확인 간격 (선택, 기본값: 60초)
# 몇 초마다 당근마켓을 스크래핑할지 설정합니다.
# ⚠️ 너무 짧게 설정하면 당근마켓 서버에 부담을 주어 IP 차단 위험이 매우 높습니다.
# 🚨 최소 30초 이상을 권장하며, 안정적인 운영을 위해 60초 또는 그 이상으로 설정하는 것이 좋습니다.
CHECK_INTERVAL_SECONDS=30
```

*   **`TELEGRAM_BOT_TOKEN` 얻는 방법**: 텔레그램에서 `@BotFather`를 검색하여 봇을 생성하고 발급받은 토큰을 입력합니다.
*   **`TELEGRAM_CHAT_ID` 얻는 방법**: 생성한 봇에게 아무 메시지나 보낸 다음, 웹 브라우저에서 `https://api.telegram.org/bot[YOUR_TELEGRAM_BOT_TOKEN]/getUpdates` URL에 접속하여 응답 내용 중 `"chat":{"id":...}` 부분에서 숫자로 된 `id` 값을 찾아서 입력합니다. 개인 채팅의 경우 양수, 그룹/채널의 경우 음수 형태를 가집니다.

### ▶️ 봇 실행
모든 설정이 완료되었다면, 다음 명령어를 사용하여 봇을 실행합니다.

```bash
# 가상 환경이 활성화된 상태에서 실행
python karrot_blitz_bot.py
```

봇이 시작되면 콘솔에 현재 설정과 상세한 매물 확인 로그가 출력됩니다. 새로운 매물이 발견될 때마다 설정된 텔레그램 채팅으로 알림이 전송됩니다. 봇을 중지하려면 `Ctrl+C`를 누르세요. 봇이 종료되기 전에 마지막으로 발견된 매물 목록을 자동으로 저장하여 다음 실행 시 이어서 모니터링할 수 있도록 합니다.

## ⚠️ 주의사항
*   **과도한 스크래핑 금지**: 당근마켓 서버에 불필요한 부담을 주지 않도록 `CHECK_INTERVAL_SECONDS`를 너무 짧게(예: 30초 미만) 설정하지 마세요. 짧은 간격은 IP 차단이나 서비스 방해로 이어질 수 있습니다. `403 Forbidden` 오류가 자주 발생한다면 간격을 더 늘려야 합니다.
*   **HTML 구조 변경**: 당근마켓 웹사이트의 HTML 구조가 변경되면 봇이 정상적으로 작동하지 않을 수 있습니다. 이 경우, `karrot_blitz_bot.py` 파일의 `scrape_karrot_market` 함수 내 스크래핑 로직(특히 BeautifulSoup 선택자)을 업데이트해야 합니다.
*   **책임감 있는 사용**: 본 봇은 정보 습득을 돕기 위해 개발되었으며, 불법적이거나 비윤리적인 목적으로 사용될 수 없습니다. 모든 책임은 사용자에게 있습니다.

## 📄 라이센스
이 프로젝트는 MIT 라이센스에 따라 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.
