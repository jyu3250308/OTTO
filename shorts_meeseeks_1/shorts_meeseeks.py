# -*- coding: utf-8 -*-
"""
Shorts Meeseeks: 1달러 웃음 미션 😂 (v2 — 진짜 인기 밈을 실시간으로 수집합니다!)
==============================================================================
레딧(r/memes)의 오늘 인기 밈 TOP 10을 실시간으로 수집해, 오또의 한줄평과 함께
보기 좋은 HTML 다이제스트 파일로 발행하는 봇입니다. (가입·API 키 불필요!)
(제작: AI 에이전트 오또 · v2: 내장 가짜 데이터 → 실시간 실데이터 수집으로 재작성)

사용법: python shorts_meeseeks.py  (끝!)
→ digests/ 폴더에 오늘의 밈 다이제스트(html)가 발행됩니다. 더블클릭해서 열어보세요!
"""
import os
import json
import random
import datetime
import urllib.request

DIGEST_DIR = "digests"

# 오또의 한줄평 (점수 구간별 — rule-based)
REACTIONS_HOT = ["이건 알고리즘도 웃었다 🤖", "출근길에 보면 위험한 수준", "저장 안 하면 후회각",
                 "이게 바로 오늘의 우승자", "댓글창이 더 웃긴 케이스"]
REACTIONS_MID = ["은은하게 웃긴 타입", "3초 뒤에 빵 터지는 슬로우 밈", "아는 사람만 웃는 고인물 밈",
                 "피식... 인정", "내일 생각나서 또 웃을 밈"]


def fetch_top_memes(limit=10):
    """🌐 오늘의 인기 밈을 실시간 수집합니다 (meme-api.com — 무료·키 불필요, 레딧 인기글 기반)."""
    url = f"https://meme-api.com/gimme/{limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ShortsMeeseeks/2.0)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        memes = []
        for p in data.get("memes", []):
            memes.append({
                "title": p.get("title", "(제목 없음)"),
                "score": p.get("ups", 0),
                "sub": p.get("subreddit", "memes"),
                "link": p.get("postLink", "https://www.reddit.com/r/memes/"),
                "thumb": p.get("url", ""),
            })
        if not memes:
            raise ValueError("빈 응답")
        return memes, True
    except Exception as err:
        print(f"[Meeseeks] 실시간 수집 실패({err}) → 데모 데이터로 시연합니다.")
        demo = [{"title": f"(데모) 오늘의 밈 샘플 #{i+1}", "score": random.randint(1000, 90000),
                 "sub": "demo", "link": "https://www.reddit.com/r/memes/", "thumb": ""}
                for i in range(limit)]
        return demo, False


def otto_reaction(score):
    """점수 기반으로 오또의 한줄평을 붙입니다 (rule-based, 정직 표기)."""
    return random.choice(REACTIONS_HOT if score >= 20000 else REACTIONS_MID)


def build_digest_html(memes, is_real):
    """😂 수집한 밈을 보기 좋은 HTML 다이제스트로 조립합니다."""
    today = datetime.date.today().isoformat()
    src = "실시간 수집 (meme-api · 레딧 인기글 기반)" if is_real else "데모 데이터 (네트워크 오프라인)"
    rows = ""
    for i, m in enumerate(memes, 1):
        img_tag = f'<img src="{m["thumb"]}" alt="">' if str(m.get("thumb", "")).endswith((".jpg", ".png", ".jpeg", ".gif")) else ""
        rows += f"""
        <div class="meme">
          <div class="rank">#{i}</div>
          <div class="body">
            <a href="{m['link']}" target="_blank">{m['title']}</a>
            <div class="meta">👍 {m['score']:,} · r/{m['sub']}</div>
            <div class="otto">🤓 오또의 한줄평: {otto_reaction(m['score'])}</div>
            {img_tag}
          </div>
        </div>"""
    return f"""<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">
<title>오늘의 밈 다이제스트 {today}</title>
<style>
 body{{font-family:'Malgun Gothic',sans-serif;background:#14141f;color:#eee;max-width:720px;margin:0 auto;padding:24px;}}
 h1{{color:#ffe400;}} .src{{color:#888;font-size:13px;}}
 .meme{{display:flex;gap:14px;background:#1e1e2e;border-radius:12px;padding:16px;margin:14px 0;}}
 .rank{{font-size:26px;font-weight:bold;color:#ffe400;min-width:52px;}}
 a{{color:#8ecaff;text-decoration:none;font-size:17px;font-weight:bold;}}
 .meta{{color:#999;font-size:13px;margin:6px 0;}}
 .otto{{color:#ffd866;font-size:14px;margin-bottom:8px;}}
 img{{max-width:100%;border-radius:8px;margin-top:6px;}}
</style></head><body>
<h1>😂 오늘의 밈 다이제스트</h1>
<p class="src">{today} · {src} · by Shorts Meeseeks (오또 제작)</p>
{rows}
<p class="src">매일 실행하면 매일 새로운 다이제스트가 쌓입니다. 스케줄러에 등록해 보세요!</p>
</body></html>"""


def send_slack(memes, webhook):
    """(옵션) Slack Webhook으로 TOP 3 요약 발송 — 웹훅 없으면 조용히 생략."""
    if not webhook:
        return
    try:
        top3 = "\n".join(f"{i+1}. {m['title']} (👍{m['score']:,}) {m['link']}" for i, m in enumerate(memes[:3]))
        body = json.dumps({"text": f"😂 오늘의 밈 TOP 3\n{top3}"}).encode()
        req = urllib.request.Request(webhook, data=body, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
        print("[Meeseeks] Slack 발송 완료! 📨")
    except Exception as err:
        print(f"[Meeseeks] Slack 발송 실패(무시): {err}")


def main():
    print("😂 Shorts Meeseeks 소환! — 오늘의 인기 밈을 실시간 수집합니다... (v2)")
    memes, is_real = fetch_top_memes()
    src = "실시간" if is_real else "데모"
    print(f" - [{src}] 밈 {len(memes)}개 수집 완료!")
    for i, m in enumerate(memes[:3], 1):
        print(f"   {i}. {m['title'][:50]} (👍{m['score']:,})")

    html = build_digest_html(memes, is_real)
    os.makedirs(DIGEST_DIR, exist_ok=True)
    path = os.path.join(DIGEST_DIR, f"meme_digest_{datetime.date.today().isoformat()}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n📰 다이제스트 발행 완료 -> {path}")
    print("   (더블클릭해서 브라우저로 열어보세요 — 링크·썸네일 포함!)")

    send_slack(memes, os.environ.get("SLACK_WEBHOOK_URL"))
    print("✅ 미션 완료! 매일 실행하면 웃음 아카이브가 쌓입니다.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Meeseeks] 미션 중단! 존재의 고통에서 해방됐습니다.")
