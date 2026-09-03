# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
# UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import random
import time
import csv
import os
from datetime import datetime
import requests

# --- 전역 상수 정의 ---
# Reddit API 호출 시 사용할 User-Agent. 환경 변수에서 가져오거나 기본값 사용.
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "LinguaNicheSentinelBot/1.0")
# Reddit 검색을 위한 기본 URL 형식.
REDDIT_BASE_URL = "https://www.reddit.com/r/{subreddit}/search.json?q={query}&sort=new&limit=50"
# 기회로 간주될 최소 성장 점수 임계값.
SCORE_THRESHOLD = 60
# API 호출 시 대기 시간 (초). API 정책 준수 및 부하 방지.
API_WAIT_TIME_SECONDS = 0.5

# --- 헬퍼 함수 정의 ---
def fetch_reddit_mentions(topic: str, subreddit: str = "all", user_agent: str = REDDIT_USER_AGENT) -> int:
    """
    Reddit에서 특정 토픽의 언급 횟수를 가져옵니다.
    :param topic: 검색할 토픽 문자열.
    :param subreddit: 검색할 서브레딧 (기본값: 'all').
    :param user_agent: Reddit API 호출 시 사용할 User-Agent.
    :return: 토픽 언급 횟수 (정수). 오류 발생 시 0 반환.
    """
    print(f"[진행] Reddit에서 '{topic}'(r/{subreddit}) 언급 검색 중...")
    try:
        headers = {"User-Agent": user_agent}
        # 쿼리 문자열을 URL 인코딩하여 안전하게 전달.
        encoded_query = requests.utils.quote(topic)
        url = REDDIT_BASE_URL.format(subreddit=subreddit, query=encoded_query)
        
        print(f"[디버그] 요청 URL: {url}")
        response = requests.get(url, headers=headers, timeout=15) # 타임아웃 15초 설정
        response.raise_for_status() # 4xx, 5xx 에러 발생 시 예외 발생.
        data = response.json()
        
        mentions_count = 0
        # Reddit API 응답 구조에 따라 게시글 목록을 순회하며 언급 횟수 계산.
        for post in data.get('data', {}).get('children', []):
            post_data = post.get('data', {})
            title = post_data.get('title', '').lower()
            selftext = post_data.get('selftext', '').lower()
            
            if topic.lower() in title or topic.lower() in selftext:
                mentions_count += 1
        print(f"[성공] '{topic}' 언급 {mentions_count}회 발견.")
        return mentions_count
    except requests.exceptions.Timeout:
        print(f"[오류] '{topic}' Reddit 데이터 가져오기 시간 초과: 지정된 시간 내 응답 없음.")
        return 0
    except requests.exceptions.RequestException as e:
        print(f"[오류] '{topic}' Reddit 데이터 가져오기 실패: {e}")
        return 0 # 오류 발생 시 0 언급으로 처리
    except ValueError as e:
        print(f"[오류] '{topic}' Reddit 응답 JSON 파싱 실패: {e}. 유효하지 않은 JSON 응답일 수 있습니다.")
        return 0

def calculate_growth_potential(initial_mentions: int, recent_mentions: int, simulated_competition: float) -> int:
    """
    토픽의 성장 잠재력을 점수화합니다. 이 모델은 초기 언급, 최근 언급 및 시뮬레이션된 경쟁도를 사용합니다.
    :param initial_mentions: 과거 또는 기준 언급 횟수.
    :param recent_mentions: 최근 언급 횟수.
    :param simulated_competition: 0-10 사이의 시뮬레이션된 경쟁도 (낮을수록 좋음).
    :return: 0-100 범위의 성장 점수 (정수).
    """
    # 멘션 증가율 계산 (+1은 0으로 나누는 것을 방지).
    mention_growth_rate = (recent_mentions - initial_mentions) / (initial_mentions + 1) * 100

    # 참여도 요소 시뮬레이션 (간단화를 위해 무작위 값 사용).
    simulated_engagement_factor = random.uniform(0.5, 1.5)

    # 점수 산정 로직: 높은 성장, 높은 참여도, 낮은 경쟁이 높은 점수를 만듭니다.
    # 가중치: 성장률(40%), 참여도(20%), 경쟁도(30%).
    score = (mention_growth_rate * 0.4) + (simulated_engagement_factor * 20) - (simulated_competition * 0.3)

    # 점수를 0에서 100 사이로 제한하여 반환.
    return max(0, min(100, int(score)))

def notify_and_save_opportunity(topic: str, score: int, recent_mentions: int, output_file: str = "niche_opportunities.csv"):
    """
    발견된 기회를 알리고 CSV 파일에 저장합니다.
    :param topic: 기회로 감지된 토픽 문자열.
    :param score: 토픽의 성장 점수.
    :param recent_mentions: 최근 언급 횟수.
    :param output_file: 결과를 저장할 CSV 파일 경로.
    """
    status = "NEW OPPORTUNITY" if score >= SCORE_THRESHOLD else "LOW POTENTIAL"
    print(f"[알림] 니치 기회 감지: '{topic}' (점수: {score}, 최근 언급: {recent_mentions}). 상태: {status}")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_exists = os.path.exists(output_file)
    try:
        with open(output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Topic", "Growth_Score", "Recent_Mentions", "Status"])
            writer.writerow([timestamp, topic, score, recent_mentions, status])
        print(f"[저장] '{topic}' 기회 상세 정보가 '{output_file}'에 저장되었습니다.")
    except IOError as e:
        print(f"[오류] '{output_file}'에 데이터를 저장하는 중 오류 발생: {e}")

# --- 메인 함수 ---
def main():
    """
    LinguaNiche Sentinel의 주 실행 함수입니다. 토픽을 모니터링하고 니치 기회를 탐지합니다.
    """
    parser = argparse.ArgumentParser(description="LinguaNiche Sentinel: 떠오르는 언어/문화 니치 토픽을 탐지합니다.")
    parser.add_argument('--topics', nargs='*', help="모니터링할 시드 토픽 목록 (예: 'sustainable fashion AI' 'web3 gaming culture').")
    args = parser.parse_args()

    topics_to_monitor = args.topics
    if not topics_to_monitor:
        print("[정보] 제공된 토픽이 없습니다. 데모를 위해 샘플 데이터를 사용합니다.")
        print("본인의 토픽을 사용하려면: python linguaniche_sentinel.py --topics '내 토픽 1' '내 토픽 2'")
        topics_to_monitor = [
            "Indie TTRPG actual play", 
            "Ethical AI in art history", 
            "Nordic folk music revival", 
            "Urban foraging guides",
            "Quantum computing ethics"
        ]

    print(f"\n--- LinguaNiche Sentinel 시작 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
    all_results = []

    for i, topic in enumerate(topics_to_monitor):
        print(f"\n[과정] ({i+1}/{len(topics_to_monitor)}) 토픽 분석 중: '{topic}'")
        
        # 초기 언급은 현재 시뮬레이션 기반 (실제로는 과거 데이터 조회가 필요).
        initial_mentions = random.randint(5, 50) # 초기 시뮬레이션 값
        print(f"[시뮬] '{topic}'에 대한 시뮬레이션된 과거 기준 언급: {initial_mentions}회")

        # Reddit에서 최근 언급 횟수 가져오기 (실제 데이터).
        recent_mentions = fetch_reddit_mentions(topic, subreddit="all")
        
        # 실제 데이터가 없거나 부족할 경우 시뮬레이션 값으로 대체하여 모델 작동 보장.
        if recent_mentions == 0 and initial_mentions == 0:
            recent_mentions = random.randint(1, 10)
            initial_mentions = random.randint(1, 5)
            print(f"[폴백] 실제 데이터 부족으로 '{topic}'에 시뮬레이션된 최근 언급 ({recent_mentions}) 및 초기 언급 ({initial_mentions}) 사용.")
        elif recent_mentions == 0 and initial_mentions > 0: # 초기 언급은 있는데 최근 언급이 0인 경우
            print(f"[주의] '{topic}'의 최근 언급이 0입니다. 성장 점수가 낮을 수 있습니다.")
        
        # 경쟁도 시뮬레이션 (0-10, 낮을수록 좋음). 니치 토픽은 경쟁도가 낮을 경향이 있음.
        simulated_competition = random.uniform(1, 8)
        print(f"[시뮬] '{topic}'에 대한 시뮬레이션된 경쟁도: {simulated_competition:.2f}")

        growth_score = calculate_growth_potential(initial_mentions, recent_mentions, simulated_competition)
        all_results.append({"topic": topic, "score": growth_score, "recent_mentions": recent_mentions})

        if growth_score >= SCORE_THRESHOLD:
            notify_and_save_opportunity(topic, growth_score, recent_mentions)
        else:
            print(f"[정보] 토픽 '{topic}'의 점수는 {growth_score}입니다. 임계값({SCORE_THRESHOLD}) 미달.")

        time.sleep(API_WAIT_TIME_SECONDS) # API 호출 간 지연 시간.

    # 모든 처리된 토픽에 대한 요약 보고서 저장.
    summary_filename = "linguaniche_summary_report.csv"
    try:
        with open(summary_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Topic", "Growth_Score", "Recent_Mentions", "Opportunity_Status"])
            for result in all_results:
                status = "High Potential" if result['score'] >= SCORE_THRESHOLD else "Low Potential"
                writer.writerow([result['topic'], result['score'], result['recent_mentions'], status])
        print(f"\n[보고] 모든 토픽에 대한 상세 요약 보고서가 '{summary_filename}'에 저장되었습니다.")
    except IOError as e:
        print(f"[오류] 요약 보고서 '{summary_filename}'를 저장하는 중 오류 발생: {e}")

    print("\n--- LinguaNiche Sentinel 종료. ---")
    print("사용 안내: python linguaniche_sentinel.py --topics '내 토픽 1' '내 토픽 2'")
    print("크론(Cron) 등으로 스크립트 스케줄링 예시: 0 9 * * * python /path/to/linguaniche_sentinel.py")

if __name__ == "__main__":
    main()
