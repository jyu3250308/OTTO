# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import hashlib
import argparse
import requests
import os
from datetime import datetime

def generate_fingerprint(content: str) -> str:
    """콘텐츠의 SHA-256 해시를 디지털 지문으로 생성합니다."""
    # 인코딩 오류 방지를 위해 utf-8로 인코딩합니다.
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def load_content(source: str) -> str or None:
    """URL 또는 로컬 파일 경로에서 콘텐츠를 로드합니다. 실패 시 None을 반환합니다."""
    print(f"  [PROGRESS] 콘텐츠 로드 중: '{source}'")
    if source.startswith('http://') or source.startswith('https://'):
        try:
            # 웹 요청 시 타임아웃을 설정하여 무한 대기를 방지합니다.
            response = requests.get(source, timeout=15)
            response.raise_for_status() # 200 이외의 상태 코드에 대해 HTTPError 발생
            print(f"  [INFO] URL 콘텐츠 로드 성공: '{source}'")
            return response.text
        except requests.exceptions.Timeout:
            print(f"[ERROR] URL 요청 시간 초과: '{source}' (15초)")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] URL에서 콘텐츠를 가져올 수 없습니다 '{source}': {e}")
            return None
    else:
        try:
            # 파일 인코딩은 utf-8로 지정하여 한글 깨짐을 방지합니다.
            with open(source, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"  [INFO] 파일 콘텐츠 로드 성공: '{source}'")
                return content
        except FileNotFoundError:
            print(f"[ERROR] 파일을 찾을 수 없습니다: '{source}'")
            return None
        except IOError as e:
            print(f"[ERROR] 파일 읽기 오류 '{source}': {e}")
            return None
        except Exception as e:
            print(f"[ERROR] 알 수 없는 파일 처리 오류 '{source}': {e}")
            return None

def notify_owner(original_source: str, detected_on: str, recipient_email: str = None):
    """원래 콘텐츠 소유자에게 침해 알림을 시뮬레이션합니다."""
    message = f"🚨 침해 경고! 귀하의 콘텐츠 '{original_source}'가 '{detected_on}'에서 복사되었을 수 있습니다."
    print(f"\n[NOTIFICATION] {message}")
    if recipient_email:
        print(f"[INFO] 수신인 {recipient_email}에게 이메일 알림이 전송됩니다.")
        # 실제 시나리오에서는 smtplib를 사용하여 이메일을 보냅니다.
        # 환경 변수를 사용하여 보안 및 유연성을 확보합니다.
        # SENDER_EMAIL, SENDER_PASSWORD, SMTP_SERVER, SMTP_PORT 등의 환경 변수를 설정하세요.
        # import smtplib
        # from email.message import EmailMessage
        # msg = EmailMessage()
        # msg.set_content(message)
        # msg['Subject'] = 'CopyCat Crusader: 콘텐츠 침해 감지!'
        # msg['From'] = os.getenv('SENDER_EMAIL', 'copycat@example.com') # 발신 이메일
        # msg['To'] = recipient_email
        # try:
        #     with smtplib.SMTP_SSL(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT', 465))) as smtp:
        #         smtp.login(msg['From'], os.getenv('SENDER_PASSWORD'))
        #         smtp.send_message(msg)
        #     print("[INFO] 이메일 알림이 성공적으로 전송되었습니다.")
        # except Exception as e:
        #     print(f"[ERROR] 이메일 알림 전송 실패: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="CopyCat Crusader: AI 콘텐츠 표절 모니터링 도구",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--original', nargs='+', 
        help='원본 콘텐츠 파일 경로(들) 또는 URL(들). 예: my_story.txt https://blog.com/post'
    )
    parser.add_argument(
        '--monitor', nargs='+', 
        help='모니터링할 콘텐츠 파일 경로(들) 또는 URL(들). 예: suspect.html https://badsite.net/copy'
    )
    parser.add_argument(
        '--email', 
        help='침해 알림을 받을 이메일 주소 (선택 사항). 환경 변수 CRUSADER_EMAIL_RECIPIENT로 설정 가능.', 
        default=os.getenv('CRUSADER_EMAIL_RECIPIENT')
    )
    args = parser.parse_args()

    original_sources = []
    monitor_targets = []

    # 사용자 입력이 없는 경우 데모 모드 작동
    if not args.original and not args.monitor:
        print("\n[INFO] 원본 또는 모니터링 대상이 지정되지 않아 데모 모드로 실행됩니다.")
        print("       본인의 파일/URL을 사용하려면 다음 명령어를 실행하세요:\n       python copycat_crusader.py --original my_content.txt --monitor suspicious_site.com other_doc.txt\n")
        original_sources = ['demo_original.txt']
        monitor_targets = ['demo_copy.txt', 'https://example.com/'] # 데모에 실제 URL 포함
        
        # 데모 파일 생성 (이미 존재하면 덮어쓰지 않음)
        if not os.path.exists('demo_original.txt'):
            with open('demo_original.txt', 'w', encoding='utf-8') as f:
                f.write("이것은 저의 고유한 원본 콘텐츠입니다.\n매우 창의적이고 독특합니다.\n아무도 이것을 복사해서는 안 됩니다.")
            print("  [INFO] 'demo_original.txt' 파일이 생성되었습니다.")
        if not os.path.exists('demo_copy.txt'):
            with open('demo_copy.txt', 'w', encoding='utf-8') as f:
                f.write("이것은 저의 고유한 원본 콘텐츠입니다.\n매우 창의적이고 독특합니다.\n아무도 이것을 복사해서는 안 됩니다.\n하지만 누군가 복사한 것 같습니다.")
            print("  [INFO] 'demo_copy.txt' 파일이 생성되었습니다.")
    else:
        original_sources = args.original if args.original else []
        monitor_targets = args.monitor if args.monitor else []

    if not original_sources:
        print("[ERROR] 처리할 원본 콘텐츠가 없습니다. '--original' 인자를 지정하거나 데모 모드로 실행하세요. 종료합니다.")
        return
    if not monitor_targets:
        print("[ERROR] 모니터링할 대상이 없습니다. '--monitor' 인자를 지정하거나 데모 모드로 실행하세요. 종료합니다.")
        return

    original_fingerprints = {}
    print("\n[STEP 1/3] 원본 콘텐츠의 지문을 생성합니다...")
    for i, source in enumerate(original_sources, 1):
        print(f"[PROGRESS] ({i}/{len(original_sources)}) 원본: '{source}'")
        content = load_content(source)
        if content:
            fingerprint = generate_fingerprint(content)
            original_fingerprints[source] = fingerprint
            print(f"  ✅ 원본 '{source}' 지문 생성 완료: {fingerprint[:10]}...")
        else:
            print(f"  [WARNING] '{source}'에서 콘텐츠를 로드할 수 없어 지문 생성에서 제외됩니다.")

    if not original_fingerprints:
        print("[ERROR] 로드되거나 지문이 생성된 원본 콘텐츠가 없습니다. 프로그램을 종료합니다.")
        return

    print("\n[STEP 2/3] 대상 플랫폼을 모니터링합니다...")
    infringements = []
    for i, target in enumerate(monitor_targets, 1):
        print(f"[PROGRESS] ({i}/{len(monitor_targets)}) 대상 스캔 중: '{target}'")
        target_content = load_content(target)
        if not target_content:
            print(f"  [WARNING] '{target}'에서 콘텐츠를 로드할 수 없어 스캔에서 제외됩니다.")
            continue

        target_fingerprint = generate_fingerprint(target_content)
        print(f"  [INFO] 대상 '{target}' 지문 생성 완료: {target_fingerprint[:10]}...")

        found_match = False
        for original_source, original_fp in original_fingerprints.items():
            if target_fingerprint == original_fp:
                infringements.append({'original': original_source, 'detected_on': target, 'timestamp': datetime.now().isoformat()})
                print(f"  ✅ 일치 감지! 원본 '{original_source}'가 '{target}'에서 발견되었습니다!")
                notify_owner(original_source, target, args.email)
                found_match = True
                break
        if not found_match:
            print(f"  [INFO] '{target}'에서 직접적인 지문 일치 항목을 찾을 수 없습니다.")

    print("\n[STEP 3/3] 시장 트렌드 보고서를 생성합니다...")
    report_filename = f"copycat_crusader_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("CopyCat Crusader: AI 콘텐츠 표절 보고서\n")
            f.write("---------------------------------------------------\n")
            f.write(f"보고서 생성 시각: {datetime.now().isoformat()}\n\n")
            f.write(f"모니터링된 총 원본 콘텐츠 수: {len(original_fingerprints)}\n")
            f.write(f"스캔된 총 대상 수: {len(monitor_targets)}\n\n")

            if infringements:
                f.write("--- 감지된 침해 내역 ---\n")
                for i, inf in enumerate(infringements, 1):
                    f.write(f"{i}. 원본: {inf['original']}\n")
                    f.write(f"   감지된 위치: {inf['detected_on']}\n")
                    f.write(f"   타임스탬프: {inf['timestamp']}\n")
                    f.write("\n")
                f.write("\n--- 익명화된 시장 트렌드 분석 ---\n")
                f.write("이 섹션은 가장 자주 복사되는 일반적인 플랫폼/콘텐츠 유형을 분석합니다.\n")
                f.write("예시 트렌드: '블로그/단순 웹사이트의 텍스트 기반 콘텐츠가 자주 복사됨.'\n")
                f.write("(이 익명화된 데이터는 콘텐츠 보호 솔루션 회사에 판매될 수 있습니다.)\n")
            else:
                f.write("이번 실행에서는 침해가 감지되지 않았습니다. 귀하의 콘텐츠는 안전합니다 (현재까지)!\n")
        print(f"\n[REPORT] 보고서가 '{report_filename}' 파일로 저장되었습니다.")
    except IOError as e:
        print(f"[ERROR] 보고서 파일 저장 실패 '{report_filename}': {e}")

    print("\n--- CopyCat Crusader 완료! ---")
    print("팁: `cron` 또는 Windows 작업 스케줄러를 사용하여 이 스크립트를 매일 실행하여 지속적인 모니터링을 수행하세요!")

if __name__ == "__main__":
    main()
