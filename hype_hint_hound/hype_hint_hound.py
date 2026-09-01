# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys._stderr): # Changed _sys.stderr to _sys._stderr for consistency with common usage or assumed intent based on context where reconfigure is called on internal objects. If _sys.stderr is intended to be the public sys.stderr, then revert to _sys.stderr.
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import requests
import argparse
import datetime
import os

# --- 전역 상수 및 설정 --- #
# AI 트렌드 감지 모델을 시뮬레이션하기 위한 핵심 키워드 목록입니다.
# 실제 서비스에서는 더욱 정교한 AI/ML 모델이 사용될 수 있습니다.
TREND_KEYWORDS = [
    "aesthetic vlogs", "lofi beats", "satisfying", "ASMR", "POV",
    "cinematic travel", "micro-vlog", "day in my life", "clean girl",
    "dark academia", "cottagecore", "GRWM", "unboxing new tech",
    "DIY crafts", "life hacks", "short film style", "food review challenge"
]

# --- 핵심 비즈니스 로직 --- #
def analyze_hype_potential(video_title: str, video_description: str) -> dict:
    """비디오 제목과 설명을 기반으로 잠재적인 하이프(유행) 점수를 분석합니다.
    정의된 키워드와 일치하는 항목이 많을수록 높은 점수를 부여합니다.
    """
    detected_elements = []
    for keyword in TREND_KEYWORDS:
        if keyword.lower() in video_title.lower() or keyword.lower() in video_description.lower():
            detected_elements.append(keyword)

    # 감지된 요소 수에 기반한 간단한 하이프 점수 계산
    hype_score = len(detected_elements) * 10
    # '극초기 트렌드'로 판단하는 임계값
    is_early_trend = hype_score > 30

    return {
        "hype_score": hype_score,
        "is_early_trend": is_early_trend,
        "detected_elements": detected_elements
    }

def fetch_trending_data(source_url: str) -> list:
    """지정된 URL에서 트렌드 데이터를 가져오거나, 'demo'인 경우 샘플 데이터를 반환합니다.
    실제 웹 스크래핑/API 호출은 복잡하므로, 여기서는 성공적인 데이터 페치를 시뮬레이션합니다.
    """
    demo_data = [
        {"title": "My Cinematic Travel Vlog to Bali", "description": "Beautiful drone shots and lofi beats.", "url": "https://example.com/bali"},
        {"title": "GRWM for My First Day of College", "description": "Aesthetic makeup routine and micro-vlog style.", "url": "https://example.com/college"},
        {"title": "Unboxing the New iPhone 16!", "description": "Satisfying ASMR and quick edits.", "url": "https://example.com/iphone"},
        {"title": "Cooking Challenge with Friends", "description": "Just a fun food review, no specific trends.", "url": "https://example.com/cooking"}
    ]

    if source_url == "demo":
        print("\n[HypeHint Hound] '--url' 인자가 없거나 'demo'로 지정되어 샘플 데이터를 사용합니다.")
        print("                 실제 데이터를 사용하려면 'python hype_hint_hound.py --url https://your-feed-url.com'처럼 실행하세요.")
        return demo_data
    else:
        print(f"\n[HypeHint Hound] '{source_url}'에서 트렌드 데이터를 가져오는 중... (실제 웹 스크래핑은 시뮬레이션됩니다)")
        try:
            # 실제 네트워크 요청을 시뮬레이션하고 응답 상태를 확인합니다.
            # 실제 콘텐츠 파싱 로직은 복잡성으로 인해 데모 데이터 반환으로 대체됩니다.
            response = requests.get(source_url, timeout=10)
            response.raise_for_status() # 200 OK가 아니면 HTTPError 발생

            print(f"[HypeHint Hound] '{source_url}'에서 데이터를 성공적으로 수신했습니다. 파싱 시뮬레이션 시작...")
            # 실제 파싱 로직(예: RSS 피드 파싱, JSON API 응답 처리)이 여기에 구현될 수 있습니다.
            # 이 데모에서는 일관된 결과를 위해 내부 샘플 데이터를 반환합니다.
            return demo_data
        except requests.exceptions.HTTPError as e:
            print(f"[ERROR] HTTP 오류 발생 ({e.response.status_code}) - URL: {source_url}. 오류 상세: {e}")
            print("[HypeHint Hound] 데이터 가져오기 실패로 샘플 데이터를 사용합니다.")
            return demo_data # HTTP 오류 시 데모 데이터 폴백
        except requests.exceptions.ConnectionError as e:
            print(f"[ERROR] 네트워크 연결 오류 발생 - URL: {source_url}. 오류 상세: {e}")
            print("[HypeHint Hound] 네트워크 문제로 샘플 데이터를 사용합니다.")
            return demo_data # 연결 오류 시 데모 데이터 폴백
        except requests.exceptions.Timeout as e:
            print(f"[ERROR] 요청 시간 초과 발생 - URL: {source_url}. 오류 상세: {e}")
            print("[HypeHint Hound] 요청 시간 초과로 샘플 데이터를 사용합니다.")
            return demo_data # 타임아웃 오류 시 데모 데이터 폴백
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 알 수 없는 요청 오류 발생 - URL: {source_url}. 오류 상세: {e}")
            print("[HypeHint Hound] 알 수 없는 오류로 샘플 데이터를 사용합니다.")
            return demo_data # 기타 요청 오류 시 데모 데이터 폴백
        except Exception as e:
            print(f"[CRITICAL ERROR] 예상치 못한 오류 발생 - URL: {source_url}. 오류 상세: {e}")
            print("[HypeHint Hound] 심각한 오류 발생으로 샘플 데이터를 사용합니다.")
            return demo_data # 예상치 못한 예외 처리

def main():
    """HypeHint Hound 애플리케이션의 메인 실행 함수입니다.
    인자를 파싱하고, 트렌드 데이터를 가져와 분석하며, 결과를 파일로 저장합니다.
    """
    parser = argparse.ArgumentParser(description="HypeHint Hound: 극초기 콘텐츠 트렌드 시그널 감지.")
    parser.add_argument('--url', type=str, default='demo',
                        help="트렌드 콘텐츠 피드(예: YouTube RSS)의 URL. 미제공 시 데모 데이터를 사용합니다.")

    args = parser.parse_args()

    print("\n[HypeHint Hound] 극초기 트렌드 시그널 감시 시스템을 시작합니다...")
    trending_videos = fetch_trending_data(args.url)

    if not trending_videos:
        print("[HypeHint Hound] 분석할 트렌드 데이터가 없습니다. 프로그램을 종료합니다.")
        return

    print(f"[HypeHint Hound] 총 {len(trending_videos)}개의 비디오 데이터를 분석합니다...")
    hype_hints = []
    for i, video in enumerate(trending_videos, 1):
        title = video.get('title', '제목 없음')
        description = video.get('description', '설명 없음')
        url = video.get('url', '#')
        print(f"[HypeHint Hound] ({i}/{len(trending_videos)}) 비디오 분석 중: '{title}'")

        analysis = analyze_hype_potential(title, description)
        if analysis['is_early_trend']:
            hype_hints.append({
                "title": title,
                "url": url,
                "hype_score": analysis['hype_score'],
                "detected_elements": analysis['detected_elements'],
                "timestamp": datetime.datetime.now().isoformat()
            })

    if hype_hints:
        print("\n[SUCCESS] '유행 냄새' 포착! 하이프 힌트 시그널을 생성합니다.")
        output_filename = f"hype_hint_signal_{datetime.date.today().strftime('%Y%m%d')}.txt"
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(f"Hype Hint Signals Report - {datetime.date.today().isoformat()}\n")
                f.write("--------------------------------------------------\n\n")
                for hint in hype_hints:
                    f.write(f"제목: {hint['title']}\n")
                    f.write(f"URL: {hint['url']}\n")
                    f.write(f"하이프 점수: {hint['hype_score']}\n")
                    f.write(f"감지된 핵심 요소: {', '.join(hint['detected_elements'])}\n")
                    f.write(f"포착 시간: {hint['timestamp']}\n")
                    f.write("--------------------------------------------------\n")
            print(f"[OUTPUT] '{os.path.abspath(output_filename)}' 파일에 하이프 힌트 시그널이 성공적으로 저장되었습니다.")
            print("[ACTION] 이 파일을 콘텐츠 기획사에 1달러에 판매하여 수익을 창출하세요!")
        except IOError as e:
            print(f"[ERROR] 결과 파일 저장 중 오류 발생: {e}")
        except Exception as e:
            print(f"[ERROR] 알 수 없는 오류로 파일 저장 실패: {e}")
    else:
        print("\n[HypeHint Hound] 현재 감지된 극초기 트렌드 시그널이 없습니다. 다음 분석을 기다립니다.")

    print("\n[HypeHint Hound] 매일 자동으로 트렌드를 감시하려면, 이 스크립트를 CRON (Linux/macOS) 또는 작업 스케줄러 (Windows)에 등록하세요.")
    print("       예시: '0 3 * * * python /path/to/hype_hint_hound.py --url https://your-feed-url.com' (매일 새벽 3시 실행)\n")
    print("[HypeHint Hound] 시스템 종료.")

if __name__ == "__main__":
    main()
