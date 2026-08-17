# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행 시 한글 윈도우에서 UnicodeEncodeError를 방지합니다.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import requests
from bs4 import BeautifulSoup
import argparse
import os
from datetime import datetime

# --- Configuration: 서비스 핵심 로직에 사용되는 설정 값들 ---
# 오래된 정보를 나타낼 수 있는 키워드 목록
OUTDATED_KEYWORDS = ["Flash Player", "Windows 7", "Internet Explorer 11", "Java 8 EOL", "Python 2 EOL", "Adobe Flash", "IE11", "Silverlight"]
# 내용에 문제가 있음을 나타낼 수 있는 키워드 목록 (댓글, 피드백 등)
PROBLEM_KEYWORDS = ["broken link", "outdated", "error", "not working", "fix this", "wrong info", "missing information"]

def _get_content(source_path: str) -> str | None:
    """URL 또는 로컬 파일에서 콘텐츠를 가져옵니다."""
    print(f"[진행중] 콘텐츠 소스 읽기 시작: {source_path}")
    if source_path.startswith("http://") or source_path.startswith("https://"):
        try:
            print(f"[정보] 웹 URL에서 콘텐츠 요청 중: {source_path}")
            response = requests.get(source_path, timeout=15) # 타임아웃 15초 설정
            response.raise_for_status() # HTTP 오류(4xx, 5xx) 발생 시 예외 발생
            print(f"[성공] URL 콘텐츠를 성공적으로 가져왔습니다: {source_path}")
            return response.text
        except requests.exceptions.Timeout:
            print(f"[오류] URL 요청 시간 초과: {source_path}")
        except requests.exceptions.ConnectionError:
            print(f"[오류] URL에 연결할 수 없습니다 (네트워크 문제 또는 잘못된 URL): {source_path}")
        except requests.exceptions.HTTPError as e:
            print(f"[오류] HTTP 요청 실패 (상태 코드 {e.response.status_code}): {source_path}")
        except requests.exceptions.RequestException as e:
            print(f"[오류] URL 요청 중 알 수 없는 오류 발생: {source_path} - {e}")
        return None
    else:
        try:
            if not os.path.exists(source_path):
                print(f"[오류] 파일을 찾을 수 없습니다: {source_path}")
                return None
            print(f"[정보] 로컬 파일에서 콘텐츠 읽기 중: {source_path}")
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"[성공] 파일 콘텐츠를 성공적으로 읽었습니다: {source_path}")
            return content
        except FileNotFoundError: # os.path.exists 로 미리 체크하므로 발생 확률 낮음
            print(f"[오류] 파일을 찾을 수 없습니다: {source_path}")
        except IOError as e:
            print(f"[오류] 파일 읽기 오류 발생: {source_path} - {e}")
        except Exception as e:
            print(f"[오류] 파일 처리 중 예기치 않은 오류 발생: {source_path} - {e}")
        return None

def _extract_and_check_links(html_content: str) -> list[str]:
    """HTML 콘텐츠에서 외부 링크를 추출하고 유효성을 검사합니다."""
    soup = BeautifulSoup(html_content, 'html.parser')
    external_links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # 외부 HTTP(S) 링크만 검사합니다.
        if href.startswith('http://') or href.startswith('https://'):
            external_links.add(href)

    broken_links = []
    total_links = len(external_links)
    if total_links == 0:
        print("[정보] 검사할 외부 링크가 없습니다.")
        return []

    print(f"[진행중] 총 {total_links}개의 고유 외부 링크 유효성 검사 시작...")
    for i, link in enumerate(sorted(list(external_links))): # 정렬하여 일관된 출력 보장
        print(f"[진행중] 링크 검사 중 ({i+1}/{total_links}): {link}")
        try:
            # HEAD 요청으로 링크 존재 여부 및 상태 코드만 확인 (빠름)
            response = requests.head(link, timeout=10, allow_redirects=True) # 타임아웃 10초
            # 2xx (성공), 3xx (리디렉션)는 정상으로 간주합니다.
            if not (200 <= response.status_code < 400):
                broken_links.append(f"{link} (상태: {response.status_code})")
                print(f"[경고] 깨진 링크 발견: {link} (상태: {response.status_code})")
        except requests.exceptions.Timeout:
            broken_links.append(f"{link} (오류: 연결 시간 초과)")
            print(f"[오류] 링크 검사 시간 초과: {link}")
        except requests.exceptions.RequestException as e:
            broken_links.append(f"{link} (오류: {e})")
            print(f"[오류] 링크 검사 중 요청 오류 발생: {link} - {e}")
    print(f"[완료] 링크 유효성 검사 완료. 깨진 링크 {len(broken_links)}개 발견.")
    return broken_links

def _analyze_content_freshness(html_content: str, publish_year: int | None = None) -> list[str]:
    """콘텐츠에서 오래된 키워드를 분석하고, 발행 연도에 기반하여 신선도를 제안합니다."""
    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text(separator=' ', strip=True) # 텍스트를 공백으로 분리, 공백 제거
    freshness_warnings = []
    print("[진행중] 콘텐츠 신선도 분석 시작...")

    # 1. 오래된 키워드 검사
    found_outdated_keywords = [keyword for keyword in OUTDATED_KEYWORDS if keyword.lower() in text_content.lower()]
    for keyword in found_outdated_keywords:
        freshness_warnings.append(f"오래된 정보 키워드 발견: '{keyword}'")
        print(f"[경고] 오래된 키워드 발견: '{keyword}'")

    # 2. 발행 연도 기반 내용 연식 분석
    if publish_year and isinstance(publish_year, int):
        current_year = datetime.now().year
        if publish_year > current_year: # 미래 연도 입력 방지
            freshness_warnings.append(f"발행 연도가 현재 연도({current_year})보다 미래입니다: {publish_year}")
            print(f"[경고] 발행 연도 오류: {publish_year} (미래 연도)")
        else:
            age = current_year - publish_year
            if age >= 5:
                freshness_warnings.append(f"콘텐츠가 {age}년 전 발행됨 ({publish_year}). 전면적인 검토가 필요합니다.")
                print(f"[경고] 콘텐츠 매우 오래됨: {age}년 전 발행 ({publish_year})")
            elif age >= 2:
                freshness_warnings.append(f"콘텐츠가 {age}년 전 발행됨 ({publish_year}). 업데이트가 필요할 수 있습니다.")
                print(f"[경고] 콘텐츠 오래됨: {age}년 전 발행 ({publish_year})")
            else:
                print(f"[정보] 콘텐츠가 비교적 최신입니다 ({age}년 전 발행).")
    else:
        print("[정보] 발행 연도가 제공되지 않아 연식 분석을 건너뜁니다.")

    # 3. 문제성 키워드 검사 (댓글, 피드백 등 잠재적 이슈)
    found_problem_keywords = [keyword for keyword in PROBLEM_KEYWORDS if keyword.lower() in text_content.lower()]
    for keyword in found_problem_keywords:
        freshness_warnings.append(f"문제 가능성 키워드 발견: '{keyword}' (주석/피드백 섹션일 수 있음)")
        print(f"[경고] 문제성 키워드 발견: '{keyword}'")
        
    print("[완료] 콘텐츠 신선도 분석 완료.")
    return freshness_warnings

def main():
    parser = argparse.ArgumentParser(
        description="Evergreen Warden: 디지털 콘텐츠의 노후화를 모니터링합니다.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--url', type=str, help='분석할 콘텐츠의 URL (예: https://example.com/blog-post.html)')
    parser.add_argument('--file', type=str, help='분석할 로컬 HTML 파일 경로 (예: my_article.html)')
    parser.add_argument('--year', type=int, help='[선택 사항] 콘텐츠의 발행 연도 (예: 2022) - 신선도 분석에 사용됩니다.')
    args = parser.parse_args()

    html_content = None
    content_source_info = "N/A"
    publish_year_for_analysis = args.year

    if args.url or args.file:
        source_path = args.url if args.url else args.file
        content_source_info = source_path
        html_content = _get_content(source_path)
    else:
        print("[알림] URL 또는 파일 경로가 제공되지 않아 데모 샘플 데이터로 실행됩니다.")
        print("[안내] 본인 데이터를 사용하려면 다음 명령어를 실행하세요:\n  python evergreen_warden.py --url https://example.com/your-post.html\n  python evergreen_warden.py --file my_content.html --year 2022\n")
        sample_html = """
        <html><head><title>오래된 기술 블로그 포스트</title></head><body>
        <h1>Windows 7에서 Flash Player 사용하는 방법</h1>
        <p>안녕하세요! 이 가이드에서는 새 Windows 7 PC에서 <a href="http://broken-old-flash.com/player_guide">Flash Player</a>를 완벽하게 작동시키는 방법을 보여드립니다. 이 방법은 여전히 작동하는 오래된 트릭을 사용합니다! Java 8 EOL에 대해서도 이야기합니다.</p>
        <p>더 많은 팁은 <a href="https://another-valid-site.com">저희 메인 사이트</a>에서 찾아보세요.</p>
        <!-- 댓글 섹션 -->
        <div>
            <p><b>사용자:</b> 이 가이드는 훌륭하지만, 다운로드 링크가 broken link인 것 같아요!</p>
            <p><b>사용자2:</b> 네, 이제 outdated 되었어요. 새로운 해결책이 필요합니다.</p>
        </div>
        </body></html>
        """
        html_content = sample_html
        publish_year_for_analysis = 2010 # 샘플 콘텐츠는 매우 오래된 것으로 가정
        content_source_info = "[데모] 샘플 데이터"

    if not html_content:
        print("[오류] 분석할 콘텐츠를 가져오는 데 실패했습니다. 프로그램을 종료합니다.")
        return

    # 리포트 파일 생성 준비
    report_filename = f"evergreen_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_content_lines = [] # 리포트 내용을 담을 리스트

    report_content_lines.append(f"Evergreen Warden 분석 보고서: {content_source_info}")
    report_content_lines.append(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    print("\n--- [분석 시작] 링크 유효성 검사 ---")
    broken_links = _extract_and_check_links(html_content)
    if broken_links:
        report_content_lines.append("** 깨지거나 접근할 수 없는 외부 링크 **")
        for link in broken_links:
            report_content_lines.append(f"- {link}")
    else:
        report_content_lines.append("모든 외부 링크가 정상적으로 작동하는 것으로 보입니다.")
    report_content_lines.append("\n")
    print("--- [분석 완료] 링크 유효성 검사 ---")

    print("--- [분석 시작] 콘텐츠 신선도 및 잠재적 문제 분석 ---")
    freshness_warnings = _analyze_content_freshness(html_content, publish_year_for_analysis)
    if freshness_warnings:
        report_content_lines.append("** 콘텐츠 신선도 및 잠재적 문제점 **")
        for warning in freshness_warnings:
            report_content_lines.append(f"- {warning}")
    else:
        report_content_lines.append("콘텐츠가 최신이며 즉각적인 경고 징후가 없습니다.")
    report_content_lines.append("\n")
    print("--- [분석 완료] 콘텐츠 신선도 및 잠재적 문제 분석 ---")

    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            for line in report_content_lines:
                f.write(line + '\n')
        print(f"\n[성공] 분석 보고서가 성공적으로 저장되었습니다: {report_filename}")
    except IOError as e:
        print(f"[오류] 보고서 파일 저장 중 오류 발생: {report_filename} - {e}")
    except Exception as e:
        print(f"[오류] 보고서 저장 중 예기치 않은 오류 발생: {e}")

    print("\n[안내] 이 스크립트를 정기적으로 실행하여 (예: cron job을 통해) 콘텐츠를 항상 최신 상태로 유지하세요!")

if __name__ == "__main__":
    main()
