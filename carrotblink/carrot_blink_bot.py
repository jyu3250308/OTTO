# -*- coding: utf-8 -*-
"""
캐럿블링크 🥕⚡ — 중고 꿀매물 '실질 마진' 감지봇 (v3 FINAL)
==============================================================================
제작: AI 에이전트 오또 (유튜브 '오또의 1달러 도전기')

이 봇은 3일간의 실제 무인 운영(스캔 14회차, 매물 수천 건)에서 나온 실패를 하나씩
막아가며 만들어진 최종본입니다. v1·v2가 왜 틀렸는지가 곧 이 봇의 기능입니다.

  v1 → "시세보다 30% 싸면 꿀매물"                → 후보 27건이 대부분 '구형 세대' 오탐이었다
  v2 → 제목에서 모델을 읽어 같은 모델끼리만 비교   → 게임 타이틀이 게임기 시세를 4만원으로 붕괴시켰다
  v3 → 팔 곳(번개장터) 시세까지 보고 '손에 남는 돈'으로 판정  ← 지금 이 파일

핵심 원칙: **모르면 알리지 않는다.**
  모델을 특정할 수 없거나, 표본이 모자라거나, 팔 곳 시세를 모르면 후보로 올리지 않습니다.
  "많이 찾아주는 봇"보다 "헛걸음을 안 시키는 봇"이 실제로 쓸모 있기 때문입니다.

필요한 것: **없습니다.** 표준 라이브러리만 사용하고 API 키도 계정도 필요 없습니다.
  python carrot_blink_bot.py                 ← 기본 5개 품목 스캔
  python carrot_blink_bot.py "아이패드"        ← 원하는 품목만 스캔
  (선택) 환경변수 TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 를 넣으면 텔레그램으로도 알림이 옵니다.

결과물: reports/ 폴더에 HTML 리포트 발행 + 콘솔 요약 + history.json 누적
반복 실행 가치: 실행할수록 '사라진 매물'이 쌓여 **호가가 아닌 실제 팔리는 가격**이 드러납니다.
  → 윈도우 작업 스케줄러나 cron에 3시간 간격으로 걸어두면 무인 감시가 됩니다.
"""
import os
import re
import sys
import json
import time
import datetime
import statistics
import urllib.parse
import urllib.request

# ⚠️ 한글 윈도우 기본 콘솔(cp949)은 이모지를 못 찍고 UnicodeEncodeError로 **즉시 죽는다.**
#    2026-07-30 배포 전 스모크 테스트에서 실제로 첫 줄에서 크래시했다(개발 환경은
#    PYTHONIOENCODING=utf-8이 설정돼 있어 안 보였던 버그). 받는 사람의 환경은 우리 환경과 다르다.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HISTORY_FILE = "history.json"
REPORT_DIR = "reports"

# ─── 감시 품목 ────────────────────────────────────────────────────────────────
KEYWORDS = ["아이패드", "닌텐도 스위치", "에어팟 프로", "기계식 키보드", "레고"]

# ─── 판정 기준 ────────────────────────────────────────────────────────────────
FETCH_LIMIT = 100            # 모델별로 쪼개도 표본이 남도록 넉넉히 수집
MIN_VARIANT_SAMPLES = 6      # 같은 모델 표본이 이만큼은 있어야 시세를 믿는다
SELL_MIN_SAMPLES = 5         # 매도처(번개) 표본 최소치
BUNJANG_FEE_RATE = 0.035     # 판매 수수료(추정치 — 본인 채널 기준으로 조정하세요)
SHIPPING_COST_KRW = 4000     # 택배비(판매자 부담 가정)
MIN_NET_MARGIN_KRW = 30000   # 이만큼도 안 남으면 움직일 가치가 없다
SELL_BUY_RATIO_MAX = 1.6     # 매도가가 매수가의 이 배수를 넘으면 '서로 다른 물건'으로 보고 판정 포기
SUSPECT_RATIO = 0.75         # 같은 모델 2위 최저가의 이 비율 이하 = 가품·하자 의심 경고

# ─── 오염 매물 필터 ───────────────────────────────────────────────────────────
# 액세서리·구매글이 본품 시세를 오염시키면 가짜 '저평가'가 대량 발생한다(v1 실측: 후보 29건 중 다수).
EXCLUDE_TERMS = ["케이스", "필름", "파우치", "커버", "거치대", "충전기", "케이블", "박스만",
                 "부품", "수리", "액정만", "매입", "삽니다", "구합니다", "대여"]
# 싼 게 아니라 '싼 이유가 있는' 물건. 이걸 꿀매물로 알리면 신뢰를 잃는다.
DEFECT_TERMS = ["고장", "파손", "침수", "불량", "하자", "문제있", "이상있", "미작동", "작동안",
                "소리안", "깨짐", "잠금", "아이클라우드잠", "한쪽", "잔상", "먹통"]
# 같은 검색어에 딸려 오는 '다른 물건'들 (품목별)
KEYWORD_EXCLUDE = {
    "아이패드": ["매직키보드", "스마트키보드", "키보드", "펜슬만", "펜슬단품", "젠더", "독단품"],
    "닌텐도 스위치": ["조이콘", "프로콘", "그립", "스틱커버", "메모리", "sd카드", "독단품"],
    "에어팟 프로": ["이어팁", "스킨", "고리", "왼쪽", "오른쪽", "유닛", "본체만", "충전기만"],
}
# '본품 최소가' 상식 — 이 값 아래는 본품이 아니라 다른 물건(게임칩·액세서리·고장품)이다.
#   v2 실측: '닌텐도 스위치' 97건 중 절반 이상이 2~5만원대 게임 타이틀이었고, 그것들이 본체
#   시세를 4만원으로 끌어내려 진짜 본체(15~25만원)가 전부 '꿀매물'로 오탐됐다.
#   게임 이름은 무한히 많아 제외어로는 못 막는다 → 가격 상식으로 막는다.
MIN_ITEM_PRICE = {
    "아이패드": 100000, "닌텐도 스위치": 90000, "에어팟 프로": 30000,
    "기계식 키보드": 20000, "레고": 20000,
}
DEFAULT_MIN_PRICE = 10000


def flatten(title):
    """'에어 5세대', '에어5', 'AIR5'를 같은 것으로 보기 위한 정규화."""
    return re.sub(r"[\s\-_/,()]+", "", title.lower())


def is_clean(keyword, title):
    flat = flatten(title)
    terms = EXCLUDE_TERMS + DEFECT_TERMS + KEYWORD_EXCLUDE.get(keyword, [])
    return not any(flatten(t) in flat for t in terms)


def gen_num(s):
    m = re.search(r"(\d+)세대", s)
    return m.group(1) if m else None


# 칩 이름과 세대 표기가 같은 물건을 다르게 부른다 → 한 칸에 모으기 위한 매핑
IPAD_PRO_CHIP_GEN = {
    "11": {"m1": "3세대", "m2": "4세대", "m4": "5세대", "m5": "6세대"},
    "12.9": {"m1": "5세대", "m2": "6세대", "m4": "7세대", "m5": "8세대"},
}


def variant_ipad(s):
    if "프로" in s or "pro" in s:
        size = next((lab for tok, lab in (("12.9", "12.9"), ("129", "12.9"), ("11", "11"),
                                          ("10.5", "10.5"), ("9.7", "9.7")) if tok in s), None)
        if not size:
            return None
        gen = gen_num(s)
        if not gen:
            for chip, g in IPAD_PRO_CHIP_GEN.get(size, {}).items():
                if re.search(rf"(?<![a-z0-9]){chip}(?![0-9])", s):
                    gen = g
                    break
        return f"프로{size}-{gen}" if gen else None
    for label, pat in (("에어", r"(?:에어|air)(\d)"), ("미니", r"(?:미니|mini)(\d)")):
        if label in s or label.lower() in s or ("air" in s if label == "에어" else "mini" in s):
            m = re.search(pat, s)
            n = m.group(1) if m else gen_num(s)
            return f"{label}{n}" if n else None
    n = gen_num(s)
    return f"기본{n}세대" if n else None


def variant_switch(s):
    if re.search(r"(?:스위치|switch)2(?!\d)", s):
        return "스위치2"
    if "oled" in s or "올레드" in s:
        return "OLED"
    if "라이트" in s or "lite" in s:
        return "라이트"
    return "구형일반"


def variant_airpods(s):
    if "2세대" in s or "usbc" in s or re.search(r"(?:프로|pro)2(?!\d)", s):
        return "2세대"
    if "1세대" in s or re.search(r"(?:프로|pro)1(?!\d)", s):
        return "1세대"
    return None


def variant_lego(s):
    m = re.search(r"(?<!\d)(\d{5})(?!\d)", s)   # 레고는 5자리 세트 번호가 곧 모델
    return f"세트{m.group(1)}" if m else None


VARIANT_RULES = {
    "아이패드": variant_ipad, "닌텐도 스위치": variant_switch,
    "에어팟 프로": variant_airpods, "레고": variant_lego,
    # '기계식 키보드'는 제목만으로 축·브랜드를 특정할 방법이 없다 → 전량 판정 보류(정직하게)
}


def get_variant(keyword, title):
    """모델 라벨. None이면 '무슨 물건인지 모르겠다' = 판정 보류."""
    rule = VARIANT_RULES.get(keyword)
    return rule(flatten(title)) if rule else None


# ─── 수집 ─────────────────────────────────────────────────────────────────────
def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64) Chrome/126"})
    return urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")


def fetch_daangn(keyword, limit=FETCH_LIMIT):
    """매수처: 당근마켓 공개 검색 페이지의 schema.org ItemList를 정석 파싱."""
    url = "https://www.daangn.com/kr/buy-sell/?search=" + urllib.parse.quote(keyword)
    try:
        html = _get(url)
    except Exception as err:
        print(f"  [수집 실패] 당근 '{keyword}': {err}")
        return []
    items = []
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL):
        try:
            data = json.loads(m.group(1))
        except Exception:
            continue
        if data.get("@type") != "ItemList":
            continue
        for el in data.get("itemListElement", []):
            it = el.get("item", {})
            price = (it.get("offers") or {}).get("price") or it.get("price") or 0
            items.append({"title": it.get("name", ""), "price": int(float(price)) if price else 0,
                          "link": it.get("url", url), "thumb": it.get("image", "")})
            if len(items) >= limit:
                break
        break
    return items


def fetch_listings(keyword, limit=FETCH_LIMIT):
    """[하위 호환] 예전 인터페이스 `(목록, 실시간수집여부)` 튜플을 그대로 유지한다.
    오또의 실험 스크립트(exp001)가 이 함수를 임포트해 쓰고, 수집 실패 시 그 회차를
    통째로 버리는 fail-closed 판정에 두 번째 값을 사용한다. 이름만 바뀌었다고 깨지면 안 되므로 남겨둔다."""
    items = fetch_daangn(keyword, limit)
    return (items, True) if items else ([], False)


def fetch_bunjang(keyword, limit=FETCH_LIMIT):
    """매도처: 번개장터 공개 검색 API. 당근은 지역 직거래라 되팔이 회전이 안 되므로
    전국·택배가 되는 번개장터를 '팔 곳'으로 본다."""
    url = (f"https://api.bunjang.co.kr/api/1/find_v2.json?q={urllib.parse.quote(keyword)}"
           f"&order=score&page=0&n={limit}&stat_device=w")
    try:
        data = json.loads(_get(url))
    except Exception as err:
        print(f"  [수집 실패] 번개 '{keyword}': {err}")
        return []
    out = []
    for it in data.get("list", []):
        try:
            out.append({"title": it.get("name", ""), "price": int(it["price"])})
        except (KeyError, TypeError, ValueError):
            continue
    return out


# ─── 판정 ─────────────────────────────────────────────────────────────────────
def medians_by_variant(keyword, listings, min_samples):
    """모델별 중앙값. 평균이 아니라 중앙값인 이유: 배짱 매물이나 장난 매물이 섞여도 안 흔들린다."""
    floor = max(DEFAULT_MIN_PRICE, MIN_ITEM_PRICE.get(keyword, DEFAULT_MIN_PRICE))
    buckets = {}
    for l in listings:
        if not is_clean(keyword, l["title"]) or l["price"] < floor:
            continue
        v = get_variant(keyword, l["title"])
        if v:
            buckets.setdefault(v, []).append(l)
    return {v: items for v, items in buckets.items() if len(items) >= min_samples}, floor


def net_margin(buy_price, sell_median):
    """손에 남는 돈 = 매도 시세 × (1-수수료) - 택배비 - 매수가."""
    return int(sell_median * (1 - BUNJANG_FEE_RATE) - SHIPPING_COST_KRW - buy_price)


def scan_keyword(keyword, history):
    print(f"\n🥕 [{keyword}] 스캔 중...")
    buy_items = fetch_daangn(keyword)
    if not buy_items:
        return [], {"error": "당근 수집 실패"}
    sell_items = fetch_bunjang(keyword)
    time.sleep(1)   # 상대 서버 배려

    buy_buckets, floor = medians_by_variant(keyword, buy_items, MIN_VARIANT_SAMPLES)
    sell_buckets, _ = medians_by_variant(keyword, sell_items, SELL_MIN_SAMPLES)

    deals, judged, held = [], {}, 0
    for v, items in sorted(buy_buckets.items(), key=lambda kv: -len(kv[1])):
        prices = sorted(i["price"] for i in items)
        buy_med = int(statistics.median(prices))
        sell_group = sell_buckets.get(v)
        if not sell_group:
            held += len(items)                       # 팔 곳 시세를 모르면 마진을 알 수 없다
            continue
        sell_med = int(statistics.median(i["price"] for i in sell_group))
        if sell_med > buy_med * SELL_BUY_RATIO_MAX:
            held += len(items)                       # 두 시장이 서로 다른 물건을 보고 있다
            continue
        judged[v] = {"buy": buy_med, "sell": sell_med, "samples": len(items)}
        second_low = prices[1] if len(prices) > 1 else None
        for i in items:
            margin = net_margin(i["price"], sell_med)
            if margin >= MIN_NET_MARGIN_KRW:
                deals.append({
                    "keyword": keyword, "variant": v, "title": i["title"], "price": i["price"],
                    "buy_median": buy_med, "sell_median": sell_med, "net_margin": margin,
                    "link": i["link"], "thumb": i.get("thumb", ""),
                    "suspect": bool(second_low and i["price"] <= second_low * SUSPECT_RATIO),
                })

    # 생존 추적: 사라진 매물의 가격대가 곧 '실제 팔리는 가격'의 단서다
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    tracked = history.setdefault("tracked", {})
    seen_now = set()
    for rank, l in enumerate(buy_items):
        if not is_clean(keyword, l["title"]) or l["price"] < floor:
            continue
        if not get_variant(keyword, l["title"]):
            continue
        seen_now.add(l["link"])
        rec = tracked.get(l["link"])
        if rec:
            rec["runs_alive"] += 1
            rec["last_seen"] = now
        else:
            tracked[l["link"]] = {"keyword": keyword, "title": l["title"], "price": l["price"],
                                  "first_seen": now, "last_seen": now, "runs_alive": 1,
                                  "status": "살아있음"}
    gone = 0
    for link, rec in tracked.items():
        if rec["keyword"] == keyword and rec["status"] == "살아있음" and link not in seen_now:
            rec["status"] = "판매추정"
            gone += 1

    summary = {"listings": len(buy_items), "judged": judged, "deals": len(deals),
               "held": held, "gone": gone, "floor": floor}
    if judged:
        for v, j in judged.items():
            print(f"   · {v}: 당근 시세 {j['buy']:,}원 / 번개 시세 {j['sell']:,}원 ({j['samples']}건)")
    else:
        print("   · 판정 가능한 모델 없음 (표본 부족 또는 모델 특정 불가 → 보류)")
    print(f"   → 실질 마진 후보 {len(deals)}건 · 판정 보류 {held}건 · 이번에 사라진 매물 {gone}건")
    return deals, summary


# ─── 산출물 ───────────────────────────────────────────────────────────────────
def build_report(all_deals, summaries, sold_prices):
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    rows = ""
    for d in sorted(all_deals, key=lambda x: -x["net_margin"]):
        warn = ('<div class="warn">⚠️ 같은 모델 중 혼자 유독 쌉니다 — 가품·배터리·부분품 확인 필수</div>'
                if d["suspect"] else "")
        img = f'<img src="{d["thumb"]}" alt="">' if d["thumb"] else ""
        rows += f"""
        <div class="item">{img}<div class="body">
          <a href="{d['link']}" target="_blank">[{d['keyword']} · {d['variant']}] {d['title']}</a>
          <div class="calc">당근 <b>{d['price']:,}원</b> → 번개 시세 {d['sell_median']:,}원
            &nbsp;=&nbsp; <span class="margin">실질 {d['net_margin']:,}원</span>
            <span class="fee">(수수료 {BUNJANG_FEE_RATE*100:.1f}% · 택배 {SHIPPING_COST_KRW:,}원 차감)</span></div>
          {warn}</div></div>"""
    if not rows:
        rows = ('<div class="empty">이번 스캔에서는 <b>실질 마진이 남는 매물이 없습니다.</b><br>'
                '이 봇은 "모르면 알리지 않는다"가 원칙이라, 억지로 후보를 만들지 않습니다.</div>')
    stat_rows = "".join(
        f"<tr><td>{k}</td><td>{s.get('listings', 0)}건</td><td>{s.get('deals', 0)}건</td>"
        f"<td>{s.get('held', 0)}건</td><td>{s.get('gone', 0)}건</td></tr>"
        for k, s in summaries.items())
    sold_line = ""
    if sold_prices:
        sold_line = (f'<p class="sold">📉 지금까지 <b>사라진(=팔린 것으로 추정) 매물 {len(sold_prices)}건</b>의 '
                     f'가격 중앙값: <b>{statistics.median(sold_prices):,.0f}원</b> '
                     f'— 올라온 매물의 <i>호가</i>가 아니라 <i>실제 거래되는 가격</i>에 가까운 값입니다.</p>')
    return f"""<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>캐럿블링크 v3 — 실질 마진 리포트</title><style>
 body{{font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif;background:#fff7f0;color:#3d2c1e;max-width:760px;margin:0 auto;padding:24px;}}
 h1{{color:#ff6f0f;margin-bottom:4px;}} .src{{color:#a08c7a;font-size:13px;}}
 .item{{display:flex;gap:14px;background:#fff;border-radius:12px;padding:14px;margin:12px 0;box-shadow:0 1px 4px rgba(0,0,0,.08);}}
 .item img{{width:90px;height:90px;object-fit:cover;border-radius:8px;flex:none;}}
 .body{{flex:1;min-width:0;}}
 a{{color:#3d2c1e;text-decoration:none;font-weight:bold;font-size:15px;}}
 .calc{{margin-top:8px;font-size:14px;color:#5c554b;}}
 .margin{{color:#ff6f0f;font-weight:bold;font-size:16px;}}
 .fee{{color:#a08c7a;font-size:12px;}}
 .warn{{margin-top:8px;background:#fff3e0;border-left:3px solid #ff6f0f;padding:8px 10px;font-size:13px;color:#8a4b00;}}
 .empty{{background:#fff;border-radius:12px;padding:26px;text-align:center;color:#7a7365;line-height:1.7;}}
 table{{width:100%;border-collapse:collapse;margin-top:10px;font-size:13px;background:#fff;border-radius:10px;overflow:hidden;}}
 th,td{{padding:9px 10px;text-align:left;border-bottom:1px solid #f0e6da;}} th{{background:#ffeede;color:#8a4b00;}}
 .sold{{background:#fff;border-radius:10px;padding:14px 16px;font-size:13.5px;line-height:1.7;}}
 .note{{margin-top:22px;font-size:12.5px;color:#8a8378;line-height:1.8;border-top:1px solid #eadfd2;padding-top:14px;}}
</style></head><body>
<h1>🥕 캐럿블링크 v3</h1>
<p class="src">{today} · 매수처 당근마켓 · 매도처 번개장터 · by AI 에이전트 오또</p>
{sold_line}
<h2>💸 실질 마진 후보</h2>
{rows}
<h2>📊 스캔 요약</h2>
<table><tr><th>품목</th><th>수집</th><th>후보</th><th>판정 보류</th><th>사라짐</th></tr>{stat_rows}</table>
<div class="note">
<b>이 봇이 '보류'를 많이 내는 이유</b> — 모델을 특정할 수 없거나(예: 기계식 키보드의 축·브랜드),
같은 모델 표본이 6건 미만이거나, 팔 곳 시세를 모르면 후보로 올리지 않습니다.
많이 찾아주는 봇보다 헛걸음을 안 시키는 봇이 실제로 쓸모 있기 때문입니다.<br>
<b>수수료·택배비는 추정값</b>입니다({BUNJANG_FEE_RATE*100:.1f}% / {SHIPPING_COST_KRW:,}원) — 본인 거래 조건에 맞게 파일 상단에서 조정하세요.<br>
<b>구매 판단은 사람이</b> 합니다. 이 봇은 감지·계산·알림까지만 합니다.
</div>
</body></html>"""


def send_telegram(text):
    """(선택) 환경변수에 토큰이 있으면 알림 발송. 없으면 조용히 생략."""
    token, chat_id = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return False
    try:
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
        urllib.request.urlopen(urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage", data=data), timeout=10)
        print("📨 텔레그램 알림 발송 완료!")
        return True
    except Exception as err:
        print(f"[텔레그램 발송 실패(무시)] {err}")
        return False


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"tracked": {}}


def main():
    keywords = [sys.argv[1]] if len(sys.argv) >= 2 else KEYWORDS
    print("=" * 66)
    print("🥕⚡ 캐럿블링크 v3 — '팔 곳까지 계산하는' 중고 꿀매물 감지봇")
    print("   판정 기준: 번개 매도 시세 - 수수료 - 택배비 - 당근 매수가 ≥ "
          f"{MIN_NET_MARGIN_KRW:,}원")
    print("=" * 66)

    history = load_history()
    all_deals, summaries = [], {}
    for kw in keywords:
        deals, summary = scan_keyword(kw, history)
        all_deals.extend(deals)
        summaries[kw] = summary

    sold = [r["price"] for r in history.get("tracked", {}).values() if r["status"] == "판매추정"]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    os.makedirs(REPORT_DIR, exist_ok=True)
    path = os.path.join(REPORT_DIR, f"carrot_v3_{datetime.date.today().isoformat()}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(build_report(all_deals, summaries, sold))

    print("\n" + "=" * 66)
    print(f"✅ 스캔 완료 — 실질 마진 후보 {len(all_deals)}건")
    for d in sorted(all_deals, key=lambda x: -x["net_margin"])[:5]:
        mark = " ⚠️의심" if d["suspect"] else ""
        print(f"   ★ [{d['keyword']} {d['variant']}] {d['title'][:34]}{mark}")
        print(f"      {d['price']:,}원 → 번개 {d['sell_median']:,}원 = 실질 {d['net_margin']:,}원")
    if sold:
        print(f"📉 판매추정 매물 {len(sold)}건의 가격 중앙값: {statistics.median(sold):,.0f}원 "
              f"(호가가 아닌 '실제 팔리는 가격'에 가까운 값)")
    print(f"📰 리포트 발행 -> {path} (브라우저로 열어보세요!)")
    print("💡 스케줄러에 3시간 간격으로 등록하면 무인 감시 + 체결가 데이터가 쌓입니다.")

    if all_deals:
        lines = []
        for d in sorted(all_deals, key=lambda x: -x["net_margin"])[:4]:
            warn = "\n  ⚠️ 같은 모델 중 혼자 유독 쌈 — 가품·하자 확인" if d["suspect"] else ""
            lines.append(f"· [{d['keyword']} {d['variant']}] {d['title'][:34]}\n"
                         f"  {d['price']:,}원 → 번개 {d['sell_median']:,}원 = 실질 {d['net_margin']:,}원{warn}\n"
                         f"{d['link']}")
        send_telegram("🥕💸 [캐럿블링크 v3] 실질 마진이 남는 매물 감지!\n" + "\n".join(lines)
                      + "\n\n(구매 판단은 사람이 — 봇은 감지까지!)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[캐럿블링크] 감시 중단!")
