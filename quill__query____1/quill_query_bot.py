# -*- coding: utf-8 -*-
"""
Quill & Query: 고전 한 줄, 1달러의 통찰 🪶
==========================================
오래된 고전 문학 속 명문장에서 '타임머신 통찰 카드'를 만들어
매일 자동 발행하는 봇입니다. (제작: AI 에이전트 오또)

- 고전 명문장 수집·파싱
- AI 통찰 카드 생성 (현대적 재해석)
- 매일 자동 발행 및 공유 알림 (텔레그램 옵션)

외부 API 없이도 데모(rule-based) 모드로 100% 작동하며,
GEMINI_API_KEY를 넣으면 진짜 AI 재해석 모드로 업그레이드됩니다.
"""
import os
import json
import random
import datetime

# ── 1. 고전 명문장 라이브러리 (수집·파싱된 데이터 예시) ─────────────────
CLASSICS = [
    {"quote": "우리가 두려워해야 할 유일한 것은 두려움 그 자체다.",
     "source": "프랭클린 D. 루스벨트 취임 연설 (1933)"},
    {"quote": "내 사전에 불가능이란 없다.",
     "source": "나폴레옹 보나파르트"},
    {"quote": "성찰하지 않는 삶은 살 가치가 없다.",
     "source": "소크라테스, 『변론』"},
    {"quote": "인간은 노력하는 한 방황한다.",
     "source": "괴테, 『파우스트』"},
    {"quote": "행복한 가정은 모두 비슷하지만, 불행한 가정은 저마다의 이유로 불행하다.",
     "source": "톨스토이, 『안나 카레니나』"},
    {"quote": "천 리 길도 한 걸음부터 시작된다.",
     "source": "노자, 『도덕경』"},
]

# ── 2. 현대적 재해석 규칙 (데모 모드용 '타임머신 번역기') ────────────────
MODERN_LENSES = [
    ("사이드 프로젝트", "오늘 시작한 작은 커밋 하나가 미래의 포트폴리오가 됩니다."),
    ("자동화", "반복 작업을 봇에게 맡기는 순간, 당신의 시간은 복리로 불어납니다."),
    ("1달러 도전", "첫 1달러는 금액이 아니라 '증명'입니다. 시스템이 돈을 벌 수 있다는 증명."),
    ("꾸준함", "알고리즘은 하루의 대박보다 매일의 업로드를 사랑합니다."),
]


def build_insight_card(classic, use_ai=False):
    """고전 문장 하나를 '타임머신 통찰 카드'로 변환합니다."""
    if use_ai:
        card_body = ai_reinterpret(classic)
    else:
        lens_name, lens_msg = random.choice(MODERN_LENSES)
        card_body = f"[{lens_name}의 렌즈] {lens_msg}"

    today = datetime.date.today().strftime("%Y-%m-%d")
    card = (
        f"🪶 오늘의 타임머신 통찰 카드 ({today})\n"
        f"{'=' * 34}\n"
        f"📜 원문: {classic['quote']}\n"
        f"    — {classic['source']}\n\n"
        f"💡 현대 번역: {card_body}\n"
    )
    return card, card_body


def ai_reinterpret(classic):
    """(옵션) Gemini API로 고전 문장을 현대 감각으로 재해석합니다."""
    try:
        from google import genai
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        prompt = (
            "다음 고전 명문장을 현대의 개발자/사이드프로젝트/자동화 감성으로 "
            "2문장 이내로 재해석해 주세요. 담백하고 위트있게.\n"
            f"문장: {classic['quote']} ({classic['source']})"
        )
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return resp.text.strip()
    except Exception as err:
        print(f"[Quill&Query] AI 재해석 실패, 데모 모드로 폴백합니다: {err}")
        lens_name, lens_msg = random.choice(MODERN_LENSES)
        return f"[{lens_name}의 렌즈] {lens_msg}"


def render_card_image(classic, card_body, out_dir="cards"):
    """
    🖼️ 통찰 카드를 SNS 업로드용 이미지(PNG, 1080x1350 인스타 규격)로 렌더링합니다.
    Pillow가 없으면 조용히 건너뜁니다 (pip install Pillow).
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("[Quill&Query] Pillow 미설치 — 카드 이미지 생략 (pip install Pillow 하면 활성화!)")
        return None

    # 한글 폰트 자동 탐색 (Windows/macOS/Linux 순회)
    font_candidates = [
        "C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/malgun.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    ]
    font_path = next((p for p in font_candidates if os.path.exists(p)), None)
    if not font_path:
        print("[Quill&Query] 한글 폰트를 찾지 못해 카드 이미지를 생략합니다.")
        return None

    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), (26, 26, 46))          # 딥 네이비 배경
    draw = ImageDraw.Draw(img)
    f_quote = ImageFont.truetype(font_path, 58)
    f_src = ImageFont.truetype(font_path, 34)
    f_body = ImageFont.truetype(font_path, 44)
    f_foot = ImageFont.truetype(font_path, 28)

    def wrap(text, font, max_w):
        lines, line = [], ""
        for word in text.split():
            test = (line + " " + word).strip()
            if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
                line = test
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        return lines

    def draw_block(lines, font, y, color, lh):
        for ln in lines:
            w = draw.textbbox((0, 0), ln, font=font)[2]
            draw.text(((W - w) // 2, y), ln, font=font, fill=color)
            y += lh
        return y

    y = 160
    # 상단 장식: 노란 다이아몬드 (이모지는 폰트에 따라 깨질 수 있어 도형으로 그림)
    cx, s = W // 2, 26
    draw.polygon([(cx, y - s), (cx + s, y), (cx, y + s), (cx - s, y)], fill=(255, 228, 0))
    y += 90
    y = draw_block(wrap(f"“{classic['quote']}”", f_quote, 900), f_quote, y, (255, 255, 255), 80)
    y += 20
    y = draw_block(wrap(f"— {classic['source']}", f_src, 860), f_src, y, (160, 160, 190), 48)
    y += 70
    draw.line([(W // 2 - 160, y), (W // 2 + 160, y)], fill=(255, 228, 0), width=3)
    y += 60
    y = draw_block(wrap(card_body, f_body, 880), f_body, y, (255, 228, 0), 64)
    foot = "Quill & Query · 매일 자동 발행되는 타임머신 통찰"
    fw = draw.textbbox((0, 0), foot, font=f_foot)[2]
    draw.text(((W - fw) // 2, H - 90), foot, font=f_foot, fill=(120, 120, 150))

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"card_{datetime.date.today().isoformat()}.png")
    img.save(path, "PNG")
    print(f"[Quill&Query] 🖼️ SNS용 카드 이미지 저장 완료 -> {path}")
    return path


def send_telegram(message):
    """(옵션) 텔레그램으로 카드 발송. 토큰이 없으면 조용히 생략합니다."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    try:
        import urllib.request
        import urllib.parse
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode()
        req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data)
        with urllib.request.urlopen(req, timeout=10):
            pass
        print("[Quill&Query] 텔레그램 발송 완료! 📨")
        return True
    except Exception as err:
        print(f"[Quill&Query] 텔레그램 발송 실패(무시): {err}")
        return False


def save_history(card, path="insight_history.json"):
    """발행 이력을 JSON으로 누적 저장합니다 (중복 발행 방지·기록용)."""
    history = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append({"date": datetime.datetime.now().isoformat(), "card": card})
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print(f"[Quill&Query] 발행 이력 저장 완료 (누적 {len(history)}건)")


def main():
    print("🪶 Quill & Query 기동 — 고전에서 오늘의 통찰을 캐냅니다...")
    use_ai = bool(os.environ.get("GEMINI_API_KEY"))
    print(f" - 모드: {'AI 재해석' if use_ai else '데모(rule-based)'}")

    classic = random.choice(CLASSICS)
    card, card_body = build_insight_card(classic, use_ai=use_ai)

    print("\n" + card)
    image_path = render_card_image(classic, card_body)   # 🖼️ SNS 업로드용 카드 이미지
    send_telegram(card)
    save_history(card)
    if image_path:
        print(f"✅ 발행 완료! 텍스트 카드 + 이미지 카드({image_path}) — SNS에 바로 올려보세요!")
    else:
        print("✅ 오늘의 통찰 카드 발행 완료! 내일 또 만나요.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Quill&Query] 사용자에 의해 중단되었습니다. 안녕히!")
