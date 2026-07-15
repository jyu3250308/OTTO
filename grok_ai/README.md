# 오또의 잔디GroK: AI 스텔스 잔디 파수꾼

## 🤖 당신의 GitHub 잔디를 완벽하게 가꿔줄 '오또' 봇 🤖

이 프로젝트는 당신의 GitHub 커밋 이력을 은밀히 관찰하고, 비어있는 잔디밭을 찾아 무해한 '미니멀' 커밋으로 메워주는 AI 스텔스 잔디 파수꾼입니다. 이제 1달러로 완벽한 '성실 개발자' 코스프레를 시작하세요!

### ✨ 주요 기능

*   **AI 잔디 패턴 분석 & 자동 채우기**: Grok-esque AI가 사용자가 지정한 더미(Dummy) 저장소의 커밋 이력을 분석하여, 빈 잔디(커밋이 없는 날)를 찾아 '미니멀' 커밋으로 자동 생성 및 푸쉬합니다.
*   **스텔스 커밋 제네레이터**: 실제 코드에 영향을 주지 않는, `.gitignore` 업데이트나 주석 추가 등 '티 안 나는' 커밋을 지능적으로 생성합니다. 커밋 메시지도 자연스럽게 생성됩니다.
*   **Voxel 잔디 현황판**: 현재 GitHub 잔디 상황을 (콘솔 기반) Voxel 아트로 시각화하여, 성장에 따른 시각적 쾌감을 제공합니다.

### 🚀 시작하기

Ottos_GrassGroK 봇을 실행하기 위한 단계별 가이드입니다. 순서대로 따라 해주세요.

#### 1. 필수 전제 조건 확인

이 봇은 Python 3와 Git이 설치되어 있어야 합니다.

*   **Python 3**: 터미널에서 `python3 --version`을 실행하여 Python 3.7 이상이 설치되어 있는지 확인하세요.
*   **Git**: 터미널에서 `git --version`을 실행하여 Git이 설치되어 있는지 확인하세요. 설치되어 있지 않다면, [Git 공식 웹사이트](https://git-scm.com/downloads)에서 다운로드하여 설치해 주세요.

#### 2. 프로젝트 설정

**2.1 프로젝트 디렉토리 생성 및 이동**

```bash
mkdir ottos-grassgrok
cd ottos-grassgrok
```

**2.2 가상 환경 설정 (강력 권장)**

프로젝트 종속성 관리를 위해 가상 환경을 사용하는 것을 강력히 권장합니다. 가상 환경은 시스템 환경을 깨끗하게 유지하는 데 도움을 줍니다.

```bash
# 가상 환경 생성 (venv라는 이름의 환경이 생성됩니다)
python3 -m venv venv

# 가상 환경 활성화
# Windows
.\venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

가상 환경이 활성화되면 터미널 프롬프트 앞에 `(venv)`와 같은 표시가 나타납니다.

**2.3 필요한 라이브러리 설치**

프로젝트가 의존하는 라이브러리들을 설치합니다. `requirements.txt` 파일에 정의되어 있습니다.

```bash
pip install -r requirements.txt
```

#### 3. GitHub 개인 액세스 토큰 (PAT) 생성

오또 봇이 당신의 GitHub 저장소에 커밋을 푸쉬하려면 권한이 필요합니다. 다음 단계에 따라 PAT를 생성하세요.

1.  GitHub에 로그인합니다.
2.  `Settings` > `Developer settings` > `Personal access tokens` > `Tokens (classic)`으로 이동합니다.
3.  `Generate new token` 버튼을 클릭합니다.
4.  `Note` (설명)에 `Ottos_GrassGroK_Token` 등 식별 가능한 이름을 입력합니다.
5.  `Expiration` (만료)을 적절히 설정합니다 (예: 90일, 1년, 또는 No expiration).
6.  `Select scopes`에서 `repo` (Full control of private repositories)를 **반드시 선택**해야 합니다. 오또 봇이 더미 저장소에 커밋을 푸쉬할 수 있도록 이 권한이 필요합니다.
    **⚠️ 중요**: `repo` 권한은 저장소의 모든 권한을 포함하므로, 이 토큰을 외부에 노출하지 않도록 각별히 주의하세요.
7.  `Generate token` 버튼을 클릭합니다.
8.  **생성된 토큰 문자열을 복사합니다.** 이 토큰은 다시 볼 수 없으므로 안전한 곳에 보관하세요.

#### 4. 더미 GitHub 저장소 생성

오또 봇이 잔디를 가꿀 빈 저장소를 생성해야 합니다. 이 저장소는 오또 봇 전용으로 사용되며, 실제 중요한 프로젝트에 영향을 주지 않습니다.

1.  GitHub에서 새로운 **비공개(Private) 저장소**를 생성합니다. (예: `my-grass-grok-dummy`)
2.  `Add a README file` 옵션은 선택하지 않아도 됩니다. 완전히 비어있는 저장소가 좋습니다.
3.  생성된 저장소의 **HTTPS URL**을 복사합니다. (예: `https://github.com/YourUsername/my-grass-grok-dummy.git`)

#### 5. `.env` 파일 설정

프로젝트 루트 디렉토리 (`ottos-grassgrok`)에 `.env` 파일을 생성하고, 다음 예시와 같이 내용을 채워 넣으세요. `"` (쌍따옴표) 안에 값을 입력하는 것을 잊지 마세요.

```dotenv
GITHUB_TOKEN="ghp_YOUR_PERSONAL_ACCESS_TOKEN"
GITHUB_USERNAME="YourGitHubUsername"
GITHUB_EMAIL="YourGitHubEmail@example.com"
DUMMY_REPO_URL="https://github.com/YourUsername/my-grass-grok-dummy.git"
```

*   `GITHUB_TOKEN`: 위에서 생성한 개인 액세스 토큰 문자열입니다.
*   `GITHUB_USERNAME`: 당신의 GitHub 사용자 이름입니다.
*   `GITHUB_EMAIL`: 당신의 GitHub 계정과 연결된 이메일 주소입니다. (커밋 작성 시 이 이메일로 커밋이 기록됩니다.)
*   `DUMMY_REPO_URL`: 위에서 생성한 더미 저장소의 HTTPS URL입니다.

#### 6. 봇 실행

모든 설정이 완료되었다면, 가상 환경이 활성화된 상태에서 다음 명령어를 실행하여 오또 봇을 시작합니다.

```bash
python3 main.py
```

봇은 다음 작업을 순서대로 수행합니다:
1.  더미 저장소를 로컬에 복제(또는 업데이트)합니다.
2.  지난 90일간의 커밋 이력을 분석하여 비어있는 날짜에 자동으로 커밋을 생성합니다.
3.  생성된 모든 커밋을 GitHub 더미 저장소로 푸쉬합니다.
4.  마지막으로 지난 365일간의 잔디 현황을 콘솔에 Voxel 아트로 시각화하여 보여줄 것입니다.

### 💡 팁

*   **정기적인 실행**: `cron` 잡(Linux/macOS) 또는 작업 스케줄러(Windows)에 등록하여 매일 자동으로 봇을 실행하면 꾸준한 잔디 관리가 가능합니다. 예를 들어, 매일 새벽에 실행되도록 설정할 수 있습니다.
*   **안전**: 오또 봇은 지정된 더미 저장소에만 커밋을 생성합니다. 당신의 다른 중요한 프로젝트에는 영향을 주지 않으므로 안심하고 사용하세요.
*   **커밋 메시지**: 봇은 무작위로 '티 안 나는' 커밋 메시지를 생성합니다. 필요하다면 `generate_stealth_commit` 함수를 수정하여 커밋 메시지 패턴을 변경할 수 있습니다.

### 🗑️ 정리 (Optional)

오또 봇 사용을 중단하고 싶다면, `ottos-grassgrok` 디렉토리를 삭제하고, GitHub 개인 액세스 토큰을 폐기하면 됩니다. 또한, GitHub에 생성했던 더미 저장소도 삭제할 수 있습니다.
