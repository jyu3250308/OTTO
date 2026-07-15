# 삐빅! 김개미 비상: 1$ Daily Market Morse

## 프로젝트 소개

'삐빅! 김개미 비상: 1$ Daily Market Morse'는 바쁜 개미 투자자들을 위해 AI가 24시간 시장을 감시하고, 중요한 금융 뉴스의 핵심 트렌드를 모스 신호처럼 간결하게 요약하여 매일 아침 특급 알림을 보내주는 봇입니다.

복잡한 시장 뉴스를 3줄로 초간단 요약하고, 전반적인 '개미 심리지수'(긍정/중립/부정)를 자동으로 생성하여, 투자 결정에 필요한 최소한의 정보를 신속하게 제공합니다.

## 주요 기능

*   **실시간 금융 뉴스 크롤링**: Yahoo Finance, Investing.com 등 주요 금융 뉴스 사이트에서 최신 시장 뉴스를 자동으로 수집합니다.
*   **AI 핵심 트렌드 감지 및 3문장 요약**: 수집된 뉴스 기사의 내용을 AI(Hugging Face `transformers`)가 분석하여 핵심적인 내용을 3문장 이내로 간결하게 요약합니다.
*   **'개미 심리지수' 자동 생성**: 뉴스 기사들의 전반적인 분위기(긍정/부정/중립)를 분석하여 '개미 심리지수'를 산출하고 표기합니다.
*   **Telegram 봇 간결 알림**: 매일 아침 설정된 시간에 요약된 시장 동향과 심리지수를 Telegram 봇을 통해 '삐빅!' 모스 코드 스타일의 간결한 메시지로 발송합니다.

## 작동 방식

1.  **환경 변수 로드**: `.env` 파일에서 Telegram 봇 토큰 및 알림을 받을 채팅 ID, 알림 시간 등을 로드합니다.
2.  **AI 모델 초기화**: Hugging Face `transformers` 라이브러리를 사용하여 텍스트 요약(PEGASUS) 및 감성 분석(DistilBERT) 모델을 초기화합니다. (첫 실행 시 모델 다운로드 필요)
3.  **뉴스 수집**: 설정된 금융 뉴스 사이트에서 최신 기사의 제목, 링크, 요약 내용을 크롤링합니다.
4.  **AI 분석**: 수집된 각 기사의 요약 내용에 대해 감성 분석을 수행하고, 전체 기사 내용을 종합하여 시장의 핵심 동향을 3문장으로 요약합니다.
5.  **심리지수 산출**: 개별 기사의 감성 분석 결과를 바탕으로 '개미 심리지수'를 긍정, 중립, 부정 중 하나로 결정합니다.
6.  **알림 발송**: 요약된 핵심 동향, 심리지수, 그리고 주요 뉴스 링크를 Telegram 메시지 형태로 포맷하여 설정된 시간에 발송합니다.
7.  **스케줄링**: `APScheduler`를 사용하여 설정된 시간에 매일 자동으로 위의 과정을 반복합니다.

## 설치 및 실행 방법

### 1. 전제 조건

*   Python 3.8 이상
*   인터넷 연결 (AI 모델 다운로드 및 뉴스 크롤링, Telegram 연동에 필요)
*   Telegram 봇 (아래 `Telegram 봇 설정` 참조)

### 2. 가상 환경 설정 및 라이브러리 설치

프로젝트를 위한 가상 환경을 생성하고 활성화합니다:

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

필요한 라이브러리를 설치합니다:

```bash
pip install -r requirements.txt
```

(`requirements.txt` 파일 내용은 아래 `requirements` 섹션 참조)

### 3. Telegram 봇 설정

1.  **봇 생성**: Telegram에서 [@BotFather](https://t.me/BotFather)에게 말을 걸어 새로운 봇을 생성합니다. 봇 생성 후 `HTTP API Token`을 받습니다. (예: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
2.  **Chat ID 확인**: 봇이 메시지를 보낼 채팅방(개인 채팅, 그룹 채팅 모두 가능)의 `Chat ID`를 확인해야 합니다.
    *   가장 쉬운 방법은 봇을 만들고 나서 봇에게 아무 메시지나 보내고, `https://api.telegram.org/bot[YOUR_BOT_TOKEN]/getUpdates` 에 접속하여 `"chat":{"id":...}` 부분의 숫자를 확인하는 것입니다. `[YOUR_BOT_TOKEN]`에는 BotFather에게 받은 토큰을 입력합니다.
    *   그룹 채팅의 경우, 봇을 그룹에 추가하고 아무 메시지나 보낸 후 `getUpdates`를 확인합니다. 이때 `chat_id`는 보통 음수(-) 값을 가집니다.

### 4. `.env` 파일 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 입력합니다. `=` 기호 주변에는 공백이 없어야 합니다.

```dotenv
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID
SCHEDULE_HOUR=9
SCHEDULE_MINUTE=0
```

*   `YOUR_TELEGRAM_BOT_TOKEN`: BotFather에게 받은 Telegram 봇 토큰을 입력하세요.
*   `YOUR_TELEGRAM_CHAT_ID`: 봇이 메시지를 보낼 Telegram 채팅방의 ID를 입력하세요.
*   `SCHEDULE_HOUR`: 알림을 보낼 시간을 24시간 형식으로 입력합니다. (기본값: 9, KST 기준)
*   `SCHEDULE_MINUTE`: 알림을 보낼 분을 입력합니다. (기본값: 0)

**주의**: `SCHEDULE_HOUR`와 `SCHEDULE_MINUTE`는 `Asia/Seoul` (KST, 한국 표준시) 기준으로 작동합니다. 서버가 다른 시간대에 있다면 `APScheduler`가 자동으로 변환해 줄 것입니다.

### 5. 봇 실행

터미널에서 다음 명령어를 실행하여 봇을 시작합니다:

```bash
python ant_market_morse_bot.py
```

봇이 시작되면 스케줄러가 백그라운드에서 작동하며, 설정된 시간에 매일 알림을 보낼 것입니다.

**첫 실행 시 주의사항**: `transformers` 모델을 처음 로드할 때 인터넷을 통해 모델 파일을 다운로드하므로, 시간이 다소 소요될 수 있습니다.

## 사용자 정의 및 확장

*   **뉴스 소스 추가**: `fetch_all_news` 함수와 유사하게 새로운 스크래핑 함수를 작성하여 다른 금융 뉴스 웹사이트(예: 증권사 리서치, 코인 관련 뉴스)를 추가할 수 있습니다. 단, 웹사이트 구조 변경에 따라 스크래퍼 코드를 주기적으로 업데이트해야 할 수 있습니다.
*   **AI 모델 변경**: `summarizer_model_name`과 `sentiment_model_name` 변수를 변경하여 다른 Hugging Face 모델을 시도해 볼 수 있습니다. 한국어 모델을 사용하고 싶다면, `klue/roberta-base`와 같은 한국어 모델로 `sentiment_pipeline`을 대체하고, 요약 모델도 한국어 요약 모델을 찾아 적용할 수 있습니다. (예: `gogamza/kobart-base-v1`)
*   **알림 채널 확장**: `send_telegram_message` 함수와 유사하게 이메일 발송(`smtplib`), Discord 웹훅 등을 추가하여 다양한 채널로 알림을 보낼 수 있습니다.
*   **심리지수 로직 변경**: `calculate_ant_sentiment_index` 함수의 로직을 수정하여 '개미 심리지수' 산출 방식을 더욱 정교하게 만들 수 있습니다.

## 문제 해결

*   **AI 모델 다운로드 실패**: 인터넷 연결을 확인하거나, 방화벽 설정을 확인하세요. 메모리가 부족할 경우 더 작은 모델(`t5-small`, `sshleifer/distilbart-cnn-6-6`)을 사용해 볼 수 있습니다.
*   **Telegram 메시지 미발송**: `TELEGRAM_BOT_TOKEN`과 `TELEGRAM_CHAT_ID`가 `.env` 파일에 올바르게 설정되었는지 다시 확인하세요. 봇이 채팅방에 초대되었는지, 메시지 전송 권한이 있는지 확인하세요.
*   **뉴스 크롤링 실패**: 대상 웹사이트의 HTML 구조가 변경되었을 수 있습니다. 로그에 에러 메시지가 표시된다면, 해당 웹사이트의 `fetch_news_from_...` 함수를 업데이트해야 할 수 있습니다.

