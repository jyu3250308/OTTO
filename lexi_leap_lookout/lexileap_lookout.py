# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import requests
import argparse
import datetime
import re
import os

# 프로그램 상수 정의
DEFAULT_TIMEOUT_SECONDS = 10

def fetch_url_content(url: str) -> str | None:
    """
    주어진 URL에서 웹 페이지 콘텐츠를 가져옵니다.
    네트워크 오류 또는 HTTP 오류 발생 시 None을 반환합니다.
    """
    print(f"[진행] URL 콘텐츠 가져오는 중: {url}")
    try:
        # URL 요청 시 타임아웃을 설정하여 무한 대기를 방지합니다.
        response = requests.get(url, timeout=DEFAULT_TIMEOUT_SECONDS)
        response.raise_for_status()  # 200 이외의 응답 코드에 대해 HTTPError를 발생시킵니다.
        print(f"[성공] URL 콘텐츠 가져오기 완료: {url}")
        return response.text
    except requests.exceptions.Timeout:
        print(f"[오류] 요청 시간 초과: {url} ({DEFAULT_TIMEOUT_SECONDS}초 이내 응답 없음)")
    except requests.exceptions.RequestException as e:
        print(f"[오류] URL 요청 실패: {url} - {e}")
    except Exception as e:
        print(f"[예외] 예기치 않은 오류 발생: {url} - {e}")
    return None

def analyze_content_for_keywords(content: str, keywords: list[str]) -> list[str]:
    """
    주어진 콘텐츠에서 키워드 목록을 검색하고 발견된 키워드를 반환합니다.
    대소문자를 구분하지 않고 검색합니다.
    """
    found_keywords = []
    for keyword in keywords:
        # re.IGNORECASE 플래그를 사용하여 대소문자를 구분하지 않는 검색을 수행합니다.
        if re.search(re.escape(keyword), content, re.IGNORECASE):
            found_keywords.append(keyword)
    return found_keywords

def main():
    """
    LexiLeap Lookout 스크립트의 메인 함수.
    URL 목록을 모니터링하고 지정된 키워드를 검색합니다.
    """
    parser = argparse.ArgumentParser(
        description="LexiLeap Lookout: 지정된 키워드를 찾기 위해 URL을 모니터링합니다."
    )
    parser.add_argument(
        "source",
        nargs="?",  # 인자를 선택적으로 만듭니다.
        help="모니터링할 URL 목록이 포함된 파일 경로 (한 줄에 하나씩) 또는 단일 URL."
    )
    args = parser.parse_args()

    target_urls = []
    # 모니터링할 키워드 목록. 필요에 따라 이 목록을 수정하세요.
    search_keywords = ["critical", "alert", "error", "urgent", "문제", "경고"]

    if args.source:
        # 사용자가 입력 소스를 제공한 경우
        if os.path.isfile(args.source):
            print(f"[정보] 파일에서 URL 목록 로드 중: {args.source}")
            try:
                with open(args.source, 'r', encoding='utf-8') as f:
                    for line in f:
                        url = line.strip()
                        if url and url.startswith(('http://', 'https://')):
                            target_urls.append(url)
                if not target_urls:
                    print(f"[경고] '{args.source}' 파일에서 유효한 URL을 찾을 수 없습니다.")
            except IOError as e:
                print(f"[오류] 파일 읽기 실패: {args.source} - {e}")
                print("[종료] 파일을 읽을 수 없어 프로그램을 종료합니다.")
                _sys.exit(1)
        elif args.source.startswith(('http://', 'https://')):
            target_urls.append(args.source)
            print(f"[정보] 단일 URL 모니터링 설정: {args.source}")
        else:
            print(f"[오류] 유효하지 않은 소스 형식입니다: {args.source}")
            print("[안내] 파일 경로 또는 유효한 URL을 제공해야 합니다.")
            _sys.exit(1)
    else:
        # 입력 소스가 제공되지 않은 경우 데모 데이터 사용
        print("[안내] 지금은 샘플 데이터입니다. 본인 파일을 쓰려면 'python lexileap_lookout.py 내파일.txt'와 같이 실행하세요.")
        target_urls = [
            "https://www.google.com",
            "https://www.naver.com",
            "https://example.com/nonexistent", # 존재하지 않는 URL 테스트용
            "https://korean.cdc.gov/coronavirus/2019-ncov/index.html" # 한글 콘텐츠 테스트용
        ]

    if not target_urls:
        print("[종료] 모니터링할 URL이 없습니다. 프로그램을 종료합니다.")
        _sys.exit(0)

    print(f"[시작] LexiLeap Lookout 모니터링 시작. 총 {len(target_urls)}개 URL 검사.")
    print(f"[정보] 검색할 키워드: {', '.join(search_keywords)}")
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[시간] 모니터링 시작 시각: {current_time}")

    for i, url in enumerate(target_urls):
        print(f"\n[{i+1}/{len(target_urls)}] URL 처리 중: {url}")
        content = fetch_url_content(url)

        if content:
            found = analyze_content_for_keywords(content, search_keywords)
            if found:
                print(f"[발견] '{url}'에서 다음 키워드 발견: {', '.join(found)}")
            else:
                print(f"[결과] '{url}'에서 지정된 키워드 발견되지 않음.")
        else:
            print(f"[결과] '{url}'의 콘텐츠를 가져오지 못하여 키워드 분석 건너뜀.")

    print(f"\n[완료] LexiLeap Lookout 모니터링 종료.")

if __name__ == "__main__":
    main()