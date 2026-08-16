# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
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
import json
from datetime import datetime

# --- Configuration (환경 설정) ---
# 트렌드 감지 기준 설정
MIN_ABSOLUTE_MENTIONS = 3  # 최소 언급량: 이 값 미만 언급은 트렌드에 포함하지 않습니다.
TREND_MULTIPLIER = 1.5     # 이전 대비 언급량 증가율: 이 배율 이상 증가 시 트렌드로 간주합니다 (예: 1.5배).

# 파일 및 디렉토리 설정
REPORT_DIR = "trend_reports"  # 분석 리포트가 저장될 디렉토리
HISTORY_FILE = "trend_history.json" # 키워드 언급량 기록을 저장할 파일

def get_text_from_url(url: str) -> str:
    """
    지정된 URL에서 HTML 콘텐츠를 가져와 텍스트만 추출합니다.
    스크립트 및 스타일 태그는 제거됩니다.
    
    Args:
        url (str): 텍스트를 추출할 웹 페이지의 URL.

    Returns:
        str: 추출된 소문자 텍스트 콘텐츠. 오류 발생 시 빈 문자열을 반환합니다.
    """
    try:
        # 5초 타임아웃 설정으로 네트워크 지연 또는 끊김에 대비합니다.
        print(f"    - URL에서 텍스트 추출 시도: {url}")
        response = requests.get(url, timeout=5)
        response.raise_for_status() # 200 이외의 HTTP 상태 코드 시 예외 발생
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 스크립트와 스타일 태그 제거하여 순수 텍스트만 남깁니다.
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
            
        text = soup.get_text(separator=' ', strip=True) # 공백을 기준으로 텍스트 병합 및 공백 제거
        print(f"    - 텍스트 추출 성공 ({len(text)} 문자)")
        return text.lower() # 모든 텍스트를 소문자로 변환하여 키워드 매칭의 일관성을 확보합니다.
    except requests.exceptions.RequestException as e:
        print(f"    [경고] {url} 처리 중 네트워크/HTTP 오류 발생: {e}")
        return ""
    except Exception as e:
        print(f"    [경고] {url} 처리 중 예상치 못한 오류 발생: {e}")
        return ""

def load_history(filename: str = HISTORY_FILE) -> dict:
    """
    이전 트렌드 기록(키워드별 총 언급량)을 파일에서 불러옵니다.
    파일이 없거나 손상된 경우 빈 딕셔너리를 반환하고 새로 시작합니다.
    
    Args:
        filename (str): 트렌드 기록 파일 경로.

    Returns:
        dict: 불러온 트렌드 기록 딕셔너리.
    """
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                history = json.load(f)
            print(f"[정보] 트렌드 기록 '{filename}'을(를) 성공적으로 불러왔습니다.")
            return history
        except json.JSONDecodeError:
            print(f"[오류] '{filename}' 파일이 손상되었거나 형식이 올바르지 않습니다. 새로운 파일로 시작합니다.")
        except Exception as e:
            print(f"[오류] 트렌드 기록 '{filename}' 불러오기 중 예상치 못한 오류 발생: {e}. 새로운 파일로 시작합니다.")
    else:
        print(f"[정보] 트렌드 기록 파일 '{filename}'을(를) 찾을 수 없습니다. 새로운 파일로 시작합니다.")
    return {}

def save_history(history: dict, filename: str = HISTORY_FILE):
    """
    현재 트렌드 기록을 파일에 저장합니다.
    
    Args:
        history (dict): 저장할 트렌드 기록 딕셔너리.
        filename (str): 트렌드 기록 파일 경로.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        print(f"[정보] 트렌드 기록 '{filename}'을(를) 성공적으로 저장했습니다.")
    except IOError as e:
        print(f"[오류] 트렌드 기록 '{filename}' 저장 중 입출력 오류 발생: {e}")
    except Exception as e:
        print(f"[오류] 트렌드 기록 '{filename}' 저장 중 예상치 못한 오류 발생: {e}")

def main():
    """
    Proto-Trend Pinger의 메인 실행 함수입니다.
    커맨드 라인 인자를 파싱하고, 커뮤니티 URL 및 키워드를 로드하여
    트렌드를 감지하고 리포트를 생성합니다.
    """
    parser = argparse.ArgumentParser(description="Proto-Trend Pinger: 틈새 커뮤니티 트렌드 감지 프로그램.")
    parser.add_argument('--communities', '-c', type=str, default='communities.txt',
                        help='모니터링할 커뮤니티 URL 목록이 담긴 파일 (한 줄에 하나씩).')
    parser.add_argument('--keywords', '-k', type=str, default='keywords.txt',
                        help='감지할 키워드 목록이 담긴 파일 (한 줄에 하나씩).')
    args = parser.parse_args()

    print(f"\n--- Proto-Trend Pinger 실행 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")

    # --- 커뮤니티 URL 파일 로드 또는 데모 폴백 ---
    community_urls = []
    if os.path.exists(args.communities):
        try:
            with open(args.communities, 'r', encoding='utf-8') as f:
                community_urls = [line.strip() for line in f if line.strip()]
            print(f"[정보] 커뮤니티 목록 '{args.communities}'을(를) 성공적으로 불러왔습니다. ({len(community_urls)}개)")
        except Exception as e:
            print(f"[오류] 커뮤니티 목록 파일 '{args.communities}' 로드 중 오류 발생: {e}. 데모 목록을 사용합니다.")
    
    if not community_urls: # 파일 로드 실패 또는 파일이 비어있는 경우 데모 데이터 사용
        print(f"[안내] '{args.communities}' 파일을 찾을 수 없거나 비어 있습니다. 데모 커뮤니티 목록을 사용합니다.")
        print("       지금은 샘플 데이터입니다. 본인 파일을 쓰려면 'python proto_trend_pinger.py --communities 내파일.txt' 와 같이 실행하세요.")
        community_urls = [
            "https://news.naver.com/main/read.naver?mode=LSD&mid=shm&sid1=105&oid=009&aid=0005273540",
            "https://news.naver.com/main/read.naver?mode=LSD&mid=shm&sid1=105&oid=030&aid=0003204968",
            "https://www.yonhapnewstv.co.kr/news/MYH20240101000100038"
        ]

    # --- 키워드 파일 로드 또는 데모 폴백 ---
    target_keywords = []
    if os.path.exists(args.keywords):
        try:
            with open(args.keywords, 'r', encoding='utf-8') as f:
                target_keywords = [line.strip().lower() for line in f if line.strip()]
            print(f"[정보] 키워드 목록 '{args.keywords}'을(를) 성공적으로 불러왔습니다. ({len(target_keywords)}개)")
        except Exception as e:
            print(f"[오류] 키워드 목록 파일 '{args.keywords}' 로드 중 오류 발생: {e}. 데모 키워드를 사용합니다.")

    if not target_keywords: # 파일 로드 실패 또는 파일이 비어있는 경우 데모 데이터 사용
        print(f"[안내] '{args.keywords}' 파일을 찾을 수 없거나 비어 있습니다. 데모 키워드를 사용합니다.")
        print("       지금은 샘플 데이터입니다. 본인 파일을 쓰려면 'python proto_trend_pinger.py --keywords 내파일.txt' 와 같이 실행하세요.")
        target_keywords = ["양자 컴퓨터", "거대 언어 모델", "메타버스", "블록체인", "생성형 ai", "인공지능 로봇"]

    if not community_urls or not target_keywords:
        print("[오류] 모니터링할 커뮤니티 URL 또는 키워드가 없어 프로그램을 종료합니다.")
        return

    print(f"\n모니터링 커뮤니티 ({len(community_urls)}개): {', '.join(community_urls[:2])}{'...' if len(community_urls)>2 else ''}")
    print(f"감지 키워드 ({len(target_keywords)}개): {', '.join(target_keywords[:5])}{'...' if len(target_keywords)>5 else ''}\n")

    # 리포트 디렉토리 생성 (이미 존재하면 무시)
    os.makedirs(REPORT_DIR, exist_ok=True)
    print(f"[정보] 리포트 저장 디렉토리 '{REPORT_DIR}' 확인 또는 생성 완료.")

    # 이전 트렌드 기록 불러오기
    trend_history = load_history()
    current_keyword_counts = {kw: 0 for kw in target_keywords} # 현재 실행의 키워드 언급량 초기화

    print("\n--- 실시간 커뮤니티 모니터링 및 언급량 계산 시작 ---")
    # --- 실시간 모니터링 및 언급량 계산 ---
    for i, url in enumerate(community_urls):
        print(f"[진행 {i+1}/{len(community_urls)}] 커뮤니티 모니터링 시작: {url}")
        content = get_text_from_url(url)
        if content:
            for keyword in target_keywords:
                count = content.count(keyword) # 텍스트 내 키워드 언급 횟수 계산
                if count > 0:
                    print(f"    - 키워드 '{keyword}': {count}회 언급 감지")
                current_keyword_counts[keyword] += count
        else:
            print(f"[경고] {url} 에서 유효한 콘텐츠를 가져오지 못했습니다. 이 URL은 분석에서 제외됩니다.")
    print("--- 실시간 커뮤니티 모니터링 및 언급량 계산 완료 ---\n")

    print("--- 트렌드 감지 및 리포트 생성 시작 ---")
    # --- 트렌드 감지 및 리포트 생성 ---
    trend_report_content = []
    report_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    trend_report_content.append(f"# Proto-Trend Pinger 트렌드 분석 리포트 - {report_timestamp}\n")
    trend_report_content.append(f"## 실시간 감지된 트렌드 목록\n")
    detected_trends = [] # 감지된 트렌드 저장

    for keyword, current_count in current_keyword_counts.items():
        previous_data = trend_history.get(keyword, {"total_mentions": 0, "last_updated": None})
        previous_count = previous_data["total_mentions"]
        
        is_trending = False
        if current_count >= MIN_ABSOLUTE_MENTIONS: # 최소 언급량 조건을 만족하는가?
            if previous_count == 0: # 처음 감지된 키워드 또는 이전 기록 없음
                if current_count > 0: # 0회 이상 언급 시 새로운 트렌드로 간주
                    is_trending = True
                    detected_trends.append((keyword, current_count, previous_count))
                    trend_report_content.append(
                        f"- **{keyword}**: 언급량 {current_count}회 (✨새로운 트렌드 감지!)\n"
                    )
            elif current_count > previous_count * TREND_MULTIPLIER: # 이전 대비 언급량 증가율 조건을 만족하는가?
                is_trending = True
                detected_trends.append((keyword, current_count, previous_count))
                trend_report_content.append(
                    f"- **{keyword}**: 언급량 {current_count}회 (이전 대비 {current_count/previous_count:.1f}배 급증!)\n"
                )
        
        # 현재 언급량으로 히스토리 업데이트 (이전 기록이 없거나 0이었어도 현재 값으로 갱신)
        trend_history[keyword] = {
            "total_mentions": current_count,
            "last_updated": datetime.now().isoformat() # ISO 8601 형식으로 저장
        }

    if not detected_trends:
        trend_report_content.append("### ⚠️ 현재 시점에는 새로운 트렌드가 감지되지 않았습니다.\n")
    else:
        print(f"[정보] 총 {len(detected_trends)}개의 트렌드가 감지되었습니다.\n")

    trend_report_content.append("\n## 콘텐츠 아이디어 제안\n")
    if detected_trends:
        trend_report_content.append("현재 급부상 중인 트렌드 키워드를 활용한 콘텐츠 아이디어를 제안합니다.\n")
        for kw, _, _ in detected_trends:
            trend_report_content.append(f"- **'{kw}' 관련 심층 분석 기사**: 해당 트렌드가 왜 뜨고 있는지, 어떤 기술적 배경이 있는지 분석하세요.\n")
            trend_report_content.append(f"- **'{kw}' 실생활 적용 사례**: 이 트렌드가 우리의 삶을 어떻게 바꿀 수 있는지 구체적인 사례를 들어 설명하세요.\n")
            trend_report_content.append(f"- **'{kw}' 전문가 인터뷰**: 해당 분야의 전문가를 찾아 트렌드에 대한 견해와 미래 전망을 들어보세요.\n")
            trend_report_content.append(f"- **'{kw}'에 대한 FAQ**: 사람들이 가장 궁금해할 만한 질문들을 모아 답변하는 콘텐츠를 만드세요.\n")
    else:
        trend_report_content.append("새로운 트렌드가 감지되지 않아 제안할 아이디어가 없습니다. 다음 실행을 기다려주세요!\n")

    # --- 리포트 파일 저장 ---
    report_filename = os.path.join(REPORT_DIR, f"trend_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.writelines(trend_report_content)
        print(f"\n[완료] 트렌드 분석 리포트가 '{report_filename}'에 성공적으로 저장되었습니다.")
    except IOError as e:
        print(f"[오류] 리포트 파일 '{report_filename}' 저장 중 입출력 오류 발생: {e}")
    
    # --- 히스토리 저장 ---
    save_history(trend_history)
    print(f"[완료] 다음 실행을 위한 트렌드 기록이 '{HISTORY_FILE}'에 업데이트되었습니다.\n")
    print("--- Proto-Trend Pinger 종료 ---")
    print("\n[팁] 이 봇을 매일/반복 실행하려면 cron, Windows 작업 스케줄러 등을 활용하여 'python proto_trend_pinger.py' 명령을 등록하세요.")

if __name__ == "__main__":
    main()
