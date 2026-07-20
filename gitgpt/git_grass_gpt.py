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
# 이름: Git잔디GPT - 오또의 자율주행 커밋봇
# 설명: GitHub 잔디밭을 자동으로 채워주는 봇. 학습, 게임, 휴가 등 다양한 테마로 커밋 메시지를 생성하고,
#       더미 파일을 수정하여 커밋을 생성하고 GitHub에 푸시합니다.
#       .env 파일에 GitHub Personal Access Token(PAT)이 필요하며, config.json을 통해 스케줄 및 테마 설정 가능.

# 설정 파일 및 리포지토리 관련 경로
CONFIG_FILE = 'config.json'  # 봇의 설정 정보를 저장하는 파일
REPO_DIR = 'otto_commit_repo' # 더미 Git 리포지토리가 생성될 로컬 디렉토리
DUMMY_FILE_NAME = 'otto_activity_log.md' # 커밋에 사용될 더미 파일 이름
DUMMY_FILE_PATH = os.path.join(REPO_DIR, DUMMY_FILE_NAME) # 더미 파일의 전체 경로

# 커밋 메시지 템플릿: 활동 테마별로 다양한 커밋 메시지 패턴을 제공
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
    """
    콘솔에 로그 메시지를 출력합니다.
    Args:
        message (str): 출력할 메시지.
        level (str): 로그 레벨 (INFO, WARN, ERROR, DEBUG).
    """
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} [{level}] {message}")

def load_config():
    """
    설정 파일을 로드하거나, 없으면 기본 설정으로 생성하고 사용자 입력을 받습니다.
    Returns:
        dict: 로드되거나 새로 생성된 설정 딕셔너리.
    """
    print_log(f"설정 파일 '{CONFIG_FILE}'을(를) 로드 시도합니다.")
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print_log(f"설정 파일을 성공적으로 로드했습니다: '{CONFIG_FILE}'")
        except json.JSONDecodeError as e:
            print_log(f"설정 파일 '{CONFIG_FILE}' 형식이 잘못되었습니다: {e}. 새 설정을 생성합니다.", "ERROR")
            config = {} # 오류 시 새 설정 생성을 위해 config 초기화
        except IOError as e:
            print_log(f"설정 파일 '{CONFIG_FILE}' 읽기 중 오류 발생: {e}. 새 설정을 생성합니다.", "ERROR")
            config = {}
    
    if not config: # 파일이 없거나 로드에 실패한 경우
        print_log("설정 파일이 없거나 로드에 실패했습니다. 새로운 설정을 생성합니다.", "WARN")
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

        print_log("--- 초기 설정 가이드 시작 ---", "INFO")
        
        # GitHub 사용자 이름 입력
        while not config["github_username"]:
            username_input = input("GitHub 사용자 이름 (예: your-username): ").strip()
            if username_input:
                config["github_username"] = username_input
            else:
                print_log("GitHub 사용자 이름은 필수입니다. 다시 입력해주세요.", "WARN")

        # GitHub 저장소 이름 입력
        repo_name_input = input(f"커밋을 올릴 GitHub 저장소 이름 (기본값: {config['github_repo_name']}): ").strip()
        if repo_name_input:
            config["github_repo_name"] = repo_name_input
        print_log(f"GitHub 저장소 이름이 '{config['github_repo_name']}'(으)로 설정되었습니다.")
        
        # 테마 활동 선택
        print_log(f"테마 활동을 선택하세요: {', '.join(COMMIT_TEMPLATES.keys())}")
        selected_theme = input(f"선택할 테마 (기본값: {config['activity_theme']}): ").strip()
        if selected_theme and selected_theme in COMMIT_TEMPLATES:
            config["activity_theme"] = selected_theme
            print_log(f"테마가 '{config['activity_theme']}'(으)로 설정되었습니다.")
        elif selected_theme:
            print_log(f"알 수 없는 테마 '{selected_theme}'입니다. 기본값 '{config['activity_theme']}'으로 설정합니다.", "WARN")
        else:
             print_log(f"테마 선택을 건너뛰어 기본값 '{config['activity_theme']}'으로 설정합니다.", "INFO")

        # 특정 활동 컨텍스트 입력
        if config["activity_theme"] in ["학습", "게임"]:
            context_prompt = f"{config['activity_theme']} 활동에 대한 구체적인 내용 (예: Python, Stardew Valley): "
            context_input = input(context_prompt).strip()
            if context_input: 
                config["specific_activity_context"][config["activity_theme"]] = context_input
                print_log(f"'{config['activity_theme']}' 컨텍스트가 '{context_input}'(으)로 설정되었습니다.")
            else:
                print_log(f"'{config['activity_theme']}' 컨텍스트 입력이 없어 기본값을 사용합니다.")
        
        # 자동 삭제 기능 설정
        print_log("커밋 자동 삭제 기능을 설정합니다. (0 입력시 비활성화)", "INFO")
        try:
            cleanup_input = input(f"몇 일 후 가짜 커밋 및 잔디 이력을 자동으로 삭제할까요? (기본값: {config['cleanup_after_days']}): ").strip()
            if cleanup_input:
                cleanup_days = int(cleanup_input)
                if cleanup_days < 0:
                    print_log("자동 삭제 일수는 0보다 크거나 같아야 합니다. 비활성화합니다.", "WARN")
                    config["cleanup_after_days"] = 0
                else:
                    config["cleanup_after_days"] = cleanup_days
                    print_log(f"자동 삭제 기능이 {cleanup_days}일 후 활성화됩니다. (0은 비활성화)")
            else:
                print_log(f"자동 삭제 설정 건너뛰어 기본값 '{config['cleanup_after_days']}'(으)로 유지합니다.")
        except ValueError:
            print_log("유효하지 않은 숫자입니다. 자동 삭제 기능을 비활성화합니다.", "WARN")
            config["cleanup_after_days"] = 0
        
        print_log("--- 초기 설정 완료. 설정 파일을 저장합니다. ---", "INFO")
        save_config(config)
    
    return config

def save_config(config):
    """
    설정 파일을 저장합니다.
    Args:
        config (dict): 저장할 설정 딕셔너리.
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print_log(f"설정 파일을 성공적으로 저장했습니다: '{CONFIG_FILE}'")
    except IOError as e:
        print_log(f"설정 파일 '{CONFIG_FILE}' 저장 중 오류 발생: {e}", "ERROR")

def get_git_token():
    """
    환경 변수에서 GitHub Personal Access Token(PAT)을 로드합니다.
    PAT는 .env 파일에 GITHUB_TOKEN="YOUR_PAT" 형식으로 저장되어야 합니다.
    Returns:
        str: GitHub PAT.
    Raises:
        SystemExit: PAT가 설정되지 않은 경우 프로그램 종료.
    """
    print_log("환경 변수 'GITHUB_TOKEN'을 로드 시도합니다.")
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print_log("환경 변수 'GITHUB_TOKEN'이 설정되지 않았습니다.", "ERROR")
        print_log("'.env' 파일을 확인하거나 시스템 환경 변수에 GitHub Personal Access Token(PAT)을 설정해주세요.", "ERROR")
        print_log("GitHub PAT는 리포지토리에 푸시하기 위해 필요하며 'repo' 스코프 권한이 있어야 합니다.", "ERROR")
        sys.exit(1)
    print_log("GitHub PAT를 성공적으로 로드했습니다.")
    return token

def run_git_command(args, cwd=REPO_DIR, check_output=False, error_on_stderr=True):
    """
    Git 명령어를 실행하고 결과를 반환합니다.
    Args:
        args (list): Git 명령어 및 인자 리스트 (예: ['init', '--bare']).
        cwd (str): 명령어를 실행할 작업 디렉토리.
        check_output (bool): 표준 출력을 반환할지 여부. True면 stdout 반환, False면 성공 여부만 반환.
        error_on_stderr (bool): stderr에 내용이 있을 경우 오류로 간주할지 여부.
    Returns:
        bool or str: 명령어가 성공하고 check_output이 True면 stdout, 아니면 성공 여부(True/False).
    """
    full_command = ['git'] + args
    command_str = ' '.join(full_command)
    print_log(f"Git 명령어 실행: {command_str} (in {cwd})", "DEBUG")
    try:
        result = subprocess.run(
            full_command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,  # 0이 아닌 종료 코드는 CalledProcessError 발생
            encoding='utf-8',
            errors='replace' # 인코딩 오류 방지
        )

        if result.stdout:
            print_log(f"Git STDOUT: {result.stdout.strip()}", "DEBUG")
        
        # 특정 경고 메시지는 무시
        ignore_stderr_messages = [
            "Already up to date",
            "nothing to commit, working tree clean",
            "couldn't find remote ref main" # 초기 푸시 시 원격에 main이 없을 수 있음 (upstream 설정)
        ]

        if result.stderr:
            # 무시할 메시지가 있는지 확인
            ignored = any(msg in result.stderr for msg in ignore_stderr_messages)
            if ignored:
                print_log(f"Git STDERR (ignored): {result.stderr.strip()}", "DEBUG")
            elif error_on_stderr:
                print_log(f"Git STDERR: {result.stderr.strip()}", "WARN") # STDERR이 있지만 치명적이지 않을 수 있음
                # return False # 치명적인 에러로 간주할 경우 False 반환

        if check_output:
            return result.stdout.strip()
        return True

    except subprocess.CalledProcessError as e:
        print_log(f"Git 명령어 실행 실패: '{command_str}'", "ERROR")
        print_log(f"STDOUT: {e.stdout.strip()}", "ERROR")
        print_log(f"STDERR: {e.stderr.strip()}", "ERROR")
        return False
    except FileNotFoundError:
        print_log("Git 실행 파일을 찾을 수 없습니다. Git이 설치되어 있고 시스템 PATH에 추가되어 있는지 확인하세요.", "ERROR")
        sys.exit(1)
    except Exception as e:
        print_log(f"알 수 없는 오류로 Git 명령어 실행 실패: '{command_str}' - {e}", "ERROR")
        return False

def init_repo(config, git_token):
    """
    더미 Git 리포지토리를 초기화하고 설정합니다.
    - 로컬 디렉토리 생성
    - Git 초기화
    - 사용자 정보 설정
    - 첫 더미 파일 생성 및 커밋
    - 원격 저장소 추가 및 초기 푸시 시도
    Args:
        config (dict): 설정 딕셔너리.
        git_token (str): GitHub PAT.
    Returns:
        bool: 리포지토리 초기화 및 설정 성공 여부.
    """
    username = config['github_username']
    repo_name = config['github_repo_name']
    
    print_log(f"리포지토리 디렉토리 '{REPO_DIR}' 존재 여부 확인.")
    if not os.path.exists(REPO_DIR):
        print_log(f"'{REPO_DIR}' 디렉토리가 없어 생성합니다.")
        try:
            os.makedirs(REPO_DIR)
        except OSError as e:
            print_log(f"'{REPO_DIR}' 디렉토리 생성 실패: {e}", "ERROR")
            return False

    git_init_needed = not os.path.exists(os.path.join(REPO_DIR, '.git'))
    
    if git_init_needed:
        print_log(f"'{REPO_DIR}'에 Git 리포지토리를 초기화합니다.")
        if not run_git_command(['init']): return False
        
        print_log(f"Git 사용자 이름 '{username}' 설정.")
        if not run_git_command(['config', 'user.name', username]): return False
        
        print_log(f"Git 사용자 이메일 '{username}@users.noreply.github.com' 설정.")
        if not run_git_command(['config', 'user.email', f"{username}@users.noreply.github.com"]): return False
        
        print_log(f"초기 더미 파일 '{DUMMY_FILE_NAME}'을(를) 생성합니다.")
        try:
            with open(DUMMY_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(f"# Otto's Autonomous Commit Log for {username}/{repo_name}\n\n")
                f.write(f"Initial commit by Otto on {datetime.datetime.now().strftime('%Y-%m-%d')}.\n")
            print_log(f"초기 더미 파일 '{DUMMY_FILE_NAME}' 생성 완료.")
        except IOError as e:
            print_log(f"초기 더미 파일 '{DUMMY_FILE_NAME}' 생성 실패: {e}", "ERROR")
            return False

        print_log("초기 더미 파일 스테이징 및 커밋을 생성합니다.")
        if not run_git_command(['add', '.']): return False
        if not run_git_command(['commit', '-m', 'feat: Initial commit by Otto, autonomous commit bot']): return False
        
        print_log(f"원격 저장소 'origin'을 설정합니다: github.com/{username}/{repo_name}.git")
        remote_url = f"https://oauth2:{git_token}@github.com/{username}/{repo_name}.git"
        if not run_git_command(['remote', 'add', 'origin', remote_url]): return False
        
        print_log("기본 브랜치 이름을 'main'으로 설정합니다.")
        if not run_git_command(['branch', '-M', 'main']): return False

        print_log("초기 커밋을 원격 저장소에 푸시하고 업스트림을 설정합니다. (첫 푸시)", "INFO")
        # 첫 푸시는 -u (upstream) 옵션이 필요할 수 있습니다.
        if not run_git_command(['push', '-u', 'origin', 'main']):
            print_log(f"**주의**: GitHub에 '{username}/{repo_name}' 리포지토리가 미리 생성되어 있어야 합니다.", "WARN")
            print_log(f"**주의**: 첫 푸시가 실패했습니다. 수동으로 'cd {REPO_DIR}' 이동 후 'git push -u origin main'을 실행해주세요.", "WARN")
            print_log("이후 다시 프로그램을 실행하면 정상 작동합니다.", "WARN")
            return False # 첫 푸시 실패 시, 사용자의 수동 개입이 필요하므로 False 반환
        
        print_log(f"'{repo_name}' 리포지토리 초기화 및 첫 커밋/푸시 완료. 이제 자동으로 잔디를 심을 준비가 되었습니다.")
    else:
        print_log(f"'{REPO_DIR}'에 Git 리포지토리가 이미 존재합니다. 기존 리포지토리를 사용합니다.")
        # 기존 리포지토리의 원격 URL을 업데이트하거나 확인
        configured_remote_url = f"https://oauth2:{git_token}@github.com/{username}/{repo_name}.git"
        current_remote = run_git_command(['remote', 'get-url', 'origin'], check_output=True)
        if current_remote and current_remote != configured_remote_url:
            print_log(f"기존 원격 저장소 URL이 다릅니다. '{configured_remote_url}'(으)로 업데이트합니다.", "WARN")
            run_git_command(['remote', 'set-url', 'origin', configured_remote_url])
        elif not current_remote:
            print_log(f"원격 저장소 'origin'이 설정되지 않았습니다. '{configured_remote_url}'(으)로 추가합니다.", "WARN")
            run_git_command(['remote', 'add', 'origin', configured_remote_url])
        else:
            print_log(f"원격 저장소 'origin'이 올바르게 설정되어 있습니다.")
    return True

def create_dummy_change(activity_theme, current_datetime):
    """
    더미 파일에 변경 사항을 추가합니다.
    파일이 없으면 생성하고, 있으면 내용을 추가하거나 수정합니다.
    Args:
        activity_theme (str): 현재 활동 테마 (로그 메시지에 사용).
        current_datetime (datetime.datetime): 현재 시간 객체.
    Returns:
        bool: 변경 사항 추가 성공 여부.
    """
    print_log(f"더미 파일 '{DUMMY_FILE_NAME}'에 변경 사항을 생성합니다.")
    
    if not os.path.exists(REPO_DIR):
        print_log(f"리포지토리 디렉토리 '{REPO_DIR}'가 존재하지 않습니다. 생성합니다.", "WARN")
        try:
            os.makedirs(REPO_DIR)
        except OSError as e:
            print_log(f"리포지토리 디렉토리 '{REPO_DIR}' 생성 실패: {e}", "ERROR")
            return False

    change_log_entry = f"- {activity_theme} 관련 활동 ({current_datetime.strftime('%Y-%m-%d %H:%M:%S')})\n"
    
    try:
        if not os.path.exists(DUMMY_FILE_PATH):
            print_log(f"더미 파일 '{DUMMY_FILE_NAME}'이(가) 없어 새로 생성하고 내용을 추가합니다.")
            with open(DUMMY_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(f"# Otto's Activity Log\n\n")
                f.write(change_log_entry)
        else:
            mode = random.choice(['append', 'modify'])
            if mode == 'append':
                print_log(f"더미 파일 '{DUMMY_FILE_NAME}'에 새로운 활동 로그를 추가합니다.")
                with open(DUMMY_FILE_PATH, 'a', encoding='utf-8') as f:
                    f.write(change_log_entry)
            elif mode == 'modify':
                print_log(f"더미 파일 '{DUMMY_FILE_NAME}'의 기존 내용을 수정합니다 (랜덤 위치에 삽입).")
                with open(DUMMY_FILE_PATH, 'r+', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) > 2: # 헤더와 최소 한 줄이 있다고 가정
                        insert_idx = random.randint(2, len(lines)) # 2번째 줄 이후부터 삽입
                        lines.insert(insert_idx, change_log_entry)
                    else:
                        lines.append(change_log_entry) # 파일이 너무 짧으면 그냥 추가
                    f.seek(0)
                    f.writelines(lines)
                    f.truncate() # 파일 크기를 현재 위치까지 자름
        print_log(f"더미 파일 '{DUMMY_FILE_NAME}'에 변경 사항을 성공적으로 추가했습니다.")
        return True
    except IOError as e:
        print_log(f"더미 파일 '{DUMMY_FILE_NAME}' 변경 중 오류 발생: {e}", "ERROR")
        return False
    except Exception as e:
        print_log(f"예상치 못한 오류로 더미 파일 변경 실패: {e}", "ERROR")
        return False

def generate_commit_message(activity_theme, specific_context=None):
    """
    현재 활동 테마에 맞는 커밋 메시지를 생성합니다.
    Args:
        activity_theme (str): 설정된 활동 테마 (예: "학습", "게임").
        specific_context (dict, optional): 특정 테마에 대한 구체적인 컨텍스트 딕셔너리.
    Returns:
        str: 생성된 커밋 메시지.
    """
    print_log(f"테마 '{activity_theme}'에 맞는 커밋 메시지를 생성합니다.")
    templates = COMMIT_TEMPLATES.get(activity_theme, COMMIT_TEMPLATES["기타"])
    selected_template = random.choice(templates)

    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    current_day = datetime.datetime.now().strftime('%A')

    # 특정 컨텍스트가 있다면 사용, 없으면 테마 자체를 컨텍스트로 사용
    context = specific_context.get(activity_theme, activity_theme) if specific_context else activity_theme
    
    commit_message = selected_template.format(
        context=context,
        date=current_date,
        day=current_day,
        time=datetime.datetime.now().strftime('%H:%M')
    )
    print_log(f"생성된 커밋 메시지: '{commit_message}'")
    return commit_message

def perform_commit(config):
    """
    더미 변경 사항을 커밋하고 GitHub에 푸시합니다.
    Args:
        config (dict): 설정 딕셔너리.
    """
    print_log("--- 커밋 작업을 시작합니다 ---", "INFO")
    current_datetime = datetime.datetime.now()
    activity_theme = config.get('activity_theme', '기타')
    specific_context = config.get('specific_activity_context', {})

    if not create_dummy_change(activity_theme, current_datetime):
        print_log("더미 파일 변경에 실패하여 커밋 작업을 건너뜁니다.", "ERROR")
        return

    commit_message = generate_commit_message(activity_theme, specific_context)

    print_log(f"변경 사항을 스테이징합니다 ('git add .').")
    if not run_git_command(['add', '.']):
        print_log("파일 스테이징에 실패했습니다. 커밋을 중단합니다.", "ERROR")
        return
    
    print_log(f"커밋을 생성합니다 ('git commit -m \"{commit_message}\"').")
    if not run_git_command(['commit', '-m', commit_message]):
        print_log("커밋 생성에 실패했습니다. 푸시를 중단합니다.", "ERROR")
        return
    
    git_token = get_git_token()
    username = config['github_username']
    repo_name = config['github_repo_name']
    remote_url = f"https://oauth2:{git_token}@github.com/{username}/{repo_name}.git"

    print_log("원격 저장소 'origin'의 URL을 확인 및 설정합니다.")
    # 현재 원격 URL 가져오기
    try:
        current_remote_url = run_git_command(['remote', 'get-url', 'origin'], check_output=True)
    except Exception: # remote get-url 실패 시 원격이 없다고 간주
        current_remote_url = None

    if not current_remote_url:
        print_log(f"원격 저장소 'origin'이 설정되어 있지 않습니다. '{remote_url}'(으)로 추가합니다.", "WARN")
        if not run_git_command(['remote', 'add', 'origin', remote_url]):
            print_log("원격 저장소 추가에 실패했습니다. 푸시를 중단합니다.", "ERROR")
            return
    elif current_remote_url != remote_url:
        print_log(f"현재 원격 저장소 URL이 다릅니다. '{current_remote_url}'에서 '{remote_url}'(으)로 업데이트합니다.", "WARN")
        if not run_git_command(['remote', 'set-url', 'origin', remote_url]):
            print_log("원격 저장소 URL 업데이트에 실패했습니다. 푸시를 중단합니다.", "ERROR")
            return
    else:
        print_log("원격 저장소 'origin'이 올바르게 설정되어 있습니다.")

    print_log("GitHub에 커밋을 푸시합니다 ('git push origin main').")
    if not run_git_command(['push', 'origin', 'main']):
        print_log("GitHub에 푸시하는 데 실패했습니다. 원격 리포지토리가 존재하는지, PAT 권한이 충분한지 확인하세요.", "ERROR")
        print_log("인증 오류가 발생하면, GitHub PAT를 재생성하거나 'git remote set-url origin <새로운 PAT 포함 URL>'을 수동으로 실행해보세요.", "INFO")
        return

    print_log(f"--- 성공적으로 커밋하고 푸시했습니다! 메시지: '{commit_message}' ---", "INFO")

def cleanup_repo(config):
    """
    지정된 기간이 지나면 로컬 리포지토리와 커밋 이력을 삭제합니다.
    Args:
        config (dict): 설정 딕셔너리.
    """
    cleanup_days = config.get('cleanup_after_days', 0)
    if cleanup_days <= 0:
        print_log("자동 삭제 기능이 비활성화되어 있습니다 (cleanup_after_days: 0).", "DEBUG")
        return

    repo_creation_date_str = config.get('repo_creation_date')
    if not repo_creation_date_str:
        print_log("리포지토리 생성 날짜 정보가 없습니다. 클린업을 건너뜁니다.", "WARN")
        # 다음 실행 시 다시 설정되도록 현재 날짜로 업데이트
        config['repo_creation_date'] = datetime.datetime.now().isoformat()
        save_config(config)
        return

    try:
        repo_creation_date = datetime.datetime.fromisoformat(repo_creation_date_str)
        time_since_creation = datetime.datetime.now() - repo_creation_date

        if time_since_creation.days >= cleanup_days:
            print_log(f"{cleanup_days}일이 경과하여 로컬 리포지토리 '{REPO_DIR}'를 삭제합니다.", "WARN")
            if os.path.exists(REPO_DIR):
                try:
                    shutil.rmtree(REPO_DIR)
                    print_log(f"'{REPO_DIR}' 디렉토리와 모든 내용을 성공적으로 삭제했습니다.")
                    # 클린업 후 config의 생성 날짜를 업데이트하여 다음 실행 시 새롭게 시작하도록 함
                    config['repo_creation_date'] = datetime.datetime.now().isoformat()
                    save_config(config)
                    print_log("새로운 리포지토리 생성 날짜로 설정 파일을 업데이트했습니다.", "INFO")
                except OSError as e:
                    print_log(f"리포지토리 삭제 중 오류 발생: {e}", "ERROR")
            else:
                print_log(f"'{REPO_DIR}' 디렉토리가 이미 존재하지 않습니다. (삭제 작업 건너뛰김)", "DEBUG")
        else:
            remaining_days = cleanup_days - time_since_creation.days
            print_log(f"리포지토리 클린업까지 {remaining_days}일 남았습니다. (설정: {cleanup_days}일)", "INFO")
    except ValueError as e:
        print_log(f"저장된 리포지토리 생성 날짜 형식 오류: {e}. 클린업을 건너뜁니다.", "ERROR")
        # 오류 발생 시 repo_creation_date를 현재 시점으로 업데이트하여 재시도 방지
        config['repo_creation_date'] = datetime.datetime.now().isoformat()
        save_config(config)
    except Exception as e:
        print_log(f"알 수 없는 오류로 클린업 기능 실패: {e}", "ERROR")

def schedule_jobs(config):
    """
    설정된 스케줄에 따라 커밋 작업을 예약합니다.
    Args:
        config (dict): 설정 딕셔너리.
    """
    print_log("--- 커밋 스케줄을 설정합니다 ---", "INFO")
    commit_schedule = config.get('commit_schedule', {})
    
    # 요일별 스케줄러 매핑
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
        if day.lower() in days_of_week: # 소문자로 변환하여 비교
            for time_str in times:
                try:
                    # 시간 형식 검증 (HH:MM)
                    datetime.datetime.strptime(time_str, '%H:%M')
                    days_of_week[day.lower()].at(time_str).do(perform_commit, config=config)
                    print_log(f"매주 {day.capitalize()} {time_str}에 커밋 작업이 예약되었습니다.", "INFO")
                    job_count += 1
                except ValueError:
                    print_log(f"잘못된 시간 형식입니다: '{time_str}'. (예상: HH:MM) 매주 {day.capitalize()} 스케줄링을 건너뜁니다.", "ERROR")
                except Exception as e:
                    print_log(f"스케줄링 실패: 매주 {day.capitalize()} {time_str} - {e}", "ERROR")
        else:
            print_log(f"알 수 없는 요일: '{day}'. 해당 스케줄링을 건너뜁니다.", "WARN")

    if job_count == 0:
        print_log("설정된 커밋 스케줄이 없습니다. 기본값으로 매 시간마다 한 번씩 커밋을 시도합니다.", "WARN")
        schedule.every(1).hour.do(perform_commit, config=config)
        print_log("기본값으로 매 시간 커밋 작업을 예약했습니다.", "INFO")
    else:
        print_log(f"총 {job_count}개의 커밋 스케줄이 설정되었습니다.", "INFO")

def main():
    """
    봇의 메인 실행 함수. 환경 변수 로드, 설정 로드/생성, 리포지토리 초기화, 스케줄 설정 및 루프를 담당합니다.
    """
    print_log("--- Git잔디GPT: 오또의 자율주행 커밋봇을 시작합니다 ---", "INFO")
    
    print_log(".env 파일에서 환경 변수를 로드합니다.")
    load_dotenv() # .env 파일에서 환경 변수 로드

    config = load_config() # 설정 로드 또는 생성
    
    git_token = get_git_token() # GitHub PAT 확인 및 로드

    print_log("로컬 Git 리포지토리 초기화 및 설정을 시작합니다.")
    if not init_repo(config, git_token):
        print_log("리포지토리 초기화 또는 첫 푸시에 실패했습니다. 위에 출력된 오류 메시지를 확인하고 조치해주세요.", "ERROR")
        print_log("프로그램을 종료합니다.", "ERROR")
        sys.exit(1)

    schedule_jobs(config) # 커밋 스케줄 설정

    print_log("--- 오또의 자율주행 커밋봇이 잔디 심기를 시작합니다. CTRL+C를 눌러 종료하세요. ---", "INFO")
    while True:
        try:
            schedule.run_pending() # 예약된 작업을 실행
            cleanup_repo(config) # 매번 스케줄러가 돌 때마다 클린업 체크
            time.sleep(1) # 1초마다 스케줄 확인
        except KeyboardInterrupt:
            print_log("사용자에 의해 봇이 종료되었습니다. 안녕히 계세요!", "INFO")
            break
        except Exception as e:
            print_log(f"메인 루프에서 예상치 못한 오류 발생: {e}", "ERROR")
            print_log("봇이 계속 실행됩니다. 오류가 반복되면 프로그램을 재시작해주세요.", "WARN")
            time.sleep(5) # 오류 발생 시 잠시 대기 후 재시도

if __name__ == '__main__':
    main()
