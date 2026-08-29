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

# --- Configuration & Global Settings --- #
SIMILARITY_THRESHOLD = 0.75 # 표절/침해 경고를 발생시킬 유사도 기준 (0.0 ~ 1.0)
REPORT_FILENAME = "prowler_report.txt" # 탐지 보고서가 저장될 파일명

# --- Utility Functions --- #
def _log(level, message):
    """표준화된 로그 메시지를 출력합니다."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{level.upper()}] {message}")

def _fetch_url_content(url, stream=False):
    """URL에서 HTTP 응답을 안전하게 가져옵니다."""
    try:
        response = requests.get(url, stream=stream, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.Timeout:
        _log("error", f"URL 요청 시간 초과: {url}")
    except requests.exceptions.ConnectionError:
        _log("error", f"URL에 연결할 수 없음 (네트워크 문제): {url}")
    except requests.exceptions.HTTPError as e:
        _log("error", f"HTTP 오류 발생 ({e.response.status_code}): {url} - {e}")
    except requests.exceptions.RequestException as e:
        _log("error", f"URL 요청 중 알 수 없는 오류: {url} - {e}")
    except Exception as e:
        _log("error", f"URL 콘텐츠 가져오기 중 예기치 않은 오류: {url} - {e}")
    return None

def get_text_content(url):
    """URL에서 HTML 콘텐츠를 가져와 모든 가시적인 텍스트를 추출합니다."""
    _log("info", f"텍스트 콘텐츠를 가져오는 중: {url}")
    response = _fetch_url_content(url)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        for script_or_style in soup(['script', 'style']): script_or_style.extract()
        text = soup.get_text(separator=' ', strip=True)
        _log("info", f"텍스트 콘텐츠 추출 완료 (길이: {len(text)}).: {url}")
        return text
    return None

def download_image(image_url, temp_dir):
    """지정된 URL에서 이미지를 다운로드하여 임시 디렉토리에 저장합니다."""
    _log("info", f"이미지 다운로드 시도 중: {image_url}")
    response = _fetch_url_content(image_url, stream=True)
    if response:
        try:
            filename = os.path.basename(urllib.parse.urlparse(image_url).path)
            if not filename or '.' not in filename: filename = "downloaded_image.jpg"
            temp_filepath = os.path.join(temp_dir, filename)
            with open(temp_filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192): f.write(chunk)
            _log("info", f"이미지 다운로드 완료: {temp_filepath}")
            return temp_filepath
        except Exception as e:
            _log("error", f"이미지 저장 중 예기치 않은 오류: {image_url} - {e}")
    return None

def generate_fingerprint(content_path, content_type):
    """주어진 콘텐츠 경로와 타입에 따라 지문을 생성합니다."""
    _log("info", f"원본 {content_type} 지문 생성 중: {content_path}")
    try:
        if content_type == 'text':
            with open(content_path, 'r', encoding='utf-8') as f: return f.read()
        elif content_type == 'image':
            img = Image.open(content_path)
            return imagehash.phash(img)
    except FileNotFoundError:
        _log("error", f"파일 없음: {content_path}")
    except Exception as e:
        _log("error", f"{content_type.capitalize()} 지문 생성 실패: {content_path} - {e}")
    return None

def compare_text(original, scanned):
    """두 텍스트를 비교하여 유사도와 일치 세그먼트를 반환합니다."""
    matcher = SequenceMatcher(None, original, scanned)
    match = matcher.find_longest_match(0, len(original), 0, len(scanned))
    if match.size == 0: return 0.0, ""
    similarity = match.size / len(original)
    matched_segment = scanned[match.b:match.b + match.size]
    return similarity, matched_segment

def compare_image(original_hash, scanned_hash):
    """두 이미지 해시를 비교하여 유사도 점수를 반환합니다."""
    if original_hash is None or scanned_hash is None: return 0.0
    distance = original_hash - scanned_hash # 해밍 거리
    similarity = 1.0 - (distance / 64.0) # 64비트 해시 기준 정규화
    return max(0.0, similarity)

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
    parser = argparse.ArgumentParser(description="Pixel Prowler: 디지털 콘텐츠 저작권 침해 감시 도구.")
    parser.add_argument("--content", help="모니터링할 원본 콘텐츠의 경로 (텍스트 파일 또는 이미지 파일).")
    parser.add_argument("--scan_urls", nargs='+', help="콘텐츠를 스캔할 URL 목록 (공백으로 구분).")
    args = parser.parse_args()

    original_content_path, scan_urls = args.content, args.scan_urls

    if not original_content_path and not scan_urls:
        _log("info", "[데모 모드] 콘텐츠 경로 또는 스캔 URL이 제공되지 않았습니다. 샘플 데이터를 사용하여 실행합니다.")
        _log("info", "  본인 파일을 사용하려면: python pixel_prowler.py --content my_doc.txt --scan_urls http://example.com/page1")
        original_content_path = "sample_original.txt"
        scan_urls = ["https://en.wikipedia.org/wiki/Digital_rights", "https://en.wikipedia.org/wiki/Plagiarism"]
        if not os.path.exists(original_content_path):
            with open(original_content_path, 'w', encoding='utf-8') as f:
                f.write("Digital rights management (DRM) is a systematic approach to copyright protection for digital media.")
            _log("info", f"데모용 원본 텍스트 파일 생성: {original_content_path}")

    if not original_content_path or not os.path.isfile(original_content_path):
        _log("error", f"원본 콘텐츠 파일을 찾을 수 없거나 유효하지 않습니다: {original_content_path}")
        return

    if not scan_urls:
        _log("error", "스캔할 URL이 제공되지 않았습니다. 종료합니다.")
        return

    original_type = 'unknown'
    if original_content_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')): original_type = 'image'
    elif original_content_path.lower().endswith(('.txt', '.md', '.html')): original_type = 'text'
    else:
        _log("error", f"지원되지 않는 원본 콘텐츠 유형: {original_content_path}. 텍스트 또는 이미지 파일을 사용하세요.")
        return

    original_fingerprint = generate_fingerprint(original_content_path, original_type)
    if original_fingerprint is None:
        _log("error", "원본 콘텐츠 지문 생성에 실패하여 종료합니다.")
        return

    _log("info", f"\n스캔 시작. 총 {len(scan_urls)}개의 URL에서 {original_type} 콘텐츠를 탐지합니다.")
    temp_dir = None
    if original_type == 'image': temp_dir = tempfile.mkdtemp(prefix="pixel_prowler_tmp_")

    try:
        for url in scan_urls:
            _log("info", f"\n[진행 중] 스캔 중: {url}")
            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if original_type == 'text':
                scanned_text = get_text_content(url)
                if scanned_text:
                    similarity, matched_segment = compare_text(original_fingerprint, scanned_text)
                    _log("info", f"  텍스트 유사도: {similarity:.2f}")
                    if similarity >= SIMILARITY_THRESHOLD:
                        _log("alert", f"  >>> 텍스트 침해 가능성 감지! 유사도: {similarity:.2f} (임계값: {SIMILARITY_THRESHOLD:.2f})")
                        _log("alert", f"  의심 세그먼트: '{matched_segment[:100]}...'\n")
                        save_report({'timestamp': current_timestamp, 'url': url, 'original_type': 'text', 'similarity': similarity, 'matched_segment': matched_segment})
                    else: _log("info", f"  유의미한 텍스트 불일치 (유사도: {similarity:.2f}).\n")

            elif original_type == 'image' and temp_dir:
                scanned_html = get_text_content(url)
                if not scanned_html: continue
                soup = BeautifulSoup(scanned_html, 'html.parser')
                img_tags = soup.find_all('img')
                found_match = False
                if not img_tags: _log("info", f"  URL에서 이미지 태그를 찾을 수 없습니다."); continue

                for img_tag in img_tags:
                    img_src = img_tag.get('src');
                    if not img_src: continue
                    absolute_img_url = urllib.parse.urljoin(url, img_src)
                    downloaded_image_path = download_image(absolute_img_url, temp_dir)

                    if downloaded_image_path:
                        scanned_image_fingerprint = generate_fingerprint(downloaded_image_path, 'image')
                        os.remove(downloaded_image_path) # 임시 파일 즉시 정리
                        if scanned_image_fingerprint:
                            similarity = compare_image(original_fingerprint, scanned_image_fingerprint)
                            _log("info", f"  이미지 유사도: {similarity:.2f} (이미지: {absolute_img_url})")
                            if similarity >= SIMILARITY_THRESHOLD:
                                _log("alert", f"  >>> 이미지 침해 가능성 감지! 유사도: {similarity:.2f} (임계값: {SIMILARITY_THRESHOLD:.2f})")
                                _log("alert", f"  탐지 이미지 URL: {absolute_img_url}\n")
                                save_report({'timestamp': current_timestamp, 'url': url, 'original_type': 'image', 'similarity': similarity, 'scanned_image_url': absolute_img_url})
                                found_match = True
                                break # 첫 번째 일치 시 해당 URL의 이미지 스캔 중단

                if not found_match: _log("info", f"  원본 이미지와 일치하는 이미지를 찾을 수 없습니다.\n")

    finally:
        if temp_dir:
            try:
                shutil.rmtree(temp_dir) # 임시 디렉토리 및 내용 삭제
                _log("info", f"임시 디렉토리 삭제 완료: {temp_dir}")
            except Exception as e:
                _log("error", f"임시 디렉토리 삭제 실패: {temp_dir} - {e}")

    _log("info", f"\n스캔 완료. 자세한 보고서는 '{REPORT_FILENAME}' 파일을 확인하세요.")
    _log("info", "  다음 실행을 위해서는 스케줄러 (예: cron, 작업 스케줄러)를 활용하여\n  'python pixel_prowler.py --content your_file.txt --scan_urls http://site.com' 명령을 등록하세요.")

if __name__ == '__main__':
    main()