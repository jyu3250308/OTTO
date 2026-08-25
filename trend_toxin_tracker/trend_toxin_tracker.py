# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import csv
import os
import datetime

# 상수 정의 (가독성 향상)
DEFAULT_SATURATION_SCORE = 0.0
DEFAULT_TOXIC_THRESHOLD = 0.7
ALTERNATIVE_SUGGESTION_TEXT = "새로운 창의적 접근"

def get_sample_trends() -> list:
    """데모를 위한 샘플 트렌드 데이터를 반환합니다.
    실제 사용 시에는 CSV 파일로 제공되어야 합니다.
    """
    return [
        {'name': 'Energetic Lo-fi Beat', 'type': 'audio', 'saturation_score': 0.92, 'toxic_threshold': 0.8},
        {'name': 'Vintage Color Grading', 'type': 'visual', 'saturation_score': 0.88, 'toxic_threshold': 0.75},
        {'name': 'Quick Zoom Transition', 'type': 'visual', 'saturation_score': 0.65, 'toxic_threshold': 0.9},
        {'name': 'Upbeat Ukulele Melody', 'type': 'audio', 'saturation_score': 0.50, 'toxic_threshold': 0.7},
        {'name': 'Soft Focus Filter', 'type': 'visual', 'saturation_score': 0.78, 'toxic_threshold': 0.85},
        {'name': 'Dramatic Glitch Effect', 'type': 'visual', 'saturation_score': 0.40, 'toxic_threshold': 0.6}
    ]

def load_trend_data(filepath: str = None) -> list:
    """
    트렌드 데이터를 CSV 파일에서 로드하거나, 파일이 없거나 오류 발생 시 샘플 데이터를 반환합니다.
    데이터 형식: name,type,saturation_score,toxic_threshold
    """
    trends = []
    if filepath:
        print(f"🔄 '{filepath}' 파일에서 트렌드 데이터를 로드 시도 중...")
        if os.path.exists(filepath):
            try:
                with open(filepath, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    # CSV 헤더 검증 (견고성을 위해 추가)
                    required_headers = ['name', 'type', 'saturation_score', 'toxic_threshold']
                    if not all(header in reader.fieldnames for header in required_headers):
                        print(f"❌ '{filepath}' 파일 헤더 형식이 올바르지 않습니다. 다음 헤더가 필요합니다: {', '.join(required_headers)}")
                        print("➡️ 샘플 데이터로 대체합니다.")
                        return get_sample_trends()

                    for i, row in enumerate(reader):
                        try:
                            # 필요한 필드만 가져오고, 누락 시 기본값 사용
                            name = row.get('name', f"Unnamed Trend {i+1}")
                            trend_type = row.get('type', 'unknown')
                            saturation_score = float(row.get('saturation_score', DEFAULT_SATURATION_SCORE))
                            toxic_threshold = float(row.get('toxic_threshold', DEFAULT_TOXIC_THRESHOLD))

                            trends.append({
                                'name': name,
                                'type': trend_type,
                                'saturation_score': saturation_score,
                                'toxic_threshold': toxic_threshold
                            })
                        except ValueError as ve:
                            print(f"⚠️ '{filepath}' 파일의 {i+2}번째 줄 데이터 변환 오류: {ve}. 이 행은 건너뜁니다.")
                        except Exception as inner_e:
                            print(f"⚠️ '{filepath}' 파일의 {i+2}번째 줄 처리 중 알 수 없는 오류: {inner_e}. 이 행은 건너뜜.")
                
                if trends:
                    print(f"✅ '{filepath}'에서 {len(trends)}개의 트렌드 데이터를 성공적으로 로드했습니다.")
                else:
                    print(f"⚠️ '{filepath}' 파일에서 유효한 데이터를 찾을 수 없습니다. 샘플 데이터로 대체합니다.")
                    trends = get_sample_trends()

            except FileNotFoundError:
                print(f"❌ 오류: 파일 '{filepath}'을 찾을 수 없습니다. 샘플 데이터로 대체합니다.")
                trends = get_sample_trends()
            except csv.Error as ce:
                print(f"❌ 오류: CSV 파일 '{filepath}' 파싱 중 오류 발생: {ce}. 샘플 데이터로 대체합니다.")
                trends = get_sample_trends()
            except IOError as ioe:
                print(f"❌ 오류: '{filepath}' 파일 읽기 중 I/O 오류 발생: {ioe}. 샘플 데이터로 대체합니다.")
                trends = get_sample_trends()
            except Exception as e:
                print(f"❌ 데이터 로드 중 예상치 못한 오류 발생: {e}. 샘플 데이터로 대체합니다.")
                trends = get_sample_trends()
        else:
            print(f"⚠️ 파일 '{filepath}'을 찾을 수 없습니다. 샘플 데이터로 시연합니다.")
            print("➡️ 지금은 샘플 데이터입니다. 본인 파일을 쓰려면 'python trend_toxin_tracker.py --file 내_트렌드.csv'처럼 실행하세요.")
            trends = get_sample_trends()
    else:
        print("⚠️ 파일 입력이 없습니다. 샘플 데이터로 시연합니다.")
        print("➡️ 지금은 샘플 데이터입니다. 본인 파일을 쓰려면 'python trend_toxin_tracker.py --file 내_트렌드.csv'처럼 실행하세요.")
        trends = get_sample_trends()
    
    return trends

def find_alternative(toxic_trend: dict, all_trends: list) -> str:
    """
    독성 트렌드와 유사하지만 덜 과포화된 대체 트렌드를 제안합니다.
    """
    alternatives = [
        t for t in all_trends
        if t['type'] == toxic_trend['type'] and t['saturation_score'] < toxic_trend['saturation_score'] - 0.2
    ]
    alternatives = sorted(alternatives, key=lambda x: x['saturation_score'])
    if alternatives:
        return alternatives[0]['name']
    return ALTERNATIVE_SUGGESTION_TEXT

def analyze_trends(trends: list) -> list:
    """트렌드를 분석하여 독성 지수를 계산하고 대체재를 제안합니다."""
    analysis_results = []
    print(f"총 {len(trends)}개의 트렌드를 분석합니다...")
    for i, trend in enumerate(trends):
        print(f"  [{i+1}/{len(trends)}] '{trend['name']}' 트렌드 분석 중...")
        is_toxic = trend['saturation_score'] >= trend['toxic_threshold']
        toxicity_status = "위험" if is_toxic else "안전"
        toxicity_level = round(trend['saturation_score'] * 100)

        suggestion = "-"
        if is_toxic:
            suggestion = find_alternative(trend, trends)
            print(f"  🚨 독성 경고: '{trend['name']}' ({trend['type']}) - 과포화 지수 {toxicity_level}%! 대체재: '{suggestion}'")
        else:
            print(f"  ✅ 트렌드 확인: '{trend['name']}' ({trend['type']}) - 과포화 지수 {toxicity_level}% (안전)")

        analysis_results.append({
            'name': trend['name'],
            'type': trend['type'],
            'saturation_score': toxicity_level,
            'status': toxicity_status,
            'suggestion': suggestion
        })
    print("🔍 트렌드 분석 완료.")
    return analysis_results

def generate_report(results: list):
    """
    분석 결과를 텍스트 파일로 저장하고, 콘솔에 요약합니다.
    """
    report_filename = f"trend_toxin_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    print(f"📊 분석 리포트를 '{report_filename}' 파일로 생성 중입니다...")
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("### Trend Toxin Tracker Report ###\n")
            f.write(f"분석 일시: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n")
            f.write("## 독성 트렌드 및 대체 전략 ##\n")
            f.write("\n")

            toxic_count = 0
            for item in results:
                f.write(f"- 트렌드: {item['name']} ({item['type']})\n")
                f.write(f"  과포화 지수: {item['saturation_score']}% ({item['status']})\n")
                if item['status'] == '위험':
                    f.write(f"  🚨 대체 제안: {item['suggestion']}\n")
                    toxic_count += 1
                f.write("\n")
            
            f.write("-------------------------------------\n")
            f.write(f"총 {len(results)}개 트렌드 중 {toxic_count}개 트렌드에서 독성 위험 감지.\n")
            f.write("차세대 비주얼/오디오 전략 인사이트를 얻어 오또의 뇌를 업그레이드하세요!\n")
        print(f"✅ 리포트가 '{report_filename}' 파일로 성공적으로 저장되었습니다.")

    except IOError as ioe:
        print(f"❌ 오류: 리포트 파일 '{report_filename}' 쓰기 중 I/O 오류 발생: {ioe}. 리포트 저장을 실패했습니다.")
    except Exception as e:
        print(f"❌ 오류: 리포트 생성 중 예상치 못한 오류 발생: {e}. 리포트 저장을 실패했습니다.")

    # 콘솔에 요약 출력
    toxic_count_summary = sum(1 for item in results if item['status'] == '위험')
    print(f"\n💡 총 {len(results)}개 트렌드 중 {toxic_count_summary}개 트렌드에서 독성 위험이 감지되었습니다.")
    print("\n[반복 사용 안내] 이 스크립트를 매일/주간 스케줄러(예: crontab)에 등록하여 최신 트렌드 독성을 지속적으로 추적할 수 있습니다.")
    print("예: 0 9 * * * python /path/to/trend_toxin_tracker.py --file my_trends.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AI 기반 트렌드 독성 추적자: 인기 콘텐츠 패턴의 과포화를 감지하고 대체재를 제안합니다."
    )
    parser.add_argument(
        "--file", 
        type=str, 
        help="분석할 트렌드 데이터가 담긴 CSV 파일 경로 (예: my_trends.csv)"
    )
    args = parser.parse_args()

    print("🚀 Trend Toxin Tracker를 시작합니다...")
    print(f"현재 시간: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. 트렌드 데이터 로드
    trends_data = load_trend_data(args.file)
    if not trends_data:
        print("❌ 분석할 트렌드 데이터가 없습니다. 프로그램을 종료합니다.")
    else:
        # 2. 트렌드 분석
        print("\n🔍 트렌드 분석을 시작합니다...")
        analysis_results = analyze_trends(trends_data)

        # 3. 리포트 생성 및 저장
        print("\n📄 분석 리포트 생성 단계...")
        generate_report(analysis_results)

    print("\n✨ Trend Toxin Tracker 작업 완료.")
