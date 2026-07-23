# Shorts Meeseeks: 1달러 웃음 미션

> 🆕 **v2 UPDATE (2026-07-23)**: 내장 샘플 데이터 대신 **실시간 인기 밈**(meme-api, 무료·키 불필요)을 진짜로 수집합니다!
> 실행하면 `digests/` 폴더에 링크·썸네일이 담긴 **HTML 다이제스트**가 발행돼요 — 더블클릭으로 열어보세요 😂

## 🤖 프로젝트 소개

'Shorts Meeseeks: 1달러 웃음 미션'은 유튜브 쇼츠에서 급부상하는 밈과 유머 영상을 AI가 찾아내고 핵심 웃음 포인트를 3줄로 요약하여 Slack 채널에 공유하는 봇입니다. 마치 "Mr. Meeseeks"처럼, 웃음 미션을 완수하고 사라지는 Slack 봇으로, 당신의 1달러짜리 웃음을 책임집니다!

## ✨ 주요 기능

*   **YouTube Shorts 핫 키워드 & 트렌딩 영상 실시간 모니터링**: 인기 검색어와 조회수 기반으로 유행하는 쇼츠 영상을 자동으로 탐색합니다.
*   **AI 기반 유머 포인트 감지 및 핵심 요약**: OpenAI GPT 모델을 활용하여 영상의 제목과 설명을 분석, 핵심적인 웃음 포인트를 3줄로 간결하게 요약합니다.
*   **Slack 채널 자동 푸시 & '삭제 예정' 미션 완료 알림**: 발견된 쇼츠와 AI 요약을 Slack 채널에 게시하고, 미션 완료 후 자동으로 메시지를 업데이트한 뒤 삭제하여 Mr. Meeseeks의 컨셉을 구현합니다.

## 🚀 시작하기

### 📋 1. 필수 준비물

성공적인 봇 실행을 위해 다음 준비물들이 필요합니다.

*   Python 3.8 이상
*   Google Cloud Project 및 YouTube Data API v3 활성화
*   OpenAI API Key
*   Slack Workspace 및 봇이 메시지를 보낼 Slack 채널

### ⚙️ 2. 환경 설정

#### 2.1. 가상 환경 설정 및 라이브러리 설치

프로젝트 디렉토리로 이동하여 가상 환경을 생성하고 활성화한 뒤, 필요한 라이브러리를 설치합니다.

```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 필요한 라이브러리 설치
pip install -r requirements.txt
```

> `requirements.txt` 파일은 다음 내용을 포함해야 합니다:
> ```
> python-dotenv
> google-api-python-client
> openai
> slack_sdk
> ```
> 만약 `requirements.txt` 파일이 없다면, `pip install python-dotenv google-api-python-client openai slack_sdk` 명령어로 직접 설치할 수 있습니다.

#### 2.2. API 키 및 채널 ID 설정 (환경 변수)

`shorts_meeseeks.py` 파일과 동일한 디렉토리에 `.env` 파일을 생성하고, 다음 형식에 맞춰 발급받은 API 키와 Slack 채널 ID를 입력하세요. 각 키는 해당 서비스에서 발급받아야 합니다.

```dotenv
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
SLACK_BOT_TOKEN="YOUR_SLACK_BOT_TOKEN"
SLACK_CHANNEL_ID="YOUR_SLACK_CHANNEL_ID"
```

**각 키 발급 방법 상세 안내:**

1.  **`GOOGLE_API_KEY` (YouTube Data API v3):**
    *   [Google Cloud Console](https://console.cloud.google.com/)에 접속합니다.
    *   새 프로젝트를 생성하거나 기존 프로젝트를 선택합니다.
    *   `API 및 서비스 > 라이브러리`로 이동하여 `YouTube Data API v3`을 검색 후 **활성화**합니다.
    *   `API 및 서비스 > 사용자 인증 정보`로 이동하여 `사용자 인증 정보 만들기 > API 키`를 선택하여 API 키를 발급받습니다. 보안 강화를 위해 `API 키 제한`을 설정하는 것을 권장합니다.

2.  **`OPENAI_API_KEY`:**
    *   [OpenAI 웹사이트](https://platform.openai.com/account/api-keys)에 로그인하여 API 키를 발급받습니다.

3.  **`SLACK_BOT_TOKEN` 및 `SLACK_CHANNEL_ID`:**
    *   [Slack API](https://api.slack.com/apps) 페이지로 이동하여 `Create an App`을 클릭합니다. (`From scratch` 선택)
    *   App 이름을 지정하고, 알림을 받을 워크스페이스를 선택합니다.
    *   **봇 권한 설정 (`OAuth & Permissions`):**
        *   `Scopes > Bot Token Scopes` 섹션에서 다음 권한을 추가합니다:
            *   `chat:write` (메시지 게시)
            *   `chat:write.customize` (봇 이름 사용자 지정)
            *   `chat:update` (게시된 메시지 업데이트)
            *   `chat:delete` (게시된 메시지 삭제)
            *   `channels:read` (채널 정보 읽기, 초기화 시 채널 유효성 검증용)
    *   **앱 설치 (`Install App to Workspace`):**
        *   권한을 추가한 후 `Install App to Workspace` 버튼을 클릭하여 워크스페이스에 앱을 설치합니다.
        *   설치 완료 후 `Bot User OAuth Token` ( `xoxb-`로 시작)이 발급됩니다. 이 토큰이 `SLACK_BOT_TOKEN`입니다.
    *   **`SLACK_CHANNEL_ID` 찾기:**
        *   Slack 클라이언트에서 봇이 메시지를 게시할 채널로 이동합니다.
        *   채널 이름을 오른쪽 클릭한 후 `링크 복사`를 선택합니다. 복사된 링크의 마지막 `/` 뒤에 오는 문자열이 채널 ID입니다. (예: `https://app.slack.com/client/T01234ABCDE/C05FGHIJKL` 에서 `C05FGHIJKL`이 채널 ID입니다.)
        *   **중요:** 발급받은 봇을 메시지를 보낼 Slack 채널에 `invite`해야 합니다 (예: `/invite @YourBotName`).

### ▶️ 3. 봇 실행

모든 설정이 완료되었다면, 다음 명령어를 사용하여 봇을 실행합니다.

```bash
python shorts_meeseeks.py
```

봇이 실행되면 YouTube에서 트렌딩 쇼츠를 검색하고, AI로 유머 포인트를 분석한 뒤, Slack 채널에 메시지를 게시하고 미션을 완료하며 사라지는 일련의 과정을 상세한 로그와 함께 확인할 수 있습니다. (기본적으로 3개의 영상만 처리하도록 설정되어 있습니다. 이 제한은 코드 내 `PROCESSED_VIDEO_LIMIT` 상수를 통해 조절할 수 있습니다.)

## 📝 참고 및 개선사항

*   **실행 주기**: 현재 스크립트는 한 번 실행된 후 종료됩니다. 주기적으로 봇을 실행하려면 `cron` 작업 스케줄러 (Linux/macOS) 또는 Windows 작업 스케줄러를 활용하거나, `APScheduler`와 같은 Python 라이브러리를 사용하여 스크립트 내에서 스케줄링 로직을 추가할 수 있습니다.
*   **AI 모델**: `gpt-3.5-turbo` 대신 `gpt-4-turbo`와 같은 상위 모델을 사용하면 유머 감지 및 요약 품질이 더욱 향상될 수 있습니다. (비용 증가)
*   **트렌딩 기준**: 현재는 특정 키워드와 `viewCount`를 기준으로 쇼츠를 검색하지만, YouTube API의 다른 필터링 옵션(예: `publishedAfter`로 최근 업로드 영상 필터링)이나 더 정교한 트렌드 분석 로직을 추가할 수 있습니다.
*   **오류 알림**: Slack 메시지 게시 실패나 YouTube/OpenAI API 오류 발생 시 Slack에 직접 알림을 보내는 기능을 추가하여 관리자가 빠르게 대응할 수 있도록 개선할 수 있습니다.
*   **코드 구조**: 현재 전역 변수로 관리되는 클라이언트 인스턴스를 클래스 기반으로 캡슐화하거나, 함수 인자로 전달하는 방식으로 개선하면 코드의 재사용성과 테스트 용이성을 높일 수 있습니다.
*   **설정 파일**: 현재 환경 변수를 사용하는 대신, `config.ini` 또는 `YAML` 파일로 설정을 분리하면 관리가 더 용이할 수 있습니다.
