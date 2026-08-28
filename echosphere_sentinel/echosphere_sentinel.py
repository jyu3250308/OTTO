# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행 시 한글 윈도우에서 UnicodeEncodeError 방지. 삭제 금지.
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import argparse
import datetime
import os

def fetch_content(url: str) -> str | None:
    """지정된 URL에서 HTML을 가져와 텍스트 콘텐츠를 추출합니다."""
    print(f"[진행] URL '{url}' 콘텐츠 가져오는 중...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        for script_or_style in soup(['script', 'style']): script_or_style.decompose() # 불필요 태그 제거
        text = soup.get_text(separator=' ', strip=True)
        
        if not text.strip():
            print(f"[경고] URL '{url}' 에서 유효한 텍스트 콘텐츠를 찾을 수 없습니다.")
            return None

        print(f"[성공] URL '{url}' 콘텐츠 추출 완료. (약 {len(text.split())} 단어)")
        return text
    except requests.exceptions.Timeout: print(f"[에러] URL '{url}' 요청 시간 초과."); return None
    except requests.exceptions.HTTPError as e: print(f"[에러] URL '{url}' HTTP 오류: {e.response.status_code} {e.response.reason}"); return None
    except requests.exceptions.ConnectionError as e: print(f"[에러] URL '{url}' 연결 실패: {e}"); return None
    except requests.exceptions.RequestException as e: print(f"[에러] URL '{url}' 예상치 못한 요청 오류: {e}"); return None
    except Exception as e: print(f"[에러] URL '{url}' 콘텐츠 처리 중 오류: {e}"); return None

def analyze_sentiment(text: str, target_keywords: list[str] | None = None) -> dict:
    """텍스트의 감성을 분석하고 키워드 언급을 추적합니다."""
    print("[진행] 텍스트 감성 및 키워드 분석 시작...")
    if not text.strip():
        print("[경고] 분석할 텍스트가 비어있습니다. 빈 감성 데이터 반환.")
        return {"overall_polarity": 0.0, "overall_subjectivity": 0.0, "keyword_counts": {}, "top_words": []}
        
    try:
        blob = TextBlob(text)
        overall_polarity = blob.sentiment.polarity
        overall_subjectivity = blob.sentiment.subjectivity

        keyword_counts = {kw.lower(): text.lower().count(kw.lower()) for kw in target_keywords} if target_keywords else {}

        stop_words = TextBlob('').words.stop_words # TextBlob 기본 불용어
        words = [word.lower() for word in blob.words if len(word) > 2 and not word.isdigit() and word.lower() not in stop_words]
        word_freq = {word: words.count(word) for word in set(words)}
        top_words = sorted(word_freq.items(), key=lambda item: item[1], reverse=True)[:10] # 상위 10개
        
        print(f"[완료] 감성 분석 완료. 극성: {overall_polarity:.2f}, 주관성: {overall_subjectivity:.2f}")
        return {"overall_polarity": overall_polarity, "overall_subjectivity": overall_subjectivity, "keyword_counts": keyword_counts, "top_words": top_words}
    except Exception as e: print(f"[에러] 텍스트 감성 분석 중 오류: {e}"); return {"overall_polarity": 0.0, "overall_subjectivity": 0.0, "keyword_counts": {}, "top_words": []}

def send_alert(message: str, webhook_url: str) -> None:
    """Slack/Telegram 웹훅을 통해 알림을 전송합니다."""
    if not webhook_url or "YOUR_SLACK_WEBHOOK" in webhook_url or "YOUR_TELEGRAM_WEBHOOK" in webhook_url:
        print("[경고] 유효한 웹훅 URL이 없어 알림을 전송하지 않습니다."); return

    print("[진행] 웹훅으로 알림 전송 시도 중...")
    payload = {"text": f"[EchoSphere Sentinel 알림]\n{message}"}
    try:
        requests.post(webhook_url, json=payload, timeout=7).raise_for_status()
        print("[성공] 웹훅 알림이 성공적으로 전송되었습니다.")
    except requests.exceptions.Timeout: print(f"[에러] 웹훅 알림 전송 시간 초과.")
    except requests.exceptions.HTTPError as e: print(f"[에러] 웹훅 서버 응답 오류: {e.response.status_code} {e.response.reason}")
    except requests.exceptions.RequestException as e: print(f"[에러] 웹훅 알림 전송 중 오류: {e}")
    except Exception as e: print(f"[에러] 웹훅 알림 전송 중 일반 오류: {e}")

def generate_report(data: dict, filename: str = "echosphere_report.txt") -> None:
    """분석 결과를 파일로 저장합니다."""
    report_path = os.path.join(os.getcwd(), filename)
    print(f"[진행] 분석 보고서를 '{report_path}' 에 저장 중...")
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"=== EchoSphere Sentinel 분석 보고서 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===\n\n")
            f.write(f"분석 대상 URL: {data.get('url', 'N/A')}\n")
            sentiment = data.get('sentiment', {})
            f.write(f"감성 극성 (Polarity): {sentiment.get('overall_polarity', 0.0):.2f} (1:긍정, -1:부정)\n")
            f.write(f"감성 주관성 (Subjectivity): {sentiment.get('overall_subjectivity', 0.0):.2f} (1:주관적, 0:객관적)\n\n")
            f.write("--- 키워드 언급 수 ---\n")
            kw_counts = sentiment.get('keyword_counts', {})
            f.write('\n'.join([f"- '{k}': {c}회" for k, c in sorted(kw_counts.items(), key=lambda item: item[1], reverse=True)]) if kw_counts else "추적된 키워드 없음.\n")
            f.write("\n\n--- 급부상하는 관심사 (상위 10개 단어) ---\n")
            top_words = sentiment.get('top_words', [])
            f.write('\n'.join([f"- '{w}': {c}회" for w, c in top_words]) if top_words else "분석된 상위 단어 없음.\n")
            f.write("\n\n--- 감지된 민심 변화 및 알림 ---\n")
            f.write(f"{data['alert_message']}\n" if data.get('alert_message') else "특별한 민심 변화 감지 안 됨.\n")
        print(f"[완료] 분석 보고서가 '{report_path}' 에 성공적으로 저장되었습니다.")
    except IOError as e: print(f"[에러] 보고서 파일 '{report_path}' 쓰기 실패: {e}")
    except Exception as e: print(f"[에러] 보고서 생성 중 오류: {e}")

def main():
    parser = argparse.ArgumentParser(description="온라인 커뮤니티 여론을 실시간 감시하는 EchoSphere Sentinel.")
    parser.add_argument("url", nargs='?', default=None, help="감시할 온라인 커뮤니티 URL (예: 블로그 댓글, 뉴스 기사)")
    parser.add_argument("--keywords", nargs='*', default=[], help="추적할 키워드 목록 (공백 구분). 예: --keywords '상품명' '불만'")
    parser.add_argument("--webhook", default="YOUR_SLACK_WEBHOOK_URL", help="알림을 받을 Slack 또는 Telegram 웹훅 URL")
    args = parser.parse_args()

    target_url = args.url
    target_keywords = args.keywords
    webhook_url = args.webhook

    if not target_url:
        print("\n[안내] URL 인자가 없어 샘플 데이터로 EchoSphere Sentinel 데모를 실행합니다.")
        print("       본인 URL 감시: python echosphere_sentinel.py 'http://your-url.com' --keywords '키워드1' --webhook 'YOUR_WEBHOOK_URL'\n")
        target_url = "https://www.yna.co.kr/view/AKR20240723145400009" # 연합뉴스 샘플 기사
        if not target_keywords: target_keywords = ['AI', '기술', '혁신'] # 샘플 키워드
        print(f"[데모] 샘플 URL: '{target_url}', 키워드: {', '.join(target_keywords)}")

    print(f"[시작] EchoSphere Sentinel이 '{target_url}' 감시를 시작합니다. (키워드: {', '.join(target_keywords) or '없음'})\n")

    content = fetch_content(target_url)
    if not content: print("[종료] 콘텐츠를 가져올 수 없어 분석을 종료합니다."); return

    sentiment_data = analyze_sentiment(content, target_keywords)
    alert_message_parts = []
    
    # 민심 변화 감지 로직
    polarity = sentiment_data.get('overall_polarity', 0.0)
    top_words_str = ', '.join([f"'{w}'({c})" for w, c in sentiment_data.get('top_words', [])[:3]])
    if polarity < -0.2: alert_message_parts.append(f"🚨 강한 부정적 여론 감지! 극성: {polarity:.2f}\n주요 언급: {top_words_str}")
    elif polarity > 0.5: alert_message_parts.append(f"🎉 매우 긍정적 여론 감지! 극성: {polarity:.2f}\n주요 언급: {top_words_str}")
    
    hot_keywords = [k for k, c in sentiment_data.get('keyword_counts', {}).items() if c >= 5 or (k in target_keywords and c > 0)]
    if hot_keywords: alert_message_parts.append(f"🔥 특정 키워드 언급 급증/감지: {', '.join(hot_keywords)}")

    alert_message = "\n---\n".join(alert_message_parts)

    if alert_message:
        print(f"\n[감지] 민심 변화 감지! 알림 메시지:\n---\n{alert_message}\n---")
        send_alert(alert_message, webhook_url)
    else: print("\n[감지] 특별한 민심 변화는 감지되지 않았습니다.")

    generate_report({"url": target_url, "sentiment": sentiment_data, "alert_message": alert_message})

    print("\n[팁] 이 스크립트를 주기적으로 실행하여 민심 변화를 추적하세요. (예: Linux cron, Windows 작업 스케줄러)\n")
    print("      예시: 0 9 * * * python /path/to/echosphere_sentinel.py 'http://your-target-url.com' --keywords '주력분야' --webhook 'YOUR_WEBHOOK_URL'")
    print("[종료] EchoSphere Sentinel 작동을 마칩니다.")

if __name__ == "__main__":
    main()