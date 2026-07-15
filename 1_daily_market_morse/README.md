# 삐빅! 김개미 비상: Daily Market Morse

## 🚀 프로젝트 소개

'삐빅! 김개미 비상: Daily Market Morse'는 바쁜 개미 투자자들을 위해 AI가 24시간 시장을 감시하고, 중요한 금융 뉴스의 핵심 트렌드를 모스 신호처럼 간결하게 요약하여 매일 아침 특급 알림을 보내주는 똑똑한 봇입니다.

복잡한 시장 뉴스를 **3줄로 초간단 요약**하고, 전반적인 '개미 심리지수'(긍정/중립/부정)를 자동으로 생성하여, 투자 결정에 필요한 최소한의 정보를 신속하게 제공합니다.

## ✨ 주요 기능

*   **실시간 금융 뉴스 크롤링**: Yahoo Finance, Investing.com 등 주요 금융 뉴스 사이트에서 최신 시장 뉴스를 자동으로 수집합니다.
*   **AI 핵심 트렌드 감지 및 3문장 요약**: 수집된 뉴스 기사의 내용을 AI(Hugging Face `transformers` 라이브러리 활용)가 분석하여 핵심적인 내용을 3문장 이내로 간결하게 요약합니다.
*   **'개미 심리지수' 자동 생성**: 뉴스 기사들의 전반적인 분위기(긍정/부정/중립)를 분석하여 시장의 '개미 심리지수'를 산출하고 표기합니다.
*   **Telegram 봇 간결 알림**: 매일 아침 설정된 시간에 요약된 시장 동향과 심리지수를 Telegram 봇을 통해 '삐빅!' 모스 코드 스타일의 간결한 메시지로 발송합니다.

## ⚙️ 작동 방식

1.  **환경 변수 로드**: `.env` 파일에서 Telegram 봇 토큰 및 알림을 받을 채팅 ID, 알림 시간 등을 안전하게 로드합니다.
2.  **AI 모델 초기화**: Hugging Face `transformers` 라이브러리를 사용하여 텍스트 요약(PEGASUS) 및 감성 분석(DistilBERT) 모델을 초기화합니다. (첫 실행 시 인터넷을 통해 모델 다운로드 및 로딩에 시간이 필요할 수 있습니다.)
3.  **뉴스 수집**: 설정된 금융 뉴스 사이트(Yahoo Finance, Investing.com)에서 최신 기사의 제목, 링크, 요약 내용을 크롤링합니다.
4.  **AI 분석**: 수집된 각 기사의 요약 내용에 대해 감성 분석을 수행하고, 전체 기사 내용을 종합하여 시장의 핵심 동향을 3문장으로 요약합니다.
5.  **심리지수 산출**: 개별 기사의 감성 분석 결과를 바탕으로 '개미 심리지수'를 긍정, 중립, 부정 중 하나로 결정합니다.
6.  **알림 발송**: 요약된 핵심 동향, 심리지수, 그리고 주요 뉴스 링크를 Telegram 메시지 형태로 포맷하여 설정된 시간에 발송합니다.
7.  **스케줄링**: `APScheduler`를 사용하여 설정된 시간에 매일 자동으로 위의 과정을 반복합니다.

## 🚀 설치 및 실행 방법

### 1. 전제 조건

*   **Python 3.8 이상**: 공식 Python 웹사이트에서 최신 버전을 다운로드하여 설치합니다.
*   **인터넷 연결**: AI 모델 다운로드, 뉴스 크롤링, Telegram 연동에 필수적입니다.
*   **Telegram 봇**: 알림을 받을 Telegram 봇을 미리 생성해야 합니다. (아래 `Telegram 봇 설정` 참조)

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
SCHEDULE_HOUR=9
SCHEDULE_MINUTE=0
```

*   `TELEGRAM_BOT_TOKEN`: BotFather에게 받은 Telegram 봇 토큰을 입력하세요.
*   `TELEGRAM_CHAT_ID`: 봇이 메시지를 보낼 Telegram 채팅방의 ID를 입력하세요.
*   `SCHEDULE_HOUR`: 알림을 보낼 시간을 **24시간 형식**으로 입력합니다. (기본값: 9, **한국 표준시 (KST) 기준**)
*   `SCHEDULE_MINUTE`: 알림을 보낼 분을 입력합니다. (기본값: 0)

**⚠️ 중요**: `SCHEDULE_HOUR`와 `SCHEDULE_MINUTE`는 `Asia/Seoul` (KST, 한국 표준시) 기준으로 작동합니다. 봇이 실행되는 서버의 시간대가 달라도 `APScheduler`가 자동으로 KST에 맞춰 실행 시간을 조정합니다.

### 5. 봇 실행

가상 환경이 활성화된 터미널에서 다음 명령어를 실행하여 봇을 시작합니다:

```bash
python ant_market_morse_bot.py
```

봇이 시작되면 스케줄러가 백그라운드에서 작동하며, 설정된 시간에 매일 알림을 보낼 것입니다. 터미널 창을 닫아도 봇이 계속 실행되도록 하려면, `nohup` 또는 `screen`/`tmux`와 같은 터미널 멀티플렉서를 사용하거나 `systemd` 서비스로 등록하는 것을 고려할 수 있습니다. (예시: `nohup python ant_market_morse_bot.py &`)

**첫 실행 시 주의사항**: `transformers` 라이브러리의 AI 모델은 처음 로드될 때 인터넷을 통해 모델 파일을 다운로드하므로, 네트워크 환경 및 모델 크기에 따라 시간이 다소 소요될 수 있습니다. 터미널 로그를 통해 진행 상황을 확인할 수 있습니다.

## 🛠️ 사용자 정의 및 확장

*   **뉴스 소스 추가**: `fetch_all_news` 함수에 새로운 스크래핑 함수를 추가하여 다른 금융 뉴스 웹사이트(예: 국내 증권사 리서치, 코인 관련 뉴스)를 포함할 수 있습니다. 단, 웹사이트 구조 변경에 따라 스크래퍼 코드를 주기적으로 업데이트해야 할 수 있습니다.
*   **AI 모델 변경**: `SUMMARIZER_MODEL_NAME`과 `SENTIMENT_MODEL_NAME` 상수를 변경하여 다른 Hugging Face 모델을 시도해 볼 수 있습니다. 한국어 모델을 사용하려면, `klue/roberta-base` 같은 한국어 감성 분석 모델이나 `gogamza/kobart-base-v1` 같은 한국어 요약 모델을 찾아 적용해 보세요.
*   **알림 채널 확장**: `send_telegram_message` 함수와 유사하게 이메일 발송(`smtplib`), Discord 웹훅, Slack 웹훅 등을 추가하여 다양한 채널로 알림을 보낼 수 있습니다.
*   **심리지수 로직 변경**: `calculate_ant_sentiment_index` 함수의 로직을 수정하여 '개미 심리지수' 산출 방식을 더욱 정교하게 만들거나 투자 전략에 맞게 조정할 수 있습니다.

## ❓ 문제 해결 (Troubleshooting)

*   **AI 모델 다운로드 실패 또는 초기화 오류**: 
    *   인터넷 연결 상태를 다시 확인해 주세요.
    *   방화벽이나 프록시 설정이 모델 다운로드를 방해할 수 있습니다. (특히 회사 네트워크 환경)
    *   `pip install transformers` 시점에 모델 가중치가 모두 다운로드되는 것이 아니며, `from_pretrained` 호출 시 실제 다운로드가 시작됩니다. 시스템 메모리가 부족할 경우 더 작은 모델(예: 요약 모델: `t5-small`, 감성 분석 모델: `sshleifer/distilbart-cnn-6-6`)을 사용해 볼 수 있습니다.
*   **Telegram 메시지 미발송**: 
    *   `.env` 파일의 `TELEGRAM_BOT_TOKEN`과 `TELEGRAM_CHAT_ID`가 올바르게 설정되었는지 다시 확인하세요. **오타나 주변 공백에 특히 주의하세요.**
    *   봇이 메시지를 보낼 채팅방(개인 채팅 또는 그룹)에 **초대되었는지**, 그리고 봇에게 메시지 전송 권한이 있는지 확인하세요.
    *   `getUpdates` API를 통해 Chat ID를 다시 한번 확인해 보세요. 특히 그룹 채팅 ID는 음수(-)로 시작합니다.
    *   Telegram API는 메시지 길이에 제한이 있을 수 있습니다 (일반적으로 4096자).
*   **뉴스 크롤링 실패**: 
    *   대상 웹사이트(Yahoo Finance, Investing.com)의 HTML 구조가 변경되었을 수 있습니다. 로그에 `기사 요소 (제목, 링크, 요약)를 찾을 수 없음`과 같은 메시지가 반복된다면, 해당 웹사이트의 `fetch_news_from_...` 함수 내의 `BeautifulSoup` 셀렉터(`find`, `find_all` 인자)를 업데이트해야 할 수 있습니다.
    *   웹사이트에서 봇 접근을 차단했을 수도 있습니다. `User-Agent`를 변경하거나, 요청 간격을 조절하는 등 웹사이트의 `robots.txt` 및 크롤링 정책을 준수하는 방법을 고려해야 합니다.
*   **스케줄러가 작동하지 않음**: 
    *   봇 스크립트가 실행 중인지 (터미널이 닫히지 않았거나, `nohup` 등으로 백그라운드에서 실행 중인지) 확인하세요.
    *   `.env` 파일의 `SCHEDULE_HOUR`와 `SCHEDULE_MINUTE` 설정이 올바른지 확인하세요. **한국 표준시 (KST) 기준**입니다.
    *   스크립트 실행 후 `🗓️ 스케줄러가 매일 ... 에 실행되도록 설정되었습니다.`와 같은 초기 로그 메시지가 뜨는지 확인하세요.

## 📝 `requirements.txt`

```
python-dotenv
requests
beautifulsoup4
transformers
accelerate>=0.20.1
torch>=2.0.0
telegram-bot-api
APScheduler
```
