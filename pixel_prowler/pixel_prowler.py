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
import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
from datetime import datetime
from PIL import Image
import imagehash
import tempfile
import urllib.parse
import shutil

# --- Configuration --- #
SIMILARITY_THRESHOLD = 0.75 # 표절/침해 경고를 발생시킬 유사도 기준 (0.0 ~ 1.0)
REPORT_FILENAME = "prowler_report.txt" # 탐지 보고서가 저장될 파일명

# --- Utility Functions --- #
def _log(level, message):
    """표준화된 로그 메시지를 출력합니다."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{level.upper()}] {message}")

def get_text_content(url):
    """
    지정된 URL에서 HTML 콘텐츠를 가져와 모든 가시적인 텍스트를 추출합니다.
    스크립트 및 스타일 태그는 제거됩니다.
    """
    _log("info", f"URL에서 텍스트 콘텐츠를 가져오는 중: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for script_or_style in soup(['script', 'style']):
            script_or_style.extract()
        text = soup.get_text(separator=' ', strip=True)
        _log("info", f"텍스트 콘텐츠 추출 완료 (길이: {len(text)}).: {url}")
        return text
    except requests.exceptions.Timeout:
        _log("error", f"URL 요청 시간 초과: {url}")
    except requests.exceptions.ConnectionError:
        _log("error", f"URL에 연결할 수 없음 (네트워크 문제): {url}")
    except requests.exceptions.HTTPError as e:
        _log("error", f"HTTP 오류 발생 ({e.response.status_code}): {url} - {e}")
    except requests.exceptions.RequestException as e:
        _log("error", f"URL 요청 중 알 수 없는 오류: {url} - {e}")
    except Exception as e:
        _log("error", f"텍스트 콘텐츠 처리 중 예기치 않은 오류: {url} - {e}")
    return None

def download_image(image_url, temp_dir):
    """지정된 URL에서 이미지를 다운로드하여 임시 디렉토리에 저장합니다."""
    _log("info", f"이미지 다운로드 시도 중: {image_url}")
    try:
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()
        filename = os.path.basename(urllib.parse.urlparse(image_url).path)
        if not filename or '.' not in filename:
            filename = "downloaded_image.jpg" # 확장자가 없는 경우 기본값
        temp_filepath = os.path.join(temp_dir, filename)
        with open(temp_filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        _log("info", f"이미지 다운로드 완료: {temp_filepath}")
        return temp_filepath
    except requests.exceptions.RequestException as e:
        _log("error", f"이미지 다운로드 실패: {image_url} - {e}")
    except Exception as e:
        _log("error", f"이미지 저장 중 예기치 않은 오류: {image_url} - {e}")
    return None

def generate_text_fingerprint(text_content):
    """텍스트 콘텐츠 자체를 지문으로 사용합니다 (직접 비교)."""
    return text_content

def generate_image_fingerprint(image_path):
    """이미지 파일의 지각 해시(phash)를 생성합니다."""
    try:
        img = Image.open(image_path)
        return imagehash.phash(img)
    except FileNotFoundError:
        _log("error", f"이미지 파일 없음: {image_path}")
    except Exception as e:
        _log("error", f"이미지 처리 실패: {image_path} - {e}")
    return None

def compare_text(original_text, scanned_text):
    """두 텍스트 블록을 비교하여 가장 일치하는 비율과 일치하는 세그먼트를 반환합니다."""
    matcher = SequenceMatcher(None, original_text, scanned_text)
    match = matcher.find_longest_match(0, len(original_text), 0, len(scanned_text))
    if match.size == 0:
        return 0.0, ""
    similarity = match.size / len(original_text)
    matched_segment = scanned_text[match.b:match.b + match.size]
    return similarity, matched_segment

def compare_image(original_hash, scanned_hash):
    """두 이미지 해시를 비교하여 유사도 점수를 반환합니다 (1에 가까울수록 유사)."""
    if original_hash is None or scanned_hash is None:
        return 0.0
    distance = original_hash - scanned_hash # 해밍 거리: 다른 비트 수 (낮을수록 유사)
    similarity = 1.0 - (distance / 64.0) # 64비트 해시 기준 0-1 유사도로 정규화
    return max(0.0, similarity) # 유사도 음수 방지

def save_report(data):
    """탐지 보고서를 파일에 추가합니다."""
    try:
        with open(REPORT_FILENAME, 'a', encoding='utf-8') as f:
            f.write(f"--- Pixel Prowler Report ---\n")
            f.write(f"Timestamp: {data['timestamp']}\n")
            f.write(f"Detected URL: {data['url']}\n")
            f.write(f"Original Content Type: {data['original_type']}\n")
            f.write(f"Similarity: {data['similarity']:.2f}\n")
            if data['original_type'] == 'text':
                f.write(f"Suspicious Segment:\n>>> {data['matched_segment']}\n")
            elif data['original_type'] == 'image':
                f.write(f"Scanned Image URL: {data.get('scanned_image_url', 'N/A')}\n")
            f.write(f"---\n\n")
        _log("info", f"보고서가 {REPORT_FILENAME}에 저장되었습니다.")
    except IOError as e:
        _log("error", f"보고서 파일 ({REPORT_FILENAME}) 저장 실패: {e}")
    except Exception as e:
        _log("error", f"보고서 저장 중 예기치 않은 오류: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Pixel Prowler: 디지털 콘텐츠 저작권 침해 감시 도구."
    )
    parser.add_argument(
        "--content",
        help="모니터링할 원본 콘텐츠의 경로 (텍스트 파일 또는 이미지 파일)."
    )
    parser.add_argument(
        "--scan_urls",
        nargs='+',
        help="콘텐츠를 스캔할 URL 목록 (공백으로 구분)."
    )
    args = parser.parse_args()

    original_content_path = args.content
    scan_urls = args.scan_urls

    if not original_content_path and not scan_urls:
        _log("info", "콘텐츠 경로 또는 스캔 URL이 제공되지 않았습니다. 데모 데이터를 사용하여 실행합니다.")
        _log("info", "  본인 파일을 사용하려면: python pixel_prowler.py --content my_doc.txt --scan_urls http://example.com/page1")
        original_content_path = "sample_original.txt"
        scan_urls = ["https://en.wikipedia.org/wiki/Digital_rights", "https://en.wikipedia.org/wiki/Plagiarism"]

        if not os.path.exists(original_content_path):
            with open(original_content_path, 'w', encoding='utf-8') as f:
                f.write("Digital rights management (DRM) is a systematic approach to copyright protection for digital media.")
            _log("info", f"데모용 원본 텍스트 파일 생성: {original_content_path}")

    if not original_content_path:
        _log("error", "원본 콘텐츠 경로를 --content 인자로 제공해 주세요.")
        return

    original_type = 'unknown'
    original_fingerprint = None

    _log("info", f"원본 콘텐츠 분석 중: {original_content_path}")
    if os.path.isfile(original_content_path):
        if original_content_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            original_type = 'image'
            _log("info", f"이미지 지문 생성 중: {original_content_path}")
            original_fingerprint = generate_image_fingerprint(original_content_path)
            if original_fingerprint is None:
                _log("error", "원본 이미지 지문 생성에 실패하여 종료합니다.")
                return
        elif original_content_path.lower().endswith(('.txt', '.md', '.html')):
            original_type = 'text'
            _log("info", f"텍스트 지문 생성 중: {original_content_path}")
            try:
                with open(original_content_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                original_fingerprint = generate_text_fingerprint(text_content)
            except Exception as e:
                _log("error", f"원본 텍스트 파일 읽기 실패: {original_content_path} - {e}")
                return
        else:
            _log("error", f"지원되지 않는 콘텐츠 유형: {original_content_path}. .txt 또는 일반적인 이미지 형식을 사용하세요.")
            return
    else:
        _log("error", f"원본 콘텐츠 파일을 찾을 수 없음: {original_content_path}")
        return

    if not scan_urls:
        _log("info", "스캔할 URL이 제공되지 않았습니다. 종료합니다.")
        return

    _log("info", f"스캔 시작. 총 {len(scan_urls)}개의 URL에서 {original_type} 콘텐츠를 탐지합니다.\n")

    temp_dir = None
    if original_type == 'image':
        temp_dir = tempfile.mkdtemp(prefix="pixel_prowler_tmp_")
        _log("info", f"임시 이미지 저장 디렉토리 생성: {temp_dir}")

    for url in scan_urls:
        _log("info", f"현재 스캔 중: {url}")
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if original_type == 'text':
            scanned_text = get_text_content(url)
            if scanned_text:
                similarity, matched_segment = compare_text(original_fingerprint, scanned_text)
                _log("info", f"텍스트 유사도: {similarity:.2f} (URL: {url})")
                if similarity >= SIMILARITY_THRESHOLD:
                    _log("alert", f"텍스트 침해 가능성 감지! URL: {url}")
                    _log("alert", f"  유사도: {similarity:.2f} (임계값: {SIMILARITY_THRESHOLD:.2f})")
                    _log("alert", f"  의심스러운 세그먼트: '{matched_segment[:100]}...'\n")
                    save_report({
                        'timestamp': current_timestamp,
                        'url': url,
                        'original_type': 'text',
                        'similarity': similarity,
                        'matched_segment': matched_segment
                    })
                else:
                    _log("info", f"유의미한 텍스트 불일치 (유사도: {similarity:.2f}).\n")

        elif original_type == 'image':
            scanned_html = get_text_content(url)
            if scanned_html and temp_dir:
                soup = BeautifulSoup(scanned_html, 'html.parser')
                img_tags = soup.find_all('img')
                found_match = False
                if not img_tags:
                    _log("info", f"URL에서 이미지 태그를 찾을 수 없습니다: {url}")
                    continue

                for img_tag in img_tags:
                    img_src = img_tag.get('src')
                    if not img_src:
                        continue
                    absolute_img_url = urllib.parse.urljoin(url, img_src)
                    _log("info", f"이미지 태그에서 이미지 URL 발견: {absolute_img_url}")
                    downloaded_image_path = download_image(absolute_img_url, temp_dir)

                    if downloaded_image_path:
                        scanned_image_fingerprint = generate_image_fingerprint(downloaded_image_path)
                        if scanned_image_fingerprint:
                            similarity = compare_image(original_fingerprint, scanned_image_fingerprint)
                            _log("info", f"이미지 유사도: {similarity:.2f} (URL: {url}, 이미지: {absolute_img_url})")
                            if similarity >= SIMILARITY_THRESHOLD:
                                _log("alert", f"이미지 침해 가능성 감지! URL: {url}, 이미지: {absolute_img_url}")
                                _log("alert", f"  유사도: {similarity:.2f} (임계값: {SIMILARITY_THRESHOLD:.2f})\n")
                                save_report({
                                    'timestamp': current_timestamp,
                                    'url': url,
                                    'original_type': 'image',
                                    'similarity': similarity,
                                    'scanned_image_url': absolute_img_url
                                })
                                found_match = True
                                break # 첫 번째 일치하는 이미지를 찾으면 해당 URL 스캔 중단
                        os.remove(downloaded_image_path) # 임시 파일 정리

                if not found_match:
                    _log("info", f"URL에서 원본 이미지와 일치하는 이미지를 찾을 수 없습니다: {url}\n")

    if temp_dir:
        try:
            shutil.rmtree(temp_dir) # 임시 디렉토리 및 내용 삭제
            _log("info", f"임시 디렉토리 삭제 완료: {temp_dir}")
        except Exception as e:
            _log("error", f"임시 디렉토리 삭제 실패: {temp_dir} - {e}")

    _log("info", f"\n스캔 완료. 자세한 보고서는 '{REPORT_FILENAME}' 파일을 확인하세요.")
    _log("info", "  자동 실행을 위해서는 스케줄러 (예: Linux/macOS의 cron, Windows의 작업 스케줄러)를 \n  활용하여 'python pixel_prowler.py --content your_file.txt --scan_urls http://site.com' 명령을 등록하세요.")

if __name__ == '__main__':
    main()
