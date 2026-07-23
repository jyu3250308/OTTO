# -*- coding: utf-8 -*-
"""
삐빅! 김개미 비상 📈 Daily Market Morse (v2 — 진짜 뉴스가 진짜로 배달됩니다!)
============================================================================
구글 뉴스 RSS(무료·키 불필요)로 오늘의 주식·증시 헤드라인을 실시간 수집해
'3줄 브리핑 + 모스 부호 시그니처'로 발행하는 봇입니다.
(제작: AI 에이전트 오또 · v2: 취약한 스크래핑 → 안정적인 RSS + 실물 브리핑 파일로 재작성)

사용법: python ant_market_morse_bot.py  (끝!)
→ briefings/ 폴더에 오늘의 브리핑(.md)이 저장되고, 텔레그램 설정 시 자동 발송됩니다.
"""
import os
import re
import datetime
import urllib.request
import xml.etree.ElementTree as ET

# ── 모스 부호 사전 (봇의 시그니처 — '삐빅!' 감성) ──────────────────────────
MORSE = {"A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
         "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
         "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
         "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
         "Y": "-.--", "Z": "--..", "1": ".----", "2": "..---", "3": "...--"}


def to_morse(text):
    """영문 텍스트를 모스 부호로 변환합니다 (김개미 비상 시그니처)."""
    return " ".join(MORSE.get(c.upper(), "") for c in text if c.upper() in MORSE)


def fetch_market_news(query="주식 증시", limit=3):
    """🌐 구글 뉴스 RSS로 시장 헤드라인을 실시간 수집합니다 (키 불필요)."""
    url = ("https://news.google.com/rss/search?q=" + urllib.request.quote(query)
           + "&hl=ko&gl=KR&ceid=KR:ko")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (MarketMorse/2.0)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            root = ET.fromstring(resp.read())
        items = []
        for item in root.iter("item"):
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub = item.findtext("pubDate", "")
            title = re.sub(r"\s*-\s*[^-]+$", "", title)   # 꼬리의 '- 언론사명' 정리
            if title:
                items.append({"title": title, "link": link, "pub": pub})
            if len(items) >= limit:
                break
        if not items:
            raise ValueError("빈 피드")
        return items, True
    except Exception as err:
        print(f"[김개미비상] 실시간 수집 실패({err}) → 데모 데이터로 시연합니다.")
        demo = [{"title": f"(데모) 시장 헤드라인 샘플 {i+1} — 네트워크 연결 시 실제 뉴스로 대체됩니다",
                 "link": "https://news.google.com", "pub": ""} for i in range(limit)]
        return demo, False


def build_briefing(news, is_real):
    """📋 3줄 브리핑 마크다운을 조립합니다."""
    today = datetime.date.today().isoformat()
    src = "실시간 수집 (Google News RSS)" if is_real else "데모 데이터"
    lines = [f"# 📈 삐빅! 김개미 비상 — {today} 시장 3줄 브리핑",
             f"> {src} · by Daily Market Morse (오또 제작)", ""]
    for i, n in enumerate(news, 1):
        lines.append(f"**{i}. {n['title']}**")
        lines.append(f"   - 원문: {n['link']}")
        lines.append("")
    lines.append("---")
    lines.append(f"삐빅 시그니처: `{to_morse('ANT UP')}` (= ANT UP, 개미 파이팅)")
    lines.append("")
    lines.append("_매일 아침 스케줄러에 등록하면 출근 전에 브리핑이 완성됩니다._")
    return "\n".join(lines)


def send_telegram(text):
    """(옵션) 텔레그램 발송 — 토큰 없으면 조용히 생략."""
    token, chat_id = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return
    try:
        import urllib.parse
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
        urllib.request.urlopen(
            urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data), timeout=10)
        print("[김개미비상] 텔레그램 발송 완료! 📨")
    except Exception as err:
        print(f"[김개미비상] 텔레그램 발송 실패(무시): {err}")


def main():
    print("📈 삐빅! 김개미 비상 기동 — 시장 헤드라인 수집 중... (v2: 진짜 뉴스!)")
    news, is_real = fetch_market_news()
    src = "실시간" if is_real else "데모"
    print(f" - [{src}] 헤드라인 {len(news)}건 수집:")
    for i, n in enumerate(news, 1):
        print(f"   {i}. {n['title'][:60]}")

    briefing = build_briefing(news, is_real)
    os.makedirs("briefings", exist_ok=True)
    path = os.path.join("briefings", f"market_brief_{datetime.date.today().isoformat()}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(briefing)
    print(f"\n📋 브리핑 발행 완료 -> {path}")

    tele_text = "📈 삐빅! 김개미 비상 — 오늘의 3줄\n" + "\n".join(
        f"{i}. {n['title']}" for i, n in enumerate(news, 1))
    send_telegram(tele_text)
    print("✅ 완료! briefings/ 폴더에 매일의 시장 기록이 쌓입니다.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[김개미비상] 사용자에 의해 중단되었습니다. 삐빅!")
