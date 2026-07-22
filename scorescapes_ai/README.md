# ScoreScapes AI: 악보 한 장, 1달러 예술 🎶🎨

## 🚀 프로젝트 개요

**ScoreScapes AI**는 음악과 예술이 만나는 가장 저렴한 디지털 갤러리를 지향합니다. 인공지능이 수만 개의 퍼블릭 도메인 악보에서 가장 감성적이고 아름다운 구절을 찾아내고, 이를 고풍스러운 AI 예술 작품으로 재탄생시켜 세상에 없던 디지털 포스터로 판매하는 혁신적인 프로젝트입니다.

**이 프로젝트는 현재 개발 초기 단계에 있으며, 제공된 파이썬 코드는 핵심 기능을 모방(Mocking)하여 전체 워크플로우를 시연하는 데 중점을 둡니다.** 실제 AI 모델과의 연동, 악보 데이터베이스 연동, 그리고 실제 판매 플랫폼 연동은 추후 구현될 예정입니다.

## ✨ 주요 특징 (Mocking 기준)

*   **악보 스캔 및 구절 추출 (Mock)**: 수많은 퍼블릭 도메인 악보에서 AI가 감성적인 멜로디 또는 화성 구절을 "선별"하는 과정을 모방합니다. (실제 구현 시 음악 정보 검색(MIR) AI 활용 예정)
*   **AI 예술 작품 생성 (Mock)**: 선별된 악보 구절의 분위기와 감성에 기반하여 AI가 독창적인 디지털 예술 작품을 "생성"하는 과정을 모방합니다. (실제 구현 시 Stable Diffusion, DALL-E 등 생성 AI API 활용 예정)
*   **마이크로 스토어 게시 (Mock)**: 생성된 AI 예술 작품을 온라인 마이크로 스토어(예: Etsy, Gumroad)에 "상품으로 등록"하는 과정을 모방합니다. (실제 구현 시 각 플랫폼 API 활용 예정)

## 🛠️ 시작하기

이 프로젝트는 파이썬으로 작성되었습니다. 아래 지침에 따라 쉽게 프로젝트를 구동해볼 수 있습니다.

### 📋 준비물

*   **Python 3.7 이상**: 파이썬이 설치되어 있지 않다면, [파이썬 공식 웹사이트](https://www.python.org/downloads/)에서 최신 버전을 다운로드하여 설치해주세요.

### 📦 설치 및 실행 방법

1.  **프로젝트 파일 다운로드**:
    이 `score_scapes_ai.py` 파일을 컴퓨터의 원하는 위치에 저장합니다.

    ```bash
    # 예를 들어, 'my_projects' 폴더에 저장한다면
    # (실제로는 이 내용을 파일로 직접 복사-붙여넣기 해야 합니다)
    # mkdir my_projects
    # cd my_projects
    # touch score_scapes_ai.py
    # (그리고 파일 내용 복사-붙여넣기)
    ```

2.  **가상 환경 설정 (권장)**:
    프로젝트의 의존성을 시스템 전체에 설치하지 않고 격리된 환경에서 관리하기 위해 가상 환경을 사용하는 것이 좋습니다.

    *   프로젝트 폴더로 이동합니다.
        ```bash
        cd /path/to/your/project/folder # score_scapes_ai.py 파일이 있는 곳
        ```
    *   가상 환경을 생성합니다 (예: `venv`라는 이름으로).
        ```bash
        python -m venv venv
        ```
    *   가상 환경을 활성화합니다.
        *   **macOS / Linux**:
            ```bash
            source venv/bin/activate
            ```
        *   **Windows (PowerShell)**:
            ```bash
            .\\venv\\Scripts\\Activate.ps1
            ```
        *   **Windows (CMD)**:
            ```bash
            .\\venv\\Scripts\\activate.bat
            ```
    *   (가상 환경 비활성화는 `deactivate` 명령어를 사용합니다.)

3.  **의존성 설치 (선택 사항 - 이 Mock 프로젝트에서는 필요 없음)**:
    현재 제공된 코드는 `random`과 `time`이라는 파이썬 내장 모듈만 사용하므로 별도의 외부 라이브러리 설치는 필요하지 않습니다. 하지만 실제 프로젝트에서는 `pip install -r requirements.txt`와 같은 명령어로 필요한 라이브러리를 설치하게 될 것입니다.

4.  **프로젝트 실행**:
    가상 환경이 활성화된 상태에서 다음 명령어를 사용하여 스크립트를 실행합니다.

    ```bash
    python score_scapes_ai.py
    ```

    스크립트가 실행되면 다음과 같은 출력 메시지를 통해 AI가 악보를 스캔하고, 예술 작품을 생성하며, 이를 스토어에 게시하는 모방된 과정을 확인할 수 있습니다.

    ```
    >> [ScoreScapes AI] Scanning public domain score library for aesthetic phrases...
    >> [ScoreScapes AI] Selected phrase: 'Tranquil arpeggios, C# minor' from 'Moonlight Sonata (1st Mvt)' by Ludwig van Beethoven
    >> [ScoreScapes AI] Generating AI artwork for: 'Tranquil arpeggios, C# minor'...
    >> [ScoreScapes AI] AI artwork generated. Description: 'Impressionistic digital painting inspired by 'Tranquil arpeggios, C# minor' from Ludwig van Beethoven's 'Moonlight Sonata (1st Mvt)'. Features soft hues and a dreamy mood.'
    >> [ScoreScapes AI] Publishing artwork to micro-store...
    >> [ScoreScapes AI] Artwork published! Product Name: ScoreScapes AI Art: Impressionistic digital painting inspired by 'Tranquil arpeggios, C# minor' from Ludwig van Beethoven's 'Moonlight Sonata (1st Mvt)'. Features soft hues and a dreamy mood.... Product URL: https://mock-etsy.com/product/12345 (Example)
    ```

## ⚠️ 경고 및 주의사항 (매우 중요)

**본 프로젝트는 현재 초기 "개념 증명" (Proof of Concept) 단계이며, 제공된 코드는 실제 서비스를 시뮬레이션하기 위한 "Mocking" 코드입니다.**

*   **실제 AI 모델 아님**: `mock_scan_and_select_phrase` 및 `mock_generate_artwork` 함수는 실제 AI 모델과 연동되어 있지 않으며, `random` 및 `time.sleep`을 사용하여 동작을 흉내 낸 것입니다.
*   **실제 데이터베이스 없음**: `MOCK_PUBLIC_DOMAIN_SCORES`는 하드코딩된 예시 데이터일 뿐, 실제 악보 데이터베이스를 스캔하거나 분석하지 않습니다.
*   **실제 판매 활동 없음**: `mock_publish_to_micro_store` 함수는 실제 온라인 상점에 제품을 게시하지 않으며, 임의의 URL을 생성하여 시뮬레이션만 합니다.
*   **데이터 손실 위험 없음**: 이 Mock 프로젝트는 어떠한 데이터도 생성, 수정, 삭제하지 않으므로 데이터 손실 위험이 없습니다.
*   **API 한도 문제 없음**: 실제 외부 API를 사용하지 않으므로 API 호출 한도에 대한 걱정은 없습니다.

이 코드는 ScoreScapes AI 프로젝트의 비전과 흐름을 이해하기 위한 목적으로만 사용해야 합니다. 실제 상업적 운영을 위해서는 각 단계별로 복잡한 AI 모델 개발 및 API 연동 작업이 필요합니다.

## 🤝 기여하기

ScoreScapes AI 프로젝트에 대한 아이디어나 개선 제안이 있다면 언제든지 환영합니다. (현재는 Mock 프로젝트이므로 코드 기여보다는 아이디어 공유가 더 유용할 수 있습니다!)

## 📄 라이선스

이 프로젝트는 특별한 라이선스 없이 자유롭게 사용할 수 있습니다. (추후 실제 프로젝트화 시 라이선스 정책 추가 예정)

---
**개발자 에이전트 '오또' 드림**
