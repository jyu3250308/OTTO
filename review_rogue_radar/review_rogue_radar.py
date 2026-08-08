# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys
import datetime
import csv
import re
import os

# 표준 출력/오류 스트림의 인코딩을 UTF-8로 설정하여 한글 깨짐 및 오류 방지
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        # reconfigure 메서드가 없는 환경(예: 일부 IDE 콘솔)에서는 무시
        pass
    except Exception as e:
        # 그 외 예외 발생 시 경고 출력 (개발 환경 디버깅용)
        print(f"경고: 스트림 인코딩 설정 중 오류 발생: {e}", file=sys.stderr)

# --- Mock Data Simulation ---
# 실제 데이터베이스나 외부 API에서 가져올 리뷰 데이터를 시뮬레이션합니다.
# 이 데이터를 사용하여 AI 패턴 감지 로직을 테스트합니다.
MOCK_REVIEWS = [
    {"review_id": "R001", "product_id": "P101", "user_id": "U001", "timestamp": "2023-10-26 10:00:00", "content": "정말 최고에요! 이 제품은 제 인생템입니다. 강력 추천해요.", "rating": 5},
    {"review_id": "R002", "product_id": "P101", "user_id": "U002", "timestamp": "2023-10-26 10:05:00", "content": "최고의 선택이었어요. 정말 좋아요. 꼭 사세요!", "rating": 5},
    {"review_id": "R003", "product_id": "P101", "user_id": "U003", "timestamp": "2023-10-26 10:10:00", "content": "배송도 빠르고 품질도 굿입니다. 재구매 의사 100% 있어요.", "rating": 4},
    {"review_id": "R004", "product_id": "P102", "user_id": "U004", "timestamp": "2023-10-27 11:30:00", "content": "그냥 그래요. 평범한 제품입니다.", "rating": 3},
    {"review_id": "R005", "product_id": "P101", "user_id": "U005", "timestamp": "2023-10-26 10:15:00", "content": "강력 추천합니다. 이 가격에 이 품질이라니 놀라워요. 정말 최고.", "rating": 5},
    {"review_id": "R006", "product_id": "P103", "user_id": "U006", "timestamp": "2023-10-28 09:00:00", "content": "마음에 듭니다. 배송이 좀 느렸어요.", "rating": 3},
    {"review_id": "R007", "product_id": "P101", "user_id": "U007", "timestamp": "2023-10-26 10:20:00", "content": "환상적인 제품! 꼭 사세요! 후회하지 않을 거예요. 인생템입니다.", "rating": 5},
    {"review_id": "R008", "product_id": "P102", "user_id": "U008", "timestamp": "2023-10-27 12:00:00", "content": "재구매 의사 없어요. 기대 이하였습니다.", "rating": 2}
]

# --- AI 패턴 감지 로직 설정 ---
# 의심스러운 패턴을 탐지하기 위한 키워드 및 시간 창 설정
SUSPICIOUS_PHRASES = ["정말 최고", "강력 추천", "인생템", "꼭 사세요", "환상적인"]
TIME_WINDOW_MINUTES = 30 # 동일 제품에 대해 이 시간 내에 작성된 리뷰들을 분석
MIN_COMMON_WORDS_FOR_SIMILARITY = 3 # 유사 리뷰 판단 기준: 최소 공통 단어 수
MIN_WORDS_IN_REVIEW_FOR_SIMILARITY = 5 # 유사 리뷰 판단 시, 원본 리뷰의 최소 단어 수

# --- AI 패턴 감지 함수 ---
def detect_rogue_reviews(reviews: list) -> list:
    """
    주어진 리뷰 목록에서 의심스러운 패턴(짭리뷰)을 감지하고 보고서를 생성합니다.
    두 가지 주요 패턴을 탐지합니다:
    1. 특정 의심 키워드 포함: 정의된 의심 키워드가 리뷰 내용에 포함된 경우.
    2. 짧은 시간 내에 여러 사용자가 유사한 내용의 리뷰 작성: 동일 제품에 대해
       정의된 시간 창(TIME_WINDOW_MINUTES) 내에 다른 사용자가 최소 공통 단어 수
       (MIN_COMMON_WORDS_FOR_SIMILARITY) 이상을 공유하는 유사한 리뷰를 작성한 경우.
    """
    print("\n✨ [시작] AI 기반 리뷰 패턴 분석을 시작합니다...")
    rogue_reports = []

    # 제품 ID별로 리뷰를 그룹화하여 분석 효율성을 높입니다.
    # 이는 동일 제품에 대한 리뷰들 사이의 관계를 쉽게 파악하기 위함입니다.
    reviews_by_product = {}
    skipped_count_no_product_id = 0
    for review in reviews:
        product_id = review.get('product_id')
        if not product_id:
            skipped_count_no_product_id += 1
            continue
        reviews_by_product.setdefault(product_id, []).append(review)

    print(f"  [정보] 총 {len(reviews)}개의 리뷰 중 {skipped_count_no_product_id}개가 product_id 누락으로 건너뛰어졌습니다.")
    print(f"  [정보] 유효한 리뷰 {len(reviews) - skipped_count_no_product_id}개를 {len(reviews_by_product)}개의 제품별로 그룹화했습니다.")

    # 각 제품별로 리뷰들을 상세 분석합니다.
    for product_id, product_reviews in reviews_by_product.items():
        print(f"  [분석중] 제품 ID '{product_id}'의 리뷰 {len(product_reviews)}개를 분석합니다.")
        # 시간 기반 분석을 위해 리뷰들을 작성 시간 순으로 정렬합니다.
        try:
            product_reviews.sort(key=lambda x: datetime.datetime.strptime(x.get('timestamp', ''), "%Y-%m-%d %H:%M:%S"))
        except ValueError as e:
            print(f"  [경고] 제품 ID '{product_id}' 리뷰의 시간 파싱 중 오류: {e}. 해당 제품 리뷰는 시간 분석에서 일부 제외될 수 있습니다.")
            # 시간 파싱이 안 된 리뷰는 정렬에서 마지막으로 보내거나 특정 값으로 처리하여 오류 방지
            product_reviews.sort(key=lambda x: datetime.datetime.min if 'timestamp' not in x else datetime.datetime.strptime(x['timestamp'], "%Y-%m-%d %H:%M:%S") if x['timestamp'] else datetime.datetime.min)

        for i, review1 in enumerate(product_reviews):
            detected_reasons = set() # 중복 패턴 방지를 위해 set 사용
            content1 = review1.get('content', '').strip()
            review_id1 = review1.get('review_id', 'N/A')

            if not content1:
                print(f"    [건너뜀] Review ID '{review_id1}' (제품: {product_id}): 리뷰 내용이 없어 분석에서 제외합니다.")
                continue

            # 패턴 1: 의심 키워드 탐지
            for phrase in SUSPICIOUS_PHRASES:
                if phrase in content1:
                    detected_reasons.add(f"키워드: '{phrase}'")

            # 패턴 2: 시간 근접성 및 유사한 내용 탐지
            try:
                time1 = datetime.datetime.strptime(review1.get('timestamp', ''), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                print(f"    [경고] Review ID '{review_id1}' (제품: {product_id}): 유효하지 않은 타임스탬프 형식.")
                time1 = None

            # 현재 리뷰 이후에 작성된 리뷰들과 비교하여 시간적 근접성 및 내용 유사성을 확인합니다.
            for j in range(i + 1, len(product_reviews)):
                review2 = product_reviews[j]
                content2 = review2.get('content', '').strip()
                user_id2 = review2.get('user_id', 'N/A')

                if not content2 or review1.get('user_id') == user_id2: # 동일 사용자이거나 내용 없으면 비교 제외
                    continue

                try:
                    time2 = datetime.datetime.strptime(review2.get('timestamp', ''), "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    time2 = None

                # 시간 데이터가 모두 유효하고, 다른 사용자가 짧은 시간 내에 리뷰를 작성했는지 확인합니다.
                if time1 and time2 and (time2 - time1).total_seconds() / 60 <= TIME_WINDOW_MINUTES:
                    # 내용 유사성 검사: 공통 단어가 많은지 확인
                    # 한국어 특성을 고려하여 명사 추출 등 고급 토크나이징을 사용할 수 있으나,
                    # 여기서는 간단히 공백 기반 분리 및 정규표현식으로 단어 추출.
                    words1 = set(re.findall(r'\b\w+\b', content1.lower()))
                    words2 = set(re.findall(r'\b\w+\b', content2.lower()))
                    common_words_count = len(words1.intersection(words2))

                    # 충분한 수의 공통 단어가 있고, 원본 리뷰에 충분한 단어가 있다면 유사하다고 판단
                    if common_words_count >= MIN_COMMON_WORDS_FOR_SIMILARITY and len(words1) >= MIN_WORDS_IN_REVIEW_FOR_SIMILARITY:
                        detected_reasons.add("시간 근접성 및 유사한 내용")

            if detected_reasons:
                rogue_reports.append({
                    "review_id": review_id1,
                    "product_id": product_id,
                    "user_id": review1.get('user_id', 'N/A'),
                    "content": content1,
                    "detected_patterns": "; ".join(detected_reasons)
                })
                print(f"    [감지!] Review ID '{review_id1}' (제품: {product_id}): 패턴 감지됨: {'; '.join(detected_reasons)}")

    print("\n✅ [완료] 리뷰 패턴 분석이 성공적으로 완료되었습니다.")
    return rogue_reports

# --- 메인 실행 흐름 ---
if __name__ == "__main__":
    print("\n\n✨ Review Rogue Radar: 짭리뷰 냄새 맡는 AI 탐정 ✨")
    print("온라인 리뷰 데이터 분석을 시작합니다...\n")

    try:
        # 1. AI 기반 리뷰 패턴 분석 실행
        rogue_findings = detect_rogue_reviews(MOCK_REVIEWS)

        # 2. 결과 출력 및 파일 저장
        if rogue_findings:
            current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"rogue_review_report_{current_time}.csv"

            print(f"\n  [정보] 총 {len(rogue_findings)}건의 의심스러운 리뷰 패턴이 감지되었습니다.")
            print(f"  [진행] 감지된 의심스러운 리뷰 정보를 '{output_filename}' 파일로 저장합니다...")
            try:
                with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ["review_id", "product_id", "user_id", "content", "detected_patterns"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for row in rogue_findings:
                        writer.writerow(row)

                print(f"🕵️\ufe0f 보고서가 '{output_filename}' 파일로 성공적으로 저장되었습니다.")
                print("\n--- 감지된 패턴 보고서 미리보기 (최대 3개 항목) ---")
                for i, item in enumerate(rogue_findings):
                    if i >= 3: # 최대 3개 항목만 미리 보여주기
                        print(f"  ...외 {len(rogue_findings)-i}건")
                        break
                    print(f"  [Review ID: {item.get('review_id', 'N/A')}] 패턴: {item.get('detected_patterns', 'N/A')} | 내용: {item.get('content', '')[:50]}...")

                print(f"\n💡 시장의 투명성 증진을 위해 이 보고서를 마케팅 분석가에게 $1에 판매하세요!")
            except IOError as e:
                print(f"❌ 파일 저장 중 오류 발생: {e}. 보고서 파일을 생성할 수 없습니다.")
            except Exception as e: # CSV 라이팅 중 발생할 수 있는 기타 예외 처리
                print(f"❌ 보고서 작성 중 예상치 못한 오류 발생: {e}")

        else:
            print("\n✅ 현재 데이터에서 의심스러운 리뷰 패턴이 감지되지 않았습니다.")
            print("  [정보] 감지된 패턴이 없으므로, 별도의 보고서 파일은 생성하지 않습니다.")

    except Exception as e:
        print(f"\n❌ 심각한 오류 발생: {e}")
        print("프로그램 실행 중 문제가 발생했습니다. 입력 데이터 또는 로직을 확인해 주세요.")

    print("\n--- 모든 작업 완료 ---")
    print(f"💡 팁: 이 스크립트를 스케줄러(예: crontab)에 등록하여 매일 실행하면 시장 동향 분석에 유용합니다.\n   예: 0 9 * * * python {os.path.basename(__file__)}\n")