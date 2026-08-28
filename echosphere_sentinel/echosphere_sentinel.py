# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행 시 한글 윈도우에서 UnicodeEncodeError 방지. 삭제 금지.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

"""
EchoSphere Sentinel: 온라인 커뮤니티 여론을 실시간 감시하고 분석하여 중요한 변화를 알립니다.
지정된 URL에서 콘텐츠를 추출하고, 감성 분석 및 키워드 추적을 수행한 후 보고서를 생성하고
필요 시 웹훅을 통해 알림을 전송합니다.
"""

import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import argparse
import datetime
import os
import logging

# 로그 설정을 통해 모든 출력 메시지를 일관된 형식으로 관리합니다.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 전역 상수 정의 (가독성 및 유지보수성 향상)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
REQUEST_TIMEOUT = 15
WEBHOOK_TIMEOUT = 7
REPORT_FILENAME = "echosphere_report.txt"
DEFAULT_SLACK_WEBHOOK = "YOUR_SLACK_WEBHOOK_URL" # 실제 Slack/Telegram 웹훅 URL로 교체 필요

def fetch_content(url: str) -> str | None:
    """
    지정된 URL에서 HTML을 가져와 불필요한 태그를 제거한 후 순수 텍스트 콘텐츠를 추출합니다.
    Args:
        url (str): 콘텐츠를 가져올 웹 페이지의 URL.
    Returns:
        str | None: 추출된 텍스트 콘텐츠 또는 오류 발생 시 None.
    """
    logger.info(f"[진행] URL '{url}' 콘텐츠 가져오는 중...")
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status() # HTTP 오류(4xx, 5xx) 발생 시 예외 발생

        soup = BeautifulSoup(response.text, 'html.parser')
        for script_or_style in soup(['script', 'style']): script_or_style.decompose() # <script> 및 <style> 태그 제거
        text = soup.get_text(separator=' ', strip=True) # 공백으로 구분하고 앞뒤 공백 제거

        if not text.strip():
            logger.warning(f"[경고] URL '{url}' 에서 유효한 텍스트 콘텐츠를 찾을 수 없습니다.")
            return None

        logger.info(f"[성공] URL '{url}' 콘텐츠 추출 완료. (약 {len(text.split())} 단어)")
        return text
    except requests.exceptions.Timeout:
        logger.error(f"[에러] URL '{url}' 요청 시간 초과. 지정된 {REQUEST_TIMEOUT}초 내에 응답이 없습니다.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"[에러] URL '{url}' HTTP 오류 발생: {e.response.status_code} {e.response.reason}")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"[에러] URL '{url}' 연결 실패: 웹 서버에 연결할 수 없거나 네트워크 문제가 발생했습니다. {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"[에러] URL '{url}' 요청 중 예상치 못한 오류 발생: {e}")
    except Exception as e:
        logger.error(f"[에러] URL '{url}' 콘텐츠 처리 중 일반 오류 발생: {e}")
    return None

def analyze_sentiment(text: str, target_keywords: list[str] | None = None) -> dict:
    """
    주어진 텍스트의 감성을 분석하고, 특정 키워드의 언급 빈도를 추적합니다.
    Args:
        text (str): 분석할 텍스트.
        target_keywords (list[str] | None): 추적할 키워드 목록.
    Returns:
        dict: 감성 극성, 주관성, 키워드 언급 수, 상위 단어 목록을 포함하는 딕셔너리.
    """
    logger.info("[진행] 텍스트 감성 및 키워드 분석 시작...")
    if not text.strip():
        logger.warning("[경고] 분석할 텍스트가 비어있습니다. 빈 감성 데이터 반환.")
        return {"overall_polarity": 0.0, "overall_subjectivity": 0.0, "keyword_counts": {}, "top_words": []}
        
    try:
        blob = TextBlob(text)
        overall_polarity = blob.sentiment.polarity # -1(부정) ~ 1(긍정)
        overall_subjectivity = blob.sentiment.subjectivity # 0(객관적) ~ 1(주관적)

        # 키워드 언급 횟수 계산 (대소문자 무시)
        keyword_counts = {kw.lower(): text.lower().count(kw.lower()) for kw in target_keywords} if target_keywords else {}

        # 불용어 제거 및 상위 10개 단어 추출
        stop_words = TextBlob('').words.stop_words # TextBlob 기본 불용어 사용
        words = [word.lower() for word in blob.words if len(word) > 2 and not word.isdigit() and word.lower() not in stop_words]
        word_freq = {word: words.count(word) for word in set(words)} # 단어 빈도 계산
        top_words = sorted(word_freq.items(), key=lambda item: item[1], reverse=True)[:10] # 상위 10개 단어
        
        logger.info(f"[완료] 감성 분석 완료. 극성: {overall_polarity:.2f}, 주관성: {overall_subjectivity:.2f}")
        return {"overall_polarity": overall_polarity, "overall_subjectivity": overall_subjectivity, "keyword_counts": keyword_counts, "top_words": top_words}
    except Exception as e:
        logger.error(f"[에러] 텍스트 감성 분석 중 오류 발생: {e}")
        return {"overall_polarity": 0.0, "overall_subjectivity": 0.0, "keyword_counts": {}, "top_words": []}

def send_alert(message: str, webhook_url: str) -> None:
    """
    Slack 또는 Telegram 웹훅을 통해 알림 메시지를 전송합니다.
    Args:
        message (str): 전송할 알림 메시지.
        webhook_url (str): 알림을 받을 웹훅 URL.
    """
    if not webhook_url or DEFAULT_SLACK_WEBHOOK in webhook_url:
        logger.warning("[경고] 유효한 웹훅 URL이 설정되지 않아 알림을 전송하지 않습니다.")
        return

    logger.info("[진행] 웹훅으로 알림 전송 시도 중...")
    payload = {"text": f"[EchoSphere Sentinel 알림]\n{message}"}
    try:
        response = requests.post(webhook_url, json=payload, timeout=WEBHOOK_TIMEOUT)
        response.raise_for_status()
        logger.info("[성공] 웹훅 알림이 성공적으로 전송되었습니다.")
    except requests.exceptions.Timeout:
        logger.error(f"[에러] 웹훅 알림 전송 시간 초과. {WEBHOOK_TIMEOUT}초 내에 응답이 없습니다.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"[에러] 웹훅 서버 응답 오류 발생: {e.response.status_code} {e.response.reason}")
    except requests.exceptions.RequestException as e:
        logger.error(f"[에러] 웹훅 알림 전송 중 요청 오류 발생: {e}")
    except Exception as e:
        logger.error(f"[에러] 웹훅 알림 전송 중 일반 오류 발생: {e}")

def generate_report(data: dict, filename: str = REPORT_FILENAME) -> None:
    """
    분석 결과를 파일로 저장합니다.
    Args:
        data (dict): 분석 결과를 포함하는 딕셔너리.
        filename (str): 보고서 파일명.
    """
    report_path = os.path.join(os.getcwd(), filename)
    logger.info(f"[진행] 분석 보고서를 '{report_path}' 에 저장 중...")
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"=== EchoSphere Sentinel 분석 보고서 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n\n")
            f.write(f"분석 대상 URL: {data.get('url', 'N/A')}\n")
            sentiment = data.get('sentiment', {})
            f.write(f"감성 극성 (Polarity): {sentiment.get('overall_polarity', 0.0):.2f} (1:긍정, -1:부정)\n")
            f.write(f"감성 주관성 (Subjectivity): {sentiment.get('overall_subjectivity', 0.0):.2f} (1:주관적, 0:객관적)\n\n")
            f.write("--- 키워드 언급 수 ---\n")
            kw_counts = sentiment.get('keyword_counts', {})
            if kw_counts:
                f.write('\n'.join([f"- '{k}': {c}회" for k, c in sorted(kw_counts.items(), key=lambda item: item[1], reverse=True)]))
            else:
                f.write("추적된 키워드 없음.")
            f.write("\n\n--- 급부상하는 관심사 (상위 10개 단어) ---\n")
            top_words = sentiment.get('top_words', [])
            if top_words:
                f.write('\n'.join([f"- '{w}': {c}회" for w, c in top_words]))
            else:
                f.write("분석된 상위 단어 없음.")
            f.write("\n\n--- 감지된 민심 변화 및 알림 ---\n")
            f.write(f"{data['alert_message']}\n" if data.get('alert_message') else "특별한 민심 변화 감지 안 됨.\n")
        logger.info(f"[완료] 분석 보고서가 '{report_path}' 에 성공적으로 저장되었습니다.")
    except IOError as e:
        logger.error(f"[에러] 보고서 파일 '{report_path}' 쓰기 실패: {e}")
    except Exception as e:
        logger.error(f"[에러] 보고서 생성 중 오류 발생: {e}")

def main():
    """
    EchoSphere Sentinel의 메인 실행 함수입니다. 명령줄 인자를 파싱하고 전체 분석 흐름을 조정합니다.
    """
    parser = argparse.ArgumentParser(description="온라인 커뮤니티 여론을 실시간 감시하는 EchoSphere Sentinel.")
    parser.add_argument("url", nargs='?', default=None, help="감시할 온라인 커뮤니티 URL (예: 블로그 댓글, 뉴스 기사)")
    parser.add_argument("--keywords", nargs='*', default=[], help="추적할 키워드 목록 (공백 구분). 예: --keywords '상품명' '불만'")
    parser.add_argument("--webhook", default=DEFAULT_SLACK_WEBHOOK, help=f"알림을 받을 Slack 또는 Telegram 웹훅 URL (기본값: {DEFAULT_SLACK_WEBHOOK})")
    args = parser.parse_args()

    target_url = args.url
    target_keywords = args.keywords
    webhook_url = args.webhook

    if not target_url:
        logger.info("\n[안내] URL 인자가 없어 샘플 데이터로 EchoSphere Sentinel 데모를 실행합니다.")
        logger.info("       본인 URL 감시: python echosphere_sentinel.py 'http://your-url.com' --keywords '키워드1' --webhook 'YOUR_WEBHOOK_URL'\n")
        target_url = "https://www.yna.co.kr/view/AKR20240723145400009" # 연합뉴스 샘플 기사
        if not target_keywords: 
            target_keywords = ['AI', '기술', '혁신'] # 샘플 키워드
        logger.info(f"[데모] 샘플 URL: '{target_url}', 키워드: {', '.join(target_keywords)}")

    logger.info(f"[시작] EchoSphere Sentinel이 '{target_url}' 감시를 시작합니다. (키워드: {', '.join(target_keywords) or '없음'})\n")

    content = fetch_content(target_url)
    if not content:
        logger.error("[종료] 콘텐츠를 가져올 수 없어 분석을 종료합니다.")
        return

    sentiment_data = analyze_sentiment(content, target_keywords)
    alert_message_parts = []
    
    # 민심 변화 감지 로직
    polarity = sentiment_data.get('overall_polarity', 0.0)
    # 상위 단어는 최소 1개 이상 있을 때만 포맷팅
    top_words_str = ', '.join([f"'{w}'({c})" for w, c in sentiment_data.get('top_words', [])[:3]]) if sentiment_data.get('top_words') else '없음'

    if polarity < -0.2: 
        alert_message_parts.append(f"🚨 강한 부정적 여론 감지! 극성: {polarity:.2f}\n주요 언급: {top_words_str}")
    elif polarity > 0.5: 
        alert_message_parts.append(f"🎉 매우 긍정적 여론 감지! 극성: {polarity:.2f}\n주요 언급: {top_words_str}")
    
    # 키워드 언급 급증 감지 (최소 1회 언급 또는 5회 이상 언급)
    hot_keywords = [k for k, c in sentiment_data.get('keyword_counts', {}).items() if c >= 5 or (k.lower() in [tk.lower() for tk in target_keywords] and c > 0)]
    if hot_keywords:
        alert_message_parts.append(f"🔥 특정 키워드 언급 급증/감지: {', '.join(hot_keywords)}")

    alert_message = "\n---\n".join(alert_message_parts)

    if alert_message:
        logger.info(f"\n[감지] 민심 변화 감지! 알림 메시지:\n---\n{alert_message}\n---")
        send_alert(alert_message, webhook_url)
    else:
        logger.info("\n[감지] 특별한 민심 변화는 감지되지 않았습니다.")

    # 최종 보고서 생성 및 저장
    generate_report({"url": target_url, "sentiment": sentiment_data, "alert_message": alert_message})

    logger.info("\n[팁] 이 스크립트를 주기적으로 실행하여 민심 변화를 추적하세요. (예: Linux cron, Windows 작업 스케줄러)")
    logger.info("      예시: 0 9 * * * python /path/to/echosphere_sentinel.py 'http://your-target-url.com' --keywords '주력분야' --webhook 'YOUR_WEBHOOK_URL'")
    logger.info("[종료] EchoSphere Sentinel 작동을 마칩니다.")

if __name__ == "__main__":
    main()
