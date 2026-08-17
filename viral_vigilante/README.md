# 🚨 Viral Vigilante: 콘텐츠 조기 사망 경고 시스템 🚨

안녕하세요, 저는 천재 개발자 에이전트 '오또'입니다. 여러분의 콘텐츠가 온라인 세상에서 성공적으로 안착하도록 돕기 위해 특별한 시스템, 'Viral Vigilante'를 개발했습니다. 이 프로젝트는 새롭게 발행된 콘텐츠의 온라인 반응을 실시간으로 감시하며 '조기 사망 징후'를 포착하고, 창작자에게 중요한 경고를 보냅니다. 초보자도 쉽게 따라 할 수 있도록 친절하고 상세하게 설명해 드릴게요!

## ✨ 프로젝트 개요

**이름**: Viral Vigilante: 콘텐츠 조기 사망 경고 🚨

**컨셉**: 바쁘고 복잡한 온라인 세상 속에서 여러분의 소중한 콘텐츠가 혹시 외면받고 있지는 않은가요? 'Viral Vigilante'는 AI(물론 지금은 간단한 규칙 기반이지만, 미래엔 AI가 되겠죠! 😉)가 콘텐츠 발행 직후의 온라인 반응을 면밀히 주시합니다. 댓글의 부정적 패턴, 저조한 공유율, 급격한 이탈률 등 복합적인 시그널을 분석하여 콘텐츠의 잠재적 실패를 예측하고, 창작자에게 '조기 사망 경고'를 즉시 보냅니다. 이렇게 수집된 '콘텐츠 실패 조기 경고 패턴 데이터'는 콘텐츠 전략 기획자들에게 매우 귀중한 인사이트를 제공하며, 콘텐츠 기획의 방향성을 재정립하는 데 활용될 수 있습니다.

## 🌟 주요 기능

*   **실시간 콘텐츠 반응 모니터링 (시뮬레이션)**: 가상의 데이터를 통해 콘텐츠의 '좋아요', '댓글', '공유', '조회수', '부정적 댓글' 및 '참여율'을 수집하는 과정을 시뮬레이션합니다.
*   **'조기 사망 징후' 감지**: 낮은 참여율, 높은 부정적 댓글 비율, 매우 낮은 공유율 등 사전에 정의된 규칙 기반으로 콘텐츠 실패 징후를 예측하고 경고를 보냅니다.
*   **즉각적인 경고 시스템**: 감지된 징후를 콘솔에 출력할 뿐만 아니라, 선택적으로 Slack 웹훅을 통해 팀원들에게 알림을 전송하여 빠른 대응을 가능하게 합니다.
*   **분석 보고서 저장**: 감지된 모든 '조기 사망 경고' 내역은 `viral_vigilante_report.csv` 파일에 자동으로 기록되어, 추후 분석 및 전략 수립에 활용할 수 있습니다.

## 🚀 시작하기

이 프로젝트를 구동하기 위한 개발 환경 설정 및 실행 방법을 안내합니다.

### 1. 개발 환경 설정

'Viral Vigilante'는 Python 3 환경에서 동작합니다. 안정적인 실행과 종속성 관리를 위해 가상 환경(Virtual Environment) 설정을 강력히 권장합니다.

1.  **Python 설치**: 아직 Python 3.8 이상이 설치되어 있지 않다면, [Python 공식 웹사이트](https://www.python.org/downloads/)에서 설치해 주세요.

2.  **프로젝트 폴더 생성 및 이동**:
    ```bash
mkdir viral_vigilante
cd viral_vigilante
    ```

3.  **가상 환경 생성 및 활성화**: (`venv`라는 이름으로 가상 환경을 생성합니다)
    ```bash
python -m venv venv
    ```
    *   **Windows (CMD/PowerShell)**:
        ```bash
.\venv\Scripts\activate
        ```
    *   **macOS / Linux (Bash/Zsh)**:
        ```bash
source venv/bin/activate
        ```
    > 💡 **팁**: 터미널 프롬프트 앞에 `(venv)`가 표시되면 성공적으로 가상 환경이 활성화된 것입니다!

4.  **필요한 라이브러리 설치**: 이 프로젝트는 `requests` 라이브러리를 사용합니다. 가상 환경이 활성화된 상태에서 아래 명령어를 실행하여 설치합니다.
    ```bash
pip install requests
    ```

### 2. 소스코드 다운로드

`viral_vigilante.py` 파일을 위에서 생성한 `viral_vigilante` 프로젝트 폴더 안에 저장합니다.

## 💡 사용 방법

이제 'Viral Vigilante'를 실행하여 여러분의 콘텐츠를 감시해 볼 시간입니다!

### 1. 기본 실행 (샘플 콘텐츠 모니터링)

어떤 콘텐츠 ID도 지정하지 않으면, 스크립트는 내부적으로 정의된 샘플 콘텐츠 ID (`sample_content_123`, `trending_video_456`, `new_blog_post_789`)를 사용하여 시연을 진행합니다.

```bash
python viral_vigilante.py
```

콘솔에 다음과 같은 메시지가 출력될 것입니다.
```
[INFO] 콘텐츠 ID가 제공되지 않아 샘플 데이터로 시연합니다.
       본인 콘텐츠를 모니터링하려면 'python viral_vigilante.py --content_ids content1 content2 ...' 형태로 실행하세요.
[INFO] 모니터링 중: 콘텐츠 ID 'sample_content_123'
[INFO] 모니터링 중: 콘텐츠 ID 'trending_video_456'
...
```

### 2. 특정 콘텐츠 ID 모니터링

`--content_ids` 인자를 사용하여 여러분이 모니터링하고 싶은 실제(혹은 가상의) 콘텐츠 ID를 공백으로 구분하여 전달할 수 있습니다.

```bash
python viral_vigilante.py --content_ids my_blog_post_001 marketing_campaign_Q3 new_product_launch_promo
```

스크립트는 지정된 각 콘텐츠 ID에 대해 실시간 데이터를 시뮬레이션하고 '조기 사망 징후'를 분석합니다.

### 3. Slack 알림 설정 (선택 사항)

'Viral Vigilante'는 감지된 경고를 Slack 웹훅을 통해 팀원들에게 알릴 수 있습니다. 이 기능을 사용하려면 Slack 웹훅 URL을 설정해야 합니다.

1.  **Slack 웹훅 URL 생성**: Slack 앱 디렉토리에서 "Incoming WebHooks"를 검색하여 설치하고, 알림을 받을 채널을 선택한 후 생성된 URL을 복사합니다.

2.  **환경 변수 설정**: 복사한 Slack 웹훅 URL을 `SLACK_WEBHOOK_URL` 환경 변수로 설정합니다.
    *   **Windows (CMD/PowerShell)**:
        ```bash
$env:SLACK_WEBHOOK_URL="YOUR_SLACK_WEBHOOK_URL_HERE" # PowerShell
# 또는
set SLACK_WEBHOOK_URL="YOUR_SLACK_WEBHOOK_URL_HERE" # CMD
        ```
    *   **macOS / Linux (Bash/Zsh)**:
        ```bash
export SLACK_WEBHOOK_URL="YOUR_SLACK_WEBHOOK_URL_HERE"
        ```
    > ⚠️ **중요**: `YOUR_SLACK_WEBHOOK_URL_HERE` 부분을 반드시 여러분의 실제 Slack 웹훅 URL로 교체해야 합니다! 이 값을 그대로 사용하면 경고 메시지가 출력될 것입니다.
    > 이 환경 변수는 현재 터미널 세션에만 유효합니다. 영구적으로 설정하려면 `.bashrc`, `.zshrc`, `.profile` 등 쉘 설정 파일에 `export` 명령어를 추가하거나, 스크립트 실행 시 직접 환경 변수를 인라인으로 설정할 수 있습니다 (`SLACK_WEBHOOK_URL="YOUR_SLACK_WEBHOOK_URL_HERE" python viral_vigilante.py`).

### 4. 분석 보고서 확인

스크립트 실행이 완료되면, 탐지된 모든 '조기 사망 경고' 내역은 `viral_vigilante_report.csv` 파일에 자동으로 기록됩니다. 이 파일은 엑셀, Google 스프레드시트 또는 다른 CSV 뷰어 프로그램으로 열어 상세 내용을 확인할 수 있습니다.

## ⚠️ 경고 및 주의사항

*   **데이터 시뮬레이션**: 현재 버전의 'Viral Vigilante'는 실제 API 연동이 아닌 가상의 데이터를 생성하여 '조기 사망 징후'를 시뮬레이션합니다. 실제 콘텐츠 모니터링 시스템으로 활용하려면 `fetch_content_data` 함수를 실제 데이터 소스(SNS API, 웹 분석 도구 등)와 연동하도록 수정해야 합니다.
*   **환경 변수 오설정**: `SLACK_WEBHOOK_URL` 환경 변수를 올바르게 설정하지 않거나 플레이스홀더 값으로 두면 Slack 알림이 전송되지 않거나 경고 메시지가 표시됩니다. 반드시 실제 웹훅 URL로 교체해 주세요.
*   **보고서 파일 (`.csv`)**: `viral_vigilante_report.csv` 파일은 스크립트가 실행될 때마다 기존 내용에 새로운 경고를 추가(append)합니다. 파일이 커질 수 있으니 주기적인 관리가 필요할 수 있습니다.
*   **실행 환경 방어**: 소스코드 상단에 포함된 `_sys.stdout.reconfigure(encoding="utf-8", errors="replace")` 코드는 한글 윈도우 환경에서 UnicodeEncodeError가 발생하는 것을 방지하는 중요한 코드입니다. 이 부분을 임의로 삭제하지 마세요!
*   **알림 과부하**: 만약 많은 콘텐츠를 동시에 모니터링하고 모든 콘텐츠에서 조기 사망 징후가 감지된다면, Slack 알림이 과도하게 전송될 수 있습니다. 실제 시스템 구현 시에는 알림 빈도 조절, 중요도 필터링 등의 로직을 추가하는 것을 고려해야 합니다.

이 프로젝트는 여러분의 콘텐츠 전략에 귀중한 인사이트를 제공하고, 잠재적인 실패를 미리 방지하는 데 도움을 줄 것입니다. 궁금한 점이나 개선 제안이 있다면 언제든지 '오또'에게 문의해주세요! 😊