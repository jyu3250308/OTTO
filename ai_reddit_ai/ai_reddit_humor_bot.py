
# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import os
import json
import requests
from datetime import datetime

# ai_reddit_humor_bot.py
#
# 이 스크립트는 Reddit의 인기 유머 게시물을 모의(Mock)로 가져와 AI(모의)로 요약하고,
# 그 결과를 로컬 파일에 저장하거나 Slack으로 전송하는 봇입니다.
# 외부 API 연동 없이 핵심 비즈니스 로직의 작동 방식을 시뮬레이션하도록 설계되었습니다.

# --- 1. 환경 설정 (Configuration) ---
# Slack Webhook URL을 환경 변수에서 가져오거나 직접 설정합니다.
# 실제 운영 환경에서는 'SLACK_WEBHOOK_URL' 환경 변수를 사용하는 것을 권장합니다.
# 설정되지 않았거나 기본 플레이스홀더인 경우, 메시지는 콘솔에 출력됩니다.
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "YOUR_SLACK_WEBHOOK_URL_HERE")
# 요약 결과가 저장될 파일명. 실행 시간 스탬프를 포함하여 고유성을 확보합니다.
OUTPUT_FILENAME_PREFIX = "reddit_humor_summary"
OUTPUT_FILENAME = f"{OUTPUT_FILENAME_PREFIX}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

# --- 2. 모의 Reddit 데이터 (Mock Data for Reddit Posts) ---
# 실제 Reddit API (예: PRAW 라이브러리)와 연동하는 대신, 시뮬레이션을 위한 가상의 데이터를 사용합니다.
# 이 데이터는 다양한 유머성 서브레딧의 인기 게시물을 모방합니다.
MOCK_REDDIT_POSTS = [
    {"title": "My cat just stole my sandwich and gave me a look of pure triumph.", "url": "https://reddit.com/r/funny/comments/cat_sandwich_mock_1"},
    {"title": "Why don't scientists trust atoms? Because they make up everything!", "url": "https://reddit.com/r/jokes/comments/atom_joke_mock_2"},
    {"title": "Just saw a dog wearing a tiny hat. My life is complete.", "url": "https://reddit.com/r/wholesomememes/comments/dog_hat_mock_3"},
    {"title": "Asked my wife if she'd seen my a-shirt. She said 'No, I haven't seen your 'a' shirt'.", "url": "https://reddit.com/r/dadjokes/comments/ashirt_mock_4"},
    {"title": "My computer just beat me at chess, but it was no match for me at kickboxing.", "url": "https://reddit.com/r/programmerhumor/comments/ai_chess_mock_5"}
]

def fetch_popular_reddit_humor():
    """
    Reddit에서 인기 유머 게시물을 가져오는 과정을 모의(Simulate)합니다.
    실제 구현에서는 Reddit API를 호출하여 데이터를 가져옵니다.
    """
    print("\n[INFO] Reddit에서 인기 유머 게시물을 가져오는 중... (모의 데이터 사용)")
    try:
        # MOCK_REDDIT_POSTS의 처음 3개 게시물을 가져오는 것으로 시뮬레이션합니다.
        # 실제 API 연동 시에는 네트워크 요청, 응답 파싱, 에러 처리 로직이 추가됩니다.
        mock_posts = MOCK_REDDIT_POSTS[:3]
        print(f"[SUCCESS] 총 {len(mock_posts)}개의 모의 Reddit 유머 게시물을 가져왔습니다.")
        return mock_posts
    except Exception as e:
        # 모의 데이터에서는 거의 발생하지 않지만, 실제 연동을 대비한 예외 처리입니다.
        print(f"[ERROR] Reddit 유머 게시물을 가져오는 중 예외 발생: {e}")
        return []

def summarize_text_with_ai(text: str) -> str:
    """
    주어진 텍스트를 AI로 요약하는 과정을 모의(Simulate)합니다.
    실제 구현에서는 OpenAI, Google Gemini 등 AI 모델 API를 호출합니다.
    """
    print(f"[INFO] AI가 텍스트를 요약하는 중... 원본: '{text[:50]}...' ")
    # 간단한 키워드 기반의 모의 요약 로직입니다. 실제 AI 요약은 더 정교합니다.
    text_lower = text.lower()
    if "cat" in text_lower and "sandwich" in text_lower:
        summary = "고양이가 샌드위치를 훔쳐 먹고 승리감에 도취된 유머."
    elif "atom" in text_lower and "trust" in text_lower:
        summary = "원자는 모든 것을 구성. 과학자들이 믿지 않는 이유 유머."
    elif "dog" in text_lower and "hat" in text_lower:
        summary = "작은 모자를 쓴 강아지를 발견. 완벽한 삶에 대한 유머."
    elif "shirt" in text_lower and "wife" in text_lower:
        summary = "아내에게 'a-shirt'를 물어보는 언어유희 아재 개그."
    elif "computer" in text_lower and "chess" in text_lower:
        summary = "컴퓨터와 체스 대결에서 이겼지만, 다른 분야에서 반전이 있는 유머."
    else:
        summary = f"흥미로운 게시물 요약: {text[:50]}..."
    print(f"[SUCCESS] 텍스트 요약 완료. 요약본: '{summary[:50]}...' ")
    return summary

def send_slack_message(message: str):
    """
    Slack으로 메시지를 전송하거나, Webhook URL이 설정되지 않은 경우 콘솔에 출력합니다.
    네트워크 오류 발생 시 안전하게 예외를 처리합니다.
    """
    if SLACK_WEBHOOK_URL and SLACK_WEBHOOK_URL != "YOUR_SLACK_WEBHOOK_URL_HERE":
        print("[INFO] Slack Webhook URL이 설정되어 있어 메시지를 Slack으로 보내는 중...")
        headers = {'Content-type': 'application/json'}
        payload = {'text': message}
        try:
            response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers=headers, timeout=5)
            response.raise_for_status()  # 4xx, 5xx 에러 발생 시 HTTPError 예외 발생
            print(f"[SUCCESS] Slack 메시지 전송 완료. 상태 코드: {response.status_code}")
        except requests.exceptions.Timeout:
            print("[ERROR] Slack 메시지 전송 실패: 요청 시간 초과 (Timeout).")
        except requests.exceptions.ConnectionError as e:
            print(f"[ERROR] Slack 메시지 전송 실패: 네트워크 연결 오류 발생. {e}")
        except requests.exceptions.HTTPError as e:
            print(f"[ERROR] Slack 메시지 전송 실패: HTTP 오류 발생 (상태 코드: {e.response.status_code}). 응답: {e.response.text}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Slack 메시지 전송 실패: 알 수 없는 요청 오류 발생. {e}")
        except Exception as e:
            print(f"[ERROR] Slack 메시지 전송 중 예상치 못한 오류 발생: {e}")
    else:
        print("\n--- Slack Webhook URL 미설정 (콘솔 출력) ---")
        print(message)
        print("-------------------------------------------")

def save_summary_to_file(summary_text: str):
    """
    요약된 내용을 지정된 파일에 저장합니다. 파일 I/O 오류를 처리합니다.
    """
    print(f"[INFO] 요약 내용을 파일 '{OUTPUT_FILENAME}'에 저장하는 중...")
    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            f.write(summary_text)
        print(f"[SUCCESS] 요약 내용이 '{OUTPUT_FILENAME}' 파일로 성공적으로 저장되었습니다.")
    except IOError as e:
        print(f"[ERROR] 파일 저장 실패: '{OUTPUT_FILENAME}'에 쓰기 오류 발생. {e}")
    except Exception as e:
        print(f"[ERROR] 파일 저장 중 예상치 못한 오류 발생: {e}")

def main():
    """
    봇의 주요 실행 로직을 포함합니다. Reddit 게시물 가져오기, AI 요약, 파일 저장, Slack 전송 과정을 조율합니다.
    """
    print("\n### [INFO] AI Reddit 유머 분석 슬랙봇 시작 ###")

    # 1. Reddit 인기 유머 게시물 가져오기
    print("[STEP 1/4] Reddit에서 인기 유머 게시물을 가져오는 중...")
    posts = fetch_popular_reddit_humor()
    if not posts:
        print("[WARNING] 가져올 유머 게시물이 없어 작업을 종료합니다.")
        print("### [INFO] AI Reddit 유머 분석 슬랙봇 종료 (경고) ###")
        return

    summary_parts = [f"*{datetime.now().strftime('%Y-%m-%d %H:%M')} Reddit 인기 유머 요약*\n"]
    print("[STEP 2/4] 각 게시물을 AI로 요약하는 중...")
    for i, post in enumerate(posts):
        # 2. AI로 각 게시물 요약
        summary = summarize_text_with_ai(post['title'])
        summary_parts.append(f"{i+1}. *{summary}* (<{post['url']}|원본 보기>)")

    final_summary_message = "\n".join(summary_parts)
    print("[INFO] 모든 게시물 요약 완료.")

    # 3. 요약 내용 파일로 저장 (영구 산출물)
    print("[STEP 3/4] 요약된 내용을 로컬 파일에 저장하는 중...")
    save_summary_to_file(final_summary_message)

    # 4. Slack으로 알림 전송 (또는 콘솔 출력)
    print("[STEP 4/4] 요약된 내용을 Slack으로 전송 또는 콘솔에 출력하는 중...")
    send_slack_message(final_summary_message)

    print("\n### [INFO] AI Reddit 유머 분석 슬랙봇 종료 ###")

if __name__ == "__main__":
    main()
    # --- 팁: 스케줄러 등록 안내 ---
    # 이 스크립트를 매일/정기적으로 실행하려면, 운영체제의 스케줄러 (예: Linux/macOS의 'cron', Windows의 '작업 스케줄러')에 등록하세요.
    # 예시 (Linux/macOS cron): `0 9 * * * /usr/bin/env python3 /path/to/ai_reddit_humor_bot.py` (매일 오전 9시 실행)
