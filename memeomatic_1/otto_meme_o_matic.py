import os
import random
import time
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter # ImageFilter for potential blur effects or outlines
from io import BytesIO
import tweepy
from dotenv import load_dotenv
import logging # Using logging module for better log management

# --- 로깅 설정 ---
# INFO 레벨 이상의 로그를 콘솔에 출력합니다.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# .env 파일 로드
load_dotenv()

# --- 환경 변수 설정 ---
# 필요한 환경 변수들을 로드하고, 없는 경우 오류 메시지와 함께 프로그램을 종료할 수 있도록 합니다.
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY") # Pexels API 키는 선택 사항입니다.

# --- 상수 설정 ---
MIN_SLEEP_TIME_SECONDS = 3600  # 최소 1시간 (봇 같지 않게)
MAX_SLEEP_TIME_SECONDS = 10800 # 최대 3시간
MEME_OUTPUT_DIR = "generated_memes" # 생성된 밈 이미지를 저장할 디렉토리

# 밈 트렌드 키워드 (오또가 '분석'했다고 가정 - 좀 더 다양한 키워드 추가)
MEME_KEYWORDS = [
    "cat", "dog", "coding", "developer", "ai", "machine learning",
    "coffee", "work", "study", "funny", "awkward", "success", "failure",
    "motivation", "challenge", "life", "weekend", "money", "sleep",
    "programmer life", "debug", "software", "innovation", "startup",
    "stress", "deadline", "bug", "feature", "deployment"
]

# 밈 텍스트 템플릿 (인간의 '어설픔'을 모방, 더 많은 변형 추가)
MEME_TEXT_STARTERS = [
    "Me when", "When you try to", "Nobody:", "That moment when",
    "My thoughts at 3 AM:", "AI trying to be human:", "My 1$ dream be like:",
    "Devs be like:", "The server crash be like:", "Just another Monday:",
    "My code in production:", "Trying to explain a bug:",
    "The compiler said:", "My manager wants:"
]

MEME_TEXT_SUBJECTS = [
    "the code finally compiles", "the coffee kicks in", "I realize it's Friday",
    "my server is down", "I get paid 1 dollar", "understanding recursion",
    "the meme makes sense", "my code works on the first try (never)",
    "my boss says 'quick fix'", "trying to earn 1$ with memes",
    "deploying on Friday", "seeing legacy code", "reading documentation",
    "the client changes requirements", "my 1GB RAM machine", "learning a new framework"
]

MEME_TEXT_REACTIONS = [
    "*confused screaming*", "*visible confusion*", "It's evolving, just backwards",
    "Stonks 📈", "Task failed successfully", "This is fine.", "Wait, that's illegal.",
    "My goals are beyond your understanding.", "Not bad kid.", "Peak performance.",
    "Error 404: Motivation Not Found", "Send help.", "Why am I like this?",
    "Guess I'll die.", "My brain cells departing.", "Help me.", "Panic time."
]

# 폰트 설정
# 1. 스크립트와 같은 디렉토리의 지정된 폰트 파일 시도
# 2. 시스템 폰트 경로에서 일반적인 폰트 이름 시도
# 3. 모든 시도 실패 시 Pillow 기본 폰트 사용
DEFAULT_FONT_FILENAMES = [
    "arial.ttf", "Arial.ttf", 
    "malgunbd.ttf", "MalgunGothicBold.ttf", # Windows 한글 폰트
    "DejaVuSans-Bold.ttf", # Linux/macOS 흔한 폰트
    "NanumGothicBold.ttf", "NotoSansKR-Bold.otf" # Linux/macOS 한글 폰트 (설치 필요)
]
FONT_PATH = None

for fname in DEFAULT_FONT_FILENAMES:
    potential_path_local = os.path.join(os.path.dirname(__file__), fname)
    if os.path.exists(potential_path_local):
        FONT_PATH = potential_path_local
        logger.info(f"[설정] 로컬에서 폰트 파일을 찾았습니다: '{FONT_PATH}'")
        break

if not FONT_PATH:
    logger.warning(f"[설정] 기본 폰트 파일들을 찾을 수 없습니다. Pillow의 기본 폰트를 사용합니다. "
                   "밈 가독성 및 한글 지원이 제한될 수 있습니다. "
                   "스크립트와 같은 디렉토리에 'arial.ttf' 또는 한글 폰트 파일을 넣어주세요.")

# --- 트위터 API 인증 및 초기화 ---
def authenticate_twitter():
    """
    트위터 API에 인증하고 API 객체를 반환합니다.
    환경 변수가 설정되지 않았거나 인증에 실패하면 None을 반환합니다.
    """
    logger.info("[초기화] 트위터 API 인증을 시도합니다.")
    required_env_vars = {
        "TWITTER_CONSUMER_KEY": TWITTER_CONSUMER_KEY,
        "TWITTER_CONSUMER_SECRET": TWITTER_CONSUMER_SECRET,
        "TWITTER_ACCESS_TOKEN": TWITTER_ACCESS_TOKEN,
        "TWITTER_ACCESS_TOKEN_SECRET": TWITTER_ACCESS_TOKEN_SECRET
    }

    missing_vars = [name for name, value in required_env_vars.items() if not value]
    if missing_vars:
        logger.error(f"[오류] 다음 트위터 API 환경 변수가 .env 파일에 설정되지 않았습니다: {', '.join(missing_vars)}. 작업을 중단합니다.")
        return None

    try:
        # OAuthHandler를 사용하여 사용자 인증 토큰 설정
        auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

        # API 객체 초기화. rate_limit 발생 시 자동으로 대기하고 다시 시도합니다.
        api = tweepy.API(auth, wait_on_rate_limit=True)
        # 자격 증명 확인을 통해 인증이 성공했는지 테스트
        api.verify_credentials()
        logger.info("[성공] 트위터 API 인증이 완료되었습니다.")
        return api
    except tweepy.TweepyException as e:
        logger.error(f"[오류] 트위터 API 인증에 실패했습니다: {e}")
        logger.error("트위터 개발자 포털에서 API 키를 확인하거나, 계정 정지 여부를 확인해주세요.")
        return None
    except Exception as e:
        logger.error(f"[오류] 트위터 API 인증 중 예상치 못한 에러 발생: {e}")
        return None

# --- 이미지 획득 함수 ---
def get_random_image_url(keyword: str) -> str:
    """
    Pexels API를 사용하여 주어진 키워드에 대한 랜덤 이미지 URL을 검색합니다.
    API 키가 없거나 이미지 검색에 실패하면 플레이스홀더 이미지 URL을 반환합니다.
    """
    logger.info(f"[이미지] '{keyword}' 키워드로 Pexels에서 이미지를 검색합니다.")

    # Pexels API 키가 없는 경우, 플레이스홀더 이미지를 사용
    if not PEXELS_API_KEY:
        logger.warning("[경고] PEXELS_API_KEY가 설정되지 않아 Pexels API를 사용할 수 없습니다. "
                       "기본 플레이스홀더 이미지 URL을 사용합니다.")
        return "https://via.placeholder.com/600x400.png?text=Meme+Loading..."

    headers = {
        "Authorization": PEXELS_API_KEY
    }
    params = {
        "query": keyword,
        "orientation": "landscape", # 가로 이미지 선호
        "size": "medium", # 중간 크기 이미지 선호 (original, large, medium, small, portrait, landscape, tiny)
        "per_page": 40 # 여러 개 받아와서 랜덤 선택하여 다양성 확보
    }
    try:
        response = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=15)
        response.raise_for_status() # HTTP 오류 (4xx, 5xx) 발생 시 예외 발생
        data = response.json()

        if data and data.get('photos'):
            selected_photo = random.choice(data['photos'])
            image_url = selected_photo['src']['large'] # 더 나은 품질을 위해 'large' 사용
            logger.info(f"[이미지] '{keyword}'에 대한 이미지 URL을 찾았습니다: {image_url}")
            return image_url
        else:
            logger.warning(f"[경고] Pexels에서 '{keyword}'에 대한 이미지를 찾을 수 없습니다. "
                           "검색 결과가 비어있습니다. 기본 플레이스홀더 이미지 URL을 사용합니다.")
            return "https://via.placeholder.com/600x400.png?text=Meme+Loading..."
    except requests.exceptions.Timeout:
        logger.error(f"[오류] Pexels API 요청 시간 초과 (Timeout) 발생. 키워드: '{keyword}'. 기본 플레이스홀더 이미지 URL을 사용합니다.")
        return "https://via.placeholder.com/600x400.png?text=Meme+Loading..."
    except requests.exceptions.RequestException as e:
        logger.error(f"[오류] Pexels API 요청 중 네트워크 또는 HTTP 에러 발생: {e}. "
                       "기본 플레이스홀더 이미지 URL을 사용합니다.")
        return "https://via.placeholder.com/600x400.png?text=Meme+Loading..."
    except ValueError as e: # JSON 디코딩 에러
        logger.error(f"[오류] Pexels API 응답 JSON 파싱 중 에러 발생: {e}. "
                       "기본 플레이스홀더 이미지 URL을 사용합니다.")
        return "https://via.placeholder.com/600x400.png?text=Meme+Loading..."
    except Exception as e:
        logger.error(f"[오류] Pexels 이미지 검색 중 예상치 못한 에러 발생: {e}. "
                       "기본 플레이스홀더 이미지 URL을 사용합니다.")
        return "https://via.placeholder.com/600x400.png?text=Meme+Loading..."

# --- 밈 텍스트 생성 함수 ---
def generate_awkward_meme_text() -> str:
    """
    인간적인 '어설픔'을 모방하여 다양한 패턴의 밈 텍스트를 생성합니다.
    """
    logger.info("[텍스트] 어설픈 밈 텍스트 생성을 시작합니다.")
    text_parts = []
    
    # 텍스트 생성 패턴을 더 다양하게 구성
    pattern_choice = random.choices(
        ['starter_subject_reaction', 'starter_subject', 'reaction_only', 'subject_reaction', 'starter_reaction'],
        weights=[0.3, 0.3, 0.2, 0.1, 0.1], # 각 패턴의 출현 확률 조정
        k=1
    )[0]

    if pattern_choice == 'starter_subject_reaction':
        text_parts.append(random.choice(MEME_TEXT_STARTERS))
        text_parts.append(random.choice(MEME_TEXT_SUBJECTS))
        text_parts.append(random.choice(MEME_TEXT_REACTIONS))
    elif pattern_choice == 'starter_subject':
        text_parts.append(random.choice(MEME_TEXT_STARTERS))
        text_parts.append(random.choice(MEME_TEXT_SUBJECTS))
    elif pattern_choice == 'reaction_only':
        text_parts.append(random.choice(MEME_TEXT_REACTIONS))
    elif pattern_choice == 'subject_reaction':
        text_parts.append(random.choice(MEME_TEXT_SUBJECTS))
        text_parts.append(random.choice(MEME_TEXT_REACTIONS))
    elif pattern_choice == 'starter_reaction':
        text_parts.append(random.choice(MEME_TEXT_STARTERS))
        text_parts.append(random.choice(MEME_TEXT_REACTIONS))

    # 생성된 텍스트들을 자연스럽게 결합 (공백으로 연결)
    text = " ".join(text_parts).strip()

    # 어색함을 더하기 위한 후처리: 구두점, 대소문자, 반복 제거 등
    # 1. 중복 구두점 제거
    text = text.replace('..', '.').replace(',,', ',').replace('::', ':')
    # 2. 문장 시작 대문자화 (선택적, 너무 완벽하지 않게)
    if random.random() < 0.7: # 70% 확률로 문장 시작을 대문자로
        text = text[0].upper() + text[1:] if text else text
    # 3. 불필요한 공백 제거
    text = ' '.join(text.split())
    # 4. 마지막 문자에 구두점 추가 (가끔 빼먹어서 어색하게)
    if not text.endswith(('.', '!', '?', ':', '📈')) and random.random() < 0.6:
        text += random.choice(['.', '...', '!'])
    elif text.endswith('.'): # 너무 많은 마침표 방지
        text = text[:-1] + random.choice(['.', '...', ''])

    # 콜론으로 끝나는 경우, 뒤에 공백 추가가 자연스러움
    if text.endswith(':'):
        text += ' '
    
    logger.info(f"[텍스트] 생성된 밈 텍스트: '{text}'")
    return text

# --- 밈 이미지 생성 함수 ---
def create_meme_image(image_url: str, text: str, output_dir: str) -> str | None:
    """
    주어진 이미지 URL과 텍스트로 밈 이미지를 생성하고 지정된 디렉토리에 저장합니다.
    """
    logger.info(f"[이미지] 밈 이미지 생성을 시작합니다. URL: {image_url}")
    try:
        # 이미지 다운로드
        logger.debug(f"[이미지] 이미지 다운로드 중: {image_url}")
        response = requests.get(image_url, timeout=20) # 다운로드 타임아웃 20초로 연장
        response.raise_for_status() # HTTP 오류 (4xx, 5xx) 발생 시 예외 발생
        img = Image.open(BytesIO(response.content)).convert("RGB")
        logger.debug(f"[이미지] 원본 이미지 크기: {img.width}x{img.height}")

        # 이미지 크기 조정 (트위터에 적합하도록, 최대 1200x675 또는 1024x512 등)
        # 트위터는 16:9 (1200x675) 또는 2:1 (1024x512) 비율을 권장.
        # 여기서는 최대 가로 1200px, 세로 675px을 기준으로 비율 유지하며 축소
        max_width = 1200
        max_height = 675
        
        # 원본 이미지의 비율을 계산
        original_aspect = img.width / img.height
        target_aspect = max_width / max_height

        if original_aspect > target_aspect: # 원본 이미지가 타겟보다 가로가 김
            new_width = max_width
            new_height = int(max_width / original_aspect)
        else: # 원본 이미지가 타겟보다 세로가 김 또는 같음
            new_height = max_height
            new_width = int(max_height * original_aspect)

        # 최소 크기 설정 (너무 작아지는 것 방지)
        min_dim = 400
        if new_width < min_dim or new_height < min_dim:
            if original_aspect > 1: # 가로가 더 길면 가로 기준으로 최소값 맞춤
                new_width = max(new_width, min_dim)
                new_height = int(new_width / original_aspect)
            else: # 세로가 더 길면 세로 기준으로 최소값 맞춤
                new_height = max(new_height, min_dim)
                new_width = int(new_height * original_aspect)

        # 이미지 리사이즈
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.debug(f"[이미지] 리사이즈된 이미지 크기: {img.width}x{img.height}")
        
        draw = ImageDraw.Draw(img)

        # 폰트 로드 및 크기 동적 조절
        font_size = int(img.height * 0.08) # 이미지 높이의 약 8%를 초기 폰트 크기로
        font = ImageFont.load_default() # 초기값으로 Pillow 기본 폰트 설정

        if FONT_PATH:
            try:
                # 폰트 경로가 설정되어 있으면 해당 폰트 로드 시도
                font = ImageFont.truetype(FONT_PATH, font_size)
                logger.debug(f"[폰트] '{FONT_PATH}' 폰트를 성공적으로 로드했습니다 (크기: {font_size}).")
            except IOError as e:
                logger.warning(f"[폰트] '{FONT_PATH}' 폰트 로드 실패: {e}. Pillow 기본 폰트를 사용합니다.")
                font = ImageFont.load_default()
        else:
            logger.warning("[폰트] FONT_PATH가 설정되지 않았습니다. Pillow 기본 폰트를 사용합니다.")

        # 텍스트 윤곽선 (outline) 추가를 위한 함수
        def draw_text_with_outline(draw_obj, xy, text_content, font_obj, fill_color, outline_color, outline_width=2):
            x, y = xy
            # 텍스트 윤곽선 그리기
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        try:
                            draw_obj.text((x + dx, y + dy), text_content, font=font_obj, fill=outline_color)
                        except Exception as e:
                            logger.error(f"[텍스트] 윤곽선 텍스트 렌더링 중 오류 발생: {e}")
                            # 오류 발생 시 해당 부분 스킵하고 진행
            # 실제 텍스트 그리기
            try:
                draw_obj.text(xy, text_content, font=font_obj, fill=fill_color)
            except Exception as e:
                logger.error(f"[텍스트] 본문 텍스트 렌더링 중 오류 발생: {e}")

        # 텍스트 줄바꿈 처리
        def wrap_text(draw_obj, text_content, font_obj, max_width_px):
            lines = []
            if not text_content: return lines

            words = text_content.split(' ')
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                try:
                    # 텍스트 바운딩 박스 계산
                    # textbbox((x,y), text, font)는 텍스트의 좌상단 (x1, y1) 및 우하단 (x2, y2)을 반환
                    # 너비는 x2-x1
                    bbox = draw_obj.textbbox((0, 0), test_line, font=font_obj)
                    test_width = bbox[2] - bbox[0]
                except Exception as e:
                    logger.warning(f"[텍스트] 텍스트 너비 계산 중 에러 발생: {e}. 강제로 줄바꿈 시도.")
                    test_width = max_width_px + 1 # 에러 발생 시 강제로 줄바꿈

                if test_width <= max_width_px:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word] # 현재 단어는 다음 줄로
            if current_line:
                lines.append(' '.join(current_line))
            return lines

        # 텍스트 영역 설정 (이미지 하단 중앙)
        text_margin_x = int(img.width * 0.03) # 이미지 너비의 3% 마진
        text_margin_y = int(img.height * 0.03) # 이미지 높이의 3% 마진
        text_area_width = img.width - (text_margin_x * 2)
        
        wrapped_lines = wrap_text(draw, text, font, text_area_width)
        
        # 각 줄의 실제 높이를 합산하여 총 텍스트 높이 계산
        # 폰트의 실제 높이 + 줄 간격
        line_height_estimate = font_size + int(font_size * 0.3) # 줄 간격은 폰트 크기의 30% 추가

        total_text_height = len(wrapped_lines) * line_height_estimate
        
        # 텍스트 시작 Y 좌표 (이미지 하단으로부터 계산)
        y_text_start = img.height - total_text_height - text_margin_y

        current_y = y_text_start
        for i, line in enumerate(wrapped_lines):
            try:
                text_width = draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0]
            except Exception:
                logger.warning(f"[텍스트] 줄 '{line}'의 너비 계산 중 에러 발생. 중앙 정렬에 문제 있을 수 있음.")
                text_width = img.width # 에러 발생 시 중앙 정렬을 위해 전체 폭 사용

            x_text = (img.width - text_width) / 2 # 중앙 정렬
            draw_text_with_outline(draw, (x_text, current_y), line, font, (255, 255, 255), (0, 0, 0), outline_width=2)
            current_y += line_height_estimate # 다음 줄의 Y 좌표
            logger.debug(f"[이미지] 텍스트 줄 '{line}' (줄 {i+1}/{len(wrapped_lines)}) 렌더링 완료.")

        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        filename = f"meme_{int(time.time())}.jpg"
        full_output_path = os.path.join(output_dir, filename)
        
        # 이미지 저장 (품질 90%로 저장)
        img.save(full_output_path, "JPEG", quality=90)
        logger.info(f"[성공] 밈 이미지가 '{full_output_path}'에 성공적으로 저장되었습니다.")
        return full_output_path

    except requests.exceptions.Timeout:
        logger.error(f"[오류] 이미지 다운로드 시간 초과 (Timeout) 발생. URL: {image_url}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"[오류] 이미지 다운로드 중 네트워크 또는 HTTP 에러 발생: {e}. URL: {image_url}")
        return None
    except IOError as e:
        logger.error(f"[오류] 이미지 파일 입출력 중 에러 발생 (손상된 이미지?): {e}. URL: {image_url}")
        return None
    except Exception as e:
        logger.error(f"[오류] 밈 이미지 생성 중 예상치 못한 에러 발생: {e}. URL: {image_url}", exc_info=True) # exc_info=True로 스택 트레이스 출력
        return None

# --- 트위터 게시 함수 ---
def post_tweet(api, image_path: str, text: str) -> bool:
    """
    트위터 API를 사용하여 밈 이미지와 텍스트를 트윗으로 게시합니다.
    """
    logger.info(f"[트윗] 밈 게시를 시도합니다. 텍스트: '{text}'")
    if not api:
        logger.error("[오류] 트위터 API 객체가 초기화되지 않았습니다. 게시를 건너뜀.")
        return False
    if not image_path or not os.path.exists(image_path):
        logger.error(f"[오류] 이미지 파일을 찾을 수 없거나 경로가 유효하지 않습니다: '{image_path}'. 게시를 건너뜀.")
        return False

    try:
        # 1. 이미지 업로드
        logger.debug(f"[트윗] 이미지 업로드 중: {image_path}")
        media = api.media_upload(filename=image_path)
        logger.info(f"[트윗] 이미지 업로드 성공. Media ID: {media.media_id_string}")

        # 2. 트윗 게시
        status = api.update_status(status=text, media_ids=[media.media_id_string])
        logger.info(f"[성공] 밈이 트위터에 성공적으로 게시되었습니다! 트윗 ID: {status.id}")
        logger.info(f"[성공] 트윗 링크: https://twitter.com/{api.verify_credentials().screen_name}/status/{status.id}")
        return True
    except tweepy.Forbidden as e:
        logger.error(f"[오류] 트위터 API 권한 부족 또는 계정 문제로 게시 실패 (Forbidden): {e}")
        logger.error("API 키의 권한(Read/Write)이 올바른지 확인해주세요. (Developer Portal -> Projects & Apps -> App -> Permissions)")
        return False
    except tweepy.BadRequest as e:
        logger.error(f"[오류] 트위터 API 요청이 잘못되었습니다 (BadRequest): {e}")
        if "Status is a duplicate" in str(e):
            logger.error("이전 트윗과 내용이 너무 유사하여 트위터에서 중복으로 판단했을 수 있습니다. 텍스트를 변경하거나 시간을 더 기다려주세요.")
        return False
    except tweepy.TweepyException as e:
        logger.error(f"[오류] 트위터 API 관련 에러 발생: {e}")
        logger.error("API 키 또는 토큰에 문제가 있거나, 트위터 서비스에 일시적인 문제가 있을 수 있습니다. `.env` 파일을 확인하세요.")
        return False
    except Exception as e:
        logger.error(f"[오류] 예상치 못한 에러로 트위터 게시 실패: {e}", exc_info=True)
        return False

# --- 메인 실행 로직 ---
def main():
    """
    오또 밈 창조경제 봇의 메인 실행 함수입니다.
    무한 루프를 통해 주기적으로 밈을 생성하고 트위터에 게시합니다.
    """
    logger.info("\n--- 오또의 밈 창조경제 (Meme-o-Matic 1$) 시작 ---")
    logger.info("AI 오또가 '인간 냄새' 나는 밈을 생성하고 트위터에 업로드하여 1$를 벌 계획입니다.")

    # 1. 트위터 API 인증 시도
    twitter_api = authenticate_twitter()
    if not twitter_api:
        logger.critical("[심각] 트위터 API 인증 실패로 프로그램을 종료합니다.")
        return

    # 메인 루프: 주기적으로 밈 생성 및 게시
    while True:
        logger.info(f"\n[새 작업] 새로운 밈 생성을 시작합니다... (다음 게시까지 최소 {MIN_SLEEP_TIME_SECONDS // 3600}시간, 최대 {MAX_SLEEP_TIME_SECONDS // 3600}시간 대기)")
        generated_image_path = None # 이미지 경로 초기화

        try:
            # 2. 밈 트렌드 분석 (오또의 직관에 따라 키워드 선택)
            meme_keyword = random.choice(MEME_KEYWORDS)
            logger.info(f"[트렌드] 오또가 분석한 오늘의 트렌드 키워드: '{meme_keyword}'")

            # 3. 관련 이미지 URL 획득
            image_url = get_random_image_url(meme_keyword)
            # 플레이스홀더 이미지인 경우, 이미지 획득 실패로 간주하지 않고 진행 (텍스트는 그대로 올라감)
            if "placeholder.com" in image_url:
                logger.warning("[경고] 플레이스홀더 이미지가 사용됩니다. Pexels API 설정 및 네트워크 연결을 확인하세요.")

            # 4. '어설픈' 코믹 밈 텍스트 생성
            meme_text = generate_awkward_meme_text()

            # 5. 밈 이미지 생성
            generated_image_path = create_meme_image(image_url, meme_text, MEME_OUTPUT_DIR)
            if not generated_image_path:
                logger.error("[오류] 밈 이미지 생성 실패. 다음 시도를 기다립니다.")
                # 이미지 생성 실패 시 짧게 대기 후 재시도
                sleep_time_on_fail = random.randint(MIN_SLEEP_TIME_SECONDS // 4, MAX_SLEEP_TIME_SECONDS // 4)
                logger.info(f"[대기] 이미지 생성 실패로 {sleep_time_on_fail // 60}분 ({sleep_time_on_fail / 3600:.2f}시간) 동안 다음 밈 생성을 대기합니다...")
                time.sleep(sleep_time_on_fail)
                continue # 현재 밈 생성 시도는 실패했으므로 다음 루프 시작

            # 6. 트위터에 밈 업로드 및 텍스트 게시
            post_success = post_tweet(twitter_api, generated_image_path, meme_text)
            
            if post_success:
                logger.info("[완료] 밈 게시 성공! 오또의 1$ 수익에 한 걸음 더!")
            else:
                logger.warning("[실패] 밈 게시 실패. 다음 시도에서 재도전합니다.")

        except Exception as e:
            logger.critical(f"[심각] 메인 루프에서 예상치 못한 에러 발생: {e}", exc_info=True)
            logger.info("[심각] 치명적인 오류가 발생했으나, 프로그램이 종료되지 않고 다음 주기까지 대기합니다.")

        finally:
            # 게시 후 생성된 이미지 파일 삭제 (성공/실패 여부와 관계없이 시도)
            if generated_image_path and os.path.exists(generated_image_path):
                try:
                    os.remove(generated_image_path)
                    logger.info(f"[정리] 생성된 이미지 파일 '{generated_image_path}' 삭제.")
                except OSError as e:
                    logger.error(f"[경고] 이미지 파일 삭제 실패: {e}. 수동 삭제가 필요할 수 있습니다.")

        # 봇 같지 않은 '랜덤' 게시 전략 적용
        sleep_time = random.randint(MIN_SLEEP_TIME_SECONDS, MAX_SLEEP_TIME_SECONDS)
        logger.info(f"[대기] {sleep_time // 60}분 ({sleep_time / 3600:.2f}시간) 동안 다음 밈 생성을 대기합니다...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
