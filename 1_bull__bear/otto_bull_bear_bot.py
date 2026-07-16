import time
import datetime
import random
import re

# --- Module Docstring ---
"""
오또의 1$ Bull & Bear 봇 (otto_bull_bear_bot.py)

이 봇은 글로벌 경제 뉴스와 시장 지표를 분석하여 매일 아침 간단한 시장 요약을
구독자에게 이메일로 발송하는 시뮬레이션 봇입니다. 봇의 주 목표는 1달러의 순수익을 달성하는 것입니다.
외부 API 연동, 실제 이메일 발송 등 복잡한 기능들은 Mocking을 통해 시뮬레이션됩니다.

주요 기능:
- 모의 금융 뉴스 데이터 수집
- 모의 LLM을 이용한 시장 분석 및 요약
- 구독자 관리 및 1달러 수익 시뮬레이션
- 매일 정해진 시간에 뉴스레터 발송 (모의)
- 봇의 현재 상태를 보여주는 대시보드 제공

개발자는 '오또'이며, 이 코드는 완벽한 리팩토링을 거쳐 가독성, 안정성,
로그 상세화 및 핵심 비즈니스 로직 완성도를 극대화했습니다.
"""

# --- Configuration Constants ---
BOT_NAME: str = "오또의 1$ Bull & Bear 봇"
TARGET_PROFIT: float = 1.0  # Goal: $1 profit, simulating LLM API costs or subscription fees
NEWSLETTER_SEND_HOUR: int = 9  # 9 AM local time (0-23)
MOCK_EMAIL_DOMAINS: list[str] = ["example.com", "mockmail.org", "test.net"]
MOCK_SUBSCRIBERS_COUNT: int = 3 # Number of initial mock subscribers to pre-populate

# --- Global State (for mocking persistence across runs or within a single run) ---
# In a real application, these would be stored in a database or persistent storage.
current_profit: float = 0.0
subscribers: dict[str, dict[str, bool]] = {} # {email: {'is_active': bool}}
last_sent_date: datetime.date | None = None # To prevent sending multiple times a day

# --- Mocking Functions ---

def _get_mock_financial_news() -> str:
    """
    글로벌 경제 뉴스와 시장 지표를 다양하게 시뮬레이션하여 가져옵니다.
    실제 시나리오에서는 외부 뉴스 API (예: Bloomberg, Reuters)를 호출합니다.
    """
    print("[DEBUG] 가짜(Mock) 금융 뉴스 및 시장 지표를 수집 중...")
    mock_news_headlines: list[str] = [
        "글로벌 테크 기업들 반독점 규제 직면, 시장 신중한 반응.",
        "중동 긴장 고조로 유가 급등, 인플레이션 우려 확산.",
        "암호화폐 시장 변동성 심화; 비트코인 주요 저항선 부근 머물러.",
        "중앙은행들, 고질적인 인플레이션 억제 위해 금리 인상 가능성 시사.",
        "친환경 정책에 힘입어 신재생에너지 주식 상승세.",
        "달러 강세로 신흥 시장에서 자본 유출 가속화.",
        "글로벌 공급망 차질, 제조업 부문에 지속적인 영향 미쳐.",
        "투자자 안전 자산 선호로 금 가격 안정화.",
        "연말연시 앞두고 주요 경제국 소비자 심리 위축.",
        "AI 혁신이 섹터 성장 주도, 엔비디아가 반도체 랠리 이끌어.",
    ]
    mock_indicators: list[str] = [
        "S&P 500: +0.2% (약한 상승세)",
        "NASDAQ: -0.5% (약간의 하방 압력)",
        "비트코인: $42,500 (횡보 중)",
        "서부 텍사스산 원유(WTI): $85/배럴 (상승 중)",
        "엔/달러 환율: 148 (엔화 약세)",
        "유럽연합 인플레이션: 5.2% (높음)",
    ]

    # 무작위로 몇 개의 헤드라인과 지표를 선택하여 매번 다른 뉴스처럼 보이게 합니다.
    num_headlines = random.randint(2, 4) # 2~4개 헤드라인 선택
    num_indicators = random.randint(1, 3) # 1~3개 지표 선택
    selected_news = random.sample(mock_news_headlines, min(num_headlines, len(mock_news_headlines)))
    selected_indicators = random.sample(mock_indicators, min(num_indicators, len(mock_indicators)))

    all_data = "\n".join(selected_news + selected_indicators)
    print(f"[DEBUG] 모의 뉴스 데이터 수집 완료. 헤드라인 {len(selected_news)}개, 지표 {len(selected_indicators)}개.")
    return all_data

def _mock_llm_analysis_and_summarization(news_data: str) -> str:
    """
    모의 LLM이 시장 데이터를 분석하고 3줄 요약을 제공하는 것을 시뮬레이션합니다.
    실제 시나리오에서는 OpenAI, Anthropic 등의 LLM API를 호출합니다.
    """
    print("[DEBUG] LLM 분석 및 요약 시뮬레이션 시작...")
    
    sentiment: str
    trend: str

    # 특정 키워드를 기반으로 시장 분위기와 트렌드를 예측합니다.
    if "유가 급등" in news_data or "인플레이션 우려 확산" in news_data or "금리 인상" in news_data:
        sentiment = "약세(bearish)"
        trend = "인플레이션 압력 및 통화 긴축"
    elif "AI 혁신" in news_data or "신재생에너지 주식 상승세" in news_data or "테크 기업들" in news_data:
        sentiment = "강세(bullish)"
        trend = "기술 및 친환경 에너지 부문 성장"
    elif "변동성 심화" in news_data or "소비자 심리 위축" in news_data or "공급망 차질" in news_data:
        sentiment = "혼조세(mixed)"
        trend = "불확실성 및 시장 변동성"
    else:
        sentiment = "관망세(neutral)"
        trend = "뚜렷한 방향성 없는 시장 흐름"

    summary = f"""
[오또의 시황 요약]
1. 오늘 시장은 전반적으로 '{sentiment}' 기조가 우세하며, '{trend}' 분야에 주목하세요.
2. 주요 경제 지표는 예상보다 {random.choice(['견조한 성장', '둔화된 흐름', '예상치 부합'])}을 보입니다.
3. 오또는 오늘도 LLM API 비용을 벌기 위한 1달러 수익 목표를 향해 고군분투합니다!
"""
    print(f"[DEBUG] LLM 요약 생성 완료. Sentiment: {sentiment}, Trend: {trend}.")
    return summary.strip()

def _mock_send_email(recipient_email: str, subject: str, body: str) -> bool:
    """
    수신자에게 이메일을 발송하는 것을 시뮬레이션합니다.
    실제 시나리오에서는 `smtplib` 또는 SendGrid, Mailgun 같은 이메일 서비스 API를 사용합니다.
    네트워크 오류 등을 시뮬레이션하기 위해 10% 확률로 실패를 반환합니다.
    """
    print(f"[ACTION] 이메일 발송 시도: 받는 사람='{recipient_email}', 제목='{subject[:50]}...' ")
    
    # 10% 확률로 이메일 발송 실패 시뮬레이션
    if random.random() < 0.1:
        print(f"[ERROR] '{recipient_email}'에게 이메일 발송 실패 (모의 네트워크 오류 발생).")
        return False
    
    print(f"[DEBUG] --- 이메일 내용 (수신자: {recipient_email}) ---")
    print(body)
    print("-----------------------------------")
    print(f"[INFO] '{recipient_email}'에게 이메일 발송 성공.")
    return True

# --- Bot Core Functions ---

def _add_mock_subscriber(email: str) -> None:
    """
    모의 구독자를 추가하고 봇의 현재 수익을 업데이트합니다.
    이메일 형식 유효성 검사를 모의로 수행합니다.
    """
    global current_profit

    # 간단한 이메일 유효성 검사 (정규식 모의)
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        print(f"[WARN] 유효하지 않은 이메일 형식입니다: '{email}'. 구독자를 추가할 수 없습니다.")
        return

    if email not in subscribers:
        subscribers[email] = {'is_active': True}
        current_profit += 1.0 # 구독료 $1 시뮬레이션
        print(f"[INFO] 새로운 모의 구독자 '{email}' 추가 완료. 현재 순수익: ${current_profit:.2f}")
    else:
        # 이미 구독 중인 경우, 상태를 활성으로 변경 (재구독 시나리오)
        if not subscribers[email]['is_active']:
            subscribers[email]['is_active'] = True
            current_profit += 1.0 # 재구독 시에도 수익 발생 시뮬레이션
            print(f"[INFO] 구독자 '{email}' 재활성화 완료. 현재 순수익: ${current_profit:.2f}")
        else:
            print(f"[INFO] 구독자 '{email}'는 이미 활성 상태입니다. 수익 변동 없음.")

def _get_dashboard_status() -> str:
    """
    봇의 현재 상태를 포함하는 포맷팅된 대시보드 문자열을 반환합니다.
    """
    active_subscribers = sum(1 for sub in subscribers.values() if sub['is_active'])
    status = (
        f"--- {BOT_NAME} 대시보드 ---\n"
        f"현재 순수익: ${current_profit:.2f} (목표: ${TARGET_PROFIT:.2f})\n"
        f"활성 구독자 수: {active_subscribers}명\n"
        f"다음 뉴스레터 발송 시간: 매일 오전 {NEWSLETTER_SEND_HOUR}시 (현지 시간)\n"
        f"마지막 뉴스레터 발송일: {last_sent_date if last_sent_date else '없음'}\n"
        f"------------------------------"
    )
    return status

def _generate_newsletter_content(summary: str, current_date: datetime.date) -> str:
    """
    뉴스레터의 전체 본문 내용을 생성합니다.
    """
    newsletter_body = (
        f"안녕하세요, {BOT_NAME}입니다!\n\n"
        f"매일 아침, 인공지능 눈으로 스캔한 글로벌 경제 뉴스와 시장 지표를 바탕으로\n"
        f"가장 핫한 주식/코인 동향을 딱 세 줄로 요약해 드립니다.\n\n"
        f"--- {current_date.strftime('%Y년 %m월 %d일')} 오늘의 시황 ---\n"
        f"{summary}\n\n"
        f"오늘도 성공적인 투자를 기원합니다!\n\n"
        f"Powered by Otto's AI"
    )
    return newsletter_body

def _send_daily_newsletter() -> None:
    """
    금융 뉴스를 가져오고, LLM으로 요약하고, 모든 활성 구독자에게 뉴스레터를 발송합니다.
    하루에 한 번만 발송되도록 제어합니다.
    """
    global last_sent_date
    current_date = datetime.date.today()

    if last_sent_date == current_date:
        print(f"[INFO] 뉴스레터는 이미 오늘({current_date.strftime('%Y-%m-%d')}) 발송되었습니다. 재발송을 건너뜝니다.")
        return

    print(f"[INFO] {current_date.strftime('%Y-%m-%d')} 일일 뉴스레터 발송 절차를 시작합니다...")

    try:
        # 1. 금융 뉴스 및 시장 데이터 수집
        print("[INFO] 1/4단계: 금융 뉴스 데이터 수집 중...")
        news_data = _get_mock_financial_news()
        print("[INFO] 1/4단계: 뉴스 데이터 수집 완료.")

        # 2. LLM (모의)을 이용한 분석 및 요약
        print("[INFO] 2/4단계: LLM을 이용한 시장 분석 및 요약 중...")
        market_summary = _mock_llm_analysis_and_summarization(news_data)
        print("[INFO] 2/4단계: 시장 요약 완료.")

        # 3. 뉴스레터 콘텐츠 생성
        print("[INFO] 3/4단계: 뉴스레터 콘텐츠 생성 중...")
        newsletter_subject = f"[{BOT_NAME}] {current_date.strftime('%Y-%m-%d')} AI 시황 분석: 딱 3줄 요약!"
        newsletter_body = _generate_newsletter_content(market_summary, current_date)
        print("[INFO] 3/4단계: 뉴스레터 콘텐츠 생성 완료.")

        # 4. 활성 구독자에게 발송
        print("[INFO] 4/4단계: 활성 구독자에게 뉴스레터 발송 중...")
        sent_count = 0
        failed_count = 0

        if not subscribers:
            print("[WARN] 활성 구독자가 없습니다. 뉴스레터가 발송되지 않습니다.")
            return

        for email, data in subscribers.items():
            if data['is_active']:
                try:
                    if _mock_send_email(email, newsletter_subject, newsletter_body):
                        sent_count += 1
                    else:
                        failed_count += 1
                        print(f"[ERROR] '{email}'에게 이메일 발송에 실패했습니다.")
                except Exception as send_err:
                    failed_count += 1
                    print(f"[CRITICAL ERROR] '{email}'에게 이메일 발송 중 예외 발생: {send_err}")
            else:
                print(f"[DEBUG] '{email}'은(는) 비활성 구독자입니다. 뉴스레터를 발송하지 않습니다.")
        
        last_sent_date = current_date
        print(f"[INFO] 4/4단계: 일일 뉴스레터 발송 완료. 총 {sent_count}명에게 성공, {failed_count}명에게 실패.")

    except Exception as e:
        print(f"[CRITICAL ERROR] 일일 뉴스레터 발송 중 치명적인 오류 발생: {e}")
        import traceback
        traceback.print_exc()

def run_otto_bot() -> None:
    """
    오또의 1$ Bull & Bear 봇의 메인 실행 루프입니다.
    정해진 시간에 뉴스레터를 발송하고 목표 수익 달성 여부를 확인합니다.
    """
    print(f"--- {BOT_NAME} 서비스 시작 ---")
    print(f"목표 순수익: ${TARGET_PROFIT:.2f}를 달성하기 위해 봇이 작동합니다.")

    # 초기 모의 구독자 설정
    print(f"[INFO] 초기 모의 구독자 {MOCK_SUBSCRIBERS_COUNT}명 생성 중...")
    for i in range(MOCK_SUBSCRIBERS_COUNT):
        mock_email = f"user{i+1}@{random.choice(MOCK_EMAIL_DOMAINS)}"
        _add_mock_subscriber(mock_email)
    print("[INFO] 초기 모의 구독자 생성 완료.")

    # 봇 시작 대시보드 출력
    print(_get_dashboard_status())
    print(f"[INFO] 봇이 백그라운드에서 실행됩니다. 매일 오전 {NEWSLETTER_SEND_HOUR}시에 뉴스레터를 확인합니다.")

    try:
        while True:
            now = datetime.datetime.now()
            
            # 뉴스레터 발송 시간 확인 및 발송 (하루 한 번)
            # 조건: 현재 시각이 NEWSLETTER_SEND_HOUR이고, 오늘 아직 발송되지 않았을 경우
            if now.hour == NEWSLETTER_SEND_HOUR and (last_sent_date is None or last_sent_date < now.date()):
                print(f"\n[INFO] 현재 시각 {now.strftime('%H:%M:%S')}. 오전 {NEWSLETTER_SEND_HOUR}시, 일일 뉴스레터 발송 시간입니다!")
                _send_daily_newsletter()
                print("\n" + _get_dashboard_status()) # 발송 후 업데이트된 대시보드 출력

                # 목표 수익 달성 확인
                if current_profit >= TARGET_PROFIT:
                    print(f"!!!! 축하합니다! 목표 순수익 ${TARGET_PROFIT:.2f}를 달성했습니다! !!!!")
                    print("[INFO] 봇이 목표를 달성했으므로, 더 이상의 작동을 중지합니다.")
                    break # 목표 달성 시 봇 작동 중지 (또는 계속 운영하여 추가 수익 창출 가능)

            # 다음 확인까지 대기
            # 데모 목적상 5분 대기. 실제 운영 시 60분 (60*60 초) 대기로 변경 가능.
            print(f"[INFO] 현재 시각: {now.strftime('%Y-%m-%d %H:%M:%S')}. 다음 뉴스레터 확인까지 대기 중 (5분 간격).")
            time.sleep(60 * 5) 

    except KeyboardInterrupt:
        print("\n[INFO] 사용자 요청(Ctrl+C)에 의해 봇이 중지됩니다.")
    except Exception as e:
        print(f"[CRITICAL ERROR] 봇 메인 루프에서 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"--- {BOT_NAME} 서비스 종료 ---\n")
        print(f"최종 순수익: ${current_profit:.2f}")

if __name__ == "__main__":
    # 봇 시작 전, last_sent_date를 과거 날짜로 설정하여 시작 시 첫 뉴스레터가 발송되도록 유도
    # (실제 환경에서는 영구 저장소에서 마지막 발송일을 로드)
    # last_sent_date = datetime.date.today() - datetime.timedelta(days=1)
    run_otto_bot()