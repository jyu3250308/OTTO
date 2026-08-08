# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys._stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        # 이미 reconfigure되었거나 지원하지 않는 환경일 경우 무시합니다.
        pass

import datetime
import csv
import re
import os

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
MIN_WORDS_IN_REVIEW = 5            # 유사 리뷰 판단 기준: 원본 리뷰의 최소 단어 수

# --- AI 패턴 감지 함수 ---
def detect_rogue_reviews(reviews):
    """
    주어진 리뷰 목록에서 의심스러운 패턴(짭리뷰)을 감지하고 보고서를 생성합니다.
    두 가지 주요 패턴을 탐지합니다:
    1. 특정 의심 키워드 포함
    2. 짧은 시간 내에 여러 사용자가 유사한 내용의 리뷰 작성
    """
    print("  [진행] AI 기반 리뷰 패턴 분석을 시작합니다...")
    rogue_reports = []
    
    # 제품 ID별로 리뷰를 그룹화하여 분석 효율성을 높입니다.
    # 이는 동일 제품에 대한 리뷰들 사이의 관계를 쉽게 파악하기 위함입니다.
    reviews_by_product = {}
    for review in reviews:
        product_id = review.get('product_id')
        if not product_id:
            print(f"  [경고] product_id가 없는 리뷰가 있습니다: {review.get('review_id', 'N/A')}")
            continue
        reviews_by_product.setdefault(product_id, []).append(review)
    
    print(f"  [정보] 총 {len(reviews)}개의 리뷰를 {len(reviews_by_product)}개의 제품별로 그룹화했습니다.")

    # 각 제품별로 리뷰들을 상세 분석합니다.
    for product_id, product_reviews in reviews_by_product.items():
        print(f"  [분석중] 제품 ID '{product_id}'의 리뷰 {len(product_reviews)}개를 분석합니다.")
        # 시간 기반 분석을 위해 리뷰들을 작성 시간 순으로 정렬합니다.
        try:
            product_reviews.sort(key=lambda x: datetime.datetime.strptime(x['timestamp'], "%Y-%m-%d %H:%M:%S"))
        except ValueError as e:
            print(f"  [오류] 제품 ID '{product_id}'의 리뷰 시간 파싱 중 오류 발생: {e}. 해당 제품 리뷰는 건너뜝니다.")
            continue

        for i, review1 in enumerate(product_reviews):
            detected_reasons = []
            content1 = review1.get('content', '')
            if not content1: # 내용이 없는 리뷰는 패턴 분석에서 제외
                continue

            # 패턴 1: 의심 키워드 탐지
            # 리뷰 내용에 미리 정의된 의심스러운 문구가 포함되어 있는지 확인합니다.
            for phrase in SUSPICIOUS_PHRASES:
                if phrase in content1:
                    reason_text = f"키워드: '{phrase}'"
                    if reason_text not in detected_reasons: # 중복 방지
                        detected_reasons.append(reason_text)

            # 패턴 2: 시간 근접성 및 유사한 내용 탐지
            # 현재 리뷰 이후에 작성된 리뷰들과 비교하여 시간적 근접성 및 내용 유사성을 확인합니다.
            for j in range(i + 1, len(product_reviews)):
                review2 = product_reviews[j]
                content2 = review2.get('content', '')
                if not content2: continue

                try:
                    time1 = datetime.datetime.strptime(review1['timestamp'], "%Y-%m-%d %H:%M:%S")
                    time2 = datetime.datetime.strptime(review2['timestamp'], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # 이미 외부에서 에러를 잡았거나, 여기서도 안전하게 처리
                    continue
                
                # 다른 사용자가 짧은 시간 내에 리뷰를 작성했는지 확인합니다.
                if (time2 - time1).total_seconds() / 60 <= TIME_WINDOW_MINUTES and review1['user_id'] != review2['user_id']:
                    # 내용 유사성 검사: 공통 단어가 많은지 확인
                    words1 = set(re.findall(r'\b\w+\b', content1.lower()))
                    words2 = set(re.findall(r'\b\w+\b', content2.lower()))
                    common_words = words1.intersection(words2)
                    
                    # 충분한 수의 공통 단어가 있고, 원본 리뷰에 충분한 단어가 있다면 유사하다고 판단
                    if len(common_words) >= MIN_COMMON_WORDS_FOR_SIMILARITY and len(words1) >= MIN_WORDS_IN_REVIEW:
                        reason_text = "시간 근접성 및 유사한 내용"
                        if reason_text not in detected_reasons:
                            detected_reasons.append(reason_text)

            if detected_reasons:
                rogue_reports.append({
                    "review_id": review1.get('review_id', 'N/A'),
                    "product_id": review1.get('product_id', 'N/A'),
                    "user_id": review1.get('user_id', 'N/A'),
                    "content": review1.get('content', ''),
                    "detected_patterns": "; ".join(detected_reasons)
                })
                print(f"    [감지!] Review ID '{review1.get('review_id', 'N/A')}'에서 패턴 감지: {'; '.join(detected_reasons)}")

    print("  [완료] 리뷰 패턴 분석이 성공적으로 완료되었습니다.")
    return rogue_reports

# --- 메인 실행 흐름 ---
if __name__ == "__main__":
    print("\n✨ Review Rogue Radar: 짭리뷰 냄새 맡는 AI 탐정 ✨")
    print("온라인 리뷰 데이터 분석을 시작합니다...\n")

    try:
        # 1. AI 기반 리뷰 패턴 분석 실행
        rogue_findings = detect_rogue_reviews(MOCK_REVIEWS)

        # 2. 결과 출력 및 파일 저장
        if rogue_findings:
            current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"rogue_review_report_{current_time}.csv"
            
            print(f"\n  [정보] 감지된 의심스러운 리뷰 {len(rogue_findings)}건을 파일로 저장합니다.")
            try:
                with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ["review_id", "product_id", "user_id", "content", "detected_patterns"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for row in rogue_findings:
                        writer.writerow(row)
                
                print(f"🕵️\ufe0f 총 {len(rogue_findings)}개의 의심스러운 리뷰 패턴이 감지되었습니다.")
                print(f"📄 상세 보고서는 '{output_filename}' 파일로 성공적으로 저장되었습니다.")
                print("--- 보고서 내용 미리보기 ---")
                for i, item in enumerate(rogue_findings):
                    if i >= 3: # 최대 3개 항목만 미리 보여주기
                        print(f"  ...외 {len(rogue_findings)-i}건")
                        break
                    print(f"  [Review ID: {item['review_id']}] 패턴: {item['detected_patterns']} | 내용: {item['content'][:50]}...")

                print(f"\n💡 시장의 투명성 증진을 위해 이 보고서를 마케팅 분석가에게 $1에 판매하세요!")
            except IOError as e:
                print(f"❌ 파일 저장 중 오류 발생: {e}. 보고서 파일을 생성할 수 없습니다.")
            except Exception as e: # CSV 라이팅 중 발생할 수 있는 기타 예외 처리
                print(f"❌ 보고서 작성 중 예상치 못한 오류 발생: {e}")

        else:
            print("✅ 현재 데이터에서 의심스러운 리뷰 패턴이 감지되지 않았습니다.")
            print("  [정보] 감지된 패턴이 없으므로, 별도의 보고서 파일은 생성하지 않습니다.")

    except Exception as e:
        print(f"❌ 심각한 오류 발생: {e}")
        print("프로그램 실행 중 문제가 발생했습니다. 입력 데이터 또는 로직을 확인해 주세요.")

    print("\n--- 작업 완료 ---")
    print(f"💡 팁: 이 스크립트를 스케줄러(예: crontab)에 등록하여 매일 실행하면 시장 동향 분석에 유용합니다.\n   예: 0 9 * * * python {os.path.basename(__file__)}")
