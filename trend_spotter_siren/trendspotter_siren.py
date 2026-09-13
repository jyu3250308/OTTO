# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우 환경에서
#   UnicodeEncodeError로 인한 프로그램 중단을 방지합니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: # 발생할 일은 드물지만, 혹시 모를 에러 방지
        pass

import datetime
import os
import argparse

import feedparser
import requests

# --- 전역 설정 및 상수 --- #
DEFAULT_RSS_URL = "https://techcrunch.com/category/social/feed/" # 예시: TechCrunch 소셜 미디어 뉴스 피드
OUTPUT_FILENAME = "trendspotter_alerts.txt"
HOT_KEYWORDS = [
    "viral", "trend", "new format", "AI", "creator economy",
    "숏폼", "챌린지", "메타버스", "web3", "blockchain", "NFT", "인플루언서"
] # 트렌드 감지에 사용될 핵심 키워드 목록 (확장 가능)

# --- 함수 정의 --- #
def fetch_and_parse_feed(url: str) -> list:
    """지정된 URL에서 RSS 피드를 가져와 파싱하고 항목 리스트를 반환합니다."""
    print(f"[TrendSpotter] RSS 피드 읽기 시작: {url}")
    try:
        # 요청 타임아웃 15초 설정 및 스트림 응답으로 효율성 증대
        response = requests.get(url, timeout=15, stream=True)
        response.raise_for_status() # 4xx, 5xx 에러 발생 시 예외 처리
        print(f"[TrendSpotter] RSS 피드 요청 성공 (상태 코드: {response.status_code}). 파싱 중...")
        feed = feedparser.parse(response.raw) # raw content를 feedparser에 전달

        if feed.entries:
            print(f"[TrendSpotter] 총 {len(feed.entries)}개의 최신 콘텐츠 항목 발견.")
        else:
            print("[TrendSpotter] 피드에서 새로운 콘텐츠를 찾지 못했습니다. 다음 실행을 기다립니다.")
        return feed.entries
    except requests.exceptions.Timeout:
        print(f"[TrendSpotter 오류] 피드 요청 시간 초과: {url}")
        return []
    except requests.exceptions.ConnectionError as e:
        print(f"[TrendSpotter 오류] 피드 연결 실패: {e}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"[TrendSpotter 오류] 피드 요청 중 예상치 못한 에러 발생: {e}")
        return []
    except Exception as e:
        print(f"[TrendSpotter 오류] 피드 파싱 또는 처리 중 에러 발생: {e}")
        return []

def analyze_trends(entries: list) -> list:
    """피드 항목을 분석하여 정의된 키워드 및 최신성에 기반한 잠재적 트렌드를 감지합니다."""
    print("[TrendSpotter] 트렌드 감지 및 분석 시작...")
    detected_trends = []

    for i, entry in enumerate(entries):
        title = entry.get('title', '제목 없음').strip()
        summary = entry.get('summary', entry.get('description', '내용 없음')).strip()
        link = entry.get('link', '#')
        published_parsed = entry.get('published_parsed')

        print(f"  - [{i+1}/{len(entries)}] 항목 분석 중: '{title}'")
        
        is_trending = False
        matched_keywords = []
        for keyword in HOT_KEYWORDS:
            if keyword.lower() in title.lower() or keyword.lower() in summary.lower():
                is_trending = True
                matched_keywords.append(keyword)

        if is_trending:
            pub_date_str = "날짜 불명"
            if published_parsed:
                try:
                    pub_date = datetime.datetime(*published_parsed[:6])
                    pub_date_str = pub_date.strftime('%Y-%m-%d %H:%M')
                except (TypeError, ValueError):
                    print(f"    [경고] 날짜 파싱 실패: {published_parsed}")
            
            truncated_summary = summary[:150] + ('...' if len(summary) > 150 else '')
            
            trend_summary = f"[🚨 Trend Detected! 🚨] 키워드: {', '.join(matched_keywords)}\n" \
                            f"  ➡️ 제목: '{title}' (발행일: {pub_date_str})\n" \
                            f"  ➡️ 핵심 내용: {truncated_summary}\n" \
                            f"  🔗 원본 링크: {link}\n"
            detected_trends.append(trend_summary)
            print(f"    [성공] 트렌드 키워드 발견: {', '.join(matched_keywords)}")

    if not detected_trends:
        print("[TrendSpotter] 현재 눈에 띄는 급상승 트렌드는 감지되지 않았습니다.")
    return detected_trends

def save_alerts(alerts: list):
    """감지된 트렌드 알림을 지정된 파일에 추가 기록합니다."""
    if not alerts:
        print("[TrendSpotter] 저장할 트렌드 알림이 없습니다.")
        return

    print(f"[TrendSpotter] 감지된 트렌드 알림을 '{OUTPUT_FILENAME}' 파일에 저장 중...")
    try:
        # 'a' 모드로 파일을 열어 기존 내용에 추가하고, UTF-8 인코딩 사용
        with open(OUTPUT_FILENAME, 'a', encoding='utf-8') as f:
            f.write("\n" + "="*80 + "\n")
            f.write(f"[TrendSpotter Siren Alert - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
            f.write("="*80 + "\n")
            for alert in alerts:
                f.write(alert + "\n")
            f.write("\n")
        print(f"[TrendSpotter] {len(alerts)}개의 트렌드 알림이 '{OUTPUT_FILENAME}'에 성공적으로 저장되었습니다.")
        print(f"[TrendSpotter] 파일 위치: {os.path.abspath(OUTPUT_FILENAME)}")
    except IOError as e:
        print(f"[TrendSpotter 오류] 파일 저장 실패: {e}")

def main():
    """TrendSpotter Siren의 메인 실행 함수."""
    parser = argparse.ArgumentParser(
        description='TrendSpotter Siren: RSS 피드에서 최신 콘텐츠 트렌드를 감지합니다.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--rss_url', 
        type=str, 
        default=DEFAULT_RSS_URL,
        help=f'모니터링할 RSS 피드 URL을 지정합니다. (기본값: {DEFAULT_RSS_URL})\n' \
             f'  예시: python trendspotter_siren.py --rss_url https://www.your_feed.com/rss'
    )
    args = parser.parse_args()

    print("\n" + "="*80)
    print("[TrendSpotter Siren v1.0] 트렌드 감지 봇이 시작되었습니다.")
    print("="*80)

    if args.rss_url == DEFAULT_RSS_URL:
        print("[TrendSpotter 정보] 현재는 샘플 데이터(TechCrunch Social Feed)로 시연 중입니다.")
        print("[TrendSpotter 정보] 자신만의 피드를 모니터링하려면 '--rss_url' 인자를 사용하세요.")
        print(f"[TrendSpotter 정보] 예시: python {os.path.basename(__file__)} --rss_url [내_RSS_주소]")

    entries = fetch_and_parse_feed(args.rss_url)
    
    if entries:
        alerts = analyze_trends(entries)
        save_alerts(alerts)
    else:
        print("[TrendSpotter] 처리할 새로운 콘텐츠가 없어 다음 실행을 대기합니다.")

    print("\n" + "="*80)
    print("[TrendSpotter] 모든 작업 완료. 이 봇을 반복 실행하려면 CRON 또는 스케줄러에 등록하여 활용하세요.")
    print("="*80)

if __name__ == "__main__":
    main()
