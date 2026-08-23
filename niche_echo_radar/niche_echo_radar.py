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
import re
import csv
from datetime import datetime
from collections import Counter

# --- Constants ---
OUTPUT_FILENAME_PREFIX = "niche_echo_vacuums"
ALERT_THRESHOLD = 2 # Minimum frequency to be considered a 'high-potential vacuum'

# --- Utility Functions ---
def load_conversations(file_path):
    """지정된 파일에서 대화 내용을 로드하거나, 파일이 없으면 샘플 데이터를 반환합니다."""
    if file_path and os.path.exists(file_path):
        print(f"[NicheEcho] 대화 파일을 로드합니다: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"[NicheEcho ERROR] 파일을 찾을 수 없습니다: {file_path}")
            return None
        except Exception as e:
            print(f"[NicheEcho ERROR] 파일 로드 중 오류 발생: {e}")
            return None
    else:
        print("[NicheEcho] 입력 파일이 제공되지 않았거나 파일을 찾을 수 없습니다.")
        print("       데모용 샘플 데이터를 사용하여 실행합니다.")
        print("       본인 데이터를 사용하려면: python niche_echo_radar.py -i your_conversations.txt -k '파이썬,데이터 과학'")
        return (
            "How can I optimize Python performance for large datasets? I'm struggling with it.\n"
            "What's the best way to handle memory in Python for data science projects?\n"
            "I need a good resource for advanced Python data structures. My current code is slow.\n"
            "Is there a missing feature in Pandas for real-time analytics? It's a common problem.\n"
            "Finding solutions for fast data processing in Python is tough. Any advice on scaling?\n"
            "I can't find clear content on distributed computing with Python for machine learning. This is a vacuum!\n"
            "My python data pipeline is too slow. What's the best way to speed it up?\n"
            "Where can I find examples of efficient Python code for numerical operations?\n"
            "Need advice on multiprocessing in Python for data processing. Existing tutorials are vague.\n"
            "The problem with current Python ML frameworks is often performance on massive scale.\n"
            "What are the best practices for content marketing in the B2B SaaS niche?\n"
            "How to identify content gaps in a competitive market? Always a challenge.\n"
            "I'm looking for unique content ideas for my blog. Need fresh perspectives.\n"
        )

def analyze_conversations(conversations_text, niche_keywords):
    """대화 내용에서 지정된 키워드와 결합된 잠재적 콘텐츠 니치 진공을 분석합니다."""
    print(f"[NicheEcho] 다음 니치 키워드를 사용하여 대화를 분석합니다: {', '.join(niche_keywords)}")
    
    # 해결되지 않은 니즈나 질문을 나타내는 키워드/구문 패턴
    need_patterns = [
        r'how to', r'what is the best way to', r'problem with', r'struggling with',
        r'need advice on', r'solution for', r'missing feature', r'can\'t find',
        r'looking for', r'where can i find', r'tough to find', r'vacuum'
    ]
    combined_patterns_regex = re.compile('|'.join(need_patterns), re.IGNORECASE)
    
    detected_vacuums = Counter()
    # 문장 단위로 분리하고 소문자로 변환하여 분석합니다.
    sentences = re.split(r'[.!?]\s*', conversations_text.lower())

    for sentence in sentences:
        # 문장이 니치 키워드를 포함하는지 확인합니다.
        has_niche_keyword = any(kw in sentence for kw in niche_keywords)
        # 문장이 해결되지 않은 니즈 패턴을 포함하는지 확인합니다.
        has_need_pattern = combined_patterns_regex.search(sentence)

        if has_niche_keyword and has_need_pattern:
            # 니치 키워드와 니즈 패턴이 모두 포함된 문장을 잠재적 진공으로 기록합니다.
            vacuum_phrase = sentence.strip()
            if vacuum_phrase:
                detected_vacuums[vacuum_phrase] += 1
    
    return detected_vacuums

def save_results(vacuums):
    """감지된 콘텐츠 니치 진공을 CSV 파일로 저장합니다."""
    filepath = f"{OUTPUT_FILENAME_PREFIX}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    print(f"[NicheEcho] 감지된 콘텐츠 니치 진공을 저장합니다: {filepath}")
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Content Niche Vacuum", "Frequency"])
            for vacuum, count in sorted(vacuums.items(), key=lambda item: item[1], reverse=True):
                writer.writerow([datetime.now().isoformat(), vacuum, count])
        print(f"[NicheEcho] 결과가 성공적으로 저장되었습니다: {filepath}")
    except Exception as e:
        print(f"[NicheEcho ERROR] CSV 파일 저장 중 오류 발생: {e}")

def send_alert(vacuum_item):
    """고빈도 콘텐츠 니치 진공에 대해 경고를 보냅니다 (현재는 콘솔 출력)."""
    # Slack, Email 등 외부 시스템과 통합하려면 여기에 로직을 추가하세요.
    # 예: import requests, requests.post(os.getenv('SLACK_WEBHOOK_URL', 'YOUR_SLACK_WEBHOOK'), json=payload)
    print(f"[NicheEcho ALERT] 고잠재력 콘텐츠 니치 진공 감지: '{vacuum_item[0]}' (빈도: {vacuum_item[1]})\n")

# --- Main Execution ---
def main():
    """NicheEcho Radar의 메인 실행 함수입니다."""
    parser = argparse.ArgumentParser(
        description="NicheEcho Radar: 대화에서 콘텐츠 니치 진공을 스캔합니다."
    )
    parser.add_argument(
        '-i', '--input_file', type=str,
        help="커뮤니티 대화가 포함된 텍스트 파일 경로."
    )
    parser.add_argument(
        '-k', '--niche_keywords', type=str, default='python,data science,content marketing',
        help="콘텐츠 니치를 정의하는 쉼표로 구분된 키워드 목록 (예: 'python,ai,marketing')."
    )
    args = parser.parse_args()

    # 니치 키워드 목록을 준비합니다.
    niche_keywords_list = [kw.strip().lower() for kw in args.niche_keywords.split(',') if kw.strip()]
    if not niche_keywords_list:
        print("[NicheEcho ERROR] 하나 이상의 니치 키워드를 제공해야 합니다.")
        return

    print("\n--- NicheEcho Radar: 콘텐츠 니치 진공 스캐너 --- ")
    print(f"[NicheEcho] 분석을 시작합니다 (키워드: {', '.join(niche_keywords_list)}).")

    try:
        # 1. 대화 로드
        conversations_text = load_conversations(args.input_file)
        if not conversations_text:
            print("[NicheEcho] 분석할 대화 내용이 없습니다. 종료합니다.")
            return

        # 2. 대화 분석
        detected_vacuums = analyze_conversations(conversations_text, niche_keywords_list)

        if detected_vacuums:
            print("\n--- 감지된 잠재적 콘텐츠 니치 진공 --- ")
            high_potential_vacuums = []
            for vacuum, count in sorted(detected_vacuums.items(), key=lambda item: item[1], reverse=True):
                print(f"  - '{vacuum}' (빈도: {count})")
                if count >= ALERT_THRESHOLD:
                    high_potential_vacuums.append((vacuum, count))
            
            # 3. 고잠재력 진공 경고
            if high_potential_vacuums:
                print("\n--- 긴급 경고: 고잠재력 콘텐츠 니치 진공 --- ")
                for item in high_potential_vacuums:
                    send_alert(item)
            else:
                print("\n[NicheEcho] 임계값 이상인 긴급 콘텐츠 니치 진공은 감지되지 않았습니다.")

            # 4. 결과 저장
            save_results(detected_vacuums)
        else:
            print("[NicheEcho] 지정된 니치 및 패턴에 대한 콘텐츠 진공을 찾지 못했습니다.")

    except Exception as e:
        print(f"[NicheEcho ERROR] 예기치 않은 오류가 발생했습니다: {e}")

    print("\n--- NicheEcho Radar 작업 완료 --- ")
    print("팁: 이 스크립트를 cron (Linux) 또는 작업 스케줄러 (Windows)를 사용하여 매일 실행하여 추세를 모니터링하세요.")

if __name__ == "__main__":
    main()