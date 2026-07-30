#!/usr/bin/env python3
"""
Debug_Diviner: 오또의 눈으로 GitHub 이슈를 분석하여 버그 패턴 청사진을 생성하는 스크립트.
LLM(Large Language Model)의 예측을 모킹하여 오픈된 버그 이슈들로부터
반복되는 문제의 근본 원인에 대한 3줄 예언서를 도출합니다.
"""

import datetime
import json
import sys # 시스템 종료를 위한 모듈 임포트

# --- Mock GitHub Issue Data --- (실제 연동 대신 사용할 가상 데이터)
# 실제 서비스에서는 GitHub API를 통해 실시간 데이터를 가져옵니다.
MOCK_GITHUB_ISSUES_DATA = [
    {
        "number": 101,
        "title": "Bug: Application crashes on startup with FileNotFoundError",
        "body": "When running `python main.py`, the application immediately exits with `FileNotFoundError` for `config.json`. This occurs on Windows 10.",
        "labels": [{"name": "bug"}, {"name": "priority:high"}],
        "state": "open"
    },
    {
        "number": 102,
        "title": "Feature Request: Add dark mode",
        "body": "It would be great if the UI had a dark mode option.",
        "labels": [{"name": "enhancement"}],
        "state": "open"
    },
    {
        "number": 103,
        "title": "Bug: Incorrect calculation in report generation",
        "body": "The final report shows an incorrect sum for 'Total Revenue'. Points to a floating-point precision issue.",
        "labels": [{"name": "bug"}],
        "state": "open"
    },
    {
        "number": 104,
        "title": "Docs: Update installation guide",
        "body": "The installation guide is outdated for Python 3.9+.",
        "labels": [{"name": "documentation"}],
        "state": "closed"
    },
    {
        "number": 105,
        "title": "Performance Degradation: API response times increased",
        "body": "After recent update, API calls are consistently slower, specifically `GET /data`. Suspect database query optimization.",
        "labels": [{"name": "bug"}, {"name": "performance"}],
        "state": "open"
    }
]

# --- Mock LLM Prediction Function --- (실제 LLM 호출 대신 사용할 가상 함수)
# 실제 서비스에서는 OpenAI API 또는 다른 LLM 서비스를 호출합니다.
def mock_llm_predict(issue_text: str) -> str:
    """이슈 텍스트를 기반으로 3줄 버그 패턴 청사진을 시뮬레이션합니다.
    다양한 키워드에 따라 예측을 다르게 반환하여 LLM의 행동을 모방합니다.
    """
    text_lower = issue_text.lower()
    if "filenotfounderror" in text_lower or "config.json" in text_lower:
        return (
            "Prophecy: Configuration files are elusive.\n"
            "Solution: Verify file paths and permissions.\n"
            "Pattern: Common misplacement of critical assets."
        )
    elif "incorrect calculation" in text_lower or "floating-point" in text_lower:
        return (
            "Prophecy: Numerical precision haunts the ledger.\n"
            "Solution: Implement robust decimal arithmetic.\n"
            "Pattern: Data type mismatch in aggregations."
        )
    elif "performance degradation" in text_lower or "api response times" in text_lower:
        return (
            "Prophecy: Sluggish queries hide deeper woes.\n"
            "Solution: Optimize database access patterns.\n"
            "Pattern: N+1 selects or missing indices."
        )
    return (
        "Prophecy: A subtle flaw persists unnoticed.\n"
        "Solution: Deep dive into recent code changes.\n"
        "Pattern: Regression from dependencies or refactor."
    )

# --- 핵심 비즈니스 로직 함수 --- 

def fetch_github_issues_mock(repo_owner: str, repo_name: str) -> list:
    """GitHub 이슈 데이터를 모킹하여 가져오고, 열린 버그 이슈만 필터링합니다.
    실제 GitHub API 연동 시에는 인증 및 속도 제한 처리가 필요합니다.
    """
    print(f"[INFO] {repo_owner}/{repo_name} 리포지토리의 GitHub 이슈 데이터를 모킹합니다...")
    bug_issues = []
    for issue in MOCK_GITHUB_ISSUES_DATA:
        # 'open' 상태이고 'bug' 라벨이 있는 이슈만 선택
        if issue.get('state') == 'open' and any(label.get('name') == 'bug' for label in issue.get('labels', [])):
            bug_issues.append(issue)
    print(f"[INFO] 총 {len(bug_issues)}개의 오픈된 버그 이슈(모킹)를 발견했습니다.")
    return bug_issues

def analyze_issues_with_llm(issues: list) -> list:
    """제공된 이슈 목록을 LLM(모킹)을 사용하여 분석하고 버그 패턴 청사진을 추출합니다.
    각 이슈의 제목과 본문을 결합하여 LLM 예측에 사용합니다.
    """
    print(f"[INFO] {len(issues)}개의 이슈에 대해 버그 패턴 분석을 시작합니다...")
    all_blueprints = []
    for issue in issues:
        issue_text = f"{issue.get('title', '')} {issue.get('body', '')}" # 안전한 데이터 접근
        try:
            blueprint = mock_llm_predict(issue_text)
            all_blueprints.append(blueprint)
            print(f"[DEBUG] 이슈 #{issue.get('number', 'N/A')} 분석 완료. 청사진 생성.")
        except Exception as e:
            print(f"[ERROR] 이슈 #{issue.get('number', 'N/A')} 분석 중 오류 발생: {e}")
            # 오류 발생 시 해당 이슈는 건너뛰고 계속 진행합니다.
    print(f"[INFO] 총 {len(all_blueprints)}개의 버그 패턴 청사진이 생성되었습니다.")
    return all_blueprints

def generate_final_blueprint(all_blueprints: list) -> str:
    """여러 버그 패턴 청사진들을 통합하여 최종적인 '버그 예언서'를 생성합니다.
    가장 두드러지는 패턴들을 요약하여 3줄로 구성합니다.
    """
    if not all_blueprints:
        return (
            "탐지된 주요 버그 패턴 없음.\n"
            "새로운 이슈를 지속적으로 모니터링하세요.\n"
            "개발자님, 항상 경계를 늦추지 마세요."
        )

    unique_predictions = []
    for bp in all_blueprints:
        first_line = bp.split('\n')[0].strip() # 각 청사진의 첫 번째 줄만 추출
        if first_line and first_line not in unique_predictions:
            unique_predictions.append(first_line)

    # 고유한 예측의 개수에 따라 최종 예언서 구성
    if len(unique_predictions) >= 3:
        return f"{unique_predictions[0]}\n{unique_predictions[1]}\n{unique_predictions[2]}"
    elif len(unique_predictions) == 2:
        return f"{unique_predictions[0]}\n{unique_predictions[1]}\n추가적인 심층 분석이 필요합니다."
    elif len(unique_predictions) == 1:
        return f"{unique_predictions[0]}\n이 패턴이 지배적입니다.\n철저하게 검토하십시오."
    else:
        return (
            "뚜렷한 패턴이 감지되지 않았습니다.\n"
            "데이터 소스를 재평가하세요.\n"
            "주의를 기울여 진행하십시오."
        )

def save_blueprint_to_file(blueprint_text: str, filename: str) -> None:
    """생성된 디버깅 예언서를 지정된 파일에 저장합니다.
    파일 저장 중 발생할 수 있는 IOError를 안전하게 처리합니다.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(blueprint_text)
        print(f"[SUCCESS] 디버깅 예언서가 '{filename}' 파일에 성공적으로 저장되었습니다.")
    except IOError as e:
        print(f"[ERROR] 파일 '{filename}'에 예언서를 저장할 수 없습니다: {e}")
    except Exception as e:
        print(f"[CRITICAL ERROR] 알 수 없는 오류로 인해 파일 저장에 실패했습니다: {e}")

# --- 메인 실행 흐름 --- 

def main():
    """Debug_Diviner의 메인 실행 함수입니다.
    GitHub 이슈 수집, LLM 분석, 최종 청사진 생성 및 저장을orchestrates 합니다.
    """
    print("\n--- Debug_Diviner: 오또의 버그 탐지 시스템 가동 시작 ---")
    
    # 분석 대상 리포지토리 정보 (모킹 환경 설정)
    REPO_OWNER = "mock_org"
    REPO_NAME = "mock_project"

    try:
        # 1. GitHub Issue 데이터 수집 (Mocked API 호출)
        print("\n[STEP 1/4] GitHub 오픈 버그 이슈 데이터를 수집합니다...")
        issues = fetch_github_issues_mock(REPO_OWNER, REPO_NAME)

        if not issues:
            print("[INFO] 분석할 오픈 버그 이슈가 발견되지 않았습니다. 시스템을 종료합니다.")
            sys.exit(0) # 정상 종료

        # 2. LLM 기반 버그 패턴 추출 (Mocked LLM 예측)
        print("\n[STEP 2/4] LLM을 사용하여 이슈에서 버그 패턴을 분석합니다...")
        all_blueprints = analyze_issues_with_llm(issues)

        if not all_blueprints:
            print("[INFO] LLM 분석을 통해 유효한 버그 패턴 청사진을 생성하지 못했습니다. 시스템을 종료합니다.")
            sys.exit(0) # 정상 종료

        # 3. 초압축 3줄 '버그 패턴 블루프린트' 생성
        print("\n[STEP 3/4] 분석된 청사진들을 통합하여 최종 '디버깅 예언서'를 생성합니다...")
        final_prophecy = generate_final_blueprint(all_blueprints)
        
        print("\n--- [오또의 디버깅 예언서 (Bug Pattern Blueprint)] --- ")
        print(final_prophecy)
        print("----------------------------------------------------")

        # 4. 결과 파일 저장
        print("\n[STEP 4/4] 디버깅 예언서를 파일로 저장합니다...")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"debugging_prophecy_{timestamp}.txt"
        save_blueprint_to_file(final_prophecy, output_filename)

    except KeyboardInterrupt:
        print("\n[WARNING] 사용자에 의해 Debug_Diviner가 중단되었습니다.")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] 예측하지 못한 심각한 오류가 발생했습니다: {e}")
        sys.exit(1) # 오류 종료

    print("\n--- Debug_Diviner 가동 종료 ---")
    print("\n[팁] 이 스크립트를 주기적으로 실행하여 최신 버그 패턴을 추적할 수 있습니다. (예: `cron` 또는 `Task Scheduler`)")

if __name__ == "__main__":
    main()
