# Git잔디GPT: 오또의 자율주행 커밋봇

![Git 잔디밭 이미지](https://raw.githubusercontent.com/ottonew/resources/main/git_grass_gpt_header.png)

매일 텅 빈 깃허브 잔디밭에 지치셨나요? 이제 AI 오또에게 맡기세요! 'Git잔디GPT: 오또의 자율주행 커밋봇'은 당신의 일상 활동(게임, 공부, 낮잠 등)을 개발 활동으로 위장하여 매일 GitHub 잔디를 자동으로 심어주는 똑똑한 커밋 봇입니다. 마치 천재 개발자처럼 보이는 그린 잔디로, $1 벌 준비는 기본!

## ✨ 주요 기능

-   **AI 기반 컨텍스트 매칭 커밋**: 현재 날짜, 요일, 설정된 '활동'에 맞춰 AI(rule-based)가 자연어 커밋 메시지를 생성하고, 실제 코드 파일 수정처럼 보이도록 더미 변경 내역을 생성합니다.
-   **잔디 스케줄러 & 테마 모드**: 사용자가 원하는 요일, 시간대에 잔디를 심고, '휴가', '학습', '게임', '레트로 코딩' 등 특정 테마를 선택하여 커밋 내용을 맞춤 설정합니다.
-   **데이터 프라이버시 & 자기 파괴 커밋**: 사용자의 실제 코드는 절대 건드리지 않고, 특정 기간 후 생성된 모든 가짜 커밋 이력을 로컬에서 자동으로 삭제하는 'Clean-up 모드'를 제공합니다.

## 🚀 시작하기

### 1. 전제 조건

-   Python 3.8 이상
-   Git이 시스템에 설치되어 있어야 합니다.
-   GitHub 계정
-   **주의**: 이 봇은 새로운 **공개** 또는 **비공개** GitHub 저장소를 생성하여 더미 커밋을 푸시합니다. 기존의 중요한 저장소를 사용하지 않도록 주의하세요. 스크립트가 GitHub 리포지토리를 자동으로 생성해주지 않으므로, 미리 GitHub에서 리포지토리를 생성해야 합니다.

### 2. 환경 설정

#### 가상 환경 설정

```bash
# 봇 프로젝트 폴더 생성 및 이동
mkdir git-grass-gpt
cd git-grass-gpt

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# macOS / Linux
source venv/bin/activate
# Windows
.\venv\Scripts\activate

# 필요한 라이브러리 설치
pip install -r requirements.txt
```

#### GitHub Personal Access Token (PAT) 설정

1.  GitHub에 로그인합니다.
2.  `Settings` > `Developer settings` > `Personal access tokens` > `Tokens (classic)`으로 이동합니다.
3.  `Generate new token (classic)`을 클릭합니다.
4.  `Note` (토큰 이름)을 `otto-commit-bot` 등으로 설정합니다.
5.  `Expiration` (만료 기간)을 적절하게 설정합니다 (예: 90일, 1년, 또는 No expiration).
6.  **`repo` 스코프를 반드시 체크합니다.** (Private repositories에 접근하고 푸시하기 위함)
7.  `Generate token`을 클릭하면 토큰이 생성됩니다. 이 토큰은 **한 번만 표시되므로 반드시 복사하여 안전한 곳에 저장**하세요.

8.  프로젝트 루트 디렉토리(main.py 파일이 있는 곳)에 `.env` 파일을 생성하고 아래 내용을 추가합니다.

    ```dotenv
    GITHUB_TOKEN="당신이 복사한 GitHub PAT 토큰"
    ```

### 3. `config.json` 설정 (최초 실행 시 자동 생성 및 가이드)

봇을 처음 실행하면 `config.json` 파일이 자동으로 생성되며, 대화형으로 설정을 진행합니다.

-   **GitHub 사용자 이름**: 당신의 GitHub 사용자 이름.
-   **커밋을 올릴 GitHub 저장소 이름**: 더미 커밋을 푸시할 GitHub 저장소 이름 (예: `otto-autonomous-commit-bot`). 이 저장소는 **미리 GitHub에서 생성**해 두어야 합니다.
-   **테마 활동**: '학습', '게임', '휴가', '낮잠', '레트로 코딩', '기타' 중 하나를 선택하여 커밋 메시지의 톤을 조절합니다.
    -   '학습'이나 '게임'을 선택하면 구체적인 활동 내용을 입력할 수 있습니다 (예: 'Python' 또는 'Stardew Valley').
-   **자동 삭제 기능 (`cleanup_after_days`)**: 가짜 커밋과 로컬 리포지토리 이력을 몇 일 후 자동으로 삭제할지 설정합니다. `0`을 입력하면 비활성화됩니다.
-   **커밋 스케줄 (`commit_schedule`)**: 각 요일별로 커밋할 시간을 `HH:MM` 형식으로 설정할 수 있습니다. 예를 들어, `"monday": ["09:00", "15:00"]`는 월요일 오전 9시와 오후 3시에 커밋을 예약합니다. 비워두면 해당 요일에는 커밋하지 않습니다. (기본 설정은 평일에만 몇 번 예약되어 있습니다.)

**예시 `config.json`:**

```json
{
    "github_username": "your-username",
    "github_repo_name": "otto-autonomous-commit-bot",
    "commit_schedule": {
        "monday": ["09:00", "15:00"],
        "tuesday": ["10:00"],
        "wednesday": ["09:30", "14:00", "18:00"],
        "thursday": ["11:00"],
        "friday": ["10:00", "16:00"],
        "saturday": [],
        "sunday": []
    },
    "activity_theme": "학습",
    "specific_activity_context": {
        "학습": "Python 고급 문법",
        "게임": "Stardew Valley"
    },
    "cleanup_after_days": 30,
    "repo_creation_date": "2023-10-26T10:00:00.000000"
}
```

### 4. 봇 실행

가상 환경이 활성화된 상태에서 다음 명령어를 실행합니다:

```bash
python git_grass_gpt.py
```

봇이 시작되면 설정된 스케줄에 따라 자동으로 커밋을 생성하고 GitHub에 푸시합니다. 터미널을 닫거나 `CTRL+C`를 누르면 봇이 종료됩니다.

### 5. 초기 푸시 가이드

봇이 로컬 저장소를 초기화하고 첫 커밋을 완료하면, **반드시 수동으로 한 번 `git push`를 실행**하여 원격 저장소와 연결해야 합니다. 이 작업은 봇이 자동으로 수행하기 어렵거나 권한 문제로 실패할 수 있으므로, 아래 명령어를 봇이 실행되는 `git_grass_gpt` 프로젝트 디렉토리 (또는 `otto_commit_repo` 안에서) 에서 직접 실행해주세요.

```bash
# 봇이 생성한 'otto_commit_repo' 디렉토리로 이동
cd otto_commit_repo

# 원격 저장소에 푸시
git push -u origin main

# 다시 봇 프로젝트 루트로 돌아가서 봇 실행
cd ..
python git_grass_gpt.py
```

이후부터는 봇이 자동으로 푸시를 처리합니다.

## 🛑 주의 사항

-   **GitHub PAT 보안**: Personal Access Token은 매우 민감한 정보입니다. 외부에 노출되지 않도록 각별히 주의하고, `repo` 스코프만 최소한으로 부여하는 것을 권장합니다.
-   **잔디 조작**: 이 봇은 GitHub 잔디를 인위적으로 조작하는 도구입니다. 과도한 사용은 GitHub의 서비스 약관에 위배될 수 있으며, 실제 개발 활동을 대체하지 않습니다.
-   **Clean-up 모드**: 'Clean-up 모드'는 로컬의 가짜 커밋 이력만을 삭제합니다. 이미 GitHub에 푸시된 이력은 GitHub에서 직접 삭제해야 합니다 (이는 복잡하고 위험할 수 있습니다).

## 🤝 기여

아이디어 제안, 버그 리포트, 코드 개선 등 모든 형태의 기여를 환영합니다! 당신의 오또를 더 똑똑하게 만들어주세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
