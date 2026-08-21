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
import datetime
from collections import Counter
import re # 단어 추출을 위한 정규식 모듈 추가

def analyze_content(content_list, main_topic="AI"): 
    """콘텐츠 목록을 분석하여 인기 주제의 과포화 및 미개척 서사 각도를 감지합니다."""
    print(f"\n[NarrativeBeacon AI] 🎯 주제 '{main_topic}'에 대한 콘텐츠 분석을 시작합니다. ({len(content_list)}개 항목)")
    
    if not content_list:
        print("[NarrativeBeacon AI] ⚠️ 분석할 콘텐츠가 없습니다. 빈 결과를 반환합니다.")
        return {
            "is_saturated": False,
            "common_narratives": {},
            "undiscovered_angles": {},
            "storyline_opportunities": {}
        }

    print("  - 텍스트에서 주요 단어를 추출하고 전처리 중입니다...")
    all_words = []
    for text in content_list:
        # 한글 및 영어 알파벳으로 구성된 단어만 추출하여 소문자로 변환
        words = re.findall(r'[가-힣a-zA-Z]+', text)
        all_words.extend([word.lower() for word in words if len(word) > 1]) # 1글자 단어는 무시

    if not all_words:
        print("[NarrativeBeacon AI] ⚠️ 추출된 유효 단어가 없습니다. 분석을 진행할 수 없습니다.")
        return {
            "is_saturated": False,
            "common_narratives": {},
            "undiscovered_angles": {},
            "storyline_opportunities": {}
        }

    word_counts = Counter(all_words)
    
    # 1. 인기 주제 및 과포화 패턴 감지
    # 긍정적이고 흔하며 일반적인 서사각을 나타내는 키워드 목록
    saturated_keywords = ["성공", "혁신", "미래", "발전", "가능성", "변화", "효율", "기회", "성장"]
    common_narratives = {
        kw: word_counts[kw] for kw in saturated_keywords if kw in word_counts
    }
    
    # 과포화 임계값: 인기 키워드 총 등장 횟수가 5회를 초과하면 과포화로 간주합니다. (조정 가능)
    is_topic_saturated = sum(common_narratives.values()) > 5 
    
    print(f"  - 인기 서사 패턴 분석 완료: {common_narratives}")
    if is_topic_saturated:
        print(f"  - 감지: 주제 '{main_topic}'의 일반적인 서사각(예: 성공, 혁신)이 과포화 상태일 수 있습니다.\n    (새로운 관점 모색 필요!)\n")
    else:
        print(f"  - 감지: 주제 '{main_topic}'의 일반적인 서사각은 아직 과포화되지 않았습니다.\n")

    # 2. 미개척 서사 각도 및 반대 관점 발굴
    # '도전', '윤리' 등 일반적으로 덜 다뤄지거나 비판적인 서사각을 나타내는 키워드 목록
    undiscovered_keywords = ["도전", "윤리", "부작용", "인간", "사회", "제한", "논란", "실패", "비판", "불균형", "소외"]
    undiscovered_angles = {
        kw: word_counts[kw] for kw in undiscovered_keywords if kw in word_counts
    }
    
    # 스토리라인 기회 포착 기준: 미개척 키워드가 1회 이상 3회 미만으로 등장한 경우
    # (너무 흔하지 않으면서도 존재하여 탐색할 가치가 있는 키워드) (조정 가능)
    storyline_opportunities = {
        kw: count for kw, count in undiscovered_angles.items() if count > 0 and count < 3
    }
    
    print(f"  - 미개척 서사 각도 분석 완료: {undiscovered_angles}")
    if storyline_opportunities:
        print(f"  - ✨ 발견: 다음은 탐색되지 않은 흥미로운 스토리라인 기회입니다: {list(storyline_opportunities.keys())}\n")
    else:
        print("  - 발견: 현재 시점에서 뚜렷한 미개척 스토리라인 기회는 보이지 않습니다.\n")
        
    print(f"[NarrativeBeacon AI] ✅ 주제 '{main_topic}'에 대한 콘텐츠 분석이 성공적으로 완료되었습니다.")
    return {
        "is_saturated": is_topic_saturated,
        "common_narratives": common_narratives,
        "undiscovered_angles": undiscovered_angles,
        "storyline_opportunities": storyline_opportunities
    }

def main():
    """NarrativeBeacon AI의 메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description="NarrativeBeacon AI: Detects saturated narrative patterns and uncovers hidden storyline angles in text content."
    )
    parser.add_argument(
        "--file", 
        type=str, 
        help="Path to a text file containing content (one article/paragraph per line) for analysis. Must be UTF-8 encoded."
    )
    parser.add_argument(
        "--topic", 
        type=str, 
        default="AI", 
        help="The main topic to analyze (e.g., 'AI', '환경', '경제')."
    )
    args = parser.parse_args()

    content_to_analyze = []
    if args.file:
        print(f"[NarrativeBeacon AI] 📂 파일 '{args.file}'에서 콘텐츠를 불러오는 중...")
        try:
            # 'with open'을 사용하여 파일 자원을 안전하게 관리
            with open(args.file, 'r', encoding='utf-8') as f:
                # 각 라인을 읽어와 공백이 아닌 유효한 라인만 추출
                content_to_analyze = [line.strip() for line in f if line.strip()]
            print(f"[NarrativeBeacon AI] 📝 총 {len(content_to_analyze)}개의 콘텐츠를 성공적으로 불러왔습니다.")
        except FileNotFoundError:
            print(f"[NarrativeBeacon AI] ❌ 오류: 파일을 찾을 수 없습니다: '{args.file}'. 샘플 데이터로 진행합니다.")
        except UnicodeDecodeError:
            print(f"[NarrativeBeacon AI] ❌ 오류: 파일 '{args.file}'의 인코딩 오류. UTF-8 인코딩인지 확인해주세요. 샘플 데이터로 진행합니다.")
        except Exception as e:
            print(f"[NarrativeBeacon AI] ❌ 오류: 파일 읽기 중 예상치 못한 오류 발생: {e}. 샘플 데이터로 진행합니다.")

    # 파일이 제공되지 않았거나 오류 발생 시 데모 데이터 사용
    if not content_to_analyze:
        print("[NarrativeBeacon AI] 💡 지금은 샘플 데이터로 시연 중입니다. 본인 파일을 쓰려면 'python narrative_beacon_ai.py --file 내파일.txt'처럼 실행하세요.")
        content_to_analyze = [
            "AI 기술의 발전은 인류에게 새로운 성공의 가능성을 제시합니다. 미래는 AI와 함께 혁신될 것입니다.",
            "많은 기업들이 AI 도입으로 효율성을 극대화하며 성공 사례를 만들고 있습니다. 이는 다음 세대의 발전 동력입니다.",
            "하지만 AI 윤리 문제와 인간의 일자리 감소에 대한 도전 과제도 간과할 수 없습니다. 사회적 논의가 필요합니다.",
            "AI가 모든 것을 해결할 수는 없으며, 일부 부작용과 한계점도 명확히 존재합니다. 비판적 시각이 중요합니다.",
            "AI 시대의 진정한 성공은 기술 혁신뿐만 아니라 인간 중심의 가치를 지키는 데 있습니다. 사회적 공감대가 필수적입니다.",
            "AI와 인간의 협업은 미래의 중요한 열쇠입니다. 새로운 발전 방향을 모색해야 합니다.",
            "AI는 아직 많은 도전 과제를 안고 있습니다. 특히 소외계층에게 미칠 수 있는 영향에 대한 심층적 분석이 필요합니다."
        ]
    
    analysis_results = analyze_content(content_to_analyze, args.topic)
    
    # 결과 저장 (스토리라인 기회 지도 파일 생성)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"narrative_beacon_map_{args.topic}_{timestamp}.txt"
    
    print(f"[NarrativeBeacon AI] 💾 분석 결과를 '{output_filename}' 파일에 저장하는 중...")
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(f"NarrativeBeacon AI - 스토리라인 기회 지도 ({timestamp})\n")
            f.write(f"분석 주제: {args.topic}\n\n")
            
            f.write("== 🌟 인기/과포화 서사 패턴 ==\n")
            if analysis_results["is_saturated"]:
                f.write(f"  - 상태: 과포화 감지 (일반적인 긍정적 서사각이 많이 다루어지고 있습니다. 새로운 관점 모색 필요!)\n")
                f.write(f"  - 흔한 키워드: {analysis_results['common_narratives']}\n")
            else:
                f.write("  - 상태: 과포화되지 않음\n")
            f.write("\n")

            f.write("== ✨ 미개척 서사 각도 및 기회 ==\n")
            if analysis_results["storyline_opportunities"]:
                f.write("  - 발견된 기회 (1달러에 판매 가능!):\n")
                for angle, count in analysis_results["storyline_opportunities"].items():
                    f.write(f"    - '{angle}': 이 키워드를 중심으로 새로운 관점의 이야기를 만들 수 있습니다. (등장 횟수: {count})\n")
                f.write("\n이 스토리라인 기회 지도를 구매하여 세상에 없던 새로운 이야기를 만들어보세요!\n")
            else:
                f.write("  - 발견된 기회: 없음 (분석 내용을 확장하거나 다른 주제를 시도해 보세요.)\n")
            f.write("\n")
            
            f.write("== 📊 모든 분석 키워드 빈도 (미개척 키워드 기준) ==\n")
            f.write(str(analysis_results["undiscovered_angles"])) # 모든 미개척 키워드 빈도 출력
            f.write("\n")

        print(f"[NarrativeBeacon AI] ✅ 분석 완료. 결과는 '{output_filename}' 파일에 저장되었습니다.")
    except Exception as e:
        print(f"[NarrativeBeacon AI] ❌ 오류: 결과 파일 저장 중 오류 발생: {e}")
        
    print("[NarrativeBeacon AI] 🤖 안내: 이 봇은 cron 등 스케줄러에 등록하여 주기적으로 실행하면 새로운 스토리 기회를 지속적으로 발굴할 수 있습니다.")

if __name__ == "__main__":
    main()
