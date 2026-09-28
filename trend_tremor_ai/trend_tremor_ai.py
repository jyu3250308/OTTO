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
import csv
from datetime import datetime
from textblob import TextBlob

def _print_log(level, message):
    """로그 메시지를 일관된 형식으로 출력합니다."""
    print(f"[{level.upper()}] {message}")

def analyze_text_for_keywords(text_data, keywords):
    """텍스트 데이터에서 키워드별 감성 변화를 분석합니다."""
    _print_log("info", f"총 {len(keywords)}개의 키워드에 대한 감성 분석을 시작합니다.")
    results = []
    for i, keyword in enumerate(keywords):
        _print_log("info", f"({i+1}/{len(keywords)}) 키워드 '{keyword}' 분석 중...")
        keyword_lower = keyword.lower()
        related_sentences = []
        
        # 텍스트 데이터를 문장 단위로 분리하고 키워드 포함 문장 필터링
        sentences = text_data.split('.')
        for sentence in sentences:
            if keyword_lower in sentence.lower():
                stripped_sentence = sentence.strip()
                if stripped_sentence: # 빈 문자열 방지
                    related_sentences.append(stripped_sentence)
        
        # 관련 내용이 없는 경우 처리
        if not related_sentences:
            _print_log("warn", f"키워드 '{keyword}' 관련 내용이 텍스트에서 발견되지 않았습니다.")
            results.append({
                "keyword": keyword,
                "occurrences": 0,
                "polarity": 0.0,
                "subjectivity": 0.0,
                "tremor_status": "Not Detected",
                "message": f"키워드 '{keyword}' 관련 내용 없음"
            })
            continue

        combined_text = ". ".join(related_sentences)
        blob = TextBlob(combined_text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        occurrences = combined_text.lower().count(keyword_lower)

        tremor_status = "Normal"
        message = "평이한 여론 흐름입니다."

        # 감성 및 출현 빈도에 따른 '트레머' 상태 결정
        if polarity > 0.5: # 강한 긍정 감성
            tremor_status = "Opportunity Detected (Strong Positive)"
            message = "온라인 여론이 긍정적으로 급등할 조짐입니다."
        elif polarity < -0.5: # 강한 부정 감성
            tremor_status = "Risk Detected (Strong Negative)"
            message = "논쟁 또는 부정적 여론이 형성될 조짐입니다."
        elif occurrences > 5 and len(related_sentences) > 2: # 출현 빈도 및 관련 문장 많음
            tremor_status = "Interest Surge Detected"
            message = "관심이 급증하고 있는 키워드입니다."

        _print_log("info", f"'{keyword}' 분석 완료: {tremor_status} (감성: {polarity:.3f}, 출현: {occurrences}회)")
        results.append({
            "keyword": keyword,
            "occurrences": occurrences,
            "polarity": round(polarity, 3),
            "subjectivity": round(subjectivity, 3),
            "tremor_status": tremor_status,
            "message": message
        })
    _print_log("info", "모든 키워드에 대한 감성 분석이 완료되었습니다.")
    return results

def save_report(results, output_filename="trend_tremor_report.csv"):
    """분석 결과를 CSV 파일로 저장합니다."""
    _print_log("info", f"분석 결과를 '{output_filename}' 파일에 저장 시도...")
    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["timestamp", "keyword", "occurrences", "polarity", "subjectivity", "tremor_status", "message"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for row in results:
                # 각 행에 현재 시간 정보 추가
                row_to_write = dict(row) # 원본 변경 방지
                row_to_write["timestamp"] = current_time
                writer.writerow(row_to_write)
        _print_log("success", f"분석 결과가 '{output_filename}' 파일에 성공적으로 저장되었습니다.")
    except IOError as e:
        _print_log("error", f"파일 '{output_filename}' 저장 중 오류 발생: {e}. 파일 쓰기 권한 또는 경로를 확인하세요.")
    except Exception as e:
        _print_log("error", f"예상치 못한 오류로 파일 저장 실패: {e}.")

def main():
    _print_log("info", "TrendTremor AI 애플리케이션을 시작합니다.")
    parser = argparse.ArgumentParser(
        description="TrendTremor AI: 온라인 여론의 떡상/떡락 전조를 감지합니다."
    )
    parser.add_argument(
        "--file", 
        type=str, 
        help="분석할 텍스트 파일 경로 (예: discussions.txt)"
    )
    parser.add_argument(
        "--keywords", 
        type=str, 
        default="AI,블록체인,환경", 
        help="분석할 키워드들을 콤마(,)로 구분하여 입력 (기본값: AI,블록체인,환경)"
    )
    args = parser.parse_args()

    text_data = ""
    if args.file:
        _print_log("info", f"입력 파일 '{args.file}'을 로드 시도합니다.")
        if os.path.exists(args.file): # 파일 존재 여부 확인
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    text_data = f.read()
                _print_log("success", f"'{args.file}' 파일에서 텍스트를 성공적으로 로드했습니다.")
            except UnicodeDecodeError as e:
                _print_log("error", f"파일 '{args.file}' 인코딩 오류: {e}. 파일 인코딩을 확인하세요. (UTF-8 권장)")
                text_data = get_demo_text()
                _print_log("info", "데모 데이터로 시연을 계속합니다.")
            except FileNotFoundError: # os.path.exists로 걸러지지만, 만약을 대비
                _print_log("error", f"파일 '{args.file}'을 찾을 수 없습니다.")
                text_data = get_demo_text()
                _print_log("info", "데모 데이터로 시연을 계속합니다.")
            except Exception as e:
                _print_log("error", f"파일 '{args.file}' 읽기 실패: {e}. 데모 데이터로 진행합니다.")
                text_data = get_demo_text()
        else:
            _print_log("error", f"지정된 파일 '{args.file}'이 존재하지 않습니다.")
            text_data = get_demo_text()
            _print_log("info", "데모 데이터로 시연을 계속합니다.")
    else:
        _print_log("info", "파일 경로가 지정되지 않았습니다. 데모 데이터로 시연합니다.")
        text_data = get_demo_text()
    
    # 데모 데이터 사용 시 안내 메시지
    if text_data == get_demo_text():
        _print_log("info", "(현재 샘플 데이터 사용 중) 본인 파일을 사용하려면 'python trend_tremor_ai.py --file 내파일.txt --keywords 키워드1,키워드2' 와 같이 실행하세요.")

    # 키워드 처리: 콤마로 분리 후 공백 제거
    keywords_list = [k.strip() for k in args.keywords.split(',') if k.strip()]
    if not keywords_list:
        default_keywords = "AI,블록체인,환경"
        keywords_list = [k.strip() for k in default_keywords.split(',')]
        _print_log("warn", f"지정된 키워드가 없거나 유효하지 않아 기본 키워드('{default_keywords}')를 사용합니다.")

    _print_log("info", f"분석할 키워드: {', '.join(keywords_list)}")
    _print_log("info", "텍스트 데이터 분석을 시작합니다...")
    analysis_results = analyze_text_for_keywords(text_data, keywords_list)

    _print_log("info", "\n--- 분석 요약 --- ")
    if not analysis_results:
        _print_log("warn", "분석 결과가 없습니다.")
    else:
        for res in analysis_results:
            _print_log("result", f"[키워드: {res['keyword']}] {res['tremor_status']} (감성: {res['polarity']}, 출현: {res['occurrences']}회). {res['message']}")
    
    save_report(analysis_results)
    
    _print_log("info", "\n[Tip] 이 봇은 온라인 여론 감지를 위해 주기적으로 실행될 때 더 큰 가치를 가집니다.")
    _print_log("info", "(예: Crontab 또는 Windows 작업 스케줄러에 등록하여 매일 실행)")
    _print_log("info", "TrendTremor AI 애플리케이션을 종료합니다.")

def get_demo_text():
    """데모용 샘플 텍스트를 반환합니다."""
    return (
        "오늘 AI 기술의 발전은 정말 놀랍습니다. GPT-4는 이제 거의 인간 수준의 대화를 나눕니다. "
        "하지만 AI 윤리에 대한 논쟁은 여전히 뜨겁습니다. "
        "블록체인은 탈중앙화된 미래를 약속하지만, 아직 해결해야 할 과제가 많습니다. "
        "환경 오염 문제는 심각하며, 새로운 정책 없이는 개선되기 어려울 것입니다. "
        "메타버스는 새로운 트렌드로 떠오르고 있지만, 실제 활용 사례는 아직 부족합니다. "
        "경제 불황으로 인해 많은 기업들이 어려움을 겪고 있습니다. AI 챗봇이 일자리를 대체한다는 우려도 있습니다. "
        "기후 변화에 대한 관심이 급증하고 있으며, 친환경 에너지 전환에 대한 논의가 활발합니다." 
        "새로운 정부의 에너지 정책은 환경 보호에 대한 의지가 부족하다는 비판을 받고 있습니다." 
        "환경 운동가들은 더 강력한 기후 변화 대응을 요구하고 있습니다." 
        "메타버스 기술은 젊은 세대에게 큰 인기를 끌고 있으며, 투자 또한 활발합니다."
    )

if __name__ == "__main__":
    main()