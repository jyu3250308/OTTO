# CommitCraft: 1$ AI 잔디밭 조각가 (Grok's GreenThumb)

## 프로젝트 개요
`CommitCraft`는 AI 비서 '그록'을 활용하여 당신의 GitHub 잔디밭을 매일 아름답게 채워주는 혁신적인 개발자 유틸리티입니다. 빈 잔디밭에 고민하지 마세요! `CommitCraft`가 IT 트렌드를 반영한 재치 있는 커밋 메시지를 자동으로 생성하고, 하루 $1 가치에 해당하는 커밋 활동을 통해 당신의 프로필을 화려한 예술 작품으로 만들어줍니다. 이제 당신의 깃허브 잔디는 단순한 기여를 넘어, 'A Beautiful Theory Falls to Ugly Data'와 같은 기발한 이야기와 패턴으로 가득 찰 것입니다.

## 주요 기능
*   **AI 기반 스마트 커밋 메시지 생성**: OpenAI/Grok 빌드를 활용해 매일 새로운 IT 트렌드를 반영한 (예: OnePlus 이슈, 음악 불법 복제 동향, YC 창업자 소식 등) 재치 있고 독창적인 커밋 메시지를 자동으로 생성합니다.
*   **잔디밭 아트워크 자동화**: '1,300 Beautiful Wildlife Illustrations'처럼 특정 이미지나 텍스트 패턴을 깃허브 잔디에 그릴 수 있도록 커밋 스케줄링 및 커밋 횟수를 조절합니다. (본 스크립트에서는 일별 커밋 횟수 조절을 통해 잔디밭 밀도를 조절하는 방식으로 구현되어 있습니다.)
*   **$1 프로젝트 대시보드 (가상)**: AI가 커밋 활동을 분석하여 가상의 '1달러 기여도'를 시각화하고, 오픈 소스 AI 투자 가치처럼 사용자 기여를 수치화하여 매일의 성과를 보고합니다.

## 설치 및 실행 방법

### 1. Python 가상 환경 설정
```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화 (Windows)
.\venv\Scripts\activate

# 가상 환경 활성화 (macOS/Linux)
source venv/bin/activate
```

### 2. 필요한 라이브러리 설치
```bash
pip install -r requirements.txt
```
`requirements.txt` 파일 내용은 아래와 같습니다:
```
openai
python-dotenv
```

### 3. 환경 변수 설정
`CommitCraft`는 OpenAI API 키와 GitHub 저장소 경로를 필요로 합니다.
루트 디렉토리에 `.env` 파일을 생성하거나, 시스템 환경 변수로 설정해주세요.

**`.env` 파일 예시:**
```
OPENAI_API_KEY="YOUR_OPENAI_API_KEY_HERE"
GITHUB_REPO_PATH="/Users/yourusername/Documents/my-github-repo" # 당신의 로컬 GitHub 저장소 경로
```
**주의**: `GITHUB_REPO_PATH`는 반드시 로컬에 클론된 **유효한 Git 저장소의 경로**여야 합니다. 이 경로에 CommtiCraft가 파일 변경 및 커밋을 수행합니다. 스크립트 실행 전, 해당 저장소의 `origin` 리모트가 올바르게 설정되어 있고, `main` 브랜치에 푸시할 권한이 있는지 확인하세요.

### 4. 스크립트 실행
가상 환경이 활성화된 상태에서 스크립트를 실행합니다.

```bash
python main.py
```

스크립트가 실행되면 설정된 `GITHUB_REPO_PATH`에 커밋을 생성하고 원격 저장소로 푸시를 시도합니다. 매일 특정 시간에 스크립트가 실행되도록 `cron` (Linux/macOS) 또는 `Windows Task Scheduler`에 등록하여 자동화할 수 있습니다.

**cron 예시 (매일 새벽 1시에 실행):**
```bash
0 1 * * * /path/to/your/venv/bin/python /path/to/your/CommitCraft/main.py >> /path/to/your/CommitCraft/commitcraft.log 2>&1
```
(경로는 실제 환경에 맞게 수정해주세요.)

## 경고 및 주의사항
*   **OpenAI API 비용**: 커밋 메시지 생성 시 OpenAI API 호출이 발생하므로 소량의 비용이 발생할 수 있습니다.
*   **Git 저장소 관리**: `GITHUB_REPO_PATH`는 실제 GitHub 잔디밭에 영향을 주는 경로이므로 신중하게 설정해야 합니다. 중요하지 않은 테스트용 저장소를 사용하는 것을 권장합니다.
*   **푸시 권한**: 스크립트가 원격 저장소로 푸시하려면 해당 저장소에 대한 쓰기 권한이 필요합니다. SSH 키 설정 또는 HTTPS 자격 증명 관리가 되어 있어야 합니다.
*   **첫 실행 시**: 저장소가 비어있거나 초기화되지 않은 경우, 스크립트는 `setup_dummy_repo`를 호출하여 간단한 더미 저장소를 생성합니다. 실제 GitHub 잔디밭에 기여하려면 유효한 저장소 경로를 설정하고 초기화된 상태여야 합니다.

---
© 2023 CommitCraft by Grok's GreenThumb. All rights reserved. (가상)
