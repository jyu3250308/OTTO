# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import pandas as pd
import datetime
import os

# --- 전역 상수 정의 ---
GHOST_THRESHOLD_DAYS = 60  # 이 기간 이상 결제가 없으면 '유령 구독'으로 간주
REPORT_FILENAME_PREFIX = "subzero_sentinel_report_"

# 구독 서비스별 해지 가이드 정보 (실제 데이터베이스 또는 API에서 로드될 수 있음)
cancellation_guides = {
    "Netflix": "넷플릭스 웹사이트 로그인 후 '계정' -> '멤버십 해지'",
    "Spotify": "스포티파이 웹사이트 로그인 후 '프로필' -> '계정' -> '요금제' -> '프리미엄 해지'",
    "Amazon Prime Video": "아마존 웹사이트 로그인 후 '계정 및 목록' -> '프라임 멤버십' -> '멤버십 종료'",
    "Adobe Creative Cloud": "어도비 계정 관리 페이지 로그인 후 '플랜' -> '플랜 취소'",
    "Duolingo Plus": "듀오링고 앱/웹사이트 설정에서 'Plus 구독 관리'",
    "Google One": "Google One 앱/웹사이트 로그인 후 '설정' -> '멤버십 취소'",
    "Old Magazine X": "해당 잡지사 고객센터 문의 또는 웹사이트 로그인 후 구독 관리",
    "Gym Membership": "헬스장 직접 문의 또는 계약서 확인" # 예시: 거래 내역에 없어도 알려진 서비스
}

def get_mock_transactions():
    """사용자의 은행/카드 거래 내역을 모의로 생성하여 반환합니다."""
    today = datetime.date.today()
    print("[정보] 모의 거래 내역을 생성합니다...")
    return [
        {"date": str(today - datetime.timedelta(days=5)), "description": "Netflix Premium", "amount": -13900},
        {"date": str(today - datetime.timedelta(days=10)), "description": "Spotify Family Plan", "amount": -16500},
        {"date": str(today - datetime.timedelta(days=15)), "description": "Amazon Prime Video", "amount": -7900},
        {"date": str(today - datetime.timedelta(days=20)), "description": "Starbucks Coffee", "amount": -5000},
        {"date": str(today - datetime.timedelta(days=35)), "description": "Adobe Creative Cloud", "amount": -23100},
        {"date": str(today - datetime.timedelta(days=70)), "description": "Duolingo Plus", "amount": -9900},
        {"date": str(today - datetime.timedelta(days=90)), "description": "Gym Membership", "amount": -45000},
        {"date": str(today - datetime.timedelta(days=120)), "description": "Google One Storage", "amount": -2400},
        {"date": str(today - datetime.timedelta(days=150)), "description": "Old Magazine X", "amount": -10000} # 잊혀진 망령
    ]

def identify_subscriptions(transactions: list) -> dict:
    """거래 내역에서 AI 분석을 통해 구독 서비스 및 잠재적 '구독 망령'을 식별합니다."""
    print("\n[AI 분석 시작] 거래 내역에서 구독 서비스를 식별 중입니다...")
    identified_subscriptions = {}
    today = datetime.date.today()

    for tx in transactions:
        try:
            description = tx.get("description", "").lower()
            amount = abs(tx.get("amount", 0))
            tx_date_str = tx.get("date", "")
            tx_date = datetime.datetime.strptime(tx_date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError) as e:
            print(f"  [경고] 잘못된 거래 내역 형식: {tx} - {e}. 이 항목을 건너뜁니다.")
            continue

        for service_name_key in cancellation_guides.keys():
            if service_name_key.lower() in description:
                if service_name_key not in identified_subscriptions:
                    identified_subscriptions[service_name_key] = {
                        "last_seen": tx_date,
                        "amount": amount,
                        "status": "Active",
                        "cancel_guide": cancellation_guides[service_name_key]
                    }
                    print(f"  [식별 완료] 새로운 구독 서비스 '{service_name_key}' (최초 발견일: {tx_date})")
                else:
                    # 더 최신 결제 내역으로 정보 업데이트
                    if tx_date > identified_subscriptions[service_name_key]["last_seen"]:
                        identified_subscriptions[service_name_key]["last_seen"] = tx_date
                        identified_subscriptions[service_name_key]["amount"] = amount
                        print(f"  [정보 업데이트] '{service_name_key}' - 최신 결제일: {tx_date}")
                break # 해당 거래는 하나의 서비스에만 매칭

    print("\n[AI 분석 진행] 구독 망령(Ghost Subscription)을 탐지합니다...")
    # '구독 망령' 식별 (오랫동안 결제가 없는 서비스)
    for service, data in identified_subscriptions.items():
        days_since_last_payment = (today - data["last_seen"]).days
        if days_since_last_payment > GHOST_THRESHOLD_DAYS:
            data["status"] = f"Ghost ({days_since_last_payment}일 미결제)"
            print(f"  [구독 망령 발견!] '{service}' - {days_since_last_payment}일 동안 결제 없음.")
        else:
            data["status"] = "Active"
            print(f"  [정상 구독] '{service}' - 최근 결제일: {data['last_seen']} ({days_since_last_payment}일 전)")

    # 예시: 거래 내역에 없지만 알려진 '구독 망령' 추가
    # 실제 환경에서는 별도의 '잊혀진 구독 목록' 데이터베이스에서 로드될 수 있습니다.
    if "Gym Membership" not in identified_subscriptions:
        identified_subscriptions["Gym Membership"] = {
            "last_seen": today - datetime.timedelta(days=90), # 모의 데이터
            "amount": 45000,
            "status": "Ghost (오래된 미결제 또는 확인 필요)",
            "cancel_guide": cancellation_guides.get("Gym Membership", "정보 없음")
        }
        print(f"  [구독 망령 추가!] 'Gym Membership' - 거래 내역에서 확인되지 않은, 알려진 망령.")

    print("[AI 분석 완료] 총 {}개의 구독 서비스가 식별되었습니다.".format(len(identified_subscriptions)))
    return identified_subscriptions

def generate_report(subscriptions: dict):
    """식별된 구독 서비스 목록으로 CSV 보고서를 생성합니다."""
    report_filename = f"{REPORT_FILENAME_PREFIX}{datetime.date.today().strftime('%Y%m%d')}.csv"
    report_data = []

    print(f"\n[보고서 생성 시작] '{report_filename}' 파일을 준비합니다...")
    if not subscriptions:
        print("  [정보] 보고서로 저장할 구독 서비스가 없습니다.")
        return

    for service, data in subscriptions.items():
        report_data.append({
            "서비스명": service,
            "결제 금액 (월/최근)": f"{data['amount']:,}원",
            "최근 결제일": str(data['last_seen']),
            "상태": data['status'],
            "해지 가이드": data['cancel_guide']
        })

    df = pd.DataFrame(report_data)

    try:
        df.to_csv(report_filename, index=False, encoding='utf-8-sig')
        print(f"[보고서 생성 완료] '{report_filename}' 파일을 성공적으로 저장했습니다!")
        print("  -> 이 보고서를 통해 당신의 돈을 잠식하는 구독 망령들을 퇴치하세요!")
    except Exception as e:
        print(f"[에러 발생] 보고서 저장 중 오류가 발생했습니다: {e}")
        print(f"  -> 파일 경로 또는 권한을 확인해 주세요: {os.path.abspath(report_filename)}")

def main():
    """SubZero Sentinel 프로그램의 메인 실행 함수입니다."""
    print("==========================================")
    print("     SubZero Sentinel (구독제로 감시병)      ")
    print("==========================================")
    print("잊고 있던 구독 망령을 찾아내 퇴치하고 보고서를 만듭니다.\n")

    try:
        # 1. 가계부/카드 내역 불러오기 (모의 데이터)
        transactions = get_mock_transactions()
        print(f"[데이터 로드 완료] 총 {len(transactions)}건의 거래 내역을 불러왔습니다.\n")

        # 2. AI 기반 구독 서비스 지출 패턴 분석 및 식별
        identified_subscriptions = identify_subscriptions(transactions)

        # 3. 구독 망령 퇴치 보고서 생성 및 저장
        if identified_subscriptions:
            generate_report(identified_subscriptions)
        else:
            print("\n[결과 없음] 식별된 구독 서비스가 없어 보고서를 생성하지 않습니다.")

    except Exception as e:
        print(f"\n[치명적인 오류 발생] 프로그램 실행 중 예상치 못한 오류가 발생했습니다: {e}")
        _sys.exit(1)

    print("\n==========================================")
    print("SubZero Sentinel 실행 완료! 안녕히 계세요, 여러분!\n")
    print("매일 실행하여 새로운 구독 망령을 감시하고 재정 건강을 지키세요. (예: cron, Windows 작업 스케줄러)")

if __name__ == "__main__":
    main()
