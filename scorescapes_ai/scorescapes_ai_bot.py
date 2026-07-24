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
        "scene": "mountain",   # 아리랑 '고개' — 멜로디가 산등성이가 되는 새벽 산맥
    },
}
# 곡별 전용 장면(무드): 음표만이 아니라 곡의 정서를 시각 언어로 번역한다 (v2.2)
SCORES["Moonlight Sonata"]["scene"] = "moonsea"      # 달빛 바다 — 멜로디가 파도가 된다
SCORES["Prelude in C (WTK I)"]["scene"] = "geometry"  # 신성한 기하학 — 질서와 조화의 만다라
SCORES["Gymnopedie No.1"]["scene"] = "mist"           # 안개 파스텔 — 몽환과 여백


def _font(size):
    """시스템 한글 폰트 로더 (공용)."""
    from PIL import ImageFont
    for p in ["C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/malgun.ttf",
              "/System/Library/Fonts/AppleSDGothicNeo.ttc",
              "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _smooth_contour(values, out_len):
    """음높이 시퀀스를 부드러운 곡선(능선/파도)으로 보간합니다."""
    import math
    n = len(values)
    out = []
    for i in range(out_len):
        pos = i / (out_len - 1) * (n - 1)
        i0 = int(pos)
        i1 = min(i0 + 1, n - 1)
        frac = pos - i0
        # 코사인 보간 → 각지지 않은 자연스러운 능선
        f = (1 - math.cos(frac * math.pi)) / 2
        out.append(values[i0] * (1 - f) + values[i1] * f)
    return out


def _poster_caption(draw, W, H, S, title, sub, color=(240, 238, 232), subcolor=(170, 168, 160)):
    """하단 포스터 타이포그래피 (공용)."""
    f_title = _font(46 * S)
    f_sub = _font(24 * S)
    tw = draw.textbbox((0, 0), title, font=f_title)[2]
    ty = H - 165 * S
    draw.line([(W // 2 - 85 * S, ty - 22 * S), (W // 2 + 85 * S, ty - 22 * S)], fill=subcolor, width=2 * S)
    draw.text(((W - tw) // 2, ty), title, font=f_title, fill=color)
    sw = draw.textbbox((0, 0), sub, font=f_sub)[2]
    draw.text(((W - sw) // 2, ty + 64 * S), sub, font=f_sub, fill=subcolor)


def render_scene_mountain(title, score, out_dir):
    """
    🏔️ [아리랑 전용 장면] 멜로디의 음높이 곡선이 '산등성이'가 되는 새벽 산맥.
    겹겹의 능선(원근 안개) + 새벽 하늘 그라데이션 + 달 + 여백의 미 — 곡의 '고개'를 그림으로.
    """
    from PIL import Image, ImageDraw, ImageFilter, ImageChops
    import math
    S = 2
    W, H = 1080 * S, 1350 * S

    # 1) 새벽 하늘: 깊은 남보라 → 지평선의 옅은 살구빛
    sky_top, sky_low = (24, 22, 52), (222, 168, 130)
    horizon = int(H * 0.62)
    img = Image.new("RGB", (W, H), sky_top)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        k = min(1.0, y / horizon)
        k = k ** 1.6
        col = tuple(int(sky_top[i] + (sky_low[i] - sky_top[i]) * k) for i in range(3))
        draw.line([(0, y), (W, y)], fill=col)

    # 2) 달 + 글로우
    moon_x, moon_y, moon_r = int(W * 0.72), int(H * 0.20), 64 * S
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([moon_x - moon_r * 3, moon_y - moon_r * 3, moon_x + moon_r * 3, moon_y + moon_r * 3],
               fill=(70, 62, 58))
    glow = glow.filter(ImageFilter.GaussianBlur(60 * S))
    img = ImageChops.screen(img, glow)
    draw = ImageDraw.Draw(img)
    draw.ellipse([moon_x - moon_r, moon_y - moon_r, moon_x + moon_r, moon_y + moon_r],
                 fill=(246, 240, 226))

    # 3) 별 (상단 하늘에만, 은은하게)
    for _ in range(50):
        sx, sy = random.randint(0, W), random.randint(0, int(H * 0.35))
        b = random.randint(90, 150)
        draw.ellipse([sx, sy, sx + 2 * S, sy + 2 * S], fill=(b, b, int(b * 1.05)))

    # 4) 능선 5겹 — 맨 뒤 능선이 '진짜 멜로디 곡선', 앞겹은 변주(전조)
    pitches = [p for p, _ in notes_of(score)]
    p_min, p_max = min(pitches), max(pitches)
    norm = [(p - p_min) / max(1, p_max - p_min) for p in pitches]
    layers = 5
    for li in range(layers):
        depth = li / (layers - 1)                     # 0=원경(밝음) → 1=근경(어두움)
        base_y = horizon - int(H * 0.10) + int(H * 0.115 * li)
        amp = (H * 0.085) * (0.75 + 0.45 * (1 - depth))
        # 원경은 원본 멜로디, 근경으로 올수록 멜로디를 이동·반전시켜 변주
        seq = norm if li == 0 else [(v + 0.13 * li) % 1.0 for v in (norm[::-1] if li % 2 else norm)]
        contour = _smooth_contour(seq, W // (2 * S))
        pts = [(int(i * (2 * S)), int(base_y - c * amp + math.sin(i * 0.018 + li) * 6 * S))
               for i, c in enumerate(contour)]
        pts = [(0, H)] + pts + [(W, H)]
        # 먹빛 → 새벽빛 사이 원근 색
        far, near = (96, 88, 122), (18, 16, 30)
        col = tuple(int(far[i] + (near[i] - far[i]) * depth) for i in range(3))
        ridge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        rd = ImageDraw.Draw(ridge)
        rd.polygon(pts, fill=col + (255,))
        img.paste(ridge, (0, 0), ridge)
        # 능선 사이 안개 띠
        if li < layers - 1:
            mist = Image.new("L", (W, H), 0)
            md = ImageDraw.Draw(mist)
            md.rectangle([0, base_y - int(H * 0.02), W, base_y + int(H * 0.05)], fill=70)
            mist = mist.filter(ImageFilter.GaussianBlur(28 * S))
            white = Image.new("RGB", (W, H), (215, 200, 200))
            img = Image.composite(white, img, mist.point(lambda v: int(v * 0.55)))
    draw = ImageDraw.Draw(img)

    # 5) 철새 몇 마리 (여백의 생명감)
    for _ in range(4):
        bx, by = random.randint(int(W * 0.15), int(W * 0.6)), random.randint(int(H * 0.24), int(H * 0.4))
        bs = random.randint(7, 12) * S
        draw.arc([bx - bs, by - bs // 2, bx, by + bs // 2], 200, 340, fill=(40, 36, 52), width=2 * S)
        draw.arc([bx, by - bs // 2, bx + bs, by + bs // 2], 200, 340, fill=(40, 36, 52), width=2 * S)

    # 6) 필름 그레인 + 비네트 (인쇄물 질감)
    for _ in range(2200):
        gx, gy = random.randint(0, W - 1), random.randint(0, H - 1)
        px = img.getpixel((gx, gy))
        d = random.randint(-7, 7)
        img.putpixel((gx, gy), tuple(max(0, min(255, c + d)) for c in px))

    _poster_caption(ImageDraw.Draw(img), W, H, S, title,
                    f"{score['composer']}  ·  Melody as Mountains  ·  ScoreScapes AI")

    final = img.resize((1080, 1350), Image.Resampling.LANCZOS)
    os.makedirs(out_dir, exist_ok=True)
    safe = "".join(c for c in title if c.isalnum() or c == " ").replace(" ", "_")
    path = os.path.join(out_dir, f"scorescape_{safe}_{datetime.date.today().isoformat()}_{random.randint(100, 999)}.png")
    final.save(path, "PNG", dpi=(300, 300))  # 엣시/인쇄 대응 300DPI
    return path


def render_scene_moonsea(title, score, out_dir):
    """
    🌊 [월광 소나타 전용 장면] 달빛 바다 — 멜로디가 파도의 능선이 되고,
    수면 위로 달빛 기둥이 어른거린다. 깊은 청색과 은빛의 우수.
    """
    from PIL import Image, ImageDraw, ImageFilter, ImageChops
    import math
    S = 2
    W, H = 1080 * S, 1350 * S

    # 1) 밤하늘: 칠흑 남색 → 수평선의 짙은 청록
    sky_top, sky_low = (8, 10, 28), (26, 44, 74)
    horizon = int(H * 0.42)
    img = Image.new("RGB", (W, H), sky_top)
    draw = ImageDraw.Draw(img)
    for y in range(horizon):
        k = (y / horizon) ** 1.4
        col = tuple(int(sky_top[i] + (sky_low[i] - sky_top[i]) * k) for i in range(3))
        draw.line([(0, y), (W, y)], fill=col)

    # 2) 달 + 글로우 (수평선 가까이 낮게 뜬 달)
    moon_x, moon_y, moon_r = int(W * 0.5), int(H * 0.22), 78 * S
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([moon_x - moon_r * 3.2, moon_y - moon_r * 3.2, moon_x + moon_r * 3.2, moon_y + moon_r * 3.2],
               fill=(52, 58, 76))
    glow = glow.filter(ImageFilter.GaussianBlur(70 * S))
    img = ImageChops.screen(img, glow)
    draw = ImageDraw.Draw(img)
    draw.ellipse([moon_x - moon_r, moon_y - moon_r, moon_x + moon_r, moon_y + moon_r], fill=(226, 230, 238))
    # 달 크레이터 음영
    draw.ellipse([moon_x - moon_r * 0.35, moon_y - moon_r * 0.3, moon_x - moon_r * 0.05, moon_y], fill=(206, 210, 222))

    # 3) 별
    for _ in range(70):
        sx, sy = random.randint(0, W), random.randint(0, horizon)
        b = random.randint(80, 150)
        draw.ellipse([sx, sy, sx + 2 * S, sy + 2 * S], fill=(b, b, int(b * 1.1)))

    # 4) 바다: 멜로디 곡선이 파도 능선이 되는 가로 밴드들
    pitches = [p for p, _ in notes_of(score)]
    p_min, p_max = min(pitches), max(pitches)
    norm = [(p - p_min) / max(1, p_max - p_min) for p in pitches]
    sea_top_col, sea_bot_col = (30, 48, 82), (6, 8, 20)
    bands = 16
    for bi in range(bands):
        depth = bi / (bands - 1)
        base_y = horizon + int((H - horizon - 60 * S) * (depth ** 1.25))
        amp = (8 + 14 * (1 - depth)) * S
        seg = norm if bi % 2 == 0 else norm[::-1]
        seq = [(v + 0.07 * bi) % 1.0 for v in seg]
        contour = _smooth_contour(seq, W // (2 * S))
        pts = [(int(i * 2 * S), int(base_y - c * amp + math.sin(i * 0.03 + bi * 1.7) * 3 * S))
               for i, c in enumerate(contour)]
        pts = [(0, H)] + pts + [(W, H)]
        col = tuple(int(sea_top_col[i] + (sea_bot_col[i] - sea_top_col[i]) * depth) for i in range(3))
        band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(band)
        bd.polygon(pts, fill=col + (255,))
        img.paste(band, (0, 0), band)
        # 파도 능선의 은빛 하이라이트 (달빛 반사)
        hi = tuple(min(255, c + 26) for c in col)
        d2 = ImageDraw.Draw(img)
        for i in range(1, len(pts) - 2):
            d2.line([pts[i], pts[i + 1]], fill=hi, width=1 * S)

    # 5) 달빛 기둥 — 수면 위 은빛 물비늘 (가로 대시들)
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(240):
        dy = random.randint(horizon + 8 * S, H - 80 * S)
        depth = (dy - horizon) / (H - horizon)
        spread = (28 + 200 * depth) * S
        dx = moon_x + random.randint(-int(spread), int(spread))
        dl = random.randint(6, int(16 + 34 * depth)) * S
        alpha = max(20, int(150 * (1 - depth * 0.75)))
        draw.line([(dx - dl // 2, dy), (dx + dl // 2, dy)],
                  fill=(222, 228, 240, alpha), width=max(2, int(2.6 * S - depth * 2)))

    # 6) 그레인
    for _ in range(2000):
        gx, gy = random.randint(0, W - 1), random.randint(0, H - 1)
        px = img.getpixel((gx, gy))
        d = random.randint(-6, 6)
        img.putpixel((gx, gy), tuple(max(0, min(255, c + d)) for c in px))

    _poster_caption(ImageDraw.Draw(img), W, H, S, title,
                    f"{score['composer']}  ·  Melody as Waves  ·  ScoreScapes AI",
                    color=(226, 230, 240), subcolor=(140, 150, 172))

    final = img.resize((1080, 1350), Image.Resampling.LANCZOS)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"scorescape_Moonlight_{datetime.date.today().isoformat()}_{random.randint(100, 999)}.png")
    final.save(path, "PNG", dpi=(300, 300))  # 엣시/인쇄 대응 300DPI
    return path


def render_scene_geometry(title, score, out_dir):
    """
    📐 [바흐 전용 장면] 신성한 기하학 — 음정이 동심원 아크의 반지름이 되고,
    4겹 대칭으로 회전하며 질서의 만다라를 이룬다. 잉크 위의 금.
    """
    from PIL import Image, ImageDraw, ImageFilter, ImageChops
    import math
    S = 2
    W, H = 1080 * S, 1350 * S
    bg = (12, 20, 24)
    gold = (212, 175, 105)
    ivory = (238, 232, 214)

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    cx, cy = W // 2, int(H * 0.46)

    # 1) 방사형 미광
    max_r = int(H * 0.75)
    for r in range(max_r, 0, -8 * S):
        k = r / max_r
        col = tuple(int(bg[i] + 16 * (1 - k)) for i in range(3))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

    # 2) 배경 격자 (아주 옅은 질서의 그리드)
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    step = 72 * S
    for gx in range(0, W, step):
        gd.line([(gx, 0), (gx, H)], fill=gold + (14,), width=1 * S)
    for gy in range(0, H, step):
        gd.line([(0, gy), (W, gy)], fill=gold + (14,), width=1 * S)
    img.paste(grid, (0, 0), grid)
    draw = ImageDraw.Draw(img, "RGBA")

    # 3) 음표 → 동심원 아크 (반지름=음높이, 호 길이=음길이, 4겹 회전 대칭)
    notes = notes_of(score)
    pitches = [p for p, _ in notes]
    p_min, p_max = min(pitches), max(pitches)
    r_in, r_out = 70 * S, int(H * 0.33)
    ang_cursor = -90.0
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gld = ImageDraw.Draw(glow)
    for i, (pitch, dur) in enumerate(notes):
        p_norm = (pitch - p_min) / max(1, p_max - p_min)
        radius = int(r_in + (r_out - r_in) * p_norm)
        span = 14 + dur * 16
        width = (3 if i % 2 else 5) * S
        for rot in range(4):                      # 4겹 대칭 = 바흐의 질서
            a0 = ang_cursor + rot * 90
            box = [cx - radius, cy - radius, cx + radius, cy + radius]
            col = gold if (i + rot) % 3 else ivory
            draw.arc(box, a0, a0 + span, fill=col + (225,), width=width)
            gld.arc(box, a0, a0 + span, fill=tuple(int(c * 0.5) for c in col), width=width * 2)
            # 아크 끝점의 점
            rad = math.radians(a0 + span)
            ex, ey = cx + radius * math.cos(rad), cy + radius * math.sin(rad)
            draw.ellipse([ex - 4 * S, ey - 4 * S, ex + 4 * S, ey + 4 * S], fill=col + (255,))
        ang_cursor += span * 0.8 + 6

    glow = glow.filter(ImageFilter.GaussianBlur(10 * S))
    img = ImageChops.screen(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # 4) 중심 문양 + 가는 축선
    draw.ellipse([cx - 10 * S, cy - 10 * S, cx + 10 * S, cy + 10 * S], fill=ivory + (255,))
    draw.ellipse([cx - 22 * S, cy - 22 * S, cx + 22 * S, cy + 22 * S], outline=gold + (200,), width=2 * S)
    for ang in (0, 90, 180, 270):
        rad = math.radians(ang)
        x2, y2 = cx + (r_out + 40 * S) * math.cos(rad), cy + (r_out + 40 * S) * math.sin(rad)
        draw.line([(cx, cy), (x2, y2)], fill=gold + (46,), width=1 * S)

    # 5) 그레인
    for _ in range(1800):
        gx, gy = random.randint(0, W - 1), random.randint(0, H - 1)
        px = img.getpixel((gx, gy))
        d = random.randint(-5, 5)
        img.putpixel((gx, gy), tuple(max(0, min(255, c + d)) for c in px))

    _poster_caption(ImageDraw.Draw(img), W, H, S, title,
                    f"{score['composer']}  ·  Sacred Geometry  ·  ScoreScapes AI",
                    color=ivory, subcolor=(150, 138, 112))

    final = img.resize((1080, 1350), Image.Resampling.LANCZOS)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"scorescape_Bach_{datetime.date.today().isoformat()}_{random.randint(100, 999)}.png")
    final.save(path, "PNG", dpi=(300, 300))  # 엣시/인쇄 대응 300DPI
    return path


def render_scene_mist(title, score, out_dir):
    """
    🌫️ [짐노페디 전용 장면] 안개 파스텔 — 부드러운 색面 사이로 멜로디가
    한 줄의 우아한 선으로 흐른다. 몽환, 여백, 느린 호흡.
    """
    from PIL import Image, ImageDraw, ImageFilter
    import math
    S = 2
    W, H = 1080 * S, 1350 * S

    # 1) 파스텔 안개층 (블러시→라벤더→페일블루 가로 색면)
    fields = [(244, 226, 222), (230, 220, 236), (214, 224, 238), (240, 234, 224)]
    img = Image.new("RGB", (W, H), fields[0])
    draw = ImageDraw.Draw(img)
    band_h = H // len(fields)
    for i, col in enumerate(fields):
        draw.rectangle([0, i * band_h - 40 * S, W, (i + 1) * band_h + 40 * S], fill=col)
    img = img.filter(ImageFilter.GaussianBlur(90 * S))
    draw = ImageDraw.Draw(img, "RGBA")

    # 2) 창백한 태양
    sx_, sy_, sr_ = int(W * 0.3), int(H * 0.24), 54 * S
    draw.ellipse([sx_ - sr_, sy_ - sr_, sx_ + sr_, sy_ + sr_], fill=(252, 246, 236, 190))

    # 3) 멜로디 선 — 화면을 가로지르는 단 하나의 우아한 곡선
    notes = notes_of(score)
    pitches = [p for p, _ in notes]
    p_min, p_max = min(pitches), max(pitches)
    norm = [(p - p_min) / max(1, p_max - p_min) for p in pitches]
    contour = _smooth_contour(norm, W // (2 * S))
    line_col = (108, 92, 110)
    center_y, amp = int(H * 0.56), int(H * 0.14)
    pts = [(int(i * 2 * S), int(center_y - (c - 0.5) * 2 * amp)) for i, c in enumerate(contour)]
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=line_col + (210,), width=3 * S)

    # 4) 음표 오브 — 곡선 위 실제 음표 위치에 은은한 원 (몇 개만, 여백의 미)
    t_total = sum(d for _, d in notes)
    t = 0
    for pitch, dur in notes:
        x = int((t + dur / 2) / t_total * (W - 1))
        y = pts[min(x // (2 * S), len(pts) - 1)][1]
        r = (10 + dur * 7) * S
        draw.ellipse([x - r - 6 * S, y - r - 6 * S, x + r + 6 * S, y + r + 6 * S], fill=(255, 255, 255, 60))
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(250, 244, 240, 200), outline=line_col + (160,), width=2 * S)
        t += dur

    # 5) 떠다니는 미세먼지 같은 입자 (몽환)
    for _ in range(90):
        px_, py_ = random.randint(0, W), random.randint(0, H)
        pr = random.randint(2, 5) * S
        draw.ellipse([px_ - pr, py_ - pr, px_ + pr, py_ + pr], fill=(255, 255, 255, random.randint(25, 60)))

    # 6) 그레인
    for _ in range(1600):
        gx, gy = random.randint(0, W - 1), random.randint(0, H - 1)
        px = img.getpixel((gx, gy))
        d = random.randint(-4, 4)
        img.putpixel((gx, gy), tuple(max(0, min(255, c + d)) for c in px))

    _poster_caption(ImageDraw.Draw(img), W, H, S, title,
                    f"{score['composer']}  ·  Pastel Fog  ·  ScoreScapes AI",
                    color=(96, 84, 98), subcolor=(150, 138, 148))

    final = img.resize((1080, 1350), Image.Resampling.LANCZOS)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"scorescape_Gymnopedie_{datetime.date.today().isoformat()}_{random.randint(100, 999)}.png")
    final.save(path, "PNG", dpi=(300, 300))  # 엣시/인쇄 대응 300DPI
    return path


def notes_of(score):
    return score["notes"]


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
    final.save(path, "PNG", dpi=(300, 300))  # 엣시/인쇄 대응 300DPI
    return path


def main():
    print("🎼 ScoreScapes AI 기동 — 악보에서 예술을 캐냅니다... (v2.2: 곡마다 전용 무드 장면!)")
    # 사용법: python scorescapes_ai_bot.py            ← 오늘의 곡 랜덤
    #        python scorescapes_ai_bot.py "Arirang"  ← 원하는 곡 지정
    #        python scorescapes_ai_bot.py list       ← 수록곡 목록
    import sys
    if len(sys.argv) >= 2 and sys.argv[1].lower() == "list":
        print(" - 수록곡:")
        for t, sc in SCORES.items():
            print(f"   · {t} ({sc['composer']}) — {sc.get('scene', 'classic')} 무드")
        return
    if len(sys.argv) >= 2:
        want = sys.argv[1].lower()
        title = next((t for t in SCORES if want in t.lower()), None)
        if not title:
            print(f" - '{sys.argv[1]}' 곡을 찾지 못해 랜덤 선택합니다. (python scorescapes_ai_bot.py list 로 목록 확인)")
            title = random.choice(list(SCORES.keys()))
    else:
        title = random.choice(list(SCORES.keys()))
    score = SCORES[title]
    print(f" - 오늘의 악보: {title} ({score['composer']}) · 음표 {len(score['notes'])}개 파싱")

    # 곡별 전용 장면(무드 엔진) — 없으면 기본 오로라 스타일
    scene = score.get("scene")
    scene_map = {"mountain": render_scene_mountain, "moonsea": render_scene_moonsea,
                 "geometry": render_scene_geometry, "mist": render_scene_mist}
    if scene in scene_map:
        path = scene_map[scene](title, score, "artworks")
    else:
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
