# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import pandas as pd
import os
from datetime import datetime
import logging
# Optional: Import requests for Telegram API, smtplib/email for Email API if needed
# import requests
# import smtplib
# from email.mime.text import MIMEText

# 로깅 설정: 상세한 진행 상황 및 에러 로깅을 위해 사용
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration Constants ---
# 팔로워 급증 감지 임계값: 이전 팔로워 대비 현재 팔로워 증가량이 이 값을 초과하면 경고 발생
ALERT_FOLLOW_SPIKE_THRESHOLD = 5000
# 좋아요 급증 감지 임계값: 이전 좋아요 대비 현재 좋아요 증가량이 이 값을 초과하면 경고 발생
ALERT_LIKE_SPIKE_THRESHOLD = 10000
# 스팸성 댓글/활동 감지에 사용될 키워드 목록 (소문자로 비교)
SPAM_KEYWORDS = ["buy followers", "get rich quick", "spam-link.com", "free money", "click here"]
# 보고서 파일이 저장될 디렉토리명
REPORT_DIR = "trollbuster_reports"

# --- Notification Service Credentials (환경 변수 사용 권장) ---
# Telegram 봇 토큰 및 채팅 ID. 환경 변수를 통해 설정하거나, 기본값을 변경하여 사용하세요.
# 예: export TELEGRAM_BOT_TOKEN="YOUR_TOKEN" in Linux/macOS or $env:TELEGRAM_BOT_TOKEN="YOUR_TOKEN" in PowerShell
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_TELEGRAM_CHAT_ID")

# 이메일 알림 설정을 위한 주석 처리된 예시 (필요시 주석 해제 후 사용)
# EMAIL_SENDER = os.getenv("EMAIL_SENDER", "your_email@example.com")
# EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "YOUR_EMAIL_PASSWORD") # 앱 비밀번호 사용 권장
# EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "agency_security@example.com")

def detect_anomalies(account_id, platform, current_followers, previous_followers,
                     current_likes, previous_likes, comments_text):
    """
    주어진 계정 데이터에서 비정상적인 활동(팔로워/좋아요 급증, 스팸 댓글)을 감지합니다.

    Args:
        account_id (str): 계정 고유 ID.
        platform (str): 계정이 속한 플랫폼 (예: 'YouTube', 'Instagram').
        current_followers (int): 현재 팔로워 수.
        previous_followers (int | None): 이전 시점의 팔로워 수 (비교 데이터가 없을 수 있음).
        current_likes (int): 현재 좋아요 수.
        previous_likes (int | None): 이전 시점의 좋아요 수 (비교 데이터가 없을 수 있음).
        comments_text (str): 최근 댓글들을 취합한 텍스트.

    Returns:
        list[str]: 감지된 이상 활동 메시지 목록. 없으면 빈 리스트.
    """
    anomalies = []
    logging.debug(f"[Detection] Analyzing account {account_id} on {platform}...")

    # 1. 팔로워 급증 감지: 이전 데이터가 있을 경우에만 비교
    if previous_followers is not None and (current_followers - previous_followers) > ALERT_FOLLOW_SPIKE_THRESHOLD:
        follower_gain = current_followers - previous_followers
        message = f"[Follower Spike] 계정 {account_id} ({platform})에서 비정상적으로 {follower_gain}명의 팔로워가 급증했습니다."
        anomalies.append(message)
        logging.warning(message)

    # 2. 좋아요 급증 감지: 이전 데이터가 있을 경우에만 비교
    if previous_likes is not None and (current_likes - previous_likes) > ALERT_LIKE_SPIKE_THRESHOLD:
        like_gain = current_likes - previous_likes
        message = f"[Like Spike] 계정 {account_id} ({platform})에서 비정상적으로 {like_gain}개의 좋아요가 급증했습니다."
        anomalies.append(message)
        logging.warning(message)

    # 3. 댓글 스팸/악용 감지
    if comments_text:
        lowercased_comments = comments_text.lower()
        for keyword in SPAM_KEYWORDS:
            if keyword in lowercased_comments:
                message = f"[Spam Comment] 계정 {account_id} ({platform})의 댓글에서 스팸 키워드 '{keyword}'가 감지되었습니다."
                anomalies.append(message)
                logging.warning(message)
                break # 하나의 댓글 블록에서 하나의 키워드만 감지되면 충분

    return anomalies

def send_alert(alert_message):
    """
    감지된 이상 활동에 대한 알림 메시지를 출력하고, 설정된 경우 외부 서비스로 전송합니다.

    Args:
        alert_message (str): 전송할 알림 메시지.
    """
    logging.info(f"\n>>> ALERT! {alert_message}")

    # --- 실시간 알림 서비스 통합 (주석 해제 후 사용) ---
    # Telegram 알림 예시
    # if TELEGRAM_BOT_TOKEN != "YOUR_TELEGRAM_BOT_TOKEN" and TELEGRAM_CHAT_ID != "YOUR_TELEGRAM_CHAT_ID":
    #     logging.info("  (Telegram 알림을 시도합니다...)")
    #     try:
    #         # 'requests' 라이브러리가 필요합니다: pip install requests
    #         response = requests.post(
    #             f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
    #             json={'chat_id': TELEGRAM_CHAT_ID, 'text': alert_message}
    #         )
    #         response.raise_for_status() # HTTP 에러 발생 시 예외 throw
    #         logging.info("  Telegram 알림 전송 성공.")
    #     except Exception as e:
    #         logging.error(f"  Telegram 알림 전송 실패: {e}")
    # else:
    #     logging.info("  (Telegram 알림 설정이 완료되지 않았습니다. 환경 변수를 확인하세요.)")

    # 이메일 알림 예시 (필요시 주석 해제 후 사용)
    # if EMAIL_SENDER != "your_email@example.com" and EMAIL_PASSWORD != "YOUR_EMAIL_PASSWORD":
    #     logging.info("  (이메일 알림을 시도합니다...)")
    #     try:
    #         # 'smtplib'와 'email' 라이브러리가 필요합니다 (파이썬 기본 내장).
    #         msg = MIMEText(alert_message, _charset='utf-8')
    #         msg['Subject'] = 'TrollBuster 긴급 알림!'
    #         msg['From'] = EMAIL_SENDER
    #         msg['To'] = EMAIL_RECEIVER
    #         with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    #             smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
    #             smtp.send_message(msg)
    #         logging.info("  이메일 알림 전송 성공.")
    #     except Exception as e:
    #         logging.error(f"  이메일 알림 전송 실패: {e}")
    # else:
    #     logging.info("  (이메일 알림 설정이 완료되지 않았습니다. 환경 변수를 확인하세요.)")

def generate_report(detected_anomalies):
    """
    감지된 모든 이상 활동을 CSV 파일로 저장하는 보고서를 생성합니다.

    Args:
        detected_anomalies (list[dict]): 감지된 이상 활동 정보를 담은 사전(dictionary) 목록.
    """
    if not detected_anomalies:
        logging.info("감지된 이상 활동이 없습니다. 보고서를 생성하지 않습니다.")
        return

    logging.info("이상 활동 보고서를 생성 중입니다...")
    try:
        os.makedirs(REPORT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = os.path.join(REPORT_DIR, f"trollbuster_report_{timestamp}.csv")
        
        report_df = pd.DataFrame(detected_anomalies)
        report_df.to_csv(report_filename, index=False, encoding='utf-8-sig') # 한글 깨짐 방지
        logging.info(f"봇 활동 보고서가 다음 위치에 저장되었습니다: {report_filename}")
    except Exception as e:
        logging.error(f"보고서 생성 중 오류 발생: {e}")

def main():
    """
    TrollBuster Alert 프로그램의 메인 실행 함수.
    명령줄 인자를 파싱하고, 계정 데이터를 로드하여 이상 활동을 감지한 후 보고서를 생성합니다.
    """
    parser = argparse.ArgumentParser(description="TrollBuster Alert: 콘텐츠 크리에이터 계정의 비정상적인 활동을 감지합니다.")
    parser.add_argument(
        "--data_file", 
        type=str, 
        help="계정 데이터를 포함하는 CSV 파일 경로 (예: accounts.csv)."
    )
    args = parser.parse_args()

    accounts_data = []
    sample_data = [
        {"account_id": "YT_Creator_1", "platform": "YouTube", "current_followers": 105000, "previous_followers": 100000, "current_likes": 52000, "previous_likes": 50000, "recent_comments_text": "Great video! Love your content. Subscribe now!"},
        {"account_id": "IG_Influencer_2", "platform": "Instagram", "current_followers": 58000, "previous_followers": 50000, "current_likes": 12000, "previous_likes": 10000, "recent_comments_text": "Check out my new post! buy followers now! Limited offer!"},
        {"account_id": "TikTok_Star_3", "platform": "TikTok", "current_followers": 200000, "previous_followers": 195000, "current_likes": 50000, "previous_likes": 48000, "recent_comments_text": "Awesome dance! spam-link.com"},
        {"account_id": "FB_Page_4", "platform": "Facebook", "current_followers": 75000, "previous_followers": 74000, "current_likes": 15000, "previous_likes": 14500, "recent_comments_text": "Thanks for sharing!"}
    ]

    if args.data_file:
        logging.info(f"데이터 파일 '{args.data_file}'에서 데이터를 로드 시도합니다...")
        try:
            df = pd.read_csv(args.data_file)
            # 필수 컬럼 검증 및 누락된 선택적 컬럼 기본값 설정
            required_cols = ['account_id', 'platform', 'current_followers', 'current_likes']
            for col in required_cols:
                if col not in df.columns:
                    raise ValueError(f"필수 컬럼이 누락되었습니다: {col}. CSV 파일을 확인해 주세요.")
            
            # 선택적 컬럼은 .get()을 사용해 안전하게 접근하거나, NaN/None 처리
            df['previous_followers'] = df.get('previous_followers', pd.NA) 
            df['previous_likes'] = df.get('previous_likes', pd.NA)       
            df['recent_comments_text'] = df.get('recent_comments_text', '').fillna('') # NaN을 빈 문자열로 채움

            accounts_data = df.to_dict('records')
            logging.info(f"'{args.data_file}'에서 {len(accounts_data)}개의 계정을 성공적으로 로드했습니다.")
        except FileNotFoundError:
            logging.error(f"오류: 데이터 파일 '{args.data_file}'을 찾을 수 없습니다. 데모 샘플 데이터를 사용합니다.")
            accounts_data = sample_data
            logging.info("지금은 샘플 데이터입니다. 본인 파일을 쓰려면 'python trollbuster_alert.py --data_file your_accounts.csv'로 실행하세요.")
        except Exception as e:
            logging.error(f"CSV 파일 읽기 중 오류 발생: {e}. 데모 샘플 데이터를 사용합니다.")
            accounts_data = sample_data
            logging.info("지금은 샘플 데이터입니다. 본인 파일을 쓰려면 'python trollbuster_alert.py --data_file your_accounts.csv'로 실행하세요.")
    else:
        logging.info("데이터 파일이 제공되지 않았습니다. 데모 샘플 데이터를 사용합니다.")
        accounts_data = sample_data
        logging.info("지금은 샘플 데이터입니다. 본인 파일을 쓰려면 'python trollbuster_alert.py --data_file your_accounts.csv'로 실행하세요.")

    all_detected_anomalies = []

    if not accounts_data:
        logging.critical("처리할 계정 데이터가 없습니다. 프로그램을 종료합니다.")
        return

    logging.info("\n--- 비정상 활동 감지 시작 ---")
    for i, account in enumerate(accounts_data):
        account_id = account.get('account_id', 'Unknown')
        platform = account.get('platform', 'Unknown')
        logging.info(f"[{i+1}/{len(accounts_data)}] 계정 처리 중: {account_id} ({platform})")
        
        try:
            anomalies = detect_anomalies(
                account_id=account_id,
                platform=platform,
                current_followers=account.get('current_followers', 0),
                previous_followers=account.get('previous_followers'), # None 가능
                current_likes=account.get('current_likes', 0),
                previous_likes=account.get('previous_likes'),       # None 가능
                comments_text=str(account.get('recent_comments_text', '')) # None -> '' 변환
            )

            if anomalies:
                for alert in anomalies:
                    send_alert(alert)
                    all_detected_anomalies.append({
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Account_ID": account_id,
                        "Platform": platform,
                        "Anomaly_Type": alert.split(']')[0].replace('[', '').strip(),
                        "Description": alert
                    })
            else:
                logging.info(f"  계정 {account_id}에 대한 비정상 활동이 감지되지 않았습니다.")
        except Exception as e:
            logging.error(f"계정 {account_id} 처리 중 예상치 못한 오류 발생: {e}")
    
    logging.info("\n--- 비정상 활동 감지 완료 ---")
    generate_report(all_detected_anomalies)
    
    logging.info("\n이 스크립트를 주기적으로 실행하려면 (예: 매일 새벽 3시), cron (Linux/macOS) 또는 작업 스케줄러 (Windows)를 사용할 수 있습니다.")
    logging.info("cron 예시: `0 3 * * * python /path/to/trollbuster_alert.py --data_file /path/to/your_accounts.csv`")

if __name__ == "__main__":
    main()
