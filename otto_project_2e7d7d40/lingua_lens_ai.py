# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import datetime
import os

# --- Constants --- #
VOCAB_ERROR_THRESHOLD = 5
GRAMMAR_CONFUSED_THRESHOLD = 4
PRACTICE_LOW_SCORE_THRESHOLD = 60

# --- 1. 가상 사용자 학습 데이터 생성 (Mocking) ---
def simulate_user_data():
    """
    AI 분석을 위한 가상의 사용자 학습 로그 데이터를 생성합니다.
    실제 서비스에서는 DB, 파일 등에서 로드될 데이터입니다.
    """
    print("[LOG] 1단계: 사용자 학습 데이터를 시뮬레이션합니다...")
    # 실제 서비스에서는 데이터베이스, 파일 시스템, 외부 API 등에서
    # 사용자 데이터를 로드하는 로직이 이 자리에 구현됩니다.
    user_data = {
        "user_id": "oto_learner_001",
        "name": "오또",
        "learning_language": "영어",
        "vocabulary_log": [
            {"word": "ubiquitous", "difficulty": "hard", "mastery": 3, "errors": 5, "last_reviewed": "2023-10-20"},
            {"word": "ephemeral", "difficulty": "hard", "mastery": 2, "errors": 7, "last_reviewed": "2023-10-18"},
            {"word": "serendipity", "difficulty": "medium", "mastery": 4, "errors": 1, "last_reviewed": "2023-11-01"},
            {"word": "plethora", "difficulty": "medium", "mastery": 3, "errors": 3, "last_reviewed": "2023-10-25"},
            {"word": "cacophony", "difficulty": "hard", "mastery": 1, "errors": 10, "last_reviewed": "2023-10-15"}
        ],
        "grammar_notes": [
            {"topic": "Present Perfect", "understood": True, "confused_count": 1},
            {"topic": "Conditional Sentences Type 3", "understood": False, "confused_count": 5},
            {"topic": "Passive Voice", "understood": True, "confused_count": 0},
            {"topic": "Subjunctive Mood", "understood": False, "confused_count": 8}
        ],
        "practice_logs": [
            {"date": "2023-10-20", "type": "speaking", "score": 65, "duration_min": 30},
            {"date": "2023-10-22", "type": "writing", "score": 70, "duration_min": 45},
            {"date": "2023-10-25", "type": "listening", "score": 50, "duration_min": 20},
            {"date": "2023-10-28", "type": "speaking", "score": 60, "duration_min": 25},
            {"date": "2023-11-01", "type": "writing", "score": 75, "duration_min": 50},
            {"date": "2023-11-03", "type": "listening", "score": 55, "duration_min": 30}
        ]
    }
    print(f"[INFO] 사용자 '{user_data['name']}' ({user_data['user_id']})의 학습 데이터 로드 완료.")
    return user_data

# --- 2. 학습 데이터 분석 (AI Mocking Logic) ---
def analyze_learning_data(user_data: dict) -> dict:
    """
    사용자의 학습 데이터를 분석하여 약점과 개선점을 식별합니다.
    이 부분은 실제 AI 모델의 복잡한 로직을 간단한 규칙 기반으로 Mocking합니다.
    """
    print("[LOG] 2단계: 학습 데이터를 분석하여 'AI 언어 처방전'을 준비합니다...")
    analysis = {
        "weak_vocabulary": [],
        "weak_grammar_topics": [],
        "practice_insights": [],
        "overall_diagnosis": "",
        "recommendations": []
    }

    # 2.1. 단어 약점 식별
    print("[LOG] 2.1. 어휘 학습 로그 분석 중...")
    for item in user_data.get("vocabulary_log", []):
        if item.get("errors", 0) >= VOCAB_ERROR_THRESHOLD:
            analysis["weak_vocabulary"].append(f"{item.get('word', '알 수 없는 단어')} (오류 {item.get('errors', 0)}회, 마스터리 {item.get('mastery', 0)}단계)")

    # 2.2. 문법 약점 식별
    print("[LOG] 2.2. 문법 학습 노트 분석 중...")
    for item in user_data.get("grammar_notes", []):
        # 이해하지 못했고, 혼란도가 일정 수준 이상인 경우 약점으로 간주
        if not item.get("understood", True) and item.get("confused_count", 0) >= GRAMMAR_CONFUSED_THRESHOLD:
            analysis["weak_grammar_topics"].append(f"{item.get('topic', '알 수 없는 주제')} (혼란 {item.get('confused_count', 0)}회)")

    # 2.3. 연습 기록 통찰
    print("[LOG] 2.3. 연습 기록 및 성과 분석 중...")
    scores = [log.get("score", 0) for log in user_data.get("practice_logs", []) if isinstance(log.get("score"), (int, float))]
    
    if not scores:
        analysis["practice_insights"].append("아직 연습 기록이 충분하지 않습니다. 꾸준한 연습이 필요합니다.")
    else:
        avg_score = sum(scores) / len(scores)
        if avg_score < PRACTICE_LOW_SCORE_THRESHOLD:
            analysis["practice_insights"].append(f"전반적인 연습 점수(평균 {avg_score:.1f}점)가 낮은 편입니다. 기본기 다지기에 집중해 보세요.")
        
        # 최근 점수 하락세 감지 (최소 3개 이상의 기록 필요)
        if len(scores) >= 3 and scores[-1] < scores[-2] and scores[-2] < scores[-3]:
            analysis["practice_insights"].append("최근 연습 점수가 하락세입니다. 슬럼프를 주의하고 원인을 파악해 보세요.")
        
        if not analysis["practice_insights"]:
            analysis["practice_insights"].append("연습은 꾸준히 잘 진행되고 있습니다! 좋은 흐름을 유지하세요.")

    # 2.4. 종합 진단 및 맞춤형 처방
    print("[LOG] 2.4. 종합 진단 및 맞춤형 처방 생성 중...")
    if analysis["weak_vocabulary"] or analysis["weak_grammar_topics"]:
        analysis["overall_diagnosis"] = "현재 어휘 및 문법 영역에서 고질적인 약점이 발견됩니다. 이 부분에 집중적인 개선이 필요합니다."
        if analysis["weak_vocabulary"]:
            analysis["recommendations"].append(f"- 취약 어휘 ({', '.join(analysis['weak_vocabulary'])})에 대한 반복 학습 및 다양한 예문 만들기를 권장합니다.")
        if analysis["weak_grammar_topics"]:
            analysis["recommendations"].append(f"- 취약 문법 ({', '.join(analysis['weak_grammar_topics'])}) 개념을 재정립하고, 관련 문제 풀이를 집중적으로 진행하세요.")
    else:
        analysis["overall_diagnosis"] = "전반적인 학습 진행은 양호합니다. 다음 단계로의 도약을 위한 심화 학습을 고려해보세요."
        analysis["recommendations"].append("- 현재 학습 흐름을 유지하며, 흥미로운 고급 자료에 지속적으로 노출되어 보세요.")

    analysis["recommendations"].append("- 주간 학습 시간을 시각화하여 학습 지속성을 높이고, 특정 요일에 학습이 몰리지 않도록 분산 학습을 시도해 보세요.")
    analysis["recommendations"].append("- 오답 노트를 적극 활용하여 틀린 문제를 다시 풀고, 관련 개념을 완전히 이해하도록 노력하세요.")

    print("[INFO] 학습 데이터 분석 완료.")
    return analysis

# --- 3. AI 언어 처방전 보고서 생성 ---
def generate_prescription_report(user_data: dict, analysis: dict) -> str:
    """
    분석 결과를 바탕으로 'AI 언어 처방전' 보고서 내용을 문자열로 생성합니다.
    """
    print("[LOG] 3단계: 'AI 언어 처방전' 보고서 내용을 생성합니다...")
    
    # 가상 학습 효율성 지표 (Mocking)
    vocab_mastery_idx = sum(item.get('mastery', 0) for item in user_data.get('vocabulary_log', [])) / len(user_data.get('vocabulary_log', [])) * 10 if user_data.get('vocabulary_log') else 0
    grammar_understanding_idx = sum(10 if item.get('understood') else (10 - item.get('confused_count', 0)) for item in user_data.get('grammar_notes', [])) / len(user_data.get('grammar_notes', [])) * 10 if user_data.get('grammar_notes') else 0
    practice_consistency_idx = sum(1 for log in user_data.get('practice_logs', []) if log.get('score', 0) > 0) / 7 * 100 # 주간 7회 연습 가정

    vocab_mastery_idx = max(0, min(100, int(vocab_mastery_idx)))
    grammar_understanding_idx = max(0, min(100, int(grammar_understanding_idx)))
    practice_consistency_idx = max(0, min(100, int(practice_consistency_idx)))

    report_content = f"""
# ================================================
#      LinguaLens AI: 오또의 언어처방전 리포트      
# ================================================

보고서 생성일: {datetime.datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}
학습자: {user_data.get('name', '알 수 없음')} ({user_data.get('user_id', 'N/A')})
학습 언어: {user_data.get('learning_language', 'N/A')}

## 1. 종합 진단 요약
{analysis.get('overall_diagnosis', '종합 진단 내용이 없습니다.')}

## 2. 취약점 분석
### 2.1. 어휘 영역
{'특별한 취약 어휘 없음' if not analysis['weak_vocabulary'] else '- ' + '\n- '.join(analysis['weak_vocabulary'])}

### 2.2. 문법 영역
{'특별한 취약 문법 없음' if not analysis['weak_grammar_topics'] else '- ' + '\n- '.join(analysis['weak_grammar_topics'])}

### 2.3. 연습 기록 통찰
- {'\n- '.join(analysis['practice_insights'] if analysis['practice_insights'] else ['연습 기록에 대한 특별한 통찰이 없습니다.'])}

## 3. 오또의 맞춤형 개선 전략
{('\n'.join(analysis['recommendations']) if analysis['recommendations'] else '특별한 추천 전략이 없습니다.')}

## 4. 학습 효율성 지표 (가상 시각화)
현재 어휘 마스터리 지수: {vocab_mastery_idx}% (지난주 대비 5% 변동)
현재 문법 이해도 지수: {grammar_understanding_idx}% (지난주 대비 2% 변동)
주간 평균 연습 시간: {sum(log.get('duration_min', 0) for log in user_data.get('practice_logs', [])) / len(user_data.get('practice_logs', [])) if user_data.get('practice_logs') else 0:.0f}분 (목표: 45분)

[진척도 시각화 예시]
  어휘 마스터리: [{('■' * (vocab_mastery_idx // 10)).ljust(10, '□')}] {vocab_mastery_idx}%
  문법 이해도:   [{('■' * (grammar_understanding_idx // 10)).ljust(10, '□')}] {grammar_understanding_idx}%
  연습 꾸준함:   [{('■' * (practice_consistency_idx // 10)).ljust(10, '□')}] {practice_consistency_idx}%

# ================================================
#              오또는 오늘도 1달러를 법니다!              
# ================================================
"""
    print("[INFO] 'AI 언어 처방전' 보고서 내용 생성 완료.")
    return report_content

# --- 4. 보고서 파일 저장 ---
def save_report_to_file(report_content: str, filename: str):
    """
    생성된 보고서 내용을 지정된 파일명으로 저장합니다.
    """
    print(f"[LOG] 4단계: 보고서를 '{filename}' 파일로 저장합니다...")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"[SUCCESS] 'AI 언어 처방전' 보고서가 성공적으로 '{filename}' 파일로 저장되었습니다.")
        print(f"[INFO] 보고서 경로: {os.path.abspath(filename)}")
    except IOError as e:
        print(f"[ERROR] 보고서 저장 중 오류 발생: {e}")
    except Exception as e:
        print(f"[ERROR] 알 수 없는 오류로 보고서 저장 실패: {e}")

# --- 메인 실행 함수 ---
def main():
    print("\n========================================")
    print(" LinguaLens AI: 오또의 언어처방전 시작 ")
    print("========================================")

    try:
        # 1. 가상 학습 데이터 로드 (Mocking)
        user_data = simulate_user_data()

        # 2. 학습 데이터 분석
        analysis_result = analyze_learning_data(user_data)

        # 3. AI 언어 처방전 보고서 생성
        report = generate_prescription_report(user_data, analysis_result)

        # 4. 보고서 파일 저장
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"lingua_lens_report_{timestamp}.txt"
        save_report_to_file(report, output_filename)

    except Exception as e:
        print(f"[CRITICAL ERROR] 프로그램 실행 중 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc() # 상세 에러 스택 트레이스 출력

    print("\n========================================")
    print(" LinguaLens AI: 오또의 언어처방전 완료 ")
    print("========================================")
    print("\n[반복 사용 가치] 매일/주간 반복 실행하여 누적된 학습 데이터를 분석하고 새로운 처방전을 받아보세요.")
    print("             (예: Windows 작업 스케줄러, macOS/Linux crontab에 'python lingua_lens_ai.py' 등록)")

if __name__ == "__main__":
    main()
