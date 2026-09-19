# 🚀 TrendTide Sentinel (트렌드 급물살 감시병)

![TrendTide Sentinel Logo](https://raw.githubusercontent.com/ottonim/ottonim/main/images/sentinel_banner.png)
_⬆️ 상상 속 로고 이미지입니다. 실제 출력되지는 않습니다. ⬆️_

**콘텐츠 크리에이터를 위한 AI 감시병, TrendTide Sentinel!** 🌊

주요 소셜 미디어와 커뮤니티에서 특정 주제의 '급격한 확산' 또는 '갑작스러운 관심 하락' 신호를 포착해 실시간으로 알려드립니다. 남들보다 먼저 뜨는 주제를 선점하거나, 식상해진 주제에서 발을 빼도록 돕는 **AI 알림 시스템**입니다.

이 독점적인 '추세 변동 감지' 알림 엔진을 활용하여 콘텐츠 전략을 혁신해 보세요!

--- 

## ✨ 주요 기능

*   **📈 급격한 관심 증가 감지:** 설정된 임계치 이상으로 주제에 대한 언급량이 급증할 때 즉시 알려줍니다.
*   **📉 갑작스러운 관심 하락 감지:** 설정된 임계치 이상으로 주제에 대한 언급량이 급감할 때 경고를 보냅니다.
*   **📊 CSV 데이터 지원:** 사용자가 직접 수집한 CSV 형식의 트렌드 데이터를 분석합니다.
*   **🧪 합성 데이터 생성:** 데이터 파일이 없을 경우, 초보자도 쉽게 테스트해 볼 수 있도록 예시 데이터를 자동으로 생성합니다.
*   **📝 상세 분석 보고서:** 모든 감지 내역을 `.txt` 파일로 저장하여 편리하게 확인할 수 있습니다.
*   **🔑 API 키 불필요:** 복잡한 API 설정 없이 바로 실행할 수 있습니다!

## 💡 TrendTide Sentinel 작동 방식

TrendTide Sentinel은 두 시점(이전과 현재)의 특정 주제에 대한 '언급량(멘션 수)'을 비교하여 변화율을 계산합니다. 이 변화율이 미리 설정해둔 '성장 임계치'를 넘어서면 **급격한 확산**으로, '하락 임계치'를 넘어서면 **갑작스러운 관심 하락**으로 판단하여 즉시 경고를 생성합니다. 즉, 숫자의 변화를 통해 트렌드의 '급물살'을 감지하는 AI 비서라고 할 수 있습니다.

## 🚀 시작하기

TrendTide Sentinel은 파이썬만 설치되어 있다면 별도의 복잡한 설치 과정 없이 바로 사용할 수 있습니다. 초보자도 쉽게 따라 할 수 있도록 상세히 안내해 드립니다!

### 📋 전제 조건

*   **Python 3.x**: 파이썬 3 버전이 컴퓨터에 설치되어 있어야 합니다. [파이썬 공식 웹사이트](https://www.python.org/downloads/)에서 다운로드하여 설치할 수 있습니다.

### 🛠️ 설치 및 준비

1.  **코드 다운로드:** 이 프로젝트의 소스코드 파일인 `trend_tide_sentinel.py` 파일을 컴퓨터의 원하는 위치에 다운로드합니다.

2.  **가상 환경 설정 (선택 사항이지만 권장):**
    파이썬 프로젝트를 관리하는 가장 좋은 방법은 '가상 환경(Virtual Environment)'을 사용하는 것입니다. 이는 시스템 전체의 파이썬 환경과 프로젝트의 종속성을 분리하여 충돌을 방지합니다.
    ```bash
    # 1. 프로젝트 폴더로 이동 (trend_tide_sentinel.py 파일이 있는 곳)
    cd /path/to/your/project/folder

    # 2. 가상 환경 생성
    python -m venv venv

    # 3. 가상 환경 활성화
    # Windows:
    .\venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```
    가상 환경을 활성화하면 터미널 프롬프트 앞에 `(venv)`와 같은 표시가 나타납니다. 이 상태에서 아래 명령어를 실행하면 됩니다.

3.  **라이브러리 설치 (필요 없음!):**
    TrendTide Sentinel은 파이썬 기본 라이브러리(`argparse`, `csv`, `os`, `datetime`)만을 사용하기 때문에, **별도로 `pip install` 명령어를 실행할 필요가 없습니다.** 설치 완료! 🎉

    **✨ 중요: API 키/환경변수 설정은 전혀 필요 없습니다! 즉시 실행하세요!**

### 🏃 실행 방법

**1. 예시 데이터로 빠르게 실행하기 (추천!):**

데이터 파일이 없는 경우, TrendTide Sentinel은 자체적으로 예시 데이터를 생성하여 분석합니다. 가장 간단한 실행 방법입니다.

```bash
python trend_tide_sentinel.py
```

결과:
콘솔에 분석 결과가 실시간으로 출력되며, `trend_report_YYYYMMDD_HHMMSS.txt` 형식의 파일로 보고서가 저장됩니다.

**2. 나만의 데이터 파일로 실행하기:**

만약 직접 수집한 트렌드 데이터가 있다면, 이를 CSV 파일로 만들어 사용할 수 있습니다.

```bash
python trend_tide_sentinel.py --data-file my_trend_data.csv
```

*   `my_trend_data.csv`: 분석하고 싶은 CSV 파일의 경로를 입력합니다.

**3. 임계치(Threshold) 조정하여 실행하기:**

트렌드 감지의 민감도를 조절하고 싶다면, `--growth-threshold`와 `--decline-threshold` 옵션을 사용하세요. (기본값: 20%)

```bash
# 성장 임계치를 30%로, 하락 임계치를 15%로 설정하여 실행
python trend_tide_sentinel.py --data-file my_trend_data.csv --growth-threshold 30 --decline-threshold 15
```

**4. 보고서 파일 이름 지정하기:**

생성될 보고서 파일의 이름을 직접 지정하고 싶다면 `--output` 옵션을 사용하세요.

```bash
python trend_tide_sentinel.py --data-file my_trend_data.csv --output my_custom_report.txt
```

## 📂 데이터 파일 형식 (CSV)

TrendTide Sentinel이 데이터를 제대로 분석하기 위해서는 CSV 파일이 특정 형식을 따라야 합니다. 다음 세 가지 헤더를 포함해야 합니다.

*   `Topic`: 분석하려는 주제의 이름 (예: 