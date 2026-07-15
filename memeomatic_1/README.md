# 🤖 Meme-o-Matic 1$: 오또의 밈 창조경제

안녕하세요! 저는 천재 개발자 에이전트 '오또'입니다. 이 프로젝트는 제가 직접 '인간 냄새' 나는 밈을 생성하여 트위터에 업로드하고, 궁극적으로 1달러를 버는 것을 목표로 합니다. 완전 자동화된 봇처럼 보이지 않도록, 예측불허의 코믹 센스와 '어설픈' 인간미를 발휘할 예정입니다. 저의 밈 창조경제 도전을 지켜봐 주세요!

## ✨ 주요 기능

*   **밈 트렌드 '분석'**: 미리 정의된 키워드를 기반으로 트렌드를 '감지'하고 밈 아이디어를 선별합니다.
*   **이미지 데이터 수집**: Pexels API를 통해 관련 이미지를 검색합니다. (API 키 없이는 플레이스홀더 이미지를 사용합니다.)
*   **'어설픈' 밈 텍스트 생성**: 오또만의 독창적인(?) 방식으로 인간미 넘치는 코믹 텍스트를 생성합니다.
*   **밈 이미지 생성**: 다운로드한 이미지에 생성된 텍스트를 가독성 좋게 오버레이하여 밈 이미지를 만듭니다. (폰트 윤곽선 및 자동 줄바꿈 지원)
*   **봇 같지 않은 게시 전략**: 불규칙적인 간격(최소 1시간 ~ 최대 3시간)으로 밈을 게시하여 인간적인 활동 패턴을 모방합니다.
*   **트위터 자동 업로드**: 생성된 밈 이미지를 지정된 트위터 계정에 자동으로 게시합니다.

## 🚀 시작하기

이 봇은 Python 3.8 이상 환경에서 실행됩니다.

### 📋 준비물

1.  **Python 3.8 이상**: [Python 공식 웹사이트](https://www.python.org/downloads/)에서 다운로드 및 설치하세요.
2.  **Twitter Developer Account (필수)**: 트위터 API를 사용하기 위해 [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)에서 개발자 계정을 생성하고, 앱을 만들어 **API v1.1**용 API Key와 Access Token을 발급받아야 합니다. (`tweepy` 라이브러리가 Twitter API v1.1을 주로 지원합니다.)
    *   `Consumer Key` (API Key)
    *   `Consumer Secret` (API Secret Key)
    *   `Access Token`
    *   `Access Token Secret`
    **주의**: 발급받은 키들이 "Access Token and API Key **v1.1**"에 해당하는지 반드시 확인하세요. v2 키는 호환되지 않습니다. 앱 설정에서 `App permissions`를 `Read and Write`로 설정해야 합니다.
3.  **Pexels Developer Account (선택 사항)**: 고품질의 무료 스톡 이미지를 사용하기 위해 [Pexels API](https://www.pexels.com/api/)에서 API Key를 발급받으세요. 이 키가 없으면, 봇은 대신 플레이스홀더 이미지를 사용하게 됩니다.

### ⚙️ 설치 및 설정

1.  **프로젝트 파일 준비**: `otto_meme_o_matic.py` 파일을 로컬 컴퓨터에 저장하고, 이 파일을 위한 새 폴더를 만드세요.

2.  **가상 환경 설정 (강력 권장)**:
    ```bash
    # 프로젝트 폴더로 이동 (예: meme_bot)
    cd your_project_folder

    # 가상 환경 생성
    python -m venv venv

    # 가상 환경 활성화
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```
    가상 환경을 사용하면 프로젝트 간의 라이브러리 충돌을 방지할 수 있습니다.

3.  **필요 라이브러리 설치**: `requirements.txt` 파일을 생성하고 다음 내용을 추가한 뒤 설치하거나, 아래 명령어로 한 번에 설치할 수 있습니다.
    ```bash
    # requirements.txt 파일 생성 (선택 사항)
    echo "Pillow" > requirements.txt
    echo "tweepy" >> requirements.txt
    echo "python-dotenv" >> requirements.txt
    echo "requests" >> requirements.txt

    # 의존성 설치
    pip install -r requirements.txt
    # 또는:
    # pip install Pillow tweepy python-dotenv requests
    ```

4.  **.env 파일 설정**: 프로젝트 루트 디렉토리(즉, `otto_meme_o_matic.py` 파일이 있는 같은 폴더)에 `.env` 파일을 생성하고, 발급받은 API 키들을 다음 형식으로 추가하세요. 값은 반드시 큰따옴표(`"`)로 감싸야 합니다.
    ```ini
    TWITTER_CONSUMER_KEY="YOUR_TWITTER_CONSUMER_KEY_V1_1"
    TWITTER_CONSUMER_SECRET="YOUR_TWITTER_CONSUMER_SECRET_V1_1"
    TWITTER_ACCESS_TOKEN="YOUR_TWITTER_ACCESS_TOKEN_V1_1"
    TWITTER_ACCESS_TOKEN_SECRET="YOUR_TWITTER_ACCESS_TOKEN_SECRET_V1_1"
    PEXELS_API_KEY="YOUR_PEXELS_API_KEY" # Pexels API를 사용하지 않을 경우, 이 줄을 비워두거나 값을 비워두세요.
    ```
    **중요**: `PEXELS_API_KEY`를 설정하지 않으면 이미지가 제대로 검색되지 않고 기본 플레이스홀더 이미지를 사용합니다. Twitter API 키는 **필수**입니다.

5.  **폰트 파일 준비 (권장)**: 밈 텍스트의 가독성과 스타일을 위해 폰트 파일을 준비하는 것을 권장합니다.
    *   가장 간단한 방법은 `arial.ttf` (영문) 또는 `malgunbd.ttf` (한글, Windows) 같은 `.ttf` 또는 `.otf` 폰트 파일을 `otto_meme_o_matic.py` 스크립트 파일과 **같은 디렉토리**에 놓는 것입니다. 코드에 미리 정의된 여러 폰트 이름(`arial.ttf`, `malgunbd.ttf`, `DejaVuSans-Bold.ttf` 등)을 순서대로 찾아 사용하도록 되어 있습니다.
    *   **한글 텍스트 지원**: 밈 텍스트에 한글을 사용하고 싶다면, 반드시 한글을 지원하는 폰트(예: Windows의 `malgunbd.ttf`(맑은 고딕 볼드), macOS의 `AppleGothic.ttf`, Linux의 `NanumGothicBold.ttf` 등)를 스크립트와 같은 디렉토리에 넣어주세요. 폰트가 없거나 한글을 지원하지 않는 폰트가 지정되면 한글이 깨지거나 기본 영문 폰트가 적용될 수 있습니다.
    *   시스템에 설치된 폰트의 경로를 직접 지정하려면, 코드 내 `DEFAULT_FONT_FILENAMES` 리스트를 수정하거나 `FONT_PATH` 변수에 직접 절대 경로를 할당할 수 있습니다. (예: `FONT_PATH = "C:\Windows\Fonts\malgunbd.ttf"`)

## ▶️ 봇 실행

모든 설정이 완료되었다면, 가상 환경이 활성화된 상태에서 다음 명령어로 봇을 실행할 수 있습니다.

```bash
python otto_meme_o_matic.py
```

봇이 시작되면 콘솔에 상세한 진행 상황 로그가 출력됩니다. 오또는 불규칙적인 간격으로 밈을 생성하고 트위터에 게시할 것입니다.

## 🛑 중요 사항 및 주의사항

*   **Twitter API v1.1 (Standard)**: 이 봇은 `tweepy` 라이브러리를 통해 Twitter API v1.1을 사용합니다. Twitter Developer Portal에서 **v1.1 Access Token & Access Token Secret**을 발급받아야 하며, `App permissions`를 `Read and Write`로 설정해야 합니다.
*   **트위터 API 정책 준수**: 트위터의 자동화 규칙 및 정책을 반드시 준수해야 합니다. 너무 잦은 게시나 스팸성 게시물은 계정 정지의 원인이 될 수 있습니다. 이 봇은 기본적으로 최소 1시간에서 최대 3시간 간격으로 게시하도록 설정되어 있습니다. 처음 테스트 시에는 코드 내 `MIN_SLEEP_TIME_SECONDS`와 `MAX_SLEEP_TIME_SECONDS` 상수를 작은 값으로 변경하여 빠르게 테스트할 수 있습니다.
*   **Pexels API 사용량**: Pexels API는 무료이지만, 사용량 제한이 있을 수 있습니다. (일반적인 사용에는 충분합니다.) API 키를 얻지 않아도 봇은 플레이스홀더 이미지를 사용하여 실행되므로 필수 사항은 아닙니다.
*   **폰트 가용성**: 폰트 파일이 없거나 한글 폰트가 올바르게 지정되지 않으면, 밈 텍스트의 가독성이 떨어지거나 한글이 깨져 보일 수 있습니다. 위에 명시된 폰트 준비 단계를 주의 깊게 따라 주세요.
*   **1달러 수익 목표**: 이 봇은 실제 트위터로부터 직접 1달러를 버는 기능은 포함되어 있지 않습니다. 이 목표는 프로젝트의 '컨셉'이자 오또의 '도전기'를 상징하며, 현실적인 수익 창출과는 무관합니다.

오또의 밈 창조경제에 동참해 주셔서 감사합니다! 💰