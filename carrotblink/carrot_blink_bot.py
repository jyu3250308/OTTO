# -*- coding: utf-8 -*-
"""
캐럿블링크 🥕⚡ 당근 꿀매물 실시간 감시봇 (v2 — 진짜 매물을 진짜로 잡아냅니다!)
==============================================================================
당근마켓 공개 검색 페이지에서 키워드 매물을 실시간 수집하고, 이전 실행과 비교해
'새로 올라온 매물'을 감지하면 알려주는 봇입니다. (표준 라이브러리만 사용, 키 불필요!)
(제작: AI 에이전트 오또 · v2: 외부 라이브러리·API 의존 제거 + 실물 리포트 파일 발행)

사용법:
  python carrot_blink_bot.py             ← 기본 키워드(아이패드) 감시
  python carrot_blink_bot.py "닌텐도"     ← 원하는 키워드 감시
→ reports/ 폴더에 매물 리포트(html) 발행 + 새 매물 감지 시 콘솔/텔레그램 알림!
"""
import os
import re
import sys
import json
import datetime
import urllib.request
import urllib.parse

HISTORY_FILE = "watch_history.json"


def fetch_listings(keyword, limit=12):
    """🌐 당근마켓 공개 검색 페이지에서 실제 매물을 수집합니다."""
    url = "https://www.daangn.com/kr/buy-sell/?search=" + urllib.parse.quote(keyword)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126"})
    try:
        html = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
        # 페이지에 내장된 schema.org ItemList(JSON)를 정석 파싱 — 매물 정보가 구조화돼 있음
        listings = []
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL):
            try:
                data = json.loads(m.group(1))
            except Exception:
                continue
            if data.get("@type") != "ItemList":
                continue
            for el in data.get("itemListElement", []):
                item = el.get("item", {})
                offers = item.get("offers", {}) or {}
                price = offers.get("price") or item.get("price") or 0
                listings.append({
                    "title": item.get("name", "(제목 없음)"),
                    "price": int(float(price)) if price else 0,
                    "link": item.get("url", url),
                    "thumb": item.get("image", ""),
                })
                if len(listings) >= limit:
                    break
            break
        if not listings:
            raise ValueError("매물 파싱 결과 없음 (페이지 구조 변경 가능성)")
        return listings, True
    except Exception as err:
        print(f"[캐럿블링크] 실시간 수집 실패({err}) → 데모 데이터로 시연합니다.")
        demo = [{"title": f"(데모) {keyword} 매물 샘플 {i+1}", "price": 50000 * (i + 1),
                 "link": "https://www.daangn.com", "thumb": ""} for i in range(5)]
        return demo, False


def load_seen():
    if os.path.exists(HISTORY_FILE):
        try:
            return json.load(open(HISTORY_FILE, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def detect_new(keyword, listings, seen):
    """이전 실행과 비교해 '새로 등장한 매물'을 감지합니다 (반복 실행의 핵심 가치!)."""
    old = set(seen.get(keyword, []))
    new_items = [l for l in listings if l["title"] not in old]
    seen[keyword] = list({l["title"] for l in listings} | old)[-300:]
    json.dump(seen, open(HISTORY_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return new_items


def build_report(keyword, listings, new_items, is_real):
    """🥕 매물 현황을 보기 좋은 HTML 리포트로 발행합니다."""
    today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    src = "실시간 수집 (daangn.com 공개 검색)" if is_real else "데모 데이터"
    new_titles = {n["title"] for n in new_items}
    rows = ""
    for l in listings:
        badge = '<span class="new">NEW!</span> ' if l["title"] in new_titles else ""
        img = f'<img src="{l["thumb"]}" alt="">' if l["thumb"] else ""
        rows += f"""
        <div class="item">{img}<div>
          <a href="{l['link']}" target="_blank">{badge}{l['title']}</a>
          <div class="price">{l['price']:,}원</div></div></div>"""
    return f"""<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">
<title>캐럿블링크 — {keyword}</title><style>
 body{{font-family:'Malgun Gothic',sans-serif;background:#fff7f0;color:#3d2c1e;max-width:680px;margin:0 auto;padding:24px;}}
 h1{{color:#ff6f0f;}} .src{{color:#a08c7a;font-size:13px;}}
 .item{{display:flex;gap:14px;background:#fff;border-radius:12px;padding:14px;margin:12px 0;box-shadow:0 1px 4px rgba(0,0,0,.08);}}
 .item img{{width:90px;height:90px;object-fit:cover;border-radius:8px;}}
 a{{color:#3d2c1e;text-decoration:none;font-weight:bold;font-size:16px;}}
 .price{{color:#ff6f0f;font-weight:bold;margin-top:6px;}}
 .new{{background:#ff6f0f;color:#fff;border-radius:6px;padding:1px 8px;font-size:12px;}}
</style></head><body>
<h1>🥕 캐럿블링크 — "{keyword}" 감시 리포트</h1>
<p class="src">{today} · {src} · 새 매물 {len(new_items)}건 감지 · by 오또</p>
{rows}
<p class="src">스케줄러로 주기 실행하면 새 매물이 올라올 때마다 NEW 뱃지로 잡아냅니다!</p>
</body></html>"""


def send_telegram(text):
    """(옵션) 텔레그램 알림 — 토큰 없으면 조용히 생략."""
    token, chat_id = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    try:
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
        urllib.request.urlopen(
            urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data), timeout=10)
        print("[캐럿블링크] 텔레그램 알림 발송! 📨")
    except Exception as err:
        print(f"[캐럿블링크] 텔레그램 발송 실패(무시): {err}")


def main():
    keyword = sys.argv[1] if len(sys.argv) >= 2 else "아이패드"
    print(f"🥕 캐럿블링크 기동 — \"{keyword}\" 매물을 실시간 감시합니다... (v2: 진짜 매물!)")

    listings, is_real = fetch_listings(keyword)
    src = "실시간" if is_real else "데모"
    print(f" - [{src}] 매물 {len(listings)}건 수집:")
    for l in listings[:3]:
        print(f"   · {l['title'][:44]} — {l['price']:,}원")

    new_items = detect_new(keyword, listings, load_seen())
    if new_items:
        print(f"\n⚡ 새 매물 {len(new_items)}건 감지!!")
        for n in new_items[:3]:
            print(f"   NEW → {n['title'][:44]} ({n['price']:,}원)")
        send_telegram(f"🥕⚡ [{keyword}] 새 매물 {len(new_items)}건!\n" + "\n".join(
            f"· {n['title']} — {n['price']:,}원\n{n['link']}" for n in new_items[:3]))
    else:
        print("\n(새 매물 없음 — 다음 실행 때 비교 감지합니다)")

    os.makedirs("reports", exist_ok=True)
    path = os.path.join("reports", f"carrot_{urllib.parse.quote(keyword)}_{datetime.date.today().isoformat()}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(build_report(keyword, listings, new_items, is_real))
    print(f"📰 감시 리포트 발행 -> {path} (브라우저로 열어보세요!)")
    print("✅ 완료! 스케줄러에 30분 간격으로 등록하면 꿀매물 알림 무인 가동!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[캐럿블링크] 감시 중단!")
