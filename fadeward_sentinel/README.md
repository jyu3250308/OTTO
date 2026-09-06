# ✨ Fadeward Sentinel (트렌드 파수꾼) ✨

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python) ![License](https://img.shields.io/badge/License-MIT-green?style=flat-square) (가상의 라이선스)

## 🚀 프로젝트 소개

"Fadeward Sentinel"은 **AI 기반 트렌드 감시 에이전트**로, 소셜 미디어와 온라인 플랫폼의 뜨거운 트렌드를 실시간으로 감시합니다. 이 봇의 핵심 임무는 트렌드의 관심도가 식기 시작하는 **'냉각 패턴'**을 포착하는 것입니다. 더 이상 뒷북 콘텐츠로 귀중한 시간과 노력을 낭비하지 마세요! ⏰

트렌드 파수꾼은 관심도 하락 징후를 감지하면 콘텐츠 제작자에게 즉시 알림을 보내어, 적절한 시점에 콘텐츠 전략을 수정할 수 있도록 돕습니다. 또한, 이렇게 감지된 '트렌드 냉각 패턴' 데이터는 익명으로 수집 및 분석되어 광고 에이전시에 유용한 시장 통찰력을 제공하는 데 활용됩니다.

## 🌟 주요 기능

*   **트렌드 데이터 로드**: JSON 파일에서 트렌드 데이터를 로드하거나, 파일이 없을 경우 샘플 데이터로 자동 시연합니다.
*   **냉각 패턴 감지**: 특정 기간 동안 트렌드 관심도가 미리 정의된 비율 이상으로 하락하는 패턴을 감지합니다.
*   **즉시 알림**: 감지된 냉각 트렌드에 대해 Slack 웹훅 또는 콘솔을 통해 콘텐츠 제작자에게 즉시 알림을 보냅니다.
*   **데이터 보고서 생성**: 감지된 냉각 트렌드 데이터를 `cooling_trends_report.csv` 파일로 기록하여 분석 및 활용을 위한 기반을 마련합니다.
*   **알림 로그 기록**: 전송된 모든 알림 메시지를 `sentinel_alert_log.txt` 파일에 기록하여 추적 및 관리를 용이하게 합니다.

## 🛠️ 시작하기

이 프로젝트는 파이썬(Python)으로 개발되었습니다. 아래 지침을 따라 Fadeward Sentinel을 쉽게 설치하고 실행할 수 있습니다.

### 📋 1. 필수 준비물

*   **Python 3.8 이상**: 파이썬이 설치되어 있지 않다면 [파이썬 공식 웹사이트](https://www.python.org/downloads/)에서 최신 버전을 다운로드하여 설치해 주세요.

### 📦 2. 가상 환경 설정 (강력 권장!)

가상 환경은 프로젝트별로 필요한 파이썬 패키지를 독립적으로 관리할 수 있게 해줍니다. 다른 프로젝트와의 충돌을 방지하기 위해 가상 환경을 사용하는 것을 강력히 권장합니다.

1.  **프로젝트 폴더 생성 및 이동**:
    ```bash
mkdir Fadeward_Sentinel
cd Fadeward_Sentinel
    ```

2.  **가상 환경 생성**:
    ```bash
python -m venv .venv
    ```

3.  **가상 환경 활성화**:
    *   **Windows**: 
        ```bash
.venv\Scripts\activate
        ```
    *   **macOS/Linux**: 
        ```bash
source .venv/bin/activate
        ```
    (터미널 프롬프트 앞에 `(.venv)`가 나타나면 성공적으로 활성화된 것입니다.)

### ⬇️ 3. 종속성 설치

필요한 파이썬 라이브러리를 설치합니다. `requests`는 Slack 알림 전송에 사용됩니다.

```bash
pip install requests
```

### 📂 4. 소스 코드 다운로드

`fadeward_sentinel.py` 파일을 프로젝트 폴더(`Fadeward_Sentinel`) 안에 저장하세요.

```python
# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import os
import json
import datetime
import random
import csv

try:
    import requests
except ImportError:
    print("경고: 'requests' 라이브러리가 설치되지 않았습니다. 알림 기능이 제한됩니다.")
    print("       pip install requests 명령어로 설치할 수 있습니다.")
    requests = None

def load_trend_data(filepath=None):
    """트렌드 데이터를 로드하거나 샘플 데이터를 생성합니다."""
    if filepath and os.path.exists(filepath):
        print(f"[INFO] 파일에서 트렌드 데이터 로드 중: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 'history'가 list of numbers인지 확인 및 변환
            for trend in data:
                if 'history' in trend and isinstance(trend['history'], list):
                    trend['history'] = [float(x) for x in trend['history']]
            return data
        except Exception as e:
            print(f"[오류] 트렌드 파일 로드 실패 ({filepath}): {e}. 샘플 데이터로 대체합니다.")

    print("[안내] 트렌드 데이터 파일을 찾을 수 없거나 오류가 발생했습니다. 샘플 데이터로 시연합니다.")
    print("       본인 파일을 사용하려면 'python fadeward_sentinel.py --trends 내트렌드.json' 처럼 실행하세요.")
    # 샘플 데이터: 이름, 플랫폼, 최근 5일간의 참여도 점수 (0-100)
    sample_trends = [
        {"name": "AI Art Trends", "platform": "YouTube", "history": [85.0, 83.0, 80.0, 75.0, 70.0]}, # Cooling
        {"name": "Vintage Fashion", "platform": "TikTok", "history": [90.0, 92.0, 91.0, 93.0, 94.0]}, # Growing
        {"name": "Remote Work Setup", "platform": "X", "history": [70.0, 68.0, 65.0, 62.0, 58.0]}, # Cooling
        {"name": "Gaming Metaverse", "platform": "YouTube", "history": [75.0, 74.0, 73.0, 72.0, 71.0]}, # Slightly Cooling
        {"name": "Sustainable Living", "platform": "Instagram", "history": [60.0, 61.0, 62.0, 63.0, 64.0]}  # Growing
    ]
    return sample_trends

def detect_cooling_pattern(trend_history, lookback_days=3, drop_percentage=10):
    """트렌드 관심도 하락 패턴을 감지합니다."""
    if len(trend_history) < lookback_days + 1:
        return False, 0.0

    current_score = trend_history[-1]
    previous_scores = trend_history[-lookback_days-1:-1] # 현재 점수 직전의 N일
    avg_previous_score = sum(previous_scores) / len(previous_scores)

    if avg_previous_score == 0:
        return False, 0.0 # 0으로 나누기 방지

    percentage_drop = ((avg_previous_score - current_score) / avg_previous_score) * 100

    if percentage_drop >= drop_percentage:
        return True, percentage_drop
    return False, percentage_drop

def send_notification(message, webhook_url=None):
    """콘텐츠 제작자에게 알림을 보냅니다 (Slack 또는 콘솔)."""
    if webhook_url and requests:
        try:
            response = requests.post(webhook_url, json={'text': message}, timeout=5)
            response.raise_for_status()
            print(f"[알림] Slack으로 알림 전송 완료: {message[:50]}...")
            return True
        except requests.exceptions.RequestException as e:
            print(f"[오류] Slack 알림 전송 실패: {e}")
    print(f"[알림] (콘솔) {message}")
    return False

def save_report(filename, data, header):
    """감지된 냉각 트렌드 데이터를 CSV 파일로 저장합니다."""
    try:
        file_exists = os.path.exists(filename)
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(header)
            writer.writerow(data)
        print(f"[INFO] 냉각 트렌드 보고서 저장 완료: {filename}")
    except Exception as e:
        print(f"[오류] 보고서 파일 저장 실패 ({filename}): {e}")

def save_alert_log(filename, message):
    """전송된 알림 메시지를 텍스트 파일로 기록합니다."""
    try:
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] {message}\n")
        print(f"[INFO] 알림 로그 기록 완료: {filename}")
    except Exception as e:
        print(f"[오류] 알림 로그 저장 실패 ({filename}): {e}")

def main():
    parser = argparse.ArgumentParser(description='Fadeward Sentinel: Detects cooling trends and sends alerts.')
    parser.add_argument('--trends', type=str, help='Path to the JSON file containing trend data.')
    parser.add_argument('--webhook', type=str, help='Slack webhook URL for notifications.')
    parser.add_argument('--lookback', type=int, default=3, help='Number of previous days to compare for trend analysis (default: 3).')
    parser.add_argument('--drop', type=float, default=10.0, help='Percentage drop to consider a trend 