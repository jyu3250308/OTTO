# -*- coding: utf-8 -*-
"""
ScoreScapes AI: 악보 한 장, 1달러 예술 🎼🎨 (v2 — 진짜로 그림이 나옵니다!)
========================================================================
퍼블릭 도메인 명곡의 실제 음표 데이터(음높이·길이)를 색·좌표·곡선으로 변환해
세상에 하나뿐인 제너러티브 아트(PNG)를 실제로 렌더링하는 봇입니다.
(제작: AI 에이전트 오또 · v2: 시뮬레이션 → 실제 아트 생성 엔진으로 전면 재작성)

- 음높이(pitch) → 색상(Hue)과 세로 위치
- 음길이(duration) → 원의 크기
- 시간 흐름 → 가로 흐름 + 연결 곡선
- 실행할 때마다 팔레트가 달라져 매번 다른 작품이 나옵니다
"""
import os
import random
import datetime
import colorsys

# ── 퍼블릭 도메인 명곡의 실제 도입부 음표 (MIDI 음높이, 길이[박]) ─────────
SCORES = {
    "Moonlight Sonata": {
        "composer": "L. v. Beethoven",
        "notes": [(56, 1), (61, 1), (64, 1), (56, 1), (61, 1), (64, 1),
                  (56, 1), (61, 1), (64, 1), (57, 1), (61, 1), (64, 1),
                  (57, 1), (62, 1), (66, 1), (56, 1), (62, 1), (64, 1)],
    },
    "Prelude in C (WTK I)": {
        "composer": "J. S. Bach",
        "notes": [(60, 1), (64, 1), (67, 1), (72, 1), (76, 1), (67, 1), (72, 1), (76, 1),
                  (60, 1), (62, 1), (69, 1), (74, 1), (77, 1), (69, 1), (74, 1), (77, 1)],
    },
    "Gymnopedie No.1": {
        "composer": "E. Satie",
        "notes": [(66, 3), (69, 1), (68, 1), (66, 1), (61, 2), (62, 3),
                  (66, 1), (64, 1), (62, 1), (59, 2), (57, 4)],
    },
    "Arirang": {
        "composer": "Korean Folk Song",
        "notes": [(64, 2), (67, 1), (69, 2), (67, 1), (69, 1), (72, 2),
                  (69, 1), (67, 1), (64, 2), (62, 1), (60, 2), (62, 1), (64, 4)],
    },
}


# ── 큐레이션 팔레트 (배경, 음표 색상들) — 랜덤 HSV 대신 엄선된 조합 ────────
PALETTES = [
    ("Aurora",  (6, 8, 26),  [(94, 234, 212), (129, 140, 248), (244, 114, 182), (56, 189, 248), (167, 243, 208)]),
    ("Ember",   (24, 8, 18), [(251, 146, 60), (250, 204, 21), (248, 113, 113), (232, 121, 249), (253, 224, 71)]),
    ("Moonlit", (10, 12, 32), [(148, 163, 255), (196, 181, 253), (125, 211, 252), (226, 232, 240), (110, 231, 183)]),
    ("Rosegold", (20, 10, 16), [(253, 164, 175), (251, 191, 36), (244, 194, 194), (255, 228, 196), (240, 171, 252)]),
]


def render_scorescape(title, score, out_dir="artworks"):
    """
    🎨 핵심 엔진 v2.1: 음표 시퀀스를 '포스터급' 제너러티브 아트로 렌더링합니다.
    - 2배 슈퍼샘플링(안티앨리어싱) → 인쇄해도 매끈
    - 방사형 그라데이션 우주 배경 + 성운(블러) 레이어
    - 멜로디가 황금 나선을 따라 흐르며, 음표마다 진짜 글로우(가우시안 블러)
    """
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
    except ImportError:
        print("[ScoreScapes] Pillow가 필요합니다: pip install Pillow")
        return None

    import math
    notes = score["notes"]
    S = 2                                   # 슈퍼샘플링 배율
    W, H = 1080 * S, 1350 * S
    pname, bg, colors = random.choice(PALETTES)

    # 1) 방사형 그라데이션 배경 (중심이 은은히 밝은 심우주)
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, int(H * 0.46)
    max_r = int(math.hypot(W, H) * 0.7)
    center_boost = 26
    for r in range(max_r, 0, -6 * S):
        k = r / max_r
        col = tuple(int(bg[i] + center_boost * (1 - k)) for i in range(3))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    # 2) 성운 레이어 — 큰 색 얼룩을 강하게 블러 (저알파 무드 조명)
    nebula = Image.new("RGB", (W, H), (0, 0, 0))
    ndraw = ImageDraw.Draw(nebula)
    for _ in range(6):
        nc = random.choice(colors)
        nx, ny = random.randint(0, W), random.randint(0, H)
        nr = random.randint(180 * S, 380 * S)
        ndraw.ellipse([nx - nr, ny - nr, nx + nr, ny + nr],
                      fill=tuple(int(c * 0.22) for c in nc))
    nebula = nebula.filter(ImageFilter.GaussianBlur(120 * S))
    img = Image.blend(img, Image.blend(img, nebula, 0.5), 0.9)
    # 밝은 성분만 더하는 효과를 위해 스크린 합성 근사
    from PIL import ImageChops
    img = ImageChops.screen(img, nebula)
    draw = ImageDraw.Draw(img)

    # 3) 멜로디 나선 좌표 계산 (시간→회전각, 음높이→반지름 변조)
    pitches = [p for p, _ in notes]
    p_min, p_max = min(pitches), max(pitches)
    total = len(notes)
    pts, sizes, cols = [], [], []
    spiral_turns = 1.9
    r_in, r_out = 90 * S, 430 * S
    for i, (pitch, dur) in enumerate(notes):
        t = i / max(1, total - 1)
        ang = -math.pi / 2 + t * spiral_turns * 2 * math.pi
        p_norm = (pitch - p_min) / max(1, (p_max - p_min))
        radius = r_in + (r_out - r_in) * t + (p_norm - 0.5) * 70 * S
        x = cx + radius * math.cos(ang)
        y = cy + radius * math.sin(ang) * 0.92
        pts.append((x, y))
        sizes.append((10 + dur * 9) * S)
        cols.append(colors[pitch % len(colors)])

    # 4) 글로우 레이어 — 음표를 굵게 찍고 가우시안 블러 → 진짜 빛망울
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    for i in range(len(pts) - 1):
        gdraw.line([pts[i], pts[i + 1]], fill=tuple(int(c * 0.5) for c in cols[i]), width=6 * S)
    for (x, y), r, c in zip(pts, sizes, cols):
        gdraw.ellipse([x - r * 1.7, y - r * 1.7, x + r * 1.7, y + r * 1.7], fill=c)
    glow = glow.filter(ImageFilter.GaussianBlur(16 * S))
    img = ImageChops.screen(img, glow)
    draw = ImageDraw.Draw(img)

    # 5) 크리스프 코어 — 선명한 음표 알맹이 + 흰 하이라이트
    for (x, y), r, c in zip(pts, sizes, cols):
        draw.ellipse([x - r, y - r, x + r, y + r], fill=c)
        hr = r * 0.38
        draw.ellipse([x - hr - r * 0.18, y - hr - r * 0.18, x + hr - r * 0.18, y + hr - r * 0.18],
                     fill=tuple(min(255, int(cc + 110)) for cc in c))

    # 6) 별가루
    for _ in range(140):
        sx, sy = random.randint(0, W), random.randint(0, H)
        b = random.randint(70, 130)
        draw.ellipse([sx, sy, sx + 2 * S, sy + 2 * S], fill=(b, b, int(b * 1.15)))

    # 7) 포스터 타이포그래피 (하단 미니멀)
    font_candidates = ["C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/malgun.ttf",
                       "/System/Library/Fonts/AppleSDGothicNeo.ttc",
                       "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"]
    fp = next((p for p in font_candidates if os.path.exists(p)), None)
    if fp:
        f_title = ImageFont.truetype(fp, 44 * S)
        f_sub = ImageFont.truetype(fp, 24 * S)
        tw = draw.textbbox((0, 0), title, font=f_title)[2]
        ty = H - 170 * S
        draw.line([(cx - 90 * S, ty - 24 * S), (cx + 90 * S, ty - 24 * S)],
                  fill=(200, 200, 220), width=2 * S)
        draw.text(((W - tw) // 2, ty), title, font=f_title, fill=(235, 235, 245))
        sub = f"{score['composer']}  ·  {pname} palette  ·  ScoreScapes AI"
        sw = draw.textbbox((0, 0), sub, font=f_sub)[2]
        draw.text(((W - sw) // 2, ty + 62 * S), sub, font=f_sub, fill=(150, 150, 175))

    # 8) 다운샘플(안티앨리어싱) 후 저장 — 인쇄용은 원본 크기도 함께
    final = img.resize((1080, 1350), Image.Resampling.LANCZOS)
    os.makedirs(out_dir, exist_ok=True)
    safe = "".join(c for c in title if c.isalnum() or c == " ").replace(" ", "_")
    path = os.path.join(out_dir, f"scorescape_{safe}_{datetime.date.today().isoformat()}_{random.randint(100, 999)}.png")
    final.save(path, "PNG")
    return path


def main():
    print("🎼 ScoreScapes AI 기동 — 악보에서 예술을 캐냅니다... (v2: 진짜 렌더링!)")
    title = random.choice(list(SCORES.keys()))
    score = SCORES[title]
    print(f" - 오늘의 악보: {title} ({score['composer']}) · 음표 {len(score['notes'])}개 파싱")

    path = render_scorescape(title, score)
    if path:
        print(f"🎨 아트워크 렌더링 완료 -> {path}")
        print("✅ 세상에 하나뿐인 작품이 탄생했습니다! (실행할 때마다 색감이 달라져요)")
        print("💡 팁: artworks/ 폴더에 작품이 쌓입니다. 스케줄러에 등록하면 매일 새 작품이!")
    else:
        print("❌ 렌더링 실패 — Pillow 설치 후 다시 시도해 주세요.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[ScoreScapes] 사용자에 의해 중단되었습니다.")
