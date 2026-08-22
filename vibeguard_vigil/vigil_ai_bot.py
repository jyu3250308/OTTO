# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        # reconfigure는 Python 3.7+에서만 사용 가능합니다.
        pass
    except Exception: # 그 외 예상치 못한 오류 처리
        pass

import argparse
import requests
import feedparser
import os
from datetime import datetime

# --- 전역 설정 (Configuration) ---
# 감시할 기본 RSS 피드 URL 템플릿 목록. {keyword}는 검색 키워드로 대체됩니다.
DEFAULT_FEEDS = [
    "https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
]
# 부정적/논란성 언급을 감지하기 위한 키워드 목록
NEGATIVE_KEYWORDS = ["비난", "논란", "문제", "의혹", "가짜뉴스", "사기", "위험", "부정적", "논란이", "비판", "불화", "혐오", "조작"]

# Slack 웹훅 URL (환경 변수에서 로드하거나 플레이스홀더 사용)
# 실제 웹훅 URL 대신 "YOUR_SLACK_WEBHOOK_HERE"를 사용해야 합니다.
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "YOUR_SLACK_WEBHOOK_HERE")

# --- 유틸리티 함수 (Utility Functions) ---
def send_slack_alert(message: str):
    """Slack으로 알림 메시지를 전송합니다."""
    if not SLACK_WEBHOOK_URL or SLACK_WEBHOOK_URL == "YOUR_SLACK_WEBHOOK_HERE":
        print("💡 Slack 웹훅 URL이 설정되지 않아 알림을 보낼 수 없습니다. 환경 변수 SLACK_WEBHOOK_URL을 설정하세요.")
        return

    print(f"✨ Slack 알림 전송 시도 중...")
    try:
        payload = {"text": message}
        # 5초 타임아웃 설정으로 네트워크 지연 방지
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status() # 200 이외의 응답 코드는 예외 발생
        print(f"✨ Slack 알림 전송 성공!")
    except requests.exceptions.Timeout:
        print(f"❌ Slack 알림 전송 실패: 요청 시간 초과 (5초)")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Slack 알림 전송 실패: 네트워크 연결 오류 - {e}")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Slack 알림 전송 실패: HTTP 오류 - 상태 코드 {e.response.status_code}, 응답: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Slack 알림 전송 실패: 알 수 없는 요청 오류 - {e}")

def analyze_vibe(text: str) -> str:
    """주어진 텍스트의 긍정/부정적 분위기를 분석합니다."""
    text_lower = text.lower()
    for neg_word in NEGATIVE_KEYWORDS:
        if neg_word in text_lower:
            return "삐빅! 위기 감지! (부정적/논란성)"
    return "긍정적/중립적"

# --- 핵심 비즈니스 로직 (Core Business Logic) ---
def monitor_keywords(keywords: list[str]) -> list[dict]:
    """지정된 키워드에 대한 웹 언급을 감시하고 데이터를 수집합니다."""
    report_data = []
    total_feeds = len(keywords) * len(DEFAULT_FEEDS)
    current_feed_count = 0

    print(f"\n🚀 VibeGuard Vigil AI: {', '.join(keywords)} 키워드에 대한 웹 언급 감시를 시작합니다.\n")

    for keyword_idx, keyword in enumerate(keywords):
        print(f"--- [{keyword_idx + 1}/{len(keywords)}] 키워드 '{keyword}' 검색 중... ---")
        for feed_url_template_idx, feed_url_template in enumerate(DEFAULT_FEEDS):
            current_feed_count += 1
            feed_url = feed_url_template.format(keyword=keyword)
            print(f"  [{current_feed_count}/{total_feeds}] 피드 요청: {feed_url}")
            
            try:
                # 봇 식별을 위한 User-Agent 헤더 추가
                headers = {'User-Agent': 'VibeGuard-Vigil-AI/1.0 (contact@example.com)'}
                response = requests.get(feed_url, headers=headers, timeout=10) # 10초 타임아웃
                response.raise_for_status() # HTTP 오류 발생 시 예외 처리
                
                feed = feedparser.parse(response.text)

                if feed.bozo: # RSS 피드 파싱 오류 감지
                    print(f"  ⚠️ RSS 피드 파싱 오류 (키워드: {keyword}, URL: {feed_url}): {feed.bozo_exception}")
                    continue

                if not feed.entries:
                    print(f"  정보: 키워드 '{keyword}'에 대한 새 항목이 없습니다.")

                for entry_idx, entry in enumerate(feed.entries):
                    title = entry.get('title', '제목 없음').strip()
                    link = entry.get('link', '링크 없음').strip()
                    # published_parsed 사용을 권장하지만, 원본 문자열 유지를 위해 그대로 둠
                    published = entry.get('published', '날짜 없음').strip()
                    summary = entry.get('summary', '요약 없음').strip()

                    vibe = analyze_vibe(title + " " + summary)
                    report_data.append({
                        "keyword": keyword,
                        "title": title,
                        "link": link,
                        "published": published,
                        "vibe": vibe
                    })
                    print(f"    [감지: {vibe}] '{title}'")

                    if "위기 감지" in vibe: # 부정적 언급 감지 시 Slack 알림 전송
                        alert_message = f"🚨 VibeGuard 위기 감지! ({keyword})\n" \
                                        f"제목: {title}\n" \
                                        f"링크: {link}\n" \
                                        f"게시일: {published}"
                        send_slack_alert(alert_message)

            except requests.exceptions.Timeout:
                print(f"❌ 웹 요청 오류 (키워드: {keyword}, URL: {feed_url}): 요청 시간 초과 (10초)")
            except requests.exceptions.ConnectionError as e:
                print(f"❌ 웹 요청 오류 (키워드: {keyword}, URL: {feed_url}): 네트워크 연결 오류 - {e}")
            except requests.exceptions.HTTPError as e:
                print(f"❌ 웹 요청 오류 (키워드: {keyword}, URL: {feed_url}): HTTP 오류 - 상태 코드 {e.response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ 웹 요청 오류 (키워드: {keyword}, URL: {feed_url}): 알 수 없는 요청 오류 - {e}")
            except Exception as e:
                print(f"❌ 알 수 없는 오류 (키워드: {keyword}, URL: {feed_url}): {e}")

    return report_data

def generate_report(report_data: list[dict]):
    """수집된 데이터를 기반으로 보고서를 생성하여 파일로 저장합니다."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"VibeGuard_Report_{timestamp}.txt"

    total_mentions = len(report_data)
    negative_mentions = sum(1 for item in report_data if "위기 감지" in item['vibe'])
    positive_mentions = total_mentions - negative_mentions

    report_content = f"--- VibeGuard Vigil AI : 콘텐츠 평판 감시 보고서 ({timestamp}) ---\n"
    report_content += f"감시 키워드: {', '.join(sorted(list(set(item['keyword'] for item in report_data))))} ({len(set(item['keyword'] for item in report_data))}개)\n"
    report_content += f"총 언급 수: {total_mentions}건\n"
    report_content += f"긍정/중립 언급 수: {positive_mentions}건\n"
    report_content += f"⚠️ 위기 감지 언급 수: {negative_mentions}건\n\n"

    report_content += "--- 상세 감지 내역 ---\n"
    if not report_data:
        report_content += "감지된 언급이 없습니다.\n"
    else:
        # 최신 언급이 상단에 오도록 published 기준으로 정렬 (날짜 형식에 따라 달라질 수 있음)
        sorted_report_data = sorted(report_data, key=lambda x: x.get('published', ''), reverse=True)
        for item_idx, item in enumerate(sorted_report_data):
            report_content += f"--- [{item_idx + 1}/{total_mentions}] ---\n"
            report_content += f"[평판]: {item['vibe']}\n"
            report_content += f"[키워드]: {item['keyword']}\n"
            report_content += f"[제목]: {item['title']}\n"
            report_content += f"[링크]: {item['link']}\n"
            report_content += f"[게시일]: {item['published']}\n"

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"\n✅ 보고서가 '{filename}' 파일로 성공적으로 저장되었습니다.")
    except IOError as e:
        print(f"❌ 보고서 저장 실패: {e}")
    except Exception as e:
        print(f"❌ 보고서 저장 중 알 수 없는 오류 발생: {e}")

# --- 메인 실행 흐름 (Main Execution Flow) ---
def main():
    """VibeGuard Vigil AI 봇의 메인 함수입니다. 키워드를 파싱하고 감시를 시작합니다."""
    parser = argparse.ArgumentParser(
        description="VibeGuard Vigil AI: 콘텐츠 평판 감시 에이전트 오또 - 지정된 키워드에 대한 웹 언급을 감시하고 보고합니다."
    )
    parser.add_argument(
        'keywords', 
        nargs='*', 
        help='감시할 브랜드명, 인물명 또는 키워드를 공백으로 구분하여 입력하세요 (예: "내브랜드" "내이름").'
    )

    args = parser.parse_args()

    if args.keywords: # 사용자가 키워드를 입력한 경우
        target_keywords = args.keywords
        print(f"\n✨ 사용자가 지정한 키워드: '{', '.join(target_keywords)}'로 감시를 시작합니다.\n")
    else: # 키워드가 입력되지 않은 경우, 데모 폴백 사용
        target_keywords = ["BTS", "뉴진스", "오또봇"]
        print("\n--- 샘플 데이터 시연 모드 ---")
        print(f"입력된 키워드가 없습니다. 샘플 키워드 '{', '.join(target_keywords)}'로 시연합니다.")
        print("본인 키워드를 사용하려면 다음과 같이 실행하세요: python vigil_ai_bot.py '내브랜드' '내이름'\n")

    print("\n💡 Slack 알림을 받으려면 환경 변수 'SLACK_WEBHOOK_URL'에 웹훅 주소를 설정하세요.")
    
    # 키워드 감시 및 데이터 수집
    collected_report_data = monitor_keywords(target_keywords)
    
    # 수집된 데이터로 보고서 생성
    generate_report(collected_report_data)

    print("\n--- VibeGuard Vigil AI 실행 완료 ---")
    print("이 봇은 지정된 키워드에 대한 웹 언급을 주기적으로 감시합니다. 매일 또는 정해진 시간에 자동 실행되도록 스케줄러에 등록하여 지속적으로 활용해 보세요.")
    print("예시 (Linux crontab): 0 9 * * * python /path/to/vigil_ai_bot.py '내브랜드' '내이름' > /dev/null 2>&1\n")

# 스크립트가 직접 실행될 때만 main 함수를 호출
if __name__ == "__main__":
    main()
