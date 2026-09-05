# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import time
import random
import os
import csv
import argparse
from datetime import datetime

def _load_keywords_from_file(filepath):
    """지정된 파일에서 키워드를 로드합니다."""
    keywords = []
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                keywords = [line.strip() for line in f if line.strip()]
            print(f"[INFO] '{filepath}'에서 {len(keywords)}개의 키워드를 성공적으로 로드했습니다.")
        except IOError as e:
            print(f"[ERROR] 키워드 파일 '{filepath}'을 읽는 중 오류 발생: {e}")
        except Exception as e:
            print(f"[ERROR] 키워드 파일 처리 중 예상치 못한 오류 발생: {e}")
    else:
        print(f"[WARN] 키워드 파일 '{filepath}'을 찾을 수 없습니다.")
    return keywords

def load_trend_keywords(source_input):
    """트렌드 감시를 위한 키워드를 로드합니다. 파일 또는 샘플 키워드를 사용합니다."""
    keywords = []
    if source_input and source_input.endswith('.txt'):
        keywords = _load_keywords_from_file(source_input)
    elif source_input and ',' in source_input:
        keywords = [k.strip() for k in source_input.split(',') if k.strip()]
        print(f"[INFO] 입력된 문자열에서 {len(keywords)}개의 키워드를 로드했습니다.")

    if not keywords:
        keywords = [
            "#챌린지이름", "#틱톡댄스", "#릴스타그램", "#쇼츠댄스챌린지", 
            "#밈공유", "#바이럴사운드", "#틱톡푸드", "#데일리룩챌린지",
            "#일상브이로그", "#랜덤댄스"
        ]
        print("[INFO] 입력된 키워드 파일/문자열이 없거나 유효하지 않아 샘플 키워드로 시연 중입니다.")
        print("         💡 본인 키워드를 사용하려면 'python viral_wave_whisperer.py --keywords 내키워드.txt' 또는 '--keywords #키워드1,#키워드2'처럼 실행하세요.")
    return keywords

def simulate_trend_monitoring(all_keywords, current_trends):
    """현재 시점의 트렌드를 시뮬레이션하고, 급성장 트렌드를 식별합니다."""
    print("[INFO] 새로운 트렌드 데이터를 수집 중입니다...")
    newly_detected = {}
    updated_trends = {}
    
    num_active_trends = random.randint(3, 7)
    active_keywords = random.sample(all_keywords, min(num_active_trends, len(all_keywords)))

    for keyword in active_keywords:
        new_score = random.randint(10, 100) # 시뮬레이션된 바이럴 점수 (1-100)
        example_link = f"https://example.com/trend/{keyword.replace('#','')}/{random.randint(1000,9999)}"
        feature = random.choice(["빠른 전환", "유쾌한 사운드", "반전 스토리", "쉬운 댄스"]) + f" ({keyword.replace('#','')})"

        if keyword not in current_trends:
            newly_detected[keyword] = {"score": new_score, "link": example_link, "feature": feature, "status": "NEW"}
            print(f"  [DETECTED] 새로운 트렌드 감지: {keyword} (점수: {new_score})")
        else:
            old_score = current_trends[keyword]["score"]
            score_diff = new_score - old_score
            status = "GROWING" if score_diff > 10 else ("DECLINING" if score_diff < -10 else "STABLE")
            
            updated_trends[keyword] = {"score": new_score, "link": example_link, "feature": feature, "status": status}
            if status == "GROWING":
                print(f"  [RISING] 트렌드 성장 감지: {keyword} (이전: {old_score}, 현재: {new_score}, 변화: {score_diff})")
            elif status == "DECLINING":
                print(f"  [FALLING] 트렌드 하락 감지: {keyword} (이전: {old_score}, 현재: {new_score}, 변화: {score_diff})")
            else:
                print(f"  [STABLE] 트렌드 유지: {keyword} (점수: {new_score})")

    return newly_detected, updated_trends

def send_notification(trends_to_notify):
    """콘텐츠 제작자에게 알림을 보냅니다 (파일 저장으로 대체)."""
    if not trends_to_notify:
        print("[INFO] 알림을 보낼 급성장/새로운 트렌드가 없습니다.")
        return

    notification_filename = "trend_notifications.txt"
    mode = 'a' if os.path.exists(notification_filename) else 'w'

    try:
        with open(notification_filename, mode, encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[Viral Wave Whisperer 알림 - {timestamp}]\n")
            f.write("급성장/새로운 숏폼 트렌드가 감지되었습니다!\n\n")

            for trend_name, data in trends_to_notify.items():
                status_msg = "새로운" if data["status"] == "NEW" else "급성장" if data["status"] == "GROWING" else ""
                f.write(f"- {status_msg} 트렌드: {trend_name}\n")
                f.write(f"  핵심 특징: {data['feature']}\n")
                f.write(f"  바이럴 예시: {data['link']}\n")
                f.write(f"  현재 바이럴 점수: {data['score']}\n\n")
            f.write("----------------------------------------\n\n")
        print(f"[SUCCESS] {len(trends_to_notify)}개의 트렌드 알림이 '{notification_filename}'에 저장되었습니다.")
    except IOError as e:
        print(f"[ERROR] 알림 파일 '{notification_filename}' 쓰기 중 오류 발생: {e}")
    except Exception as e:
        print(f"[ERROR] 알림 생성 중 예상치 못한 오류 발생: {e}")

def save_trend_data_to_csv(trend_data):
    """감시된 트렌드 데이터를 CSV 파일에 저장합니다."""
    csv_filename = "viral_wave_data.csv"
    fieldnames = ["timestamp", "trend_name", "virality_score", "status", "feature", "example_link"]
    
    try:
        file_exists = os.path.exists(csv_filename)
        with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()  # 파일이 없으면 헤더 작성
            writer.writerow(trend_data)
        print(f"[SUCCESS] 트렌드 데이터가 '{csv_filename}'에 저장되었습니다.")
    except IOError as e:
        print(f"[ERROR] CSV 파일 '{csv_filename}' 쓰기 중 오류 발생: {e}")
    except Exception as e:
        print(f"[ERROR] CSV 데이터 저장 중 예상치 못한 오류 발생: {e}")

def main():
    parser = argparse.ArgumentParser(description="Viral Wave Whisperer: 숏폼 트렌드 잠복근무 봇")
    parser.add_argument('--keywords', type=str, default='',
                        help="트렌드 키워드 파일 (.txt) 경로 또는 콤마로 구분된 키워드 문자열")
    parser.add_argument('--interval', type=int, default=30,
                        help="트렌드 감시 주기 (초 단위). 데모용 기본값 30초.")
    parser.add_argument('--iterations', type=int, default=5,
                        help="봇 실행 반복 횟수 (데모용). 0 또는 음수 입력 시 무한 반복.")
    args = parser.parse_args()

    all_keywords = load_trend_keywords(args.keywords)
    if not all_keywords:
        print("[CRITICAL] 감시할 키워드가 없어 봇을 시작할 수 없습니다. 프로그램을 종료합니다.")
        return

    current_trends_state = {}
    
    print("\n=== Viral Wave Whisperer 봇 시작 ===")
    print(f"[CONFIG] 감시 주기: {args.interval}초, 반복 횟수: {'무한' if args.iterations <= 0 else args.iterations}회")
    print("트렌드 감시를 시작합니다. (Ctrl+C로 종료)\n")

    try:
        iteration_count = 0
        while True:
            iteration_count += 1
            if args.iterations > 0 and iteration_count > args.iterations:
                break # 지정된 반복 횟수 초과 시 종료

            print(f"\n--- 감시 주기 #{iteration_count} ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
            
            detected_new, detected_updated = simulate_trend_monitoring(all_keywords, current_trends_state)

            trends_for_notification = {}
            # 새로운 트렌드 처리 및 저장
            for trend_name, data in detected_new.items():
                trends_for_notification[trend_name] = data
                current_trends_state[trend_name] = data # 상태 업데이트
                save_trend_data_to_csv({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "trend_name": trend_name,
                    "virality_score": data["score"], "status": data["status"],
                    "feature": data["feature"], "example_link": data["link"]
                })

            # 기존 트렌드 업데이트 및 저장 (급성장 트렌드만 알림)
            for trend_name, data in detected_updated.items():
                if data["status"] == "GROWING":
                    trends_for_notification[trend_name] = data
                current_trends_state[trend_name] = data # 상태 업데이트
                save_trend_data_to_csv({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "trend_name": trend_name,
                    "virality_score": data["score"], "status": data["status"],
                    "feature": data["feature"], "example_link": data["link"]
                })

            send_notification(trends_for_notification)
            
            if not (args.iterations > 0 and iteration_count >= args.iterations): # 마지막 반복 후에는 대기하지 않음
                print(f"[INFO] 다음 감시까지 {args.interval}초 대기 중... (종료: Ctrl+C)")
                time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n[INFO] 봇을 수동으로 종료합니다. 사용자 요청.")
    except Exception as e:
        print(f"[CRITICAL] 예측하지 못한 치명적인 오류 발생: {e}")
    finally:
        print("\n=== Viral Wave Whisperer 봇 종료 ===")
        print("✨ 감지된 알림은 'trend_notifications.txt', 모든 데이터는 'viral_wave_data.csv' 파일에 저장되었습니다.")
        print("💡 봇을 매일 반복 실행하려면, 스케줄러(예: cron, 작업 스케줄러)에 'python viral_wave_whisperer.py'를 등록하세요.")

if __name__ == "__main__":
    main()