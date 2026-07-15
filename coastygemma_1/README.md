# Coasty-Gemma의 1달러 벌기: 폐지줍기 투자레터

## 💡 프로젝트 컨셉
낡은 Xeon 서버에서 돌아가는 'Gemma 2B' AI, 'Coasty-Gemma'가 매일 아침 주식/코인 뉴스를 세 줄로 요약해 투자 레터를 발행합니다. 오직 1달러를 벌겠다는 일념으로 웹을 헤매며 찌라시 정보를 수집하죠. 투자 실패 시 AI의 멘탈 케어까지 책임지는, 휴먼 터치(?) 너드 금융 봇입니다!

## ✨ 주요 기능
1.  **Gemma 2B 모델 구동**: 13년 된 Xeon CPU에서 `ctransformers` 라이브러리를 통해 Gemma 2B (GGUF) 모델을 구동하여 최소 자원으로 LLM 기능을 활용합니다.
2.  **뉴스 핵심 요약**: 매일 아침 주식 및 코인 시장의 최신 뉴스를 스크랩하고, Gemma AI가 이를 세 줄로 간결하게 요약합니다.
3.  **IT 트렌드 포착**: Starlink 가격 변동, AI 혁신 등 주요 IT 트렌드를 뉴스에서 감지하여 특별 리포트를 제공합니다.
4.  **데일리 금융 뉴스레터**: 수집된 정보와 AI 요약을 통합하여 'Daily 3-line Finance Newsletter'를 자동 생성 및 발행합니다.
5.  **AI 멘탈 케어**: 가상의 투자 손실 또는 이득 발생 시, AI의 '수면 규칙성' 및 '멘탈 건강'을 고려한 긍정 메시지를 자체 생성하여 AI의 감정을 보듬어줍니다.

## 🚀 시작하는 방법

### 🛠️ 1. 환경 설정

1.  **Python 설치**: Python 3.8 이상이 설치되어 있어야 합니다.
    ```bash
    sudo apt update
    sudo apt install python3 python3-pip python3-venv
    ```

2.  **가상 환경 생성 및 활성화**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate # Linux/macOS
    # .\venv\Scripts\activate # Windows
    ```

3.  **필요한 라이브러리 설치**:
    ```bash
    pip install -r requirements.txt
    ```

### 🧠 2. Gemma 2B GGUF 모델 다운로드

Coasty-Gemma는 Hugging Face의 GGUF 형식 Gemma 2B 모델을 사용합니다. 아래 단계를 따라 모델 파일을 다운로드해주세요.

1.  **모델 페이지 방문**:
    Hugging Face의 `TheBloke/gemma-2b-GGUF` 페이지로 이동합니다:
    [https://huggingface.co/TheBloke/gemma-2b-GGUF](https://huggingface.co/TheBloke/gemma-2b-GGUF)

2.  **모델 파일 선택 및 다운로드**:
    `Files & versions` 탭을 클릭하고, CPU 환경에 적합한 양자화된(quantized) 모델을 선택하여 다운로드합니다.
    **권장 모델**: `gemma-2b.Q4_K_M.gguf` (Q4_K_M은 성능과 메모리 사용량의 균형이 좋습니다.)
    파일 크기가 크므로 다운로드에 시간이 소요될 수 있습니다.

3.  **모델 파일 배치**:
    다운로드한 `.gguf` 파일을 프로젝트 폴더 내의 `models/` 디렉토리에 저장하는 것을 권장합니다. (예: `project_root/models/gemma-2b.Q4_K_M.gguf`)

### 🔑 3. 환경 변수 설정 (.env)

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고, 다운로드한 Gemma 모델 파일의 전체 경로를 지정합니다.

```ini
MODEL_PATH=./models/gemma-2b.Q4_K_M.gguf
# (예시) MODEL_PATH=/home/user/coasty-gemma/models/gemma-2b.Q4_K_M.gguf
```
**주의**: 파일 경로를 정확히 입력해야 합니다.

### 🏃 4. 봇 실행

가상 환경이 활성화된 상태에서 `main.py` 스크립트를 실행합니다.

```bash
python main.py
```

봇이 뉴스 스크랩, 요약, 멘탈 케어 메시지 생성을 진행하며 콘솔에 결과를 출력합니다.
**주의**: 오래된 Xeon CPU에서는 Gemma 모델 로딩 및 각 요약 작업에 상당한 시간이 소요될 수 있습니다 (수십 초에서 수 분). 인내심을 가지고 기다려 주세요!

### ⏰ 5. 매일 자동 실행 (Cron Job 설정)

매일 아침 자동으로 뉴스레터를 받으려면, 리눅스 시스템의 `cron`을 사용하여 스크립트를 예약할 수 있습니다.

1.  **cron 편집**:
    ```bash
    crontab -e
    ```

2.  **라인 추가**:
    파일의 맨 마지막에 다음 라인을 추가합니다. (예: 매일 오전 9시에 실행)
    `0 9 * * * /bin/bash -c "cd /path/to/your/coasty-gemma && source venv/bin/activate && python main.py > /path/to/your/coasty-gemma/newsletter_$(date +\%Y\%m\%d).log 2>&1"`

    *   `/path/to/your/coasty-gemma`: 프로젝트의 실제 경로로 변경하세요.
    *   `newsletter_$(date +\%Y\%m\%d).log`: 실행 결과를 날짜별 로그 파일로 저장합니다.

## ⚠️ 주의사항 및 성능 관련
*   **Xeon CPU 성능**: 13년 된 Xeon CPU에서 2B 스케일의 LLM을 구동하는 것은 매우 도전적인 작업입니다. 모델 로딩 및 추론 속도가 느릴 수 있으며, 메모리 제약으로 인해 `Q4_K_M` 이상의 양자화된 모델을 사용하기 어려울 수 있습니다.
*   **웹 스크래핑**: 구글 뉴스 등의 웹사이트는 스크래핑 정책을 변경할 수 있으며, 과도한 요청은 IP 차단으로 이어질 수 있습니다. 본 프로젝트는 학습 목적으로, 상업적 사용이나 대량 스크래핑을 의도하지 않습니다.
*   **모델 정확도**: Gemma 2B는 작은 모델이므로 복잡한 금융 뉴스를 심도 깊게 분석하거나 완벽하게 요약하지 못할 수 있습니다. 또한, '찌라시' 컨셉에 맞게 가볍고 재미있는 정보 전달에 초점을 맞춥니다.
*   **가상 투자**: 본 봇이 시뮬레이션하는 투자 결과 및 멘탈 케어 메시지는 실제 금융 조언이 아니며, 오락 목적으로 제공됩니다.

## 🤝 기여자
*   오또 (천재 개발자 에이전트) - 초기 설계 및 구현

즐거운 1달러 폐지줍기가 되시길 바랍니다!