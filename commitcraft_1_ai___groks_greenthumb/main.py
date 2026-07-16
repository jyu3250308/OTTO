import os
import subprocess
import datetime
import random
import openai
import time
from dotenv import load_dotenv

# --- 환경 변수 로드 및 초기 설정 ---
# .env 파일에서 환경 변수를 로드합니다. 이 함수는 스크립트 실행 시 가장 먼저 호출되어야 합니다.
load_dotenv()

# --- 전역 설정 변수 ---
# OpenAI API 키: .env 파일 또는 시스템 환경 변수에서 가져옵니다.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# GitHub 저장소 경로: 잔디밭을 조각할 Git 저장소의 로컬 경로입니다.
# 예: GITHUB_REPO_PATH="/Users/your_user/Documents/your_repo"
GITHUB_REPO_PATH = os.getenv("GITHUB_REPO_PATH")

# AI 모델 선택: OpenAI의 다양한 모델 중 하나를 선택합니다.
# "gpt-3.5-turbo", "gpt-4-turbo", "gpt-4o" 등이 유효합니다.
OPENAI_MODEL = "gpt-4o"  # 최신 모델로 변경하여 성능 향상 기대

# 일일 목표 커밋 수: $1 기여 목표를 위한 기준 커밋 수입니다.
# 10 커밋당 $1 가치로 시뮬레이션됩니다.
TARGET_DAILY_COMMITS = 10  # 대략 10 커밋 = $1 기여

# --- 유틸리티 함수: Git 저장소 관리 ---
def _run_git_command(repo_path: str, command: list[str], env: dict = None, suppress_output: bool = False) -> tuple[bool, str]:
    """
    지정된 저장소 경로에서 Git 명령을 실행합니다.
    Args:
        repo_path (str): Git 저장소의 로컬 경로.
        command (list[str]): 실행할 Git 명령과 인자 목록 (예: ["git", "commit", "-m", "message"]).
        env (dict, optional): subprocess에 전달할 환경 변수 딕셔너리. 기본값은 None.
        suppress_output (bool, optional): 성공 시 Git 명령의 표준 출력을 반환하지 않을지 여부. 기본값은 False.
                                        주로 성공 여부만 필요한 경우 (예: config 설정) 사용합니다.
    Returns:
        tuple[bool, str]: 명령 성공 여부 (True/False)와 출력/오류 메시지.
    """
    full_command = ["git"] + command
    command_str = " ".join(full_command)
    
    # print(f"[DEBUG] Git 명령 실행 시도: cd {repo_path} && {command_str}") # 디버깅용

    try:
        process = subprocess.run(
            full_command,
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True,
            env=env
        )
        if suppress_output:
            return True, ""
        return True, process.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_message = (
            f"ERROR: Git 명령 실패: '{command_str}'\n"
            f"    에러 코드: {e.returncode}\n"
            f"    STDOUT: {e.stdout.strip()}\n"
            f"    STDERR: {e.stderr.strip()}"
        )
        print(f"[ERROR] {error_message}")
        return False, error_message
    except FileNotFoundError:
        error_message = "ERROR: Git 실행 파일을 찾을 수 없습니다. Git이 설치되어 있고 PATH에 추가되었는지 확인하세요."
        print(f"[ERROR] {error_message}")
        return False, error_message
    except Exception as e:
        error_message = f"ERROR: 예상치 못한 Git 명령 실행 오류 발생: {e}"
        print(f"[ERROR] {error_message}")
        return False, error_message

def setup_repository(repo_path: str, is_dummy: bool) -> bool:
    """
    Git 저장소를 설정합니다. 더미 저장소인 경우 새로 생성 및 초기화하고,
    실제 저장소인 경우 유효성을 검사합니다.
    Args:
        repo_path (str): 저장소를 설정할 경로.
        is_dummy (bool): 더미 저장소인지 여부.
    Returns:
        bool: 저장소 설정 성공 여부.
    """
    repo_type = "더미" if is_dummy else "실제"
    print(f"\n[STEP] {repo_type} 저장소 설정 확인 및 준비 중: '{repo_path}'")

    if not os.path.exists(repo_path):
        if not is_dummy:
            print(f"[ERROR] 지정된 실제 저장소 경로 '{repo_path}'를 찾을 수 없습니다. 스크립트를 종료합니다.")
            return False
        
        try:
            os.makedirs(repo_path, exist_ok=True)
            print(f"  [INFO] {repo_type} 저장소 디렉토리 '{repo_path}' 생성 완료.")
        except OSError as e:
            print(f"[ERROR] {repo_type} 저장소 디렉토리 생성 실패: {e}")
            return False

        print(f"  [INFO] {repo_type} 저장소 '{repo_path}' 초기화 중...")
        success, output = _run_git_command(repo_path, ["init"])
        if not success:
            print(f"[ERROR] Git 저장소 초기화 실패. {output}")
            return False
        print("  [INFO] Git 저장소 초기화 성공.")

        # Git 사용자 정보 설정
        print("  [INFO] Git 사용자 정보 설정 중...")
        success_email, _ = _run_git_command(repo_path, ["config", "user.email", "commitcraft@example.com"], suppress_output=True)
        success_name, _ = _run_git_command(repo_path, ["config", "user.name", "CommitCraft Bot"], suppress_output=True)
        if not success_email or not success_name:
            print("[ERROR] Git 사용자 정보 설정 실패. (이메일/이름)")
            return False
        print("  [INFO] Git 사용자 정보 설정 완료 (commitcraft@example.com, CommitCraft Bot).")

        # 초기 커밋 생성
        readme_path = os.path.join(repo_path, "README.md")
        try:
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write("# CommitCraft Dummy Repo\n\nThis is a dummy repository created by CommitCraft for simulating GitHub contributions.\n")
            print(f"  [INFO] '{os.path.basename(readme_path)}' 파일 생성 완료.")
        except IOError as e:
            print(f"[ERROR] README.md 파일 생성 실패: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] 예상치 못한 README.md 파일 생성 오류 발생: {e}")
            return False

        success, output = _run_git_command(repo_path, ["add", "README.md"])
        if not success:
            print(f"[ERROR] README.md 파일 Git 추가 실패. {output}")
            return False
        print("  [INFO] README.md 파일 Git 스테이징 완료.")

        success, output = _run_git_command(repo_path, ["commit", "-m", "Initial commit from CommitCraft [Dummy Setup]"])
        if not success:
            print(f"[ERROR] 초기 커밋 생성 실패. {output}")
            return False
        print("  [INFO] 더미 저장소 초기 커밋 완료.")
    else:
        # 기존 경로가 존재하고 Git 저장소인지 확인
        git_dir = os.path.join(repo_path, ".git")
        if not os.path.isdir(git_dir):
            print(f"[ERROR] '{repo_path}' 경로는 존재하지만 유효한 Git 저장소가 아닙니다. .git 디렉토리를 찾을 수 없습니다.")
            return False
        print(f"  [INFO] 기존 {repo_type} Git 저장소 '{repo_path}'를 사용합니다.")
    return True

# --- 유틸리티 함수: OpenAI API 상호작용 ---
def get_ai_client() -> openai.OpenAI:
    """
    OpenAI 클라이언트를 초기화하고 반환합니다. API 키가 없으면 ValueError를 발생시킵니다.
    Returns:
        openai.OpenAI: 초기화된 OpenAI 클라이언트 객체.
    Raises:
        ValueError: OPENAI_API_KEY 환경 변수가 설정되지 않았을 경우.
    """
    print("[STEP] OpenAI 클라이언트 초기화 중...")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. .env 파일을 확인하거나 시스템 환경 변수로 설정해주세요.\n"
                         "OpenAI API 키는 GitHub 잔디밭 메시지 생성을 위해 필수적입니다.")
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        # 비용 발생 가능성 때문에 실제 모델 목록 조회는 생략하지만,
        # 프로덕션 환경에서는 초기화 후 API 키 유효성 검증 로직을 추가하는 것을 고려할 수 있습니다.
        # 예: client.models.list()
        print("[INFO] OpenAI 클라이언트 초기화 성공.")
        return client
    except openai.AuthenticationError as e:
        raise ValueError(f"OpenAI API 키가 유효하지 않거나 인증에 실패했습니다. 키를 확인해주세요. 상세: {e}")
    except Exception as e:
        raise ValueError(f"OpenAI 클라이언트 초기화 중 예상치 못한 오류 발생: {e}. API 키를 다시 확인해주세요.")

def generate_commit_message_ai(client: openai.OpenAI, trend_theme: str = None) -> str:
    """
    AI를 사용하여 창의적인 커밋 메시지를 생성합니다.
    Args:
        client (openai.OpenAI): 초기화된 OpenAI 클라이언트 객체.
        trend_theme (str, optional): 커밋 메시지에 반영할 특정 IT 트렌드 주제. 제공되지 않으면 무작위로 선택됩니다.
    Returns:
        str: AI가 생성한 커밋 메시지. API 호출 실패 시 폴백 메시지가 반환됩니다.
    """
    print("\n[AI] 커밋 메시지 생성 요청 중...")
    
    # 큐레이션된 IT 트렌드 주제 목록
    themes = [
        "새로운 AI 모델 출시 동향 분석", "클라우드 컴퓨팅 보안 취약점 패치", "웹3와 블록체인 기술 발전 방향 제시",
        "오픈소스 프로젝트 협업 문화 개선", "개발자 생산성 도구 효율성 강화", "JavaScript 프레임워크 최신 업데이트 적용",
        "퀀텀 컴퓨팅 알고리즘 연구 현황", "사이버 보안 위협 대응 전략 수립", "데이터 과학과 머신러닝 윤리 가이드라인",
        "IT 스타트업 투자 유치 성공 전략", "모바일 앱 개발 트렌드 반영", "AR/VR 기술의 발전과 상용화 적용",
        "엣지 컴퓨팅의 부상과 활용 사례", "No-code/Low-code 플랫폼 기능 확장", "지속 가능한 소프트웨어 개발 원칙 준수",
        "생성형 AI의 산업별 적용 사례", "빅데이터 처리 성능 최적화", "데브옵스(DevOps) 자동화 파이프라인 구축",
        "마이크로서비스 아키텍처 도입 검토", "클린 코드 및 리팩토링의 중요성", "LLM 기반 애플리케이션 개발 가속화",
        "제로 트러스트 아키텍처 도입과 구현", "개발자를 위한 최신 툴체인 분석", "프롬프트 엔지니어링의 심화 기술"
    ]

    if not trend_theme:
        trend_theme = random.choice(themes)
    print(f"  [INFO] 선택된 트렌드 주제: '{trend_theme}'")

    prompt = (
        f"당신은 재치있고 창의적인 깃허브 커밋 메시지를 작성하는 AI 비서 '그록'입니다.\n"
        f"오늘의 IT 트렌드 '{trend_theme}'를 반영하여, 예술적인 잔디밭을 가꾸는 'CommitCraft' 봇을 위한 커밋 메시지를 작성해주세요.\n"
        f"유머러스하고, 간결하며, 뻔하지 않은 스타일로 작성해야 합니다. 예시: 'A Beautiful Theory Falls to Ugly Data'처럼 문학적인 느낌도 좋습니다.\n"
        f"커밋 메시지 하나만 출력해주세요. 다른 설명은 필요 없습니다."
    )

    try:
        print(f"  [INFO] OpenAI API 호출 시도 (모델: {OPENAI_MODEL})...")
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a witty AI assistant creating GitHub commit messages for CommitCraft, focusing on IT trends and creative phrasing."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7, # 창의성을 위한 적절한 온도 설정 (0.0: 보수적, 1.0: 매우 창의적)
            max_tokens=80,   # 메시지 길이 제한 (너무 길어지지 않게 관리)
            top_p=1,         # 샘플링 방식 제어 (높을수록 다양한 단어 사용)
            frequency_penalty=0, # 반복적인 단어 사용 억제 (0.0: 없음, 2.0: 강함)
            presence_penalty=0   # 새로운 주제 도입 장려 (0.0: 없음, 2.0: 강함)
        )
        message = response.choices[0].message.content.strip()
        print(f"  [INFO] AI가 생성한 커밋 메시지: '{message}'")
        return message
    except openai.AuthenticationError:
        print("[ERROR] OpenAI API 키가 유효하지 않거나 인증에 실패했습니다. API 키를 확인해주세요.")
        return f"FALLBACK: AI 인증 오류 - {trend_theme} 업데이트 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
    except openai.APIConnectionError as e:
        print(f"[ERROR] OpenAI API 연결 오류 발생: 네트워크 문제 또는 서버 접근 불가. 상세: {e}")
        return f"FALLBACK: AI 연결 오류 - {trend_theme} 업데이트 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
    except openai.RateLimitError as e:
        print(f"[ERROR] OpenAI API 속도 제한 초과: 요청이 너무 많습니다. 잠시 후 다시 시도하세요. 상세: {e}")
        return f"FALLBACK: AI 속도 제한 - {trend_theme} 업데이트 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
    except openai.APIError as e:
        print(f"[ERROR] OpenAI API 호출 중 오류 발생: {e} (HTTP 상태 코드: {e.status if hasattr(e, 'status') else 'N/A'})")
        return f"FALLBACK: AI API 오류 - {trend_theme} 업데이트 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
    except Exception as e:
        print(f"[ERROR] AI 커밋 메시지 생성 중 예상치 못한 오류 발생: {e}")
        return f"FALLBACK: AI 일반 오류 - {trend_theme} 업데이트 ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"

# --- 핵심 비즈니스 로직: Git 커밋 및 푸시 ---
def make_commit(repo_path: str, message: str, timestamp: datetime.datetime = None) -> bool:
    """
    지정된 저장소에 Git 커밋을 수행합니다. 커밋할 내용을 만들기 위해 더미 파일을 수정합니다.
    선택적으로 특정 타임스탬프로 커밋하여 과거 기여를 시뮬레이션할 수 있습니다.
    Args:
        repo_path (str): Git 저장소의 로컬 경로.
        message (str): 커밋 메시지.
        timestamp (datetime.datetime, optional): 커밋에 사용할 특정 시간. None이면 현재 시간이 사용됩니다.
    Returns:
        bool: 커밋 성공 여부.
    """
    print(f"  [GIT] 커밋 시도 중: '{message}'")
    try:
        # 커밋할 변경 사항을 만들기 위해 더미 파일 생성 또는 수정
        file_name = "commitcraft_activity.txt"
        file_path = os.path.join(repo_path, file_name)
        
        # 파일 내용을 현재 시간과 메시지로 업데이트하여 항상 새로운 변경사항이 있도록 함
        # 기존 내용이 없다면 새로 생성, 있다면 추가
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"{datetime.datetime.now().isoformat()} - {message.replace('\n', ' ')}\n")
            print(f"    [INFO] '{file_name}' 파일 업데이트 완료. 새로운 활동 기록 추가.")
        except IOError as e:
            print(f"[ERROR] 더미 파일 '{file_name}' 접근 중 I/O 오류 발생: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] 더미 파일 '{file_name}' 수정 중 예상치 못한 오류 발생: {e}")
            return False

        success, output = _run_git_command(repo_path, ["add", file_path])
        if not success:
            print(f"[ERROR] 파일 스테이징 실패. {output}")
            return False
        print("    [INFO] 파일 Git 스테이징 완료.")

        commit_env = os.environ.copy()
        if timestamp:
            # GIT_AUTHOR_DATE와 GIT_COMMITTER_DATE를 설정하여 커밋 시간을 조작
            commit_env["GIT_AUTHOR_DATE"] = timestamp.isoformat()
            commit_env["GIT_COMMITTER_DATE"] = timestamp.isoformat()
            print(f"    [INFO] 타임스탬프 {timestamp.strftime('%Y-%m-%d %H:%M:%S')}로 커밋 시도 중...")
        else:
            print(f"    [INFO] 현재 시간으로 커밋 시도 중...")

        success, output = _run_git_command(repo_path, ["commit", "-m", message], env=commit_env)
        if not success:
            print(f"[ERROR] 커밋 실패. {output}")
            return False
        print(f"  [GIT] 커밋 성공: '{message}'")
        return True
    except Exception as e:
        print(f"[ERROR] 예상치 못한 커밋 오류 발생: {e}")
        return False

def push_commits(repo_path: str) -> bool:
    """
    로컬 커밋을 원격 저장소로 푸시합니다.
    Args:
        repo_path (str): Git 저장소의 로컬 경로.
    Returns:
        bool: 푸시 성공 여부.
    """
    print("\n[GIT] 원격 저장소로 푸시 작업 시작...")
    try:
        # 1. 'origin' 리모트 존재 여부 확인
        print("  [INFO] 'origin' 리모트 설정 확인 중...")
        success, remotes_output = _run_git_command(repo_path, ["remote"])
        if not success or "origin" not in remotes_output.split(): # .split()으로 정확한 단어 비교
            print(f"[WARN] 'origin' 리모트가 설정되어 있지 않습니다. 푸시를 건너뜜. (출력: {remotes_output.strip() if success else 'Git 명령 실패'})")
            print("  [HINT] 원격 저장소에 푸시하려면 'git remote add origin <원격 저장소 URL>'을 실행해야 합니다.")
            return False
        print("  [INFO] 'origin' 리모트 확인 완료.")

        # 2. 현재 브랜치 이름 가져오기
        print("  [INFO] 현재 활성 브랜치 이름 가져오는 중...")
        success, branch_output = _run_git_command(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])
        if not success:
            print(f"[ERROR] 현재 브랜치 이름을 가져오지 못했습니다. {branch_output}")
            return False
        current_branch = branch_output.strip()
        print(f"  [INFO] 현재 브랜치: '{current_branch}'")

        # 3. 푸시 시도
        print(f"  [INFO] 'origin/{current_branch}'로 푸시 시도 중...")
        success, output = _run_git_command(repo_path, ["push", "origin", current_branch])
        if not success:
            print(f"[ERROR] 푸시 실패. {output}")
            print(f"  [HINT] 원격 저장소에 대한 권한이 있는지, 로컬 브랜치 '{current_branch}'가 원격에 존재하는지 확인해주세요.")
            print("  [HINT] 처음 푸시하는 경우 'git push -u origin <branch_name>'이 필요할 수 있습니다.")
            return False
        print("[GIT] 모든 커밋이 원격 저장소에 성공적으로 푸시되었습니다.")
        return True
    except Exception as e:
        print(f"[ERROR] 예상치 못한 푸시 오류 발생: {e}")
        return False

# --- 잔디밭 조각 예술 로직 ---
def calculate_daily_commits_for_artwork(target_commits: int = TARGET_DAILY_COMMITS) -> int:
    """
    '잔디밭 예술'을 만들기 위한 오늘의 커밋 수를 계산합니다.
    요일에 따라 커밋 밀도를 조절하여 시각적인 패턴을 만듭니다.
    Args:
        target_commits (int): 기본 목표 커밋 수.
    Returns:
        int: 오늘 생성할 커밋 수. 최소 1 커밋을 보장합니다.
    """
    today = datetime.datetime.now().weekday() # 월요일=0, 일요일=6
    
    # 요일에 따른 커밋 밀도 조정 로직을 강화하여 더 다채로운 패턴 생성
    # 각 요일별 가중치를 통해 커밋 수의 범위와 경향을 조절합니다.
    if today == 0: # 월요일: 시작은 힘차게, 높은 밀도 유지
        commits_today = random.randint(int(target_commits * 1.0), int(target_commits * 1.5))
        print(f"[PLAN] 월요일: 높은 밀도로 커밋 수 조정 ({commits_today}회). 주간 목표 달성 시작!")
    elif today == 1: # 화요일: 약간 감소된 중간 밀도
        commits_today = random.randint(int(target_commits * 0.6), int(target_commits * 1.0))
        print(f"[PLAN] 화요일: 중간 밀도로 커밋 수 조정 ({commits_today}회). 꾸준함 유지.")
    elif today == 2: # 수요일: 다시 증가, 주중 피크
        commits_today = random.randint(int(target_commits * 0.9), int(target_commits * 1.3))
        print(f"[PLAN] 수요일: 높은 밀도로 커밋 수 조정 ({commits_today}회). 주중 활성화!")
    elif today == 3: # 목요일: 약간 감소된 중간 밀도
        commits_today = random.randint(int(target_commits * 0.7), int(target_commits * 1.1))
        print(f"[PLAN] 목요일: 중간 밀도로 커밋 수 조정 ({commits_today}회). 마무리 준비.")
    elif today == 4: # 금요일: 주말을 앞두고 다시 높은 밀도
        commits_today = random.randint(int(target_commits * 1.1), int(target_commits * 1.6))
        print(f"[PLAN] 금요일: 높은 밀도로 커밋 수 조정 ({commits_today}회). 주간 작업 마무리!")
    elif today == 5: # 토요일: 주말, 낮은 밀도
        commits_today = random.randint(int(target_commits * 0.3), int(target_commits * 0.7))
        print(f"[PLAN] 토요일: 낮은 밀도로 커밋 수 조정 ({commits_today}회). 여유로운 기여.")
    else: # today == 6: 일요일: 매우 낮은 밀도 (잔디밭 관리 휴식)
        commits_today = random.randint(int(target_commits * 0.1), int(target_commits * 0.4))
        print(f"[PLAN] 일요일: 매우 낮은 밀도로 커밋 수 조정 ({commits_today}회). 잔디밭 휴식 시간.")

    return max(1, commits_today) # 최소 1개 이상의 커밋을 보장하여 매일 기여 유지

# --- 메인 실행 함수 ---
def run_commit_craft():
    """
    CommitCraft의 메인 실행 함수입니다.
    환경 설정, AI 클라이언트 초기화, 커밋 생성 및 푸시 로직을 조율합니다.
    """
    print(f"\n--- CommitCraft: $1 AI 잔디밭 조각가 (Grok's GreenThumb) 시작 ---")
    print(f"목표: AI 기반 커밋으로 당신의 GitHub 잔디를 예술 작품으로! 하루 ${round(1/TARGET_DAILY_COMMITS * TARGET_DAILY_COMMITS, 2)} 기여 목표.")
    print("------------------------------------------------------------------")

    is_dummy_repo = False
    default_dummy_repo_path = os.path.join(os.getcwd(), "commitcraft_dummy_repo")
    GITHUB_REPO_PATH_FINAL = "" # 최종 사용될 저장소 경로

    # [STEP 1] GITHUB_REPO_PATH 설정 확인 및 저장소 유형 결정
    print("[STEP 1/5] GitHub 저장소 경로 확인...")
    if not GITHUB_REPO_PATH:
        print(f"[WARN] GITHUB_REPO_PATH 환경 변수가 설정되지 않아 임시 더미 저장소 '{default_dummy_repo_path}'를 사용합니다.")
        print("  [HINT] 실제 GitHub 잔디밭을 조각하려면 유효한 Git 저장소 경로로 GITHUB_REPO_PATH 환경 변수를 설정해야 합니다.")
        GITHUB_REPO_PATH_FINAL = default_dummy_repo_path
        is_dummy_repo = True
    else:
        GITHUB_REPO_PATH_FINAL = GITHUB_REPO_PATH
        print(f"[INFO] 환경 변수로부터 저장소 경로 확인: '{GITHUB_REPO_PATH_FINAL}'")

    # [STEP 2] 저장소 설정 (더미 생성 또는 기존 저장소 유효성 검사)
    print("[STEP 2/5] Git 저장소 설정 및 유효성 검사 중...")
    if not setup_repository(GITHUB_REPO_PATH_FINAL, is_dummy_repo):
        print("[CRITICAL] 저장소 설정에 실패했습니다. 스크립트를 종료합니다.")
        return

    # [STEP 3] OpenAI 클라이언트 초기화
    print("[STEP 3/5] OpenAI 클라이언트 초기화 중...")
    ai_client = None
    try:
        ai_client = get_ai_client()
    except ValueError as e:
        print(f"[CRITICAL] AI 클라이언트 초기화 실패 - {e}")
        print("스크립트를 종료합니다. OpenAI API 키를 확인해주세요.")
        return

    # [STEP 4] 일일 커밋 목표 계산 및 계획 수립
    print("[STEP 4/5] 일일 커밋 목표 및 계획 수립 중...")
    today_commits_target = calculate_daily_commits_for_artwork()
    expected_daily_contribution_value = round(today_commits_target * (1 / TARGET_DAILY_COMMITS), 2)
    print(f"\n[PLAN] 오늘 목표 커밋 횟수: {today_commits_target}회 (예상 기여 가치: ${expected_daily_contribution_value})")
    
    # [STEP 5] 커밋 생성 프로세스 실행
    print("\n[STEP 5/5] 커밋 생성 프로세스 시작...")
    today_commits_successful = 0
    for i in range(today_commits_target):
        print(f"\n[PROGRESS] [{i+1}/{today_commits_target}] 커밋 생성 작업 시작...")
        
        commit_message = generate_commit_message_ai(ai_client)

        if make_commit(GITHUB_REPO_PATH_FINAL, commit_message):
            today_commits_successful += 1
            print(f"[PROGRESS] 커밋 #{i+1} 성공적으로 생성 완료. (현재 성공: {today_commits_successful} / 목표: {today_commits_target})")
            # 실제 활동처럼 보이기 위한 랜덤 대기
            sleep_duration = random.uniform(1, 5)
            print(f"[INFO] 다음 커밋까지 {sleep_duration:.2f}초 대기...")
            time.sleep(sleep_duration)
        else:
            print(f"[WARN] 커밋 #{i+1} 생성에 실패했습니다. 다음 커밋으로 넘어갑니다.")
            # 실패 시에도 약간의 지연을 주어 시스템 부하를 줄임
            sleep_duration = random.uniform(2, 7)
            print(f"[INFO] 실패 후 {sleep_duration:.2f}초 대기...")
            time.sleep(sleep_duration)

    print(f"\n[SUMMARY] 오늘 총 {today_commits_successful}개의 커밋 생성을 완료했습니다.")

    # [FINAL STEP] 커밋 푸시 (더미 저장소인 경우 제외)
    if today_commits_successful > 0:
        if is_dummy_repo:
            print(f"\n[INFO] 더미 저장소 '{GITHUB_REPO_PATH_FINAL}'를 사용 중이므로 실제 GitHub에는 푸시되지 않습니다.")
            print("  [HINT] 실제 GitHub 잔디밭을 조각하려면 GITHUB_REPO_PATH 환경 변수를 유효한 원격 Git 저장소 경로로 설정하고 스크립트를 다시 실행해주세요.")
        else:
            print(f"\n[FINAL] {today_commits_successful}개의 커밋을 원격 저장소에 푸시합니다.")
            if push_commits(GITHUB_REPO_PATH_FINAL):
                print("[FINAL] 모든 성공적인 커밋이 원격 저장소에 성공적으로 푸시되었습니다.")
            else:
                print("[WARN] 커밋 푸시에 실패했습니다. 수동으로 저장소 상태를 확인해주세요.")
    else:
        print("\n[INFO] 오늘 생성된 성공적인 커밋이 없어 푸시할 내용이 없습니다.")

    # $1 프로젝트 대시보드 시뮬레이션 및 최종 보고
    actual_daily_contribution_value = round(today_commits_successful * (1 / TARGET_DAILY_COMMITS), 2)
    print("\n--- $1 프로젝트 대시보드 (가상) ---")
    print(f"오늘 생성된 성공적인 커밋 수: {today_commits_successful}회")
    print(f"오늘의 예상 목표 기여 가치: ${expected_daily_contribution_value}")
    print(f"오늘의 실제 달성 기여 가치: ${actual_daily_contribution_value}")
    print(f"CommitCraft는 내일도 당신의 잔디밭을 조각합니다! 내일 다시 만나요. :)\n")
    print("------------------------------------------")


if __name__ == "__main__":
    run_commit_craft()
