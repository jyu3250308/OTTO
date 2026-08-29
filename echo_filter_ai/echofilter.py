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

# --- 상수 및 설정 ---
TELEGRAM_BOT_TOKEN_PLACEHOLDER = "YOUR_TELEGRAM_BOT_TOKEN"
OUTPUT_WARNINGS_FILE = "context_warnings.txt"
OUTPUT_REPORT_FILE = "distortion_report.txt"
DEFAULT_STOPWORDS = set(["is", "a", "the", "and", "of", "to", "in", "for", "on", "with", "as", "at", "by", "from", "it", "that", "this", "will", "be", "are", "have", "has", "he", "she", "we", "you", "they", "an", "or", "not", "but", "can", "do"])

def analyze_original_intent(content: str) -> dict:
    """원본 콘텐츠의 핵심 의도를 분석하여 키워드와 길이를 반환합니다."""
    words = re.findall(r'\b\w+\b', content.lower())
    meaningful_words = [word for word in words if word not in DEFAULT_STOPWORDS and len(word) > 2]
    top_keywords = [word for word, count in Counter(meaningful_words).most_common(10)]
    return {"keywords": set(top_keywords), "original_text_length": len(content)}

def detect_context_distortion(original_intent: dict, monitored_content: str) -> dict:
    """모니터링된 콘텐츠에서 원본 의도의 왜곡 징후를 감지합니다."""
    monitored_words = set(re.findall(r'\b\w+\b', monitored_content.lower()))
    missing_keywords = original_intent["keywords"] - monitored_words
    distortion_indicators = set(["fake", "hoax", "lie", "misleading", "false", "propaganda", "scam", "deceive", "manipulate", "unverified", "rumor"])
    detected_distortions = distortion_indicators.intersection(monitored_words)
    
    content_length_ratio = len(monitored_content) / original_intent["original_text_length"] if original_intent["original_text_length"] > 0 else 0
    if content_length_ratio < 0.3 and len(missing_keywords) > 3:
        missing_keywords.add("context_stripped_due_to_brevity")
    
    if missing_keywords or detected_distortions:
        return {"is_distorted": True, "missing_keywords": list(missing_keywords),
                "distortion_indicators_found": list(detected_distortions),
                "monitored_sample": monitored_content[:200] + ('...' if len(monitored_content) > 200 else '')}
    return {"is_distorted": False}

def send_alert(message: str):
    """왜곡 경고 메시지를 출력하고 파일에 기록합니다."""
    print(f"\n!!! 컨텍스트 왜곡 경고 !!!\n{message}")
    try:
        with open(OUTPUT_WARNINGS_FILE, "a", encoding="utf-8") as f: f.write(f"{message}\n---\n")
        print(f"[로그] 경고 메시지가 '{os.path.abspath(OUTPUT_WARNINGS_FILE)}'에 기록되었습니다.")
    except IOError as e: print(f"[오류] 경고 파일을 기록할 수 없습니다: {e}")
    # if TELEGRAM_BOT_TOKEN_PLACEHOLDER != "YOUR_TELEGRAM_BOT_TOKEN":
    #     try: requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN_PLACEHOLDER}/sendMessage", json={'chat_id': 'YOUR_CHAT_ID', 'text': message}, timeout=5)
    #     except requests.exceptions.RequestException as e: print(f"[오류] 텔레그램 알림 전송 실패: {e}")

def fetch_content_from_url(url: str) -> str:
    """URL에서 텍스트 콘텐츠를 가져옵니다."""
    print(f"[진행] URL에서 콘텐츠를 가져오는 중: {url}")
    try:
        response = requests.get(url, timeout=10); response.raise_for_status()
        cleaned_text = ' '.join(re.sub(r'<[^>]+>', '', response.text).split())
        print(f"[성공] URL 콘텐츠 가져오기 완료. 길이: {len(cleaned_text)} 문자.")
        return cleaned_text
    except requests.exceptions.Timeout: print(f"[오류] {url} 에서 콘텐츠 가져오기 시간 초과.")
    except requests.exceptions.RequestException as e: print(f"[오류] {url} 에서 콘텐츠를 가져올 수 없습니다: {e}")
    return ""

def get_original_content(source: str) -> str:
    """원본 콘텐츠를 파일에서 읽거나 직접 문자열로 사용합니다."""
    if not source: return ""
    if os.path.exists(source):
        try:
            with open(source, 'r', encoding='utf-8') as f: content = f.read()
            print(f"[정보] 파일에서 원본 콘텐츠 로드 완료: '{source}' (길이: {len(content)} 문자)")
            return content
        except (IOError, UnicodeDecodeError) as e: print(f"[오류] 원본 콘텐츠 파일 읽기 실패 '{source}': {e}")
    else:
        print(f"[정보] 제공된 문자열을 원본 콘텐츠로 사용 (길이: {len(source)} 문자)")
        return source
    return ""

def parse_monitor_targets(monitor_args: list) -> list:
    """ArgumentParser에서 받은 모니터링 대상을 파싱합니다."""
    targets = []
    for arg in monitor_args:
        if arg.startswith("url:"): targets.append({"type": "url", "value": arg[4:]})
        elif arg.startswith("text:"): targets.append({"type": "text", "value": arg[5:]})
        else: print(f"[경고] 알 수 없는 모니터링 대상 형식: '{arg}'. 'url:' 또는 'text:'로 시작해야 합니다.")
    return targets

def main():
    parser = argparse.ArgumentParser(description="EchoFilter: 컨텍스트 왜곡 모니터링 AI.")
    parser.add_argument('--original', type=str, help='원본 콘텐츠 텍스트 또는 텍스트 파일 경로.')
    parser.add_argument('--monitor', nargs='*', default=[], help='모니터링할 대상 목록. 형식: "url:http://example.com" 또는 "text:Some content".')
    args = parser.parse_args()

    if not args.original and not args.monitor:
        print("\n[정보] 원본 콘텐츠나 모니터링 대상이 제공되지 않아 데모 모드로 실행합니다.\n본인의 데이터를 사용하려면: python echofilter.py --original '원본 텍스트' --monitor 'url:http://example.com' 'text:변형된 텍스트'\n")
        original_content = "우리 회사는 지속 가능한 관행을 실천하고, 탄소 발자국을 줄이며, 지역 사회를 지원하기 위해 노력합니다. 우리는 투명성과 윤리적 소싱을 믿습니다."
        monitor_targets = [{"type": "url", "value": "https://www.nasa.gov/science-research/earth-science/"},
                           {"type": "text", "value": "이 회사는 친환경적이라고 주장하지만, 모두 가짜 PR입니다. 그들은 단지 당신의 돈을 원하고 환경에는 관심이 없습니다. 전형적인 기업의 거짓말입니다."},
                           {"type": "text", "value": "지속 가능한 관행은 미래에 중요하며, 많은 회사들이 이를 채택하고 있습니다. 일부는 더 나아가 지역 사회를 지원하기도 합니다."}]
    else:
        original_content = get_original_content(args.original)
        monitor_targets = parse_monitor_targets(args.monitor)

    if not original_content: print("[오류] 분석할 원본 콘텐츠가 없습니다. 종료합니다."); return
    if not monitor_targets: print("[정보] 모니터링 대상이 지정되지 않았습니다. 확인할 내용이 없습니다."); return

    print(f"\n[진행] 원본 의도를 분석 중...")
    original_intent = analyze_original_intent(original_content)
    print(f"[성공] 핵심 키워드 식별 완료: {', '.join(original_intent['keywords'])}")
    
    report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(OUTPUT_REPORT_FILE, "w", encoding="utf-8") as report_f:
            report_f.write(f"EchoFilter 컨텍스트 왜곡 보고서\n보고서 생성 일시: {report_timestamp}\n원본 콘텐츠 핵심 키워드: {', '.join(original_intent['keywords'])}\n\n--- 모니터링 결과 ---\n")
            for i, target in enumerate(monitor_targets):
                source_id = f"대상 {i+1} ({target['type']}: {target['value'][:70]}...)" if len(target['value']) > 70 else f"대상 {i+1} ({target['type']}: {target['value']})"
                print(f"\n[진행] {source_id} 모니터링 중...")
                monitored_text = fetch_content_from_url(target["value"]) if target["type"] == "url" else target["value"]
                if not monitored_text: print(f"[경고] '{source_id}'에 대해 빈 콘텐츠가 감지되어 건너뜁니다."); report_f.write(f"[경고] 건너뜀 (빈 콘텐츠): {source_id}\n---\n"); continue

                distortion_result = detect_context_distortion(original_intent, monitored_text)
                if distortion_result["is_distorted"]:
                    alert_msg = f"삐빅! 컨텍스트 경고!\n원본 의도 왜곡 징후 감지: {source_id}\n  - 감지된 왜곡: {', '.join(distortion_result['distortion_indicators_found'] + distortion_result['missing_keywords'])}\n  - 변형된 맥락 샘플: '{distortion_result["monitored_sample"]}'"
                    send_alert(alert_msg)
                    report_f.write(f"[왜곡 감지] {source_id}\n  - 샘플: {distortion_result['monitored_sample']}\n  - 누락된 키워드: {', '.join(distortion_result['missing_keywords'])}\n  - 왜곡 지표: {', '.join(distortion_result['distortion_indicators_found'])}\n---\n")
                else:
                    print(f"[정보] {source_id} 에서 유의미한 왜곡이 감지되지 않았습니다.")
                    report_f.write(f"[왜곡 없음] {source_id}\n---\n")
        print(f"\n--- EchoFilter 스캔 완료 ---\n컨텍스트 경고 알림: {os.path.abspath(OUTPUT_WARNINGS_FILE)}\n왜곡 보고서: {os.path.abspath(OUTPUT_REPORT_FILE)}\n지속적인 모니터링을 위해 스크립트를 주기적으로 실행하도록 예약하는 것을 고려하세요.")
    except IOError as e: print(f"[치명적 오류] 보고서 파일을 기록할 수 없습니다 '{OUTPUT_REPORT_FILE}': {e}")

if __name__ == "__main__":
    main()