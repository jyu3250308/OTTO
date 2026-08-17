# -*- coding: utf-8 -*-
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import requests
from bs4 import BeautifulSoup
import re
import csv
import datetime
import os
from urllib.parse import urlparse

# --- 전역 상수 및 설정 ---
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
REQUEST_TIMEOUT = 15 # 네트워크 요청 타임아웃 (초)
REPORT_FILENAME = "shadow_citation_report.csv"
SNIPPET_CONTEXT_LENGTH = 100 # 키워드 주변 텍스트 길이

# --- 유틸리티 함수 ---
def get_web_content(url: str) -> str | None:
    """지정된 URL에서 웹 콘텐츠를 안전하게 가져옵니다."""
    print(f"  [네트워크] {url} 에서 콘텐츠를 가져오는 중...")
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status() # 200 이외의 HTTP 상태 코드에 대해 예외 발생
        print(f"  [성공] {url} 에서 콘텐츠를 성공적으로 가져왔습니다.")
        return response.text
    except requests.exceptions.HTTPError as e:
        print(f"  [오류] HTTP 요청 실패 (상태 코드: {e.response.status_code}). URL: {url}, 오류: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"  [오류] 네트워크 연결 실패. URL: {url}, 오류: {e}")
    except requests.exceptions.Timeout as e:
        print(f"  [오류] 요청 시간 초과 ({REQUEST_TIMEOUT}초). URL: {url}, 오류: {e}")
    except requests.exceptions.RequestException as e:
        print(f"  [오류] 알 수 없는 요청 오류. URL: {url}, 오류: {e}")
    except Exception as e:
        print(f"  [치명적 오류] 웹 콘텐츠 가져오기 중 예기치 않은 오류 발생. URL: {url}, 오류: {e}")
    return None

def analyze_page_for_mentions(html_content: str, keywords: list[str], target_domain: str) -> list[dict]:
    """HTML 콘텐츠에서 키워드를 찾고, 타겟 도메인으로의 링크 유무를 판단합니다."""
    soup = BeautifulSoup(html_content, 'html.parser')
    # HTML 태그를 제거하고 텍스트만 추출, 소문자로 변환하여 검색 효율 증대
    page_text = soup.get_text(separator=' ', strip=True).lower()
    found_mentions = []

    # 타겟 도메인을 포함하는 모든 링크를 미리 찾아둡니다.
    has_target_link = any(target_domain in (a_tag.get('href') or '') for a_tag in soup.find_all('a', href=True))

    for keyword in keywords:
        lower_keyword = keyword.lower()
        if lower_keyword in page_text:
            # 키워드가 언급된 주변 텍스트 스니펫 추출
            # re.escape를 사용하여 키워드 내 특수 문자가 정규식 문자로 해석되지 않도록 방지
            snippet_match = re.search(f'(.{{0,{SNIPPET_CONTEXT_LENGTH}}}){re.escape(lower_keyword)}(.{{0,{SNIPPET_CONTEXT_LENGTH}}})', page_text, re.IGNORECASE)
            snippet = snippet_match.group(0).strip() if snippet_match else f"...{keyword}... (콘텍스트 없음)"
            
            found_mentions.append({"keyword": keyword, "has_link": has_target_link, "snippet": snippet})
    return found_mentions

def save_report(data: list[dict], filename: str = REPORT_FILENAME) -> None:
    """발견된 그림자 인용 데이터를 CSV 파일로 저장합니다."""
    print(f"[저장] 보고서를 '{filename}' 파일에 저장 중입니다...")
    fieldnames = ["Date", "Keyword", "Mentioned URL", "Snippet", "Has Link"]
    file_exists = os.path.isfile(filename)
    
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader() # 파일이 없으면 헤더 작성
            writer.writerows(data)
        print("[완료] 보고서 저장이 완료되었습니다.")
    except IOError as e:
        print(f"[오류] CSV 파일 저장 중 오류 발생: {e}")
    except Exception as e:
        print(f"[치명적 오류] 보고서 저장 중 예기치 않은 오류 발생: {e}")

def extract_domain(url_or_domain: str) -> str:
    """URL 또는 도메인 문자열에서 순수 도메인 이름만 추출합니다."""
    if not url_or_domain.startswith(('http://', 'https://')):
        url_or_domain = 'http://' + url_or_domain # urlparse가 작동하도록 scheme 추가
    parsed_uri = urlparse(url_or_domain)
    domain = parsed_uri.netloc
    return domain.split(':')[0] if ':' in domain else domain # 포트번호 제거

def main():
    print("\n=== CiteSense AI: 그림자 인용 알리미 시작 ===")
    print("AI가 웹 전체에서 당신의 콘텐츠를 '링크 없이' 언급한 그림자 인용을 찾아냅니다.\n")

    user_keywords_input = input("모니터링할 키워드를 쉼표로 구분하여 입력하세요 (예: 제 브랜드, 제 이름, 제 콘텐츠): ")
    target_domain_input = input("당신의 웹사이트/콘텐츠 도메인을 입력하세요 (예: mywebsite.com): ")

    is_demo_mode = not user_keywords_input or not target_domain_input

    if is_demo_mode:
        print("\n[안내] 입력이 없어 샘플 데이터로 시연합니다. 본인 데이터를 사용하려면 키워드와 도메인을 입력하세요.")
        keywords = ["오또봇", "AI 비서"]
        target_domain = "ottobot.com"
        # 데모 모드에서는 실제 웹 요청 대신 샘플 콘텐츠를 사용합니다.
        monitor_sources = [
            {"url": "https://example.com/news1", "content": "<h1>오또봇 최신 기능</h1><p>오또봇은 강력한 AI 비서입니다. 자세한 내용은 <a href=\"https://ottobot.com/features\">여기</a>에서 확인하세요.</p>"},
            {"url": "https://example.com/blog/review", "content": "<p>오늘의 뉴스: AI 비서 시장이 뜨겁습니다. 오또봇이라는 새로운 서비스가 출시되었지만 아직 링크가 없습니다.</p><p>제이름의 다른 서비스도 언급되었습니다.</p>"},
            {"url": "https://example.com/no-mention", "content": "<p>다른 내용들...</p>"}
        ]
    else:
        keywords = [kw.strip() for kw in user_keywords_input.split(',') if kw.strip()]
        target_domain = extract_domain(target_domain_input.strip())
        
        # 실제 웹 모니터링을 위한 예시 URL 목록.
        # 웹 전체를 모니터링하려면 Google Custom Search, Bing Search API 등 유료 API가 필요합니다.
        monitor_sources = [
            {"url": "https://www.zdnet.co.kr/", "content": None}, # content=None 이면 get_web_content 호출
            {"url": "https://www.mk.co.kr/", "content": None},
            {"url": "https://news.naver.com/", "content": None},
            {"url": "https://www.hankyung.com/", "content": None},
            {"url": "https://www.chosun.com/", "content": None}
        ]

    if not keywords or not target_domain:
        print("[오류] 키워드와 타겟 도메인은 필수 입력 사항입니다. 프로그램을 종료합니다.")
        return

    print(f"\n[정보] 모니터링 키워드: {', '.join(keywords)}")
    print(f"[정보] 타겟 도메인 (링크 판단 기준): {target_domain}")
    print(f"[정보] 모니터링할 {len(monitor_sources)}개 URL/소스: {', '.join([s['url'] for s in monitor_sources[:3]])}{'...' if len(monitor_sources) > 3 else ''}\n")

    all_found_data = []
    current_date = datetime.date.today().isoformat()

    for i, source in enumerate(monitor_sources):
        url = source['url']
        print(f"[진행] {i+1}/{len(monitor_sources)}: {url} 분석 중...")
        
        html_content = source['content'] if source['content'] is not None else get_web_content(url)
        
        if html_content:
            mentions = analyze_page_for_mentions(html_content, keywords, target_domain)
            if mentions:
                print(f"  [발견] {url} 에서 {len(mentions)}건의 언급을 찾았습니다.")
                for mention in mentions:
                    alert_type = "✅ 링크 있음" if mention["has_link"] else "❗ 링크 없음 (그림자 인용 가능성)"
                    print(f"    - 키워드: '{mention['keyword']}', 유형: {alert_type}, 스니펫: '{mention['snippet']}'")
                    all_found_data.append({
                        "Date": current_date,
                        "Keyword": mention["keyword"],
                        "Mentioned URL": url,
                        "Snippet": mention["snippet"],
                        "Has Link": "Yes" if mention["has_link"] else "No"
                    })
            else:
                print(f"  [정보] {url} 에서 지정된 키워드를 찾지 못했습니다.")
        else:
            print(f"  [건너뛰기] {url} 의 콘텐츠를 가져오지 못하여 분석을 건너뜁니다.")

    if all_found_data:
        save_report(all_found_data)

        # 간단한 분석 요약
        unlinked_mentions_count = sum(1 for item in all_found_data if item["Has Link"] == "No")
        total_mentions_count = len(all_found_data)

        print(f"\n=== 분석 결과 요약 ({current_date}) ===")
        print(f"총 {total_mentions_count}건의 언급을 발견했습니다.")
        print(f"이 중 {unlinked_mentions_count}건이 링크 없는 그림자 인용입니다.")
        if total_mentions_count > 0:
            print(f"  (전체 언급의 {unlinked_mentions_count/total_mentions_count*100:.2f}%) ")
        
        if unlinked_mentions_count > 0:
            print("\n💡 링크 없는 언급에 대해 기회를 놓치지 않도록 적절한 조치를 고려해보세요!")
            print("   (예: 해당 웹사이트/블로그에 연락하여 링크 추가 요청, 협업 제안 등)")
        elif total_mentions_count > 0:
            print("\n👍 훌륭합니다! 모든 언급에 링크가 포함되어 있어 당신의 콘텐츠가 잘 연결되어 있습니다.")
        else:
            print("\n[정보] 이번 검색에서 언급된 내용을 찾지 못했습니다.")
    else:
        print("\n[정보] 이번 검색에서 언급된 내용을 전혀 찾지 못했습니다.")

    print("\n=== CiteSense AI 종료 ===")
    print("Tip: 이 스크립트를 작업 스케줄러에 등록하여 정기적으로 자동으로 실행할 수 있습니다. (예: `cron` 또는 `Windows Task Scheduler`)")

if __name__ == "__main__":
    main()
