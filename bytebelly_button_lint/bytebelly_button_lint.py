
# ─────────────────────────────────────────────────────────────────────────────
# [실행 환경 방어] 한글 윈도우에서 출력을 파일로 저장하거나 다른 프로그램에 넘길 때
#   (예: python bot.py > log.txt / 작업 스케줄러 등록 / 주피터 / VS Code 일부 설정)
#   파이썬이 콘솔 기본 인코딩(cp949)을 쓰게 되어 이모지 출력 순간 UnicodeEncodeError로 죽습니다.
#   아래 3줄이 그걸 막아줍니다. 지우지 마세요!
# ─────────────────────────────────────────────────────────────────────────────
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


import os
import uuid
import datetime

# Configuration
LEDGER_FILE = "bytebelly_ledger.csv"
CERTIFICATE_DIR = "bytebelly_certificates"
LINT_SIZE_BYTES = 16 # Size of the "digital lint" in bytes
MOCK_TELEGRAM_BOT_TOKEN = "YOUR_MOCK_TELEGRAM_BOT_TOKEN" # Placeholder for a real Telegram bot token

def harvest_ephemeral_data(size_bytes: int) -> bytes:
    """
    Simulates harvesting unpredictable bit sequences from system's 'invisible' corners.
    For demonstration, generates cryptographically strong random bytes.
    """
    try:
        # os.urandom provides cryptographically strong random bytes,
        # simulating entropy from system processes/memory.
        lint_data = os.urandom(size_bytes)
        print(f"\    [HARVEST] Collected {len(lint_data)} bytes of digital lint.")
        return lint_data
    except Exception as e:
        print(f"\    [ERROR] Failed to harvest data: {e}")
        return b''

def mint_unique_artifact(lint_data: bytes) -> dict:
    """
    Mints a unique digital artifact with ID, timestamp, and lint details.
    """
    if not lint_data:
        print("\    [MINT] No lint data to mint.")
        return {}

    artifact_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()
    # Store a hex preview for the ledger, and full hex for the certificate.
    lint_hex_preview = lint_data.hex()[:32] + "..." if len(lint_data) > 32 else lint_data.hex()

    artifact = {
        "id": artifact_id,
        "timestamp": timestamp,
        "lint_data_hex_preview": lint_hex_preview,
        "raw_lint_full_hex": lint_data.hex() # Storing full hex for certificate
    }
    print(f"\    [MINT] Minted unique artifact: {artifact_id}")
    return artifact

def update_proof_of_scarcity_ledger(artifact: dict):
    """
    Records artifact details to a simple CSV ledger for scarcity proof.
    Creates the file if it doesn't exist.
    """
    if not artifact:
        return

    file_exists = os.path.exists(LEDGER_FILE)
    try:
        with open(LEDGER_FILE, 'a', encoding='utf-8') as f:
            if not file_exists:
                f.write("ID,Timestamp,LintPreview\
") # Header for new file
            f.write(f"{artifact['id']},{artifact['timestamp']},{artifact['lint_data_hex_preview']}\
")
        print(f"\    [LEDGER] Artifact {artifact['id']} recorded in ledger.")
    except IOError as e:
        print(f"\    [ERROR] Failed to update ledger file '{LEDGER_FILE}': {e}")

def generate_purchase_certificate(artifact: dict, buyer_info: str = "Mock Buyer"):
    """
    Mocks the 1-Dollar Digital Kiosk by generating a text certificate.
    """
    if not artifact:
        print("\    [KIOSK] No artifact to generate certificate for.")
        return None

    # Ensure the directory for certificates exists
    if not os.path.exists(CERTIFICATE_DIR):
        try:
            os.makedirs(CERTIFICATE_DIR)
            print(f"\    [KIOSK] Created certificate directory: {CERTIFICATE_DIR}")
        except OSError as e:
            print(f"\    [ERROR] Failed to create directory '{CERTIFICATE_DIR}': {e}")
            return None

    certificate_filename = os.path.join(CERTIFICATE_DIR, f"certificate_{artifact['id']}.txt")
    try:
        with open(certificate_filename, 'w', encoding='utf-8') as f:
            f.write("--- ByteBelly Button Lint - Purchase Certificate ---\
")
            f.write(f"\
This certifies the purchase of a unique digital artifact.\
")
            f.write(f"\
Artifact ID: {artifact['id']}\
")
            f.write(f"Minted On: {artifact['timestamp']}\
")
            f.write(f"Digital Lint (Hex): {artifact['raw_lint_full_hex']}\
")
            f.write(f"\
Buyer: {buyer_info}\
")
            f.write(f"Price: $1.00 (USD)\
")
            f.write("\
Thank you for collecting digital scarcity!\
")
            f.write("-----------------------------------------------------\
")
        print(f"\    [KIOSK] Purchase certificate generated: {certificate_filename}")
        return certificate_filename
    except IOError as e:
        print(f"\    [ERROR] Failed to generate certificate '{certificate_filename}': {e}")
        return None

def mock_telegram_bot_sale_logic(artifact: dict):
    """
    Mocks the Telegram bot interaction for selling an artifact.
    In a real scenario, this would involve sending messages and handling commands.
    Here, we simulate a 'sale' by generating a certificate.
    """
    print("\
[MOCK TELEGRAM BOT] Simulating a $1 sale request...")
    certificate_path = generate_purchase_certificate(artifact)
    if certificate_path:
        print(f"[MOCK TELEGRAM BOT] Successfully 'sold' artifact {artifact['id']} and generated certificate.")
        print(f"\    \    (Imagine this certificate and artifact ID being sent to a user via Telegram.)")
    else:
        print("[MOCK TELEGRAM BOT] Sale simulation failed.")

def main():
    print("--- ByteBelly Button Lint Collector v1.0 ---")
    print("[INIT] Starting digital lint harvesting process...")

    # 1. Ephemeral Data Harvesting
    lint_data = harvest_ephemeral_data(LINT_SIZE_BYTES)
    if not lint_data:
        print("[EXIT] No lint data harvested. Exiting.")
        return

    # 2. Unique Artifact Minting
    artifact = mint_unique_artifact(lint_data)
    if not artifact:
        print("[EXIT] Failed to mint artifact. Exiting.")
        return

    # 3. Proof-of-Scarcity Ledger
    update_proof_of_scarcity_ledger(artifact)

    # 4. 1-Dollar Digital Kiosk (Mocked Telegram Bot Interaction)
    mock_telegram_bot_sale_logic(artifact)

    print("\
--- ByteBelly Button Lint Process Complete ---")
    print(f"Check '{LEDGER_FILE}' for ledger history and '{CERTIFICATE_DIR}/' for generated certificates.")
    print("\
[USAGE TIP] Schedule this script to run daily for a continuous supply of unique digital lint!")
    print("\    Example: Add 'python main.py' to your cronjob or Windows Task Scheduler.")


if __name__ == "__main__":
    main()
