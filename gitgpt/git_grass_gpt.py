import os
import subprocess
import datetime
import json
import random
import time
import shutil
import sys
from dotenv import load_dotenv
import schedule

# --- Configuration & Constants ---
CONFIG_FILE = 'config.json'
REPO_DIR = 'otto_commit_repo' # Local directory for the dummy Git repository
DUMMY_FILE_NAME = 'otto_activity_log.md'
DUMMY_FILE_PATH = os.path.join(REPO_DIR, DUMMY_FILE_NAME)

COMMIT_TEMPLATES = {
    "학습": [
        "feat: {context} 관련 코드 학습 및 정리 ({date})",
        "docs: {context} 개념 노트 추가 및 복습 ({date})",
        "refactor: {context} 예제 코드 리팩토링 및 개선 ({date})",
        "chore: {context} 학습 환경 설정 업데이트 ({date})",
        "perf: {context} 알고리즘 효율성 분석 및 최적화 시도 ({date})"
    ],
    "게임": [
        "feat: {context} 전략 시뮬레이션 로직 개선 ({date})",
        "docs: {context} 공략법 데이터베이스 업데이트 ({date})",
        "chore: {context} 관련 스크립트 디버깅 및 최적화 ({date})",
        "test: {context} 버그 리포트 분석 및 재현 테스트 완료 ({date})",
        "refactor: {context} 설정 파일 구조 개선 ({date})"
    ],
    "휴가": [
        "docs: 휴가 중 아이디어 스케치 및 컨셉 정리 ({date})",
        "chore: 다음 프로젝트를 위한 영감 수집 및 브레인스토밍 ({date})",
        "refactor: 코드 베이스 아키텍처 구상 및 설계 문서 초안 작성 ({date})",
        "feat: 장기적인 개발 방향성 모색 및 계획 수립 ({date})",
        "style: 자연에서 얻은 인사이트를 코딩 스타일에 반영 준비 ({date})"
    ],
    "낮잠": [
        "chore: 에너지 충전을 위한 시스템 일시 정지 ({date})",
        "docs: '꿈'이라는 비동기 프로세스에서 얻은 인사이트 기록 ({date})",
        "refactor: 뇌 최적화를 위한 딥 슬립 모드 진입 ({date})",
        "feat: 잠재의식 속에서 새로운 알고리즘 발견 (미확정) ({date})",
        "build: 몸과 마음의 빌드 시간 단축을 위한 노력 ({date})"
    ],
    "레트로 코딩": [
        "feat: 80년대 스타일 UI 컴포넌트 구현 시도 ({date})",
        "refactor: 어셈블리/C 언어에서 영감을 받은 코드 최적화 ({date})",
        "docs: 레거시 시스템 분석 및 현대화 방안 연구 ({date})",
        "build: 도트 매트릭스 프린터 출력 시뮬레이션 추가 ({date})",
        "chore: 고전 게임 복원 프로젝트 관련 자료 조사 ({date})"
    ],
    "기타": [
        "chore: 일상 활동 정리 및 생산성 향상 방안 모색 ({date})",
        "docs: 새로운 기술 동향 학습 및 요약 ({date})",
        "feat: 개인 프로젝트 아이디어 구체화 작업 ({date})",
        "refactor: 기존 코드 베이스 점진적 개선 계획 수립 ({date})",
        "style: 개발 환경 개인화 설정 업데이트 ({date})"
    ]
}

# --- Helper Functions ---
def print_log(message, level="INFO"):
    """콘솔에 로그 메시지를 출력합니다."""
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} [{level}] {message}")

def load_config():
    """설정 파일을 로드하거나, 없으면 기본 설정으로 생성하고 사용자 입력을 받습니다."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print_log(f"설정 파일을 로드했습니다: {CONFIG_FILE}")
    else:
        print_log("설정 파일이 없습니다. 새로운 설정을 생성합니다.", "WARN")
        config = {
            "github_username": "",
            "github_repo_name": "otto-autonomous-commit-bot",
            "commit_schedule": {
                "monday": ["09:00", "15:00"],
                "tuesday": ["10:00"],
                "wednesday": ["09:30", "14:00", "18:00"],
                "thursday": ["11:00"],
                "friday": ["10:00", "16:00"],
                "saturday": [], # 주말은 기본적으로 비워둠
                "sunday": []
            },
            "activity_theme": "학습",
            "specific_activity_context": {},
            "cleanup_after_days": 0, # 0이면 자동 삭제 안함
            "repo_creation_date": datetime.datetime.now().isoformat() # 리포지토리 생성(또는 초기화) 날짜
        }

        # 사용자 입력 받기
        print_log("--- 초기 설정 가이드 ---")
        config["github_username"] = input("GitHub 사용자 이름 (예: your-username): ").strip()
        if not config["github_username"]:
            print_log("GitHub 사용자 이름은 필수입니다. 프로그램을 종료합니다.", "ERROR")
            sys.exit(1)

        config["github_repo_name"] = input("커밋을 올릴 GitHub 저장소 이름 (기본값: otto-autonomous-commit-bot): ").strip()
        if not config["github_repo_name"]:
            config["github_repo_name"] = "otto-autonomous-commit-bot"
        
        print_log("테마 활동을 선택하세요: 학습, 게임, 휴가, 낮잠, 레트로 코딩, 기타")
        selected_theme = input(f"선택할 테마 (기본값: {config['activity_theme']}): ").strip()
        if selected_theme and selected_theme in COMMIT_TEMPLATES:
            config["activity_theme"] = selected_theme
        elif selected_theme and selected_theme not in COMMIT_TEMPLATES:
            print_log(f"알 수 없는 테마 '{selected_theme}'입니다. 기본값 '{config['activity_theme']}'으로 설정합니다.", "WARN")

        if config["activity_theme"] in ["학습", "게임"]:
            context = input(f"{config['activity_theme']} 활동에 대한 구체적인 내용 (예: Python, Stardew Valley): ").strip()
            if context: 
                config["specific_activity_context"][config["activity_theme"]] = context
        
        print_log("커밋 자동 삭제 기능을 설정합니다. (0 입력시 비활성화)")
        try:
            cleanup_days = int(input(f"몇 일 후 가짜 커밋 및 잔디 이력을 자동으로 삭제할까요? (기본값: {config['cleanup_after_days']}): ").strip() or config['cleanup_after_days'])
            config["cleanup_after_days"] = cleanup_days
        except ValueError:
            print_log("유효하지 않은 숫자입니다. 자동 삭제 기능을 비활성화합니다.", "WARN")
            config["cleanup_after_days"] = 0
        
        print_log("--- 초기 설정 완료 ---")
        save_config(config)
    return config

def save_config(config):
    """설정 파일을 저장합니다."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    print_log(f"설정 파일을 저장했습니다: {CONFIG_FILE}")

def get_git_token():
    """환경 변수에서 GitHub Personal Access Token(PAT)을 로드합니다."""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print_log("환경 변수 GITHUB_TOKEN이 설정되지 않았습니다. .env 파일을 확인하거나 직접 설정해주세요.", "ERROR")
        print_log("GitHub PAT는 리포지토리에 푸시하기 위해 필요합니다.", "ERROR")
        sys.exit(1)
    return token

def run_git_command(args, cwd=REPO_DIR):
    """Git 명령어를 실행하고 결과를 반환합니다."""
    full_command = ['git'] + args
    try:
        result = subprocess.run(full_command, cwd=cwd, capture_output=True, text=True, check=True, encoding='utf-8')
        if result.stdout:
            print_log(f"Git STDOUT: {result.stdout.strip()}", "DEBUG")
        if result.stderr and "Already up to date" not in result.stderr and "nothing to commit" not in result.stderr:
            print_log(f"Git STDERR: {result.stderr.strip()}", "WARN")
        return True
    except subprocess.CalledProcessError as e:
        print_log(f"Git 명령어 실행 실패: {' '.join(full_command)}", "ERROR")
        print_log(f"STDOUT: {e.stdout.strip()}", "ERROR")
        print_log(f"STDERR: {e.stderr.strip()}", "ERROR")
        return False
    except FileNotFoundError:
        print_log("Git 실행 파일을 찾을 수 없습니다. Git이 설치되어 있고 PATH에 추가되어 있는지 확인하세요.", "ERROR")
        sys.exit(1)

def init_repo(config, git_token):
    """더미 Git 리포지토리를 초기화하고 설정합니다."""
    username = config['github_username']
    repo_name = config['github_repo_name']
    
    if not os.path.exists(REPO_DIR):
        os.makedirs(REPO_DIR)
        print_log(f"리포지토리 디렉토리 '{REPO_DIR}'를 생성했습니다.")

    if not os.path.exists(os.path.join(REPO_DIR, '.git')):
        print_log(f"'{REPO_DIR}'에 Git 리포지토리를 초기화합니다.")
        if not run_git_command(['init']): return False
        if not run_git_command(['config', 'user.name', username]): return False
        if not run_git_command(['config', 'user.email', f"{username}@users.noreply.github.com"]): return False
        
        # 첫 더미 파일 생성 및 커밋
        with open(DUMMY_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(f"# Otto's Autonomous Commit Log for {username}/{repo_name}\n\n")
            f.write(f"Initial commit by Otto on {datetime.datetime.now().strftime('%Y-%m-%d')}.\n")
        if not run_git_command(['add', '.']): return False
        if not run_git_command(['commit', '-m', 'feat: Initial commit by Otto, autonomous commit bot']): return False

        remote_url = f"https://oauth2:{git_token}@github.com/{username}/{repo_name}.git"
        if not run_git_command(['remote', 'add', 'origin', remote_url]): return False
        if not run_git_command(['branch', '-M', 'main']): return False
        print_log(f"'{repo_name}' 리포지토리 초기화 및 첫 커밋 완료. 이제 푸시할 준비가 되었습니다.")

        # GitHub에 리포지토리가 존재하는지 확인하고, 없으면 사용자에게 생성 요청
        # (주의: 이 스크립트가 리모트 리포지토리를 직접 생성하지는 않습니다. 사용자가 미리 생성해야 합니다.)
        print_log(f"GitHub에 '{username}/{repo_name}' 리포지토리가 미리 생성되어 있어야 합니다.", "WARN")
        print_log(f"생성 후 'git push -u origin main' 명령을 수동으로 한번 실행해주세요.", "WARN")
    else:
        print_log(f"'{REPO_DIR}'에 이미 Git 리포지토리가 존재합니다.")
    return True

def create_dummy_change(activity_theme, current_datetime):
    """더미 파일에 변경 사항을 추가합니다."""
    if not os.path.exists(REPO_DIR):
        os.makedirs(REPO_DIR)

    mode = random.choice(['append', 'modify'])
    change_log = f"- {activity_theme} 관련 활동 ({current_datetime.strftime('%Y-%m-%d %H:%M:%S')})\n"
    
    try:
        if not os.path.exists(DUMMY_FILE_PATH):
            with open(DUMMY_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(f"# Otto's Activity Log\n\n")
                f.write(change_log)
        elif mode == 'append':
            with open(DUMMY_FILE_PATH, 'a', encoding='utf-8') as f:
                f.write(change_log)
        elif mode == 'modify':
            # 기존 내용을 읽어서 중간에 삽입 또는 일부 수정
            with open(DUMMY_FILE_PATH, 'r+', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) > 2:
                    insert_idx = random.randint(2, len(lines) - 1)
                    lines.insert(insert_idx, change_log)
                else:
                    lines.append(change_log)
                f.seek(0)
                f.writelines(lines)

        print_log(f"더미 파일 '{DUMMY_FILE_NAME}'에 변경 사항을 추가했습니다.")
        return True
    except IOError as e:
        print_log(f"더미 파일 변경 중 오류 발생: {e}", "ERROR")
        return False

def generate_commit_message(activity_theme, specific_context=None):
    """현재 활동 테마에 맞는 커밋 메시지를 생성합니다."""
    templates = COMMIT_TEMPLATES.get(activity_theme, COMMIT_TEMPLATES["기타"])
    selected_template = random.choice(templates)

    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    current_day = datetime.datetime.now().strftime('%A')

    context = specific_context.get(activity_theme, activity_theme) if specific_context else activity_theme
    
    # 요일, 날짜, 시간에 따른 추가 컨텍스트 삽입 (AI-ish)
    commit_message = selected_template.format(
        context=context,
        date=current_date,
        day=current_day,
        time=datetime.datetime.now().strftime('%H:%M')
    )
    return commit_message

def perform_commit(config):
    """더미 변경 사항을 커밋하고 GitHub에 푸시합니다."""
    print_log("커밋 작업을 시작합니다.")
    current_datetime = datetime.datetime.now()
    activity_theme = config.get('activity_theme', '기타')
    specific_context = config.get('specific_activity_context', {})

    if not create_dummy_change(activity_theme, current_datetime):
        print_log("더미 파일 변경에 실패하여 커밋을 건너뜕니다.", "ERROR")
        return

    commit_message = generate_commit_message(activity_theme, specific_context)

    if not run_git_command(['add', '.']):
        print_log("파일 스테이징에 실패했습니다.", "ERROR")
        return
    if not run_git_command(['commit', '-m', commit_message]):
        print_log("커밋 생성에 실패했습니다.", "ERROR")
        return
    
    git_token = get_git_token()
    username = config['github_username']
    repo_name = config['github_repo_name']
    remote_url = f"https://oauth2:{git_token}@github.com/{username}/{repo_name}.git"
    # 원격 URL이 올바르게 설정되었는지 확인
    current_remote_result = subprocess.run(['git', 'remote', 'get-url', 'origin'], cwd=REPO_DIR, capture_output=True, text=True, encoding='utf-8')
    current_remote = current_remote_result.stdout.strip()

    # Check if the current remote URL is the one we intend to use for authenticated push.
    # This check is basic and might need more robustness for edge cases.
    if not (current_remote.startswith(f"https://oauth2:{git_token}@github.com/{username}/") and current_remote.endswith(f"/{repo_name}.git")):
        print_log(f"원격 저장소 URL이 설정되지 않았거나 잘못되었습니다. 다시 설정합니다.", "WARN")
        # First try to remove existing origin if it's incorrect or to avoid 'remote origin already exists' error
        run_git_command(['remote', 'remove', 'origin']) # This might fail if origin doesn't exist, ignore error
        run_git_command(['remote', 'add', 'origin', remote_url]) # Add/update if needed

    if not run_git_command(['push', 'origin', 'main']): # Assume 'main' branch
        print_log("GitHub에 푸시하는 데 실패했습니다. 원격 리포지토리가 존재하는지, PAT 권한이 충분한지 확인하세요.", "ERROR")
        return

    print_log(f"성공적으로 커밋하고 푸시했습니다! 메시지: '{commit_message}'")

def cleanup_repo(config):
    """지정된 기간이 지나면 로컬 리포지토리와 커밋 이력을 삭제합니다."""
    cleanup_days = config.get('cleanup_after_days', 0)
    if cleanup_days <= 0:
        return

    repo_creation_date_str = config.get('repo_creation_date')
    if not repo_creation_date_str:
        print_log("리포지토리 생성 날짜 정보가 없습니다. 클린업을 건너뜁니다.", "WARN")
        return

    repo_creation_date = datetime.datetime.fromisoformat(repo_creation_date_str)
    if (datetime.datetime.now() - repo_creation_date).days >= cleanup_days:
        print_log(f"{cleanup_days}일이 경과하여 로컬 리포지토리 '{REPO_DIR}'를 삭제합니다.", "WARN")
        if os.path.exists(REPO_DIR):
            try:
                shutil.rmtree(REPO_DIR)
                print_log(f"'{REPO_DIR}' 디렉토리와 모든 내용을 삭제했습니다.")
                # 클린업 후 config의 생성 날짜를 업데이트하여 다음 실행 시 새롭게 시작하도록 함
                config['repo_creation_date'] = datetime.datetime.now().isoformat()
                save_config(config)
            except OSError as e:
                print_log(f"리포지토리 삭제 중 오류 발생: {e}", "ERROR")
        else:
            print_log(f"'{REPO_DIR}' 디렉토리가 이미 존재하지 않습니다.")
    else:
        remaining_days = cleanup_days - (datetime.datetime.now() - repo_creation_date).days
        print_log(f"리포지토리 클린업까지 {remaining_days}일 남았습니다.")

def schedule_jobs(config):
    """설정된 스케줄에 따라 커밋 작업을 예약합니다."""
    print_log("커밋 스케줄을 설정합니다.")
    commit_schedule = config.get('commit_schedule', {})
    
    days_of_week = {
        "monday": schedule.every().monday,
        "tuesday": schedule.every().tuesday,
        "wednesday": schedule.every().wednesday,
        "thursday": schedule.every().thursday,
        "friday": schedule.every().friday,
        "saturday": schedule.every().saturday,
        "sunday": schedule.every().sunday,
    }

    job_count = 0
    for day, times in commit_schedule.items():
        if day in days_of_week:
            for time_str in times:
                try:
                    days_of_week[day].at(time_str).do(perform_commit, config=config)
                    print_log(f"매주 {day.capitalize()} {time_str}에 커밋 작업이 예약되었습니다.")
                    job_count += 1
                except Exception as e:
                    print_log(f"스케줄링 실패: {day} {time_str} - {e}", "ERROR")
        else:
            print_log(f"알 수 없는 요일: {day}. 스케줄링을 건너뜕니다.", "WARN")

    if job_count == 0:
        print_log("설정된 커밋 스케줄이 없습니다. 매 시간마다 한 번씩 커밋을 시도합니다.", "WARN")
        schedule.every(1).hour.do(perform_commit, config=config)
        print_log("기본값으로 매 시간 커밋 작업을 예약했습니다.")

def main():
    print_log("Git잔디GPT: 오또의 자율주행 커밋봇을 시작합니다.")
    load_dotenv() # .env 파일에서 환경 변수 로드

    config = load_config()
    
    git_token = get_git_token() # PAT 확인

    if not init_repo(config, git_token):
        print_log("리포지토리 초기화에 실패했습니다. 설정을 확인하거나 수동으로 리포지토리를 생성해주세요.", "ERROR")
        sys.exit(1)

    schedule_jobs(config)

    print_log("오또의 자율주행 커밋봇이 잔디 심기를 시작합니다. CTRL+C를 눌러 종료하세요.")
    while True:
        schedule.run_pending()
        cleanup_repo(config) # 매번 스케줄러가 돌 때마다 클린업 체크
        time.sleep(1) # 1초마다 스케줄 확인

if __name__ == '__main__':
    main()