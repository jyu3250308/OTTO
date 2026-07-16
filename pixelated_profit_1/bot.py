
import os
import tweepy
import requests
from PIL import Image, ImageDraw, ImageFont
import random
import io
import time
from dotenv import load_dotenv
import logging

# Configure logging for better insights
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
# This ensures sensitive API keys are not hardcoded and are loaded securely.
load_dotenv()

# --- Configuration ---
# Twitter API Credentials: These are essential for authenticating with Twitter.
# Ensure these are set in your .env file for security (e.g., TWITTER_CONSUMER_KEY="your_key").
TWITTER_CONSUMER_KEY = os.getenv("TWITTER_CONSUMER_KEY")
TWITTER_CONSUMER_SECRET = os.getenv("TWITTER_CONSUMER_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Mock LLM API Endpoint: This URL is a placeholder and is NOT used in the current
# mock implementation for caption generation. It serves as an example for
# where a real LLM API endpoint (e.g., OpenAI, Gemini, Hugging Face) would go.
MOCK_LLM_API_URL = "https://api.example.com/mock-llm" # Placeholder, not actively used in this mock setup.

# Budget Configuration (Conceptual for a single run)
# These costs are illustrative and help simulate resource consumption.
# In a real-world application, CURRENT_SPEND would be persisted (e.g., in a database,
# a file, or a cloud key-value store) to maintain state across multiple runs.
# For this script, CURRENT_SPEND resets with each execution of the bot.
IMAGE_FETCH_COST = 0.05      # Cost to fetch one image
CAPTION_GEN_COST = 0.15      # Cost to generate one caption using a mock LLM (simulated)
TWEET_POST_COST = 0.02       # Cost to post one tweet (upload media + status update)
DAILY_BUDGET = 1.00          # Maximum budget for daily operations
CURRENT_SPEND = 0.0          # Tracks total spending for the current bot run

# Public Domain Image Sources (Examples)
# These URLs point to public domain images, typically from Wikimedia Commons.
# For a robust bot, consider integrating with APIs from services like Wikimedia Commons,
# Pexels, Unsplash (check licenses carefully), or a self-curated database
# to get a wider variety of images and potentially associated metadata.
PUBLIC_DOMAIN_IMAGE_URLS = [
    "https://upload.wikimedia.org/wikipedia/commons/e/ee/19th_century_illustration_-_Man_on_horse.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Currier_and_Ives_-_A_Grand_M%C3%AAl%C3%A9e.jpg/1024px-Currier_and_Ives_-_A_Grand_M%C3%AAl%C3%A9e.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/William_Blake_-_Urizen_with_the_Book_of_Experience.jpg/800px-William_Blake_-_Urizen_with_the_Book_of_Experience.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Thomas_Rowlandson_-_A_French_Ordinary.jpg/1024px-Thomas_Rowlandson_-_A_French_Ordinary.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Honore_Daumier_-_The_legislative_belly.jpg/1024px-Honore_Daumier_-_The_legislative_belly.jpg"
]

# --- Helper Functions ---

def get_twitter_api() -> tweepy.API | None:
    """
    Authenticates with the Twitter API (v1.1) using OAuth 1.0a and returns the API object.
    Requires consumer keys, access tokens, and their secrets to be set as environment variables.

    Returns:
        tweepy.API | None: An authenticated Tweepy API object, or None if authentication fails.
    """
    if not all([TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        logger.error("Twitter API keys are not fully configured. Please check your .env file.")
        return None
    
    logger.info("Attempting to authenticate with Twitter API...")
    try:
        auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        
        # Use wait_on_rate_limit=True to automatically wait when rate limits are hit.
        # This prevents the bot from being blocked for making too many requests.
        api = tweepy.API(auth, wait_on_rate_limit=True)
        
        # Verify credentials to ensure the authentication was successful
        api.verify_credentials()
        logger.info("Twitter API authentication successful. Credentials verified.")
        return api
    except tweepy.TweepyException as e:
        logger.error(f"Twitter API authentication failed: {e}")
        logger.error("Please check your API keys and tokens for correctness and ensure they have the necessary permissions.")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during Twitter API authentication: {e}")
        return None

def check_and_update_budget(cost: float, operation_name: str) -> bool:
    """
    Checks if an operation can proceed within the daily budget and updates the current spend.

    Args:
        cost (float): The cost of the current operation.
        operation_name (str): A descriptive name for the operation (e.g., "image fetch").

    Returns:
        bool: True if the operation can proceed within budget, False otherwise.
    """
    global CURRENT_SPEND
    if CURRENT_SPEND + cost > DAILY_BUDGET:
        logger.warning(f"Budget exceeded for '{operation_name}'. Remaining budget: ${DAILY_BUDGET - CURRENT_SPEND:.2f}, required: ${cost:.2f}.")
        return False
    return True

def record_spend(cost: float, operation_name: str):
    """
    Records the cost of an operation and updates the global spend counter.

    Args:
        cost (float): The cost to add to the current spend.
        operation_name (str): A descriptive name for the operation.
    """
    global CURRENT_SPEND
    CURRENT_SPEND += cost
    logger.info(f"'{operation_name}' cost: ${cost:.2f}. Current total spend: ${CURRENT_SPEND:.2f}/{DAILY_BUDGET:.2f}")


def fetch_public_domain_image() -> tuple[Image.Image | None, str | None]:
    """
    Fetches a random public domain image URL from the predefined list and downloads it.
    Performs a budget check before attempting the fetch.

    Returns:
        tuple[Image.Image | None, str | None]: A tuple containing the PIL Image object
                                                and its original URL, or (None, None) if
                                                the operation fails or budget is exceeded.
    """
    if not check_and_update_budget(IMAGE_FETCH_COST, "image fetch"):
        return None, None

    image_url = random.choice(PUBLIC_DOMAIN_IMAGE_URLS)
    logger.info(f"Attempting to fetch image from: {image_url}")
    try:
        # Use stream=True for potentially large images, but read content fully for PIL.
        # timeout ensures the request doesn't hang indefinitely.
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        
        # Read content into a BytesIO object for PIL to open directly from memory.
        image_data = io.BytesIO(response.content)
        img = Image.open(image_data).convert("RGB") # Convert to RGB to ensure consistent color mode
        
        record_spend(IMAGE_FETCH_COST, "image fetch")
        logger.info(f"Image fetched successfully from {image_url}. Dimensions: {img.width}x{img.height}")
        return img, image_url
    except requests.exceptions.Timeout:
        logger.error(f"Timeout occurred while fetching image from {image_url}. The request took too long.")
        return None, None
    except requests.exceptions.RequestException as e:
        logger.error(f"Network or HTTP error fetching image from {image_url}: {e}")
        return None, None
    except Image.UnidentifiedImageError:
        logger.error(f"Failed to identify image format from {image_url}. It might be corrupted or an unsupported type.")
        return None, None
    except Exception as e:
        logger.error(f"An unexpected error occurred while processing image from {image_url}: {e}")
        return None, None

def reinterpret_image(img: Image.Image) -> Image.Image:
    """
    Applies a series of visual reinterpretations to the input image,
    simulating a 'meme-ification' or 'vintage restoration' effect.
    This includes resizing, a sepia-like filter, and adding a border.

    Args:
        img (Image.Image): The input PIL Image object to be reinterpreted.

    Returns:
        Image.Image: The reinterpreted PIL Image object.
    """
    logger.info("Starting image reinterpretation process...")
    
    # 1. Resize for consistency and to optimize subsequent processing.
    # LANCZOS is a high-quality downsampling filter.
    target_size = (800, 600)
    logger.debug(f"Resizing image from {img.width}x{img.height} to {target_size[0]}x{target_size[1]} pixels.")
    img = img.resize(target_size, Image.Resampling.LANCZOS)

    # 2. Apply a vintage-like filter (e.g., sepia tone)
    # This loop iterates through each pixel and applies a transformation.
    logger.debug("Applying sepia tone filter...")
    img_data = img.getdata()
    new_img_data = []
    for r, g, b in img_data:
        # Sepia tone formula: Adjusts RGB values to give a warm, brownish tint.
        # These coefficients are standard for sepia conversion.
        new_r = int(0.393 * r + 0.769 * g + 0.189 * b)
        new_g = int(0.349 * r + 0.686 * g + 0.168 * b)
        new_b = int(0.272 * r + 0.534 * g + 0.131 * b)
        # Clamp values to 0-255 range to prevent overflow
        new_img_data.append((min(255, new_r), min(255, new_g), min(255, new_b)))
    img.putdata(new_img_data)
    logger.debug("Sepia tone filter applied.")

    # 3. Add a simple border to frame the image.
    border_size = 15 # A slightly larger border for more emphasis
    border_color = (20, 20, 20) # Dark grey border
    logger.debug(f"Adding a {border_size}-pixel wide border with color {border_color}.")
    bordered_img = Image.new("RGB", (img.width + border_size*2, img.height + border_size*2), border_color)
    bordered_img.paste(img, (border_size, border_size))
    
    logger.info("Image reinterpretation complete.")
    return bordered_img

def generate_meme_caption(image_description: str) -> str | None:
    """
    Generates a meme caption using a mock LLM API.
    In a real application, this would involve calling a sophisticated
    Large Language Model (LLM) API (e.g., OpenAI GPT, Google Gemini, Anthropic Claude)
    with the image_description and desired tone/style.

    For this demonstration, it simulates LLM behavior with predefined,
    randomly selected, and context-aware (using image_description) responses.
    A budget check is performed before simulation.

    Args:
        image_description (str): A textual description of the image to guide caption generation.

    Returns:
        str | None: A humorous meme caption, or None if budget is exceeded or an error occurs.
    """
    if not check_and_update_budget(CAPTION_GEN_COST, "caption generation"):
        return None

    logger.info(f"Attempting to generate caption for image described as: '{image_description}'")
    
    # Simulate API call latency to mimic real LLM response times.
    time.sleep(random.uniform(1.5, 3.0)) # Random delay between 1.5 and 3 seconds
    
    # Predefined mock responses. We try to make them slightly context-aware
    # by incorporating parts of the image_description or current year.
    mock_responses = [
        f"When you try to explain modern internet culture to someone from the {random.randint(18, 19)}th century, as seen in this {image_description}.",
        f"Me trying to navigate {random.choice(['the stock market', 'social media trends', 'my dating life', 'the ancient texts'])} in {time.strftime('%Y')} while looking like this {image_description}.",
        f"That moment when you realize the 'past' isn't so different from the 'present' after all. #MemeHistory featuring {image_description}.",
        f"They say a picture is worth a thousand words, but this {image_description} is definitely worth a thousand laughs. What a classic!",
        f"When you spent 10 minutes trying to find a meme, and this ancient gem pops up. Peak entertainment from a {image_description}.",
        f"The original 'oof' moment, probably. #VintageMeme by {image_description.split('from ')[-1] if 'from ' in image_description else 'an unknown artist'}.",
        f"This illustration captures the true essence of {random.choice(['monday mornings', 'awkward family gatherings', 'online meetings', 'existential dread'])} with a {image_description} vibe.",
        f"Before the internet, there was just... this. And it was glorious. A true {image_description} masterpiece.",
        f"Feeling like this {image_description} on a Tuesday morning.",
        f"This is peak {random.choice(['humanity', 'drama', 'serenity'])} encapsulated in a {image_description}."
    ]
    
    try:
        caption = random.choice(mock_responses)
        record_spend(CAPTION_GEN_COST, "caption generation")
        logger.info(f"Caption generated: '{caption}'")
        return caption
    except Exception as e:
        logger.error(f"Error during mock caption generation: {e}")
        return None

def post_tweet(api: tweepy.API, image_buffer: io.BytesIO, status_text: str) -> bool:
    """
    Posts the image and caption to Twitter using the provided API object.
    Performs a budget check before attempting to post.

    Args:
        api (tweepy.API): The authenticated Tweepy API object.
        image_buffer (io.BytesIO): A file-like object containing the image data (e.g., PNG format).
        status_text (str): The text content of the tweet (caption).

    Returns:
        bool: True if the tweet was posted successfully, False otherwise.
    """
    if not check_and_update_budget(TWEET_POST_COST, "tweet post"):
        return False

    if not api:
        logger.error("Twitter API is not initialized. Cannot post tweet.")
        return False

    try:
        logger.info("Starting image upload to Twitter...")
        # Upload media directly from BytesIO buffer.
        # This avoids writing and deleting a temporary file on disk.
        media = api.media_upload(filename="meme_image.png", file=image_buffer)
        logger.info(f"Image uploaded successfully. Media ID: {media.media_id}")
        
        logger.info(f"Posting tweet with status: '{status_text}'")
        # Ensure status_text does not exceed Twitter's character limit (280 for v1.1, though images count).
        # We won't implement full character counting here but keep it in mind for real LLM outputs.
        api.update_status(status=status_text, media_ids=[media.media_id])
        
        record_spend(TWEET_POST_COST, "tweet post")
        logger.info("Tweet posted successfully!")
        return True
    except tweepy.TweepyException as e:
        logger.error(f"Error posting tweet to Twitter: {e}")
        logger.error("Please check Twitter API permissions and tweet content (e.g., duplicate status, length).")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during tweet posting: {e}")
        return False

# --- Main Bot Logic ---

def run_pixelated_profit_bot():
    """
    Main function to orchestrate the 'Pixelated Profit' bot's operations.
    This bot fetches a public domain image, reinterprets it, generates a
    humorous caption using a mock LLM, and posts the resulting meme to Twitter.
    It includes budget management and robust error handling for each step.
    """
    logger.info("--- Pixelated Profit: 1-달러 밈 발굴봇 시작 ---")
    logger.info(f"일일 예산: ${DAILY_BUDGET:.2f}")
    
    # Initialize CURRENT_SPEND for this run (resets per execution)
    global CURRENT_SPEND
    CURRENT_SPEND = 0.0

    # 0. Initial Setup and Pre-checks
    # Ensure all necessary Twitter API keys are present.
    if not all([TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        logger.critical("오류: Twitter API 키가 모두 설정되지 않았습니다. .env 파일을 확인해주세요. 봇을 종료합니다.")
        return

    # Authenticate with Twitter API. Exit if authentication fails.
    api = get_twitter_api()
    if not api:
        logger.critical("봇을 시작할 수 없습니다. Twitter API 초기화 실패. 봇을 종료합니다.")
        return

    logger.info(f"현재 예산 지출: ${CURRENT_SPEND:.2f}")
    if CURRENT_SPEND >= DAILY_BUDGET:
        logger.warning("일일 예산이 모두 소진되었습니다. 내일 다시 시도해주세요. 봇을 종료합니다.")
        return

    # Using a try-finally block to ensure any resources (like temp files, though we avoid them now)
    # are cleaned up if unexpected errors occur.
    try:
        # 1. 밈 발굴 (이미지 가져오기)
        logger.info("단계 1/4: 공공 도메인 이미지 발굴을 시작합니다.")
        original_image, image_url = fetch_public_domain_image()
        if original_image is None:
            logger.error("이미지 발굴 실패. 봇 종료.")
            return

        # 2. 밈 재해석 및 복원 (이미지 처리)
        logger.info("단계 2/4: 발굴된 이미지를 밈 스타일로 재해석합니다.")
        reinterpreted_image = reinterpret_image(original_image)
        
        # Prepare the reinterpreted image for upload by saving it to an in-memory byte buffer.
        # This avoids writing to disk, improving performance and reducing I/O errors.
        img_byte_arr = io.BytesIO()
        try:
            reinterpreted_image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0) # Reset buffer position to the beginning for reading
            logger.info("재해석된 이미지를 메모리 버퍼에 PNG 형식으로 저장했습니다.")
        except Exception as e:
            logger.error(f"재해석된 이미지를 메모리 버퍼에 저장 중 오류 발생: {e}. 봇 종료.")
            return

        # 3. 문맥 맞춤형 밈 캡션 자동 생성
        logger.info("단계 3/4: 밈 캡션 생성을 시작합니다.")
        # Generate a descriptive string for the image based on its properties and source.
        # In a real LLM integration, one might use an image-to-text model for better description.
        # For this mock, we parse the URL for a basic context.
        image_name_from_url = image_url.split('/')[-1].split('.')[0].replace('_', ' ') if image_url else "an old illustration"
        image_description_for_llm = f"{image_name_from_url} ({original_image.width}x{original_image.height} pixels)"
        
        caption_text = generate_meme_caption(image_description_for_llm)
        if caption_text is None:
            logger.error("캡션 생성 실패. 봇 종료.")
            return
        
        # Add relevant hashtags to the caption to increase visibility and contextualize the tweet.
        caption_text += f" #PixelatedProfit #OldMeme #1DollarBot #AIArt #MemeRescue #VintageArt #ClassicMeme"
        
        # Ensure the final caption length is within Twitter's limits (approx 280 chars for v1.1).
        # Truncate if necessary, but add an ellipsis if truncated.
        max_tweet_length = 280 # Twitter v1.1 allows 280 characters. Media URLs are compacted.
        if len(caption_text) > max_tweet_length:
            logger.warning(f"Caption exceeds {max_tweet_length} characters. Truncating.")
            caption_text = caption_text[:max_tweet_length - 3] + "..."
            
        logger.info(f"최종 캡션 (길이 {len(caption_text)}): '{caption_text}'")

        # 4. 트위터 발행
        logger.info("단계 4/4: 생성된 밈을 트위터에 발행합니다.")
        tweet_successful = post_tweet(api, img_byte_arr, caption_text)
        
        if tweet_successful:
            logger.info("밈 트윗 발행 성공!")
        else:
            logger.error("밈 트윗 발행 실패.")

    except Exception as e:
        logger.critical(f"봇 실행 중 치명적인 오류 발생: {e}", exc_info=True)
        logger.error("예상치 못한 오류로 인해 봇이 비정상적으로 종료됩니다.")
    finally:
        logger.info(f"최종 일일 예산 지출: ${CURRENT_SPEND:.2f}/{DAILY_BUDGET:.2f}")
        logger.info("--- Pixelated Profit: 1-달러 밈 발굴봇 종료 ---")

if __name__ == "__main__":
    run_pixelated_profit_bot()
