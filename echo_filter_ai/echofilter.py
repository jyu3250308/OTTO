# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import os
import requests
import re
from collections import Counter
from datetime import datetime

# --- 상수 및 설정 --- #
TELEGRAM_BOT_TOKEN_PLACEHOLDER = "YOUR_TELEGRAM_BOT_TOKEN" # 선택 사항: 실제 알림을 위해 토큰으로 교체하세요
OUTPUT_WARNINGS_FILE = "context_warnings.txt"
OUTPUT_REPORT_FILE = "distortion_report.txt"

# --- 핵심 AI 기능 --- #
def analyze_original_intent(content: str) -> dict:
    """원본 콘텐츠의 핵심 의도를 분석하여 키워드와 길이를 반환합니다."""
    # 텍스트에서 단어를 추출하고 소문자로 변환
    words = re.findall(r'\b\w+\b', content.lower())
    
    # 기본 영어 불용어 (stopwords) 목록
    stopwords = set(["is", "a", "the", "and", "of", "to", "in", "for", "on", "with", "as", "at", "by", "from", "it", "that", "this", "will", "be", "are", "have", "has", "he", "she", "we", "you", "they", "an", "or", "not", "but", "can", "do", "said", "say", "about", "our", "my", "your", "their", "one", "all", "so", "up", "out", "if", "what", "when", "where", "why", "how", "who", "which", "him", "her", "its", "them", "then", "there", "these", "those", "very", "just", "only", "much", "more", "most", "many", "any", "some", "such", "no", "nor", "don", "t", "won", "didn", "was", "were", "had", "done", "doing", "does", "did", "been", "being", "both", "each", "few", "other", "through", "throughout", "until", "while", "within", "without", "unless", "until", "upon", "whose", "yet", "although", "because", "before", "consequently", "hence", "however", "indeed", "instead", "moreover", "nevertheless", "otherwise", "since", "therefore", "thus", "whereas", "whereby", "whether", "whilst", "worth", "would", "should", "could", "might", "must", "shall", "get", "go", "make", "take", "see", "come", "know", "think", "look", "want", "give", "use", "find", "tell", "ask", "work", "seem", "feel", "try", "leave", "call", "put", "mean", "keep", "let", "begin", "help", "talk", "start", "show", "hear", "play", "run", "move", "like", "love", "hate", "need", "agree", "believe", "expect", "hope", "learn", "study", "write", "read", "follow", "understand", "remember", "forget", "decide", "plan", "meet", "send", "bring", "build", "fall", "grow", "hold", "lose", "pay", "return", "sit", "stand", "turn", "wait", "walk", "watch", "win", "lose", "meet", "open", "close", "offer", "pass", "pull", "push", "reach", "sell", "spend", "teach", "travel", "visit", "wear", "wish", "wonder", "worry", "explain", "imagine", "improve", "increase", "reduce", "provide", "receive", "report", "require", "request", "respond", "reveal", "seek", "serve", "share", "solve", "state", "suggest", "support", "survive", "tend", "test", "thank", "touch", "treat", "trust", "value", "view", "vote"])
    
    # 불용어를 제거하고 길이가 2보다 긴 유의미한 단어만 필터링
    meaningful_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    # 가장 자주 등장하는 상위 10개 키워드 추출
    top_keywords = [word for word, count in Counter(meaningful_words).most_common(10)]
    return {"keywords": set(top_keywords), "original_text_length": len(content)}

def detect_context_distortion(original_intent: dict, monitored_content: str) -> dict:
    """모니터링된 콘텐츠에서 원본 의도의 왜곡 징후를 감지합니다."""
    monitored_words = set(re.findall(r'\b\w+\b', monitored_content.lower()))
    missing_keywords = original_intent["keywords"] - monitored_words
    
    # 왜곡 지표 (확장 가능)
    distortion_indicators = set(["fake", "hoax", "lie", "misleading", "false", "propaganda", "scam", "deceive", "manipulate", "unverified", "rumor"])
    detected_distortions = distortion_indicators.intersection(monitored_words)
    
    # 텍스트 길이 감소를 통한 맥락 소실 감지
    content_length_ratio = len(monitored_content) / original_intent["original_text_length"] if original_intent["original_text_length"] > 0 else 0
    if content_length_ratio < 0.3 and len(missing_keywords) > 3:
        missing_keywords.add("context_stripped_due_to_brevity")
    
    if missing_keywords or detected_distortions:
        return {
            "is_distorted": True,
            "missing_keywords": list(missing_keywords),
            "distortion_indicators_found": list(detected_distortions),
            "monitored_sample": monitored_content[:200] + ('...' if len(monitored_content) > 200 else '')
        }
    return {"is_distorted": False}

def send_alert(message: str):
    """왜곡 경고 메시지를 출력하고 파일에 기록합니다."""
    print(f"\n!!! 컨텍스트 왜곡 경고 !!!\n{message}")
    try:
        with open(OUTPUT_WARNINGS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{message}\n---\n")
        print(f"[로그] 경고 메시지가 '{os.path.abspath(OUTPUT_WARNINGS_FILE)}'에 기록되었습니다.")
    except IOError as e:
        print(f"[오류] 경고 파일을 기록할 수 없습니다: {e}")
    
    # 선택 사항: 텔레그램/이메일 전송 구현 (TELEGRAM_BOT_TOKEN_PLACEHOLDER가 설정된 경우)
    # if TELEGRAM_BOT_TOKEN_PLACEHOLDER != "YOUR_TELEGRAM_BOT_TOKEN":
    #     try:
    #         requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN_PLACEHOLDER}/sendMessage", json={'chat_id': 'YOUR_CHAT_ID', 'text': message}, timeout=5)
    #         print("[로그] 텔레그램 알림을 성공적으로 보냈습니다.")
    #     except requests.exceptions.RequestException as e:
    #         print(f"[오류] 텔레그램 알림 전송 실패: {e}")

def fetch_content_from_url(url: str) -> str:
    """URL에서 텍스트 콘텐츠를 가져옵니다."""
    try:
        print(f"[진행] URL에서 콘텐츠를 가져오는 중: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # 4xx/5xx 응답 코드에 대해 예외 발생
        
        # 기본적인 HTML 태그 제거 및 공백 정규화
        text = re.sub(r'<[^>]+>', '', response.text)
        cleaned_text = ' '.join(text.split())
        print(f"[성공] URL 콘텐츠 가져오기 완료. 길이: {len(cleaned_text)} 문자.")
        return cleaned_text
    except requests.exceptions.Timeout:
        print(f"[오류] {url} 에서 콘텐츠를 가져오는 데 시간 초과.\n  - URL 응답이 10초를 초과했습니다.")
    except requests.exceptions.RequestException as e:
        print(f"[오류] {url} 에서 콘텐츠를 가져올 수 없습니다: {e}")
    return ""

def get_original_content(original_source: str) -> str:
    """원본 콘텐츠를 파일에서 읽거나 직접 문자열로 사용합니다."""
    if not original_source: return ""
    
    if os.path.exists(original_source):
        try:
            with open(original_source, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"[정보] 파일에서 원본 콘텐츠 로드 완료: '{original_source}' (길이: {len(content)} 문자)")
            return content
        except IOError as e:
            print(f"[오류] 원본 콘텐츠 파일을 읽을 수 없습니다 '{original_source}': {e}")
        except UnicodeDecodeError:
            print(f"[오류] 원본 콘텐츠 파일의 인코딩 문제: '{original_source}'. UTF-8인지 확인하세요.")
        return ""
    else:
        print(f"[정보] 제공된 문자열을 원본 콘텐츠로 사용 (길이: {len(original_source)} 문자)")
        return original_source

def parse_monitor_targets(monitor_args: list) -> list:
    """ArgumentParser에서 받은 모니터링 대상을 파싱합니다."""
    targets = []
    for arg in monitor_args:
        if arg.startswith("url:"):
            targets.append({"type": "url", "value": arg[4:]})
        elif arg.startswith("text:"):
            targets.append({"type": "text", "value": arg[5:]})
        else:
            print(f"[경고] 알 수 없는 모니터링 대상 형식: '{arg}'. 'url:' 또는 'text:'로 시작해야 합니다.")
    return targets

def main():
    parser = argparse.ArgumentParser(description="EchoFilter: 컨텍스트 왜곡 모니터링 AI.")
    parser.add_argument('--original', type=str, help='원본 콘텐츠 텍스트 또는 텍스트 파일 경로.')
    parser.add_argument('--monitor', nargs='*', default=[], help='모니터링할 대상 목록. 형식: "url:http://example.com" 또는 "text:Some content".')
    args = parser.parse_args()

    original_content = ""
    monitor_targets = []

    # --- 데모 폴백 로직 --- #
    if not args.original and not args.monitor:
        print("\n[정보] 원본 콘텐츠나 모니터링 대상이 제공되지 않았습니다. 데모 모드로 실행합니다.\n")
        print("       본인의 데이터를 사용하려면 다음과 같이 실행하세요: python echofilter.py --original '원본 텍스트' --monitor 'url:http://example.com' 'text:변형된 텍스트'\n")
        original_content = "우리 회사는 지속 가능한 관행을 실천하고, 탄소 발자국을 줄이며, 지역 사회를 지원하기 위해 노력합니다. 우리는 투명성과 윤리적 소싱을 믿습니다."
        monitor_targets.append({"type": "url", "value": "https://www.nasa.gov/science-research/earth-science/"})
        monitor_targets.append({"type": "text", "value": "이 회사는 친환경적이라고 주장하지만, 모두 가짜 PR입니다. 그들은 단지 당신의 돈을 원하고 환경에는 관심이 없습니다. 전형적인 기업의 거짓말입니다."})
        monitor_targets.append({"type": "text", "value": "지속 가능한 관행은 미래에 중요하며, 많은 회사들이 이를 채택하고 있습니다. 일부는 더 나아가 지역 사회를 지원하기도 합니다."})
    else:
        original_content = get_original_content(args.original)
        monitor_targets = parse_monitor_targets(args.monitor)

    if not original_content:
        print("[오류] 분석할 원본 콘텐츠가 없습니다. 종료합니다.")
        return

    if not monitor_targets:
        print("[정보] 모니터링 대상이 지정되지 않았습니다. 확인할 내용이 없습니다.")
        return

    print(f"\n[진행] 원본 의도를 분석 중...")
    original_intent = analyze_original_intent(original_content)
    print(f"[성공] 핵심 키워드 식별 완료: {', '.join(original_intent['keywords'])}")
    
    all_distortions_found = []
    report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(OUTPUT_REPORT_FILE, "w", encoding="utf-8") as report_f:
            report_f.write("EchoFilter 컨텍스트 왜곡 보고서\n")
            report_f.write(f"보고서 생성 일시: {report_timestamp}\n")
            report_f.write(f"원본 콘텐츠 핵심 키워드: {', '.join(original_intent['keywords'])}\n\n")
            report_f.write("--- 모니터링 결과 ---\n")

            for i, target in enumerate(monitor_targets):
                source_id = f"대상 {i+1} ({target['type']}: {target['value'][:70]}...)" if len(target['value']) > 70 else f"대상 {i+1} ({target['type']}: {target['value']})"
                print(f"\n[진행] {source_id} 모니터링 중...")
                monitored_text = ""
                if target["type"] == "url":
                    monitored_text = fetch_content_from_url(target["value"])
                else: # "text"
                    monitored_text = target["value"]
                
                if not monitored_text:
                    print(f"[경고] '{source_id}'에 대해 빈 콘텐츠가 감지되어 건너뜁니다.")
                    report_f.write(f"[경고] 건너뜀 (빈 콘텐츠): {source_id}\n---\n")
                    continue

                distortion_result = detect_context_distortion(original_intent, monitored_text)
                
                if distortion_result["is_distorted"]:
                    alert_message = (
                        f"삐빅! 컨텍스트 경고!\n" +
                        f"원본 의도 왜곡 징후 감지: {source_id}\n" +
                        f"  - 감지된 왜곡: " + ", ".join(distortion_result["distortion_indicators_found"] + distortion_result["missing_keywords"]) + "\n" +
                        f"  - 변형된 맥락 샘플: '{distortion_result["monitored_sample"]}'\n" +
                        f"  - 원본 키워드 불일치: {', '.join(distortion_result['missing_keywords']) if distortion_result['missing_keywords'] else '없음'}\n"
                    )
                    send_alert(alert_message)
                    all_distortions_found.append(distortion_result)
                    
                    report_f.write(f"[왜곡 감지] {source_id}\n")
                    report_f.write(f"  - 샘플: {distortion_result['monitored_sample']}\n")
                    report_f.write(f"  - 누락된 키워드: {', '.join(distortion_result['missing_keywords'])}\n")
                    report_f.write(f"  - 왜곡 지표: {', '.join(distortion_result['distortion_indicators_found'])}\n---\n")
                else:
                    print(f"[정보] {source_id} 에서 유의미한 왜곡이 감지되지 않았습니다.")
                    report_f.write(f"[왜곡 없음] {source_id}\n---\n")
        
        print("\n--- EchoFilter 스캔 완료 ---")
        print(f"컨텍스트 경고 알림은 다음 파일에 저장되었습니다: {os.path.abspath(OUTPUT_WARNINGS_FILE)}")
        print(f"왜곡 보고서는 다음 파일에 저장되었습니다: {os.path.abspath(OUTPUT_REPORT_FILE)}")
        print("왜곡 보고서(distortion_report.txt)에서 '익명 컨텍스트 왜곡 확산 패턴 보고서'를 검토할 수 있습니다.")
        print("지속적인 모니터링을 위해 이 스크립트를 주기적으로 실행하도록 예약하는 것을 고려하세요 (예: Linux의 cron 또는 Windows의 작업 스케줄러).")

    except IOError as e:
        print(f"[치명적 오류] 보고서 파일을 기록할 수 없습니다 '{OUTPUT_REPORT_FILE}': {e}")

if __name__ == "__main__":
    main()
