# Pixel Prowler: 디지털 원본 감시병 🕵️‍♀️🔍

![Pixel Prowler Logo](https://img.shields.io/badge/Project-Pixel%20Prowler-blue?style=for-the-badge&logo=python)

당신의 소중한 디지털 콘텐츠(이미지, 텍스트)를 웹에서 24시간 감시하고, 무단 도용을 즉시 알려주는 AI 기반 감시병!

## 🚀 프로젝트 소개

**Pixel Prowler**는 당신의 창작물이 웹에서 무단으로 사용되는 것을 막기 위해 탄생했습니다. 이 강력한 AI 에이전트는 당신의 소중한 디지털 콘텐츠(이미지, 텍스트)를 웹에서 밤낮없이 감시합니다. 만약 누군가 당신의 창작물을 허락 없이 사용한다면, 즉시 알림을 보내 표절자를 잡을 수 있도록 돕습니다.

나아가, 이 과정에서 수집되는 익명의 '콘텐츠 침해 패턴' 데이터는 분석되어 관련 플랫폼에 $1에 판매되며, 이는 창작물 보호를 위한 기술 발전에 기여하게 됩니다.

## ✨ 주요 기능

*   **텍스트 콘텐츠 감시**: 웹 페이지의 텍스트를 분석하여 당신의 원본 텍스트와의 유사도를 정밀하게 비교합니다.
*   **이미지 콘텐츠 감시**: 이미지의 고유한 지문(Perceptual Hash)을 생성하여 웹상의 이미지와 비교, 도용 여부를 식별합니다.
*   **실시간 웹 스캔**: 당신이 지정한 URL들을 방문하여 콘텐츠 침해 여부를 지속적으로 감시합니다.
*   **상세 침해 보고서**: 침해 의심 사례가 발견될 경우, 시간, 감지된 URL, 콘텐츠 유형, 유사도, 의심 구간 등이 포함된 상세 보고서를 자동으로 생성합니다.
*   **간편한 설정**: 유사도 임계값 등 주요 감시 기준을 쉽게 조절할 수 있습니다.

## ⚙️ 작동 방식

Pixel Prowler는 다음과 같은 단계를 통해 당신의 콘텐츠를 보호합니다.

1.  **원본 콘텐츠 준비**: 감시하고자 하는 당신의 원본 텍스트 파일(.txt) 또는 이미지 파일(.jpg, .png 등)을 준비합니다.
2.  **웹 스캔**: Pixel Prowler가 당신이 지정한 웹사이트들을 방문합니다.
3.  **콘텐츠 추출 및 지문 생성**: 웹사이트에서 텍스트 콘텐츠를 추출하거나 이미지를 다운로드하여 고유한 '지문(fingerprint)'을 생성합니다.
4.  **유사도 비교**: 원본 콘텐츠의 지문과 스캔된 웹사이트 콘텐츠의 지문을 비교하여 유사도를 측정합니다.
5.  **보고서 작성**: 유사도가 설정된 임계값(기본 75%)을 초과하면, 상세한 침해 보고서를 `prowler_report.txt` 파일에 자동으로 기록합니다.

## 🔧 설치 방법

Pixel Prowler를 실행하기 위해 필요한 단계를 따라주세요.

### 1단계: Python 설치

Python 3.8 이상 버전이 설치되어 있어야 합니다. 다음 명령어로 설치 여부를 확인할 수 있습니다.

```bash
python --version
```

설치되어 있지 않다면, [Python 공식 웹사이트](https://www.python.org/downloads/)에서 다운로드하여 설치해 주세요.

### 2단계: 가상 환경 설정 (권장)

프로젝트의 의존성을 분리하기 위해 가상 환경을 사용하는 것을 강력히 권장합니다.

```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3단계: 필요 라이브러리 설치

가상 환경이 활성화된 상태에서, Pixel Prowler가 필요로 하는 라이브러리들을 설치합니다.

```bash
pip install requests beautifulsoup4 Pillow imagehash
```

## 🚀 실행 방법

**⭐️ 키 불필요, 바로 실행! ⭐️**

Pixel Prowler는 별도의 API 키나 복잡한 환경 변수 설정 없이 바로 실행할 수 있습니다. 설치 단계를 마쳤다면 이제 콘텐츠 감시를 시작할 준비가 되었습니다!

### 실행 명령어 형식

```bash
python pixel_prowler.py --content <원본_콘텐츠_경로> --scan_urls <스캔할_URL_1> [<스캔할_URL_2> ...]
```

*   `--content <원본_콘텐츠_경로>`:
    *   감시할 당신의 **원본 텍스트 파일(.txt)** 또는 **이미지 파일(.png, .jpg 등)** 의 경로를 지정합니다.
    *   예시: `my_document.txt` 또는 `my_artwork.jpg`
*   `--scan_urls <스캔할_URL_1> [<스캔할_URL_2> ...]`:
    *   콘텐츠 침해 여부를 감시할 웹사이트 URL들을 **공백으로 구분하여 나열**합니다.
    *   예시: `https://example.com/blog https://another-site.net/gallery`

### 예시 1: 텍스트 콘텐츠 감시

`my_original_article.txt` 라는 파일에 당신의 원본 텍스트가 저장되어 있고, `https://blog.naver.com/some_post` 와 `https://tistory.com/another_article` 에서 도용 여부를 감시하고 싶을 때:

```bash
python pixel_prowler.py --content my_original_article.txt --scan_urls https://blog.naver.com/some_post https://tistory.com/another_article
```

### 예시 2: 이미지 콘텐츠 감시

`my_artwork.png` 라는 당신의 원본 이미지가 있고, `https://www.artstation.com/someone_else` 와 `https://deviantart.com/uploader` 에서 도용 여부를 감시하고 싶을 때:

```bash
python pixel_prowler.py --content my_artwork.png --scan_urls https://www.artstation.com/someone_else https://deviantart.com/uploader
```

### 결과 확인

감시가 완료되면, 침해 의심 사례는 현재 디렉토리에 생성되는 `prowler_report.txt` 파일에 기록됩니다. 이 파일을 열어 상세 내용을 확인하세요.

## 🛠️ 설정 (고급)

`pixel_prowler.py` 파일 상단에 있는 다음 변수들을 직접 수정하여 Pixel Prowler의 작동 방식을 커스터마이징할 수 있습니다.

*   `SIMILARITY_THRESHOLD`: 유사도 임계값을 설정합니다. 기본값은 `0.75` (75%)이며, 이 값 이상으로 유사하면 침해로 간주하여 보고합니다. `0.0`부터 `1.0` 사이의 값으로 설정할 수 있습니다.
    ```python
    SIMILARITY_THRESHOLD = 0.80 # 80% similarity
    ```
*   `REPORT_FILENAME`: 보고서 파일의 이름을 변경할 수 있습니다. 기본값은 `