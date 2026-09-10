
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
import requests
import random
from datetime import datetime

# --- Configuration & Constants ---
DEMO_TRENDING_SOUNDS = [
    "Upbeat Summer Pop",
    "Chill Lo-fi Vibes",
    "Dramatic Cinematic Score",
    "Retro Synthwave",
    "Motivational Speech Excerpt"
]

DEFAULT_REPORT_FILENAME_PATTERN = "viral_siren_report_{timestamp}.json"

# --- Core Functions ---
def fetch_trending_sounds(source_url: str = None) -> list:
    """Fetches trending sounds from a URL or uses demo data."""
    if source_url:
        try:
            print(f"[INFO] 트렌드 사운드 데이터를 {source_url} 에서 가져오는 중...")
            response = requests.get(source_url, timeout=5)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            trends = response.json()
            if not isinstance(trends, list) or not all(isinstance(t, str) for t in trends):
                print("[WARN] 가져온 데이터 형식이 예상과 다릅니다. (기대: 문자열 리스트)")
                raise ValueError("Invalid data format")
            print(f"[INFO] {len(trends)} 개의 트렌드 사운드를 성공적으로 가져왔습니다.")
            return trends
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 트렌드 데이터 URL 접근 실패: {e}. 데모 데이터로 대체합니다.")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[ERROR] 가져온 데이터를 파싱할 수 없습니다: {e}. 데모 데이터로 대체합니다.")
    
    print("[INFO] 지금은 샘플 데이터(DEMO_TRENDING_SOUNDS)로 시연 중입니다.")
    print("       본인 소스의 트렌드 사운드 데이터를 쓰려면 '--source-url <YOUR_JSON_URL>' 처럼 실행하세요.")
    return DEMO_TRENDING_SOUNDS

def simulate_reach_and_engagement(sound_name: str) -> dict:
    """Simulates estimated reach and engagement for a given sound."""
    # A simple simulation based on random factors for demonstration
    base_reach = random.randint(100_000, 5_000_000)
    engagement_multiplier = random.uniform(0.01, 0.15) # 1-15% engagement rate
    
    # Introduce some 