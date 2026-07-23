# -*- coding: utf-8 -*-
"""
오또의 밈오매틱 🏭😂 (v2 — API 키 0개, 진짜 밈이 나오는 밈 공장!)
================================================================
개발자·직장인 공감 밈 문구를 표준 밈 스타일(상단/하단 임팩트 텍스트)로
실제 밈 이미지(PNG)로 찍어내는 봇입니다. 실행할 때마다 새 밈이 탄생!
(제작: AI 에이전트 오또 · v2: 유료 API 의존 제거 → 완전 자급자족 밈 공장)

사용법:
  python otto_meme_o_matic.py                       ← 랜덤 밈 생산
  python otto_meme_o_matic.py "상단 문구" "하단 문구"  ← 내 밈 주문 제작
"""
import os
import sys
import json
import random
import datetime

# ── 밈 문구 라이브러리 (상단 셋업 → 하단 펀치라인) ─────────────────────────
MEME_LINES = [
    ("금요일 오후 5시 59분", "월요일 오전 9시 1분"),
    ("내가 짠 코드", "6개월 뒤에 본 내 코드"),
    ("오늘은 일찍 자야지", "새벽 3시의 나"),
    ("딱 한 판만 하고 자야지", "동트는 소리"),
    ("이번 달엔 저축해야지", "택배 기사님과 절친이 된 나"),
    ("버그 고치는 데 5분이면 돼요", "3일째 같은 버그"),
    ("주석은 내일 달아야지", "그 내일은 오지 않았다"),
    ("운동은 내일부터", "1년째 내일"),
    ("회의 5분이면 끝나요", "2시간째 회의 중"),
    ("이 기능 간단해요", "간단하지 않았다"),
]

# 배경 색 조합 (상단 그라데이션풍, 매번 다른 무드)
PALETTES = [
    ((255, 214, 98), (255, 152, 80)),   # 노랑→주황
    ((142, 202, 255), (94, 114, 235)),  # 하늘→파랑
    ((255, 154, 158), (250, 208, 196)), # 핑크 파스텔
    ((168, 237, 234), (254, 214, 227)), # 민트→핑크
    ((210, 153, 255), (136, 96, 208)),  # 라벤더→보라
]


def draw_otto_face(draw, cx, cy, size):
    """가운데에 오또 스타일 얼굴(뿔테안경 너드)을 실제로 그립니다."""
    s = size
    draw.ellipse([cx - s, cy - s, cx + s, cy + s], fill=(255, 224, 189), outline=(60, 50, 40), width=6)   # 얼굴
    draw.arc([cx - s, cy - s * 1.35, cx + s, cy + s * 0.4], 180, 360, fill=(90, 60, 40), width=int(s * 0.45))  # 머리
    g = s * 0.42
    for gx in (cx - s * 0.45, cx + s * 0.45):                                # 뿔테안경
        draw.ellipse([gx - g, cy - g * 0.9, gx + g, cy + g * 0.9], outline=(40, 40, 40), width=8)
        draw.ellipse([gx - g * 0.35, cy - g * 0.3, gx - g * 0.05, cy], fill=(40, 40, 40))  # 눈동자
    draw.line([cx - s * 0.1, cy - s * 0.05, cx + s * 0.1, cy - s * 0.05], fill=(40, 40, 40), width=8)     # 안경 브릿지
    draw.arc([cx - s * 0.35, cy + s * 0.15, cx + s * 0.35, cy + s * 0.65], 0, 180, fill=(180, 90, 80), width=10)  # 미소


def render_meme(top_text, bottom_text, out_dir="memes"):
    """🏭 핵심 엔진: 표준 밈 스타일 이미지를 실제로 렌더링합니다."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("[밈오매틱] Pillow가 필요합니다: pip install Pillow")
        return None
    font_candidates = ["C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/malgun.ttf",
                       "/System/Library/Fonts/AppleSDGothicNeo.ttc",
                       "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"]
    fp = next((p for p in font_candidates if os.path.exists(p)), None)
    if not fp:
        print("[밈오매틱] 한글 폰트를 찾지 못했습니다.")
        return None

    W, H = 1080, 1080
    c1, c2 = random.choice(PALETTES)
    img = Image.new("RGB", (W, H), c1)
    draw = ImageDraw.Draw(img)
    for y in range(H):                                  # 세로 그라데이션 배경
        ratio = y / H
        row = tuple(int(c1[i] + (c2[i] - c1[i]) * ratio) for i in range(3))
        draw.line([(0, y), (W, y)], fill=row)

    draw_otto_face(draw, W // 2, H // 2, 190)

    font = ImageFont.truetype(fp, 88)

    def wrap(text, max_w):
        lines, line = [], ""
        for word in text.split():
            test = (line + " " + word).strip()
            if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
                line = test
            else:
                lines.append(line); line = word
        if line:
            lines.append(line)
        return lines

    def meme_text(text, anchor_top):
        lines = wrap(text, 980)
        y = 60 if anchor_top else H - 60 - len(lines) * 108
        for ln in lines:
            w = draw.textbbox((0, 0), ln, font=font)[2]
            draw.text(((W - w) // 2, y), ln, font=font, fill=(255, 255, 255),
                      stroke_width=10, stroke_fill=(0, 0, 0))
            y += 108

    meme_text(top_text, True)
    meme_text(bottom_text, False)

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"meme_{datetime.date.today().isoformat()}_{random.randint(100, 999)}.png")
    img.save(path, "PNG")
    return path


def save_history(top, bottom, path, history_file="meme_history.json"):
    """생산 이력을 누적 저장합니다 (오늘까지 몇 개 찍었는지 자랑용)."""
    history = []
    if os.path.exists(history_file):
        try:
            history = json.load(open(history_file, encoding="utf-8"))
        except Exception:
            history = []
    history.append({"date": datetime.datetime.now().isoformat(), "top": top, "bottom": bottom, "file": path})
    json.dump(history, open(history_file, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[밈오매틱] 생산 이력 기록 완료 (누적 {len(history)}개 밈 생산!)")


def main():
    print("🏭 밈오매틱 공장 가동 — 오늘의 밈을 찍어냅니다... (v2: 진짜 밈 생산!)")
    if len(sys.argv) >= 3:
        top, bottom = sys.argv[1], sys.argv[2]
        print(" - 주문 제작 모드!")
    else:
        top, bottom = random.choice(MEME_LINES)
        print(" - 랜덤 생산 모드!")

    path = render_meme(top, bottom)
    if path:
        print(f"\n😂 \"{top}\" → \"{bottom}\"")
        print(f"🖼️ 밈 출고 완료 -> {path} (SNS에 바로 올려보세요!)")
        save_history(top, bottom, path)
        print("💡 팁: python otto_meme_o_matic.py \"상단\" \"하단\" 으로 내 밈도 주문 제작!")
    else:
        print("❌ 생산 실패 — Pillow 설치 후 다시 시도해 주세요.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[밈오매틱] 공장 가동 중단!")
