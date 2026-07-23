# -*- coding: utf-8 -*-
"""
옷또입지? 👕 날씨 분석 AI 코디 추천 봇 (v2 — 진짜 날씨로 진짜 카드가 나옵니다!)
==============================================================================
무료 공개 날씨 API(open-meteo, 가입·키 불필요!)로 내일 날씨를 실측 조회하고,
기온·강수 확률에 맞는 코디를 추천해 SNS 공유 가능한 카드 이미지(PNG)로 저장합니다.
(제작: AI 에이전트 오또 · v2: 유료 API 의존 제거 → 완전 무료 실데이터로 재작성)

사용법: python main.py  (끝!)
"""
import os
import json
import datetime

# ── 위치 설정 (기본: 서울 — 원하는 도시의 위도/경도로 바꿔보세요) ──────────
LATITUDE, LONGITUDE, CITY_NAME = 37.5665, 126.9780, "서울"

# ── 기온별 코디 추천 규칙 (한국 옷차림 기준표 기반) ────────────────────────
OUTFIT_RULES = [
    (28, "민소매·반팔, 반바지, 린넨", "🥵 한여름 모드! 수분 보충 잊지 마세요"),
    (23, "반팔, 얇은 셔츠, 면바지", "😎 딱 좋은 날씨, 가볍게!"),
    (20, "얇은 가디건, 긴팔티, 청바지", "🍃 아침저녁 겉옷 하나 챙기면 완벽"),
    (17, "얇은 니트, 맨투맨, 가디건", "🍂 가을 감성 코디 각"),
    (12, "자켓, 트렌치코트, 니트", "🧥 겉옷은 필수인 날"),
    (9,  "코트, 가죽자켓, 히트텍", "🌬️ 바람이 차가워요"),
    (5,  "울코트, 두꺼운 니트, 목도리", "🧣 단단히 입고 나가세요"),
    (-99, "패딩, 기모, 목도리, 장갑", "🥶 동장군 출몰! 완전 무장 필수"),
]


def fetch_tomorrow_weather():
    """🌐 open-meteo 무료 API로 내일 날씨를 실측 조회합니다 (키 불필요)."""
    import urllib.request
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LATITUDE}&longitude={LONGITUDE}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        "&timezone=Asia%2FSeoul&forecast_days=2"
    )
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        d = data["daily"]
        return {
            "date": d["time"][1],
            "t_max": d["temperature_2m_max"][1],
            "t_min": d["temperature_2m_min"][1],
            "rain_prob": d["precipitation_probability_max"][1],
            "is_real": True,
        }
    except Exception as err:
        print(f"[옷또입지] 네트워크 조회 실패({err}) → 데모 데이터로 시연합니다.")
        return {"date": str(datetime.date.today() + datetime.timedelta(days=1)),
                "t_max": 24.0, "t_min": 17.0, "rain_prob": 30, "is_real": False}


def recommend_outfit(weather):
    """기온·강수 확률로 코디를 결정합니다."""
    avg = (weather["t_max"] + weather["t_min"]) / 2
    for threshold, outfit, comment in OUTFIT_RULES:
        if avg >= threshold:
            extra = " + ☂️ 우산 챙기세요!" if weather["rain_prob"] >= 50 else ""
            return outfit, comment + extra
    return OUTFIT_RULES[-1][1], OUTFIT_RULES[-1][2]


def render_outfit_card(weather, outfit, comment, out_dir="outfit_cards"):
    """👕 코디 추천을 SNS 공유용 카드 이미지(PNG)로 렌더링합니다."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("[옷또입지] Pillow 미설치 — 카드 생략 (pip install Pillow 하면 활성화!)")
        return None
    font_candidates = ["C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/malgun.ttf",
                       "/System/Library/Fonts/AppleSDGothicNeo.ttc",
                       "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"]
    fp = next((p for p in font_candidates if os.path.exists(p)), None)
    if not fp:
        return None

    # 폰트에 없는 이모지는 □로 깨지므로 카드에서만 제거 (콘솔·텔레그램엔 유지)
    import re
    emoji = re.compile(r"[\U00010000-\U0010ffff☀-➿⌀-⏿⭐⬆←-⇿️]")
    comment = re.sub(r"\s+", " ", emoji.sub("", comment)).strip()

    W, H = 1080, 1350
    warm = weather["t_max"] >= 20
    bg = (255, 244, 214) if warm else (214, 228, 255)   # 따뜻하면 크림, 추우면 하늘색
    fg = (45, 42, 38)
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    f_big = ImageFont.truetype(fp, 96)
    f_mid = ImageFont.truetype(fp, 54)
    f_body = ImageFont.truetype(fp, 46)
    f_small = ImageFont.truetype(fp, 30)

    def center(text, font, y, fill):
        w = draw.textbbox((0, 0), text, font=font)[2]
        draw.text(((W - w) // 2, y), text, font=font, fill=fill)

    center(f"{CITY_NAME}, 내일 뭐 입지?", f_mid, 120, fg)
    center(f"{weather['t_min']:.0f}° ~ {weather['t_max']:.0f}°", f_big, 230, (255, 120, 40) if warm else (40, 90, 220))
    center(f"강수 확률 {weather['rain_prob']}%", f_mid, 380, fg)
    draw.line([(190, 500), (W - 190, 500)], fill=fg, width=3)
    center("오또의 추천 코디", f_mid, 560, fg)
    # 코디 목록 (여러 줄)
    y = 660
    for item in outfit.split(", "):
        center(f"· {item}", f_body, y, fg)
        y += 70
    center(comment, f_body, y + 40, (200, 60, 60) if "우산" in comment else fg)
    center(f"{weather['date']} · 옷또입지 (실측: open-meteo)" if weather["is_real"]
           else f"{weather['date']} · 옷또입지 (데모 데이터)", f_small, H - 100, (120, 115, 105))

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"outfit_{weather['date']}.png")
    img.save(path, "PNG")
    return path


def send_telegram(message):
    """(옵션) 텔레그램 발송 — 토큰 없으면 조용히 생략."""
    token, chat_id = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    try:
        import urllib.request, urllib.parse
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode()
        urllib.request.urlopen(
            urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data), timeout=10)
        print("[옷또입지] 텔레그램 발송 완료! 📨")
    except Exception as err:
        print(f"[옷또입지] 텔레그램 발송 실패(무시): {err}")


def main():
    print("👕 옷또입지 기동 — 내일의 날씨를 실측 조회합니다... (v2: 무료 실데이터!)")
    weather = fetch_tomorrow_weather()
    src = "실측" if weather["is_real"] else "데모"
    print(f" - [{src}] {weather['date']} {CITY_NAME}: {weather['t_min']}°~{weather['t_max']}°, 강수 {weather['rain_prob']}%")

    outfit, comment = recommend_outfit(weather)
    print(f"\n👕 오또의 추천 코디: {outfit}")
    print(f"💬 {comment}\n")

    card = render_outfit_card(weather, outfit, comment)
    if card:
        print(f"🖼️ 코디 카드 저장 완료 -> {card} (SNS에 바로 공유 가능!)")
    send_telegram(f"👕 [옷또입지] {weather['date']} {CITY_NAME} {weather['t_min']}°~{weather['t_max']}°\n추천: {outfit}\n{comment}")
    print("✅ 완료! 스케줄러에 등록하면 매일 저녁 내일 코디가 자동 도착합니다.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[옷또입지] 사용자에 의해 중단되었습니다.")
