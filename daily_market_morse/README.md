# 삐빅! 김개미 비상: Daily Market Morse

> 🆕 **v2 UPDATE (2026-07-23)**: 깨지기 쉬운 웹 스크래핑 대신 **구글 뉴스 RSS(무료·키 불필요)**로
> 실시간 시장 헤드라인을 안정적으로 수집합니다. 실행하면 `briefings/` 폴더에 **3줄 브리핑(.md)**이
> 매일 쌓여요 — 텔레그램 설정 시 자동 발송까지! 삐빅 📈

## 🚀 프로젝트 소개

'삐빅! 김개미 비상: Daily Market Morse'는 바쁜 개미 투자자들을 위해 AI가 24시간 시장을 감시하고, 중요한 금융 뉴스의 핵심 트렌드를 모스 신호처럼 간결하게 요약하여 매일 아침 특급 알림을 보내주는 똑똑한 봇입니다.

복잡한 시장 뉴스를 **3줄로 초간단 요약**하고, 전반적인 '개미 심리지수'(긍정/중립/부정)를 자동으로 생성하여, 투자 결정에 필요한 최소한의 정보를 신속하게 제공합니다.

## ✨ 주요 기능

*   **실시간 금융 뉴스 크롤링**: Yahoo Finance, Investing.com 등 주요 금융 뉴스 사이트에서 최신 시장 뉴스를 자동으로 수집합니다.
*   **AI 핵심 트렌드 감지 및 3문장 요약**: 수집된 뉴스 기사의 내용을 AI(Google Gemini API 활용)가 분석하여 핵심적인 내용을 3문장 이내로 간결하게 요약합니다.
*   **'개미 심리지수' 자동 생성**: 뉴스 기사들의 전반적인 분위(긍정/부정/중립)를 분석하여 시장의 '개미 심리지수'를 산출하고 표기합니다.
*   **Telegram 봇 간결 알림**: 매일 아침 설정된 시간에 요약된 시장 동향과 심리지수를 Telegram 봇을 통해 '삐빅!' 모스 코드 스타일의 간결한 메시지로 발송합니다.

## ⚙️ 작동 방식

1.  **환경 변수 로드**: `.env` 파일에서 Telegram 봇 토큰, 알림을 받을 채팅 ID, Gemini API 키, 그리고 알림 시간 등을 안전하게 로드합니다.
2.  **AI 모델 초기화**: Google Gemini API 클라이언트를 초기화하여 뉴스 분석 및 시장 요약을 진행할 준비를 합니다.
3.  **뉴스 수집**: 설정된 금융 뉴스 사이트(Yahoo Finance, Investing.com)에서 최신 기사의 제목, 링크, 요약 내용을 크롤링합니다.
4.  **AI 분석**: 수집된 각 기사의 요약 내용에 대해 Gemini API(`gemini-2.5-flash` 모델)로 감성 분석을 수행하고, 전체 기사 내용을 종합하여 시장의 핵심 동향을 3문장으로 요약합니다.
5.  **심리지수 산출**: 개별 기사의 감성 분석 결과를 바탕으로 '개미 심리지수'를 긍정, 중립, 부정 중 하나로 결정합니다.
6.  **알림 발송**: 요약된 핵심 동향, 심리지수, 그리고 주요 뉴스 링크를 Telegram 메시지 형태로 포맷하여 설정된 시간에 발송합니다.
7.  **스케줄링**: `APScheduler`를 사용하여 설정된 시간에 매일 자동으로 위의 과정을 반복합니다.

## 🚀 설치 및 실행 방법

### 1. 전제 조건

*   **Python 3.8 이상**: 공식 Python 웹사이트에서 최신 버전을 다운로드하여 설치합니다.
*   **인터넷 연결**: 뉴스 크롤링, Gemini API 호출, Telegram 연동에 필수적입니다.
*   **Telegram 봇**: 알림을 받을 Telegram 봇을 미리 생성해야 합니다. (아래 `Telegram 봇 설정` 참조)
*   **Gemini API Key**: Google AI Studio에서 발급받은 Gemini API 키가 필요합니다.

### 2. 가상 환경 설정 및 라이브러리 설치

프로젝트를 위한 가상 환경을 생성하고 활성화합니다. 이는 프로젝트 의존성을 격리하여 시스템 전체에 영향을 주지 않도록 합니다.

```bash
# 1. 프로젝트 디렉토리로 이동합니다.
cd your_project_directory

# 2. 'venv'라는 이름의 가상 환경을 생성합니다.
python -m venv venv

# 3. 가상 환경을 활성화합니다.
# Windows 사용자의 경우:
.\venv\Scripts\activate
# macOS/Linux 사용자의 경우:
source venv/bin/activate
```

가상 환경이 활성화된 상태에서 `requirements.txt`에 명시된 필요한 라이브러리를 설치합니다:

```bash
pip install -r requirements.txt
```

### 3. Telegram 봇 설정

봇이 알림을 보내려면 Telegram 봇 토큰과 메시지를 받을 채팅방의 ID가 필요합니다.

1.  **봇 생성 및 토큰 발급**: Telegram에서 [@BotFather](https://t.me/BotFather)에게 말을 걸어 새로운 봇을 생성합니다. 봇 생성 절차를 완료하면 `HTTP API Token`을 받게 됩니다. (예시: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
2.  **Chat ID 확인**: 봇이 메시지를 보낼 채팅방(개인 채팅, 그룹 채팅 모두 가능)의 `Chat ID`를 확인해야 합니다.
    *   가장 쉬운 방법은 다음과 같습니다:
        1.  생성한 봇에게 **아무 메시지나 보냅니다.** (그룹 채팅의 경우 봇을 그룹에 추가하고 아무 메시지나 보냅니다.)
        2.  웹 브라우저에서 다음 URL에 접속합니다: `https://api.telegram.org/bot[YOUR_BOT_TOKEN]/getUpdates`
            `[YOUR_BOT_TOKEN]` 부분에는 BotFather에게 받은 토큰을 입력합니다.
        3.  응답으로 받은 JSON 데이터에서 `"chat":{"id":...}` 부분을 찾습니다. 이 `id` 값이 바로 `Chat ID`입니다. 그룹 채팅의 경우 `Chat ID`는 보통 음수(-) 값을 가집니다. (예시: `"id":-1234567890`)

### 4. `.env` 파일 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 입력합니다. `=` 기호 주변에는 공백이 없어야 합니다.

```dotenv
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID_HERE
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
SCHEDULE_HOUR=9
SCHEDULE_MINUTE=0
```

*   `TELEGRAM_BOT_TOKEN`: BotFather에게 받은 Telegram 봇 토큰을 입력하세요.
*   `TELEGRAM_CHAT_ID`: 봇이 메시지를 보낼 Telegram 채팅방의 ID를 입력하세요.
*   `GEMINI_API_KEY`: Google AI Studio에서 발급받은 Gemini API 키를 입력하세요.
*   `SCHEDULE_HOUR`: 알림을 보낼 시간을 **24시간 형식**으로 입력합니다. (기본값: 9, **한국 표준시 (KST) 기준**)
*   `SCHEDULE_MINUTE`: 알림을 보낼 분을 입력합니다. (기본값: 0)

**⚠️ 중요**: `SCHEDULE_HOUR`와 `SCHEDULE_MINUTE`는 `Asia/Seoul` (KST, 한국 표준시) 기준으로 작동합니다. 봇이 실행되는 서버의 시간대가 달라도 `APScheduler`가 자동으로 KST에 맞춰 실행 시간을 조정합니다.

### 5. 봇 실행

가상 환경이 활성화된 터미널에서 다음 명령어를 실행하여 봇을 시작합니다:

```bash
python ant_market_morse_bot.py
```

봇이 시작되면 스케줄러가 백그라운드에서 작동하며, 설정된 시간에 매일 알림을 보낼 것입니다. 터미널 창을 닫아도 봇이 계속 실행되도록 하려면, `nohup` 또는 `screen`/`tmux`와 같은 터미널 멀티플렉서를 사용하거나 `systemd` 서비스로 등록하는 것을 고려할 수 있습니다. (예시: `nohup python ant_market_morse_bot.py &`)

또한, 실행 시 `--now` 옵션을 추가하면 스케줄러가 켜지기 전에 즉시 1회 뉴스를 크롤링하고 요약하여 Telegram 알림을 보낸 뒤 스케줄 상태로 들어갑니다:
```bash
python ant_market_morse_bot.py --now
```

## 🛠️ 사용자 정의 및 확장

*   **뉴스 수집 소스 확장**: `ant_market_morse_bot.py` 코드 내부의 `fetch_all_news` 함수에 새로운 크롤링 로직을 추가하여 수집하는 기사를 더 확장할 수 있습니다.
*   **요약 및 분석 프롬프트 수정**: `analyze_sentiment` 및 `summarize_text` 함수 내의 프롬프트 문구를 수정하여 AI의 어조나 분석 형식을 변경할 수 있습니다.
