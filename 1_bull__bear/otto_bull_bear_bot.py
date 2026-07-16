import time
import datetime
import random
import re
import traceback

# --- Module Docstring ---
"""
오또의 1$ Bull & Bear 봇 (otto_bull_bear_bot.py)

이 봇은 글로벌 경제 뉴스와 시장 지표를 분석하여 매일 아침 간단한 시장 요약을
구독자에게 이메일로 발송하는 시뮬레이션 봇입니다. 봇의 주 목표는 1달러의 순수익을 달성하는 것입니다.
외부 API 연동, 실제 이메일 발송 등 복잡한 기능들은 Mocking을 통해 시뮬레이션됩니다.

주요 기능:
- 모의 금융 뉴스 데이터 수집 및 가공
- 모의 LLM을 이용한 시장 분석 및 요약
- 구독자 관리 및 1달러 수익 시뮬레이션
- 매일 정해진 시간에 뉴스레터 발송 (모의)
- 봇의 현재 상태를 보여주는 대시보드 제공

개발자는 '오또'이며, 이 코드는 완벽한 리팩토링을 거쳐 가독성, 안정성,
로그 상세화 및 핵심 비즈니스 로직 완성도를 극대화했습니다.
"""

class OttoBullBearBot:
    """
    오또의 1$ Bull & Bear 봇 클래스.
    글로벌 경제 뉴스를 분석하고 시장 요약을 구독자에게 이메일로 발송하는
    시뮬레이션 봇의 모든 기능을 캡슐화합니다.
    """

    # --- Configuration Constants (Class Attributes) ---
    BOT_NAME: str = "오또의 1$ Bull & Bear 봇"
    DEFAULT_TARGET_PROFIT: float = 1.0  # Goal: $1 profit, simulating LLM API costs or subscription fees
    DEFAULT_NEWSLETTER_SEND_HOUR: int = 9  # 9 AM local time (0-23)
    DEFAULT_MOCK_EMAIL_DOMAINS: list[str] = ["example.com", "mockmail.org", "test.net"]
    DEFAULT_MOCK_SUBSCRIBERS_COUNT: int = 3 # Number of initial mock subscribers to pre-populate
    EMAIL_REGEX: str = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$" # More robust email regex

    def __init__(self,
                 target_profit: float = DEFAULT_TARGET_PROFIT,
                 newsletter_send_hour: int = DEFAULT_NEWSLETTER_SEND_HOUR,
                 mock_email_domains: list[str] = None,
                 mock_subscribers_count: int = DEFAULT_MOCK_SUBSCRIBERS_COUNT):
        """
        봇 인스턴스를 초기화합니다.
        
        Args:
            target_profit (float): 봇의 목표 순수익 금액.
            newsletter_send_hour (int): 뉴스레터 발송 예정 시간 (0-23시).
            mock_email_domains (list[str]): 모의 구독자 이메일 생성에 사용될 도메인 목록.
            mock_subscribers_count (int): 초기 생성될 모의 구독자 수.
        """
        self.target_profit: float = target_profit
        self.newsletter_send_hour: int = newsletter_send_hour
        self.mock_email_domains: list[str] = mock_email_domains if mock_email_domains else self.DEFAULT_MOCK_EMAIL_DOMAINS
        self.mock_subscribers_count: int = mock_subscribers_count

        # --- Bot's Internal State ---
        # 실제 애플리케이션에서는 데이터베이스나 영구 저장소에 저장됩니다.
        self.current_profit: float = 0.0
        # {email: {'is_active': bool, 'subscribed_date': datetime.date}}
        self.subscribers: dict[str, dict[str, bool | datetime.date]] = {}
        self.last_sent_date: datetime.date | None = None # 마지막 뉴스레터 발송일

        self._running: bool = False # 봇의 실행 상태를 제어하는 플래그
        self._shutdown_event: bool = False # 봇 종료 요청 플래그

        self._log("INIT", f"봇 인스턴스가 초기화되었습니다. 목표 수익: ${self.target_profit:.2f}")

    # --- Internal Logging Helper (Optional but good practice for consistency) ---
    def _log(self, level: str, message: str) -> None:
        """
        일관된 형식으로 로그 메시지를 출력합니다.
        Args:
            level (str): 로그 레벨 (e.g., INFO, DEBUG, WARN, ERROR, CRITICAL).
            message (str): 출력할 메시지.
        """
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")

    # --- Mocking Functions (now methods) ---

    def _get_mock_financial_news(self) -> str:
        """
        글로벌 경제 뉴스와 시장 지표를 다양하게 시뮬레이션하여 가져옵니다.
        실제 시나리오에서는 외부 뉴스 API (예: Bloomberg, Reuters)를 호출합니다.
        Returns:
            str: 모의 금융 뉴스 데이터.
        """
        self._log("DEBUG", "가짜(Mock) 금융 뉴스 및 시장 지표를 수집 중...")
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
            "글로벌 경기 둔화 우려, 기업 실적 발표에 촉각.",
            "미국 고용 지표, 예상 상회하며 금리 인하 기대감 후퇴.",
        ]
        mock_indicators: list[str] = [
            "S&P 500: +0.2% (약한 상승세)",
            "NASDAQ: -0.5% (약간의 하방 압력)",
            "비트코인: $42,500 (횡보 중)",
            "서부 텍사스산 원유(WTI): $85/배럴 (상승 중)",
            "엔/달러 환율: 148 (엔화 약세)",
            "유럽연합 인플레이션: 5.2% (높음)",
            "미국 10년 만기 국채 수익률: 4.5% (상승)",
            "금 가격: 온스당 $2,050 (안정화)",
        ]

        # 무작위로 몇 개의 헤드라인과 지표를 선택하여 매번 다른 뉴스처럼 보이게 합니다.
        num_headlines = random.randint(2, min(4, len(mock_news_headlines))) # 2~4개 헤드라인 선택
        num_indicators = random.randint(1, min(3, len(mock_indicators))) # 1~3개 지표 선택
        
        selected_news = random.sample(mock_news_headlines, num_headlines)
        selected_indicators = random.sample(mock_indicators, num_indicators)

        all_data = "\n".join(selected_news + selected_indicators)
        self._log("DEBUG", f"모의 뉴스 데이터 수집 완료. 헤드라인 {len(selected_news)}개, 지표 {len(selected_indicators)}개.")
        return all_data

    def _mock_llm_analysis_and_summarization(self, news_data: str) -> str:
        """
        모의 LLM이 시장 데이터를 분석하고 3줄 요약을 제공하는 것을 시뮬레이션합니다.
        실제 시나리오에서는 OpenAI, Anthropic 등의 LLM API를 호출하여 비용이 발생한다고 가정합니다.
        Args:
            news_data (str): 분석할 금융 뉴스 데이터.
        Returns:
            str: LLM이 생성한 시장 요약.
        """
        self._log("DEBUG", "LLM 분석 및 요약 시뮬레이션 시작...")
        
        sentiment: str
        trend: str

        # 특정 키워드를 기반으로 시장 분위기와 트렌드를 예측합니다.
        if "유가 급등" in news_data or "인플레이션 우려 확산" in news_data or "금리 인상" in news_data or "경기 둔화" in news_data:
            sentiment = "약세(bearish)"
            trend = "인플레이션 압력 및 통화 긴축"
        elif "AI 혁신" in news_data or "신재생에너지 주식 상승세" in news_data or "테크 기업들" in news_data:
            sentiment = "강세(bullish)"
            trend = "기술 및 친환경 에너지 부문 성장"
        elif "변동성 심화" in news_data or "소비자 심리 위축" in news_data or "공급망 차질" in news_data or "반독점 규제" in news_data:
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
        self._log("DEBUG", f"LLM 요약 생성 완료. Sentiment: {sentiment}, Trend: {trend}.")
        return summary.strip()

    def _mock_send_email(self, recipient_email: str, subject: str, body: str) -> bool:
        """
        수신자에게 이메일을 발송하는 것을 시뮬레이션합니다.
        실제 시나리오에서는 `smtplib` 또는 SendGrid, Mailgun 같은 이메일 서비스 API를 사용합니다.
        네트워크 오류 등을 시뮬레이션하기 위해 10% 확률로 실패를 반환합니다.
        Args:
            recipient_email (str): 이메일 수신자 주소.
            subject (str): 이메일 제목.
            body (str): 이메일 본문.
        Returns:
            bool: 이메일 발송 성공 여부.
        """
        self._log("ACTION", f"이메일 발송 시도: 받는 사람='{recipient_email}', 제목='{subject[:50]}...'")
        
        # 10% 확률로 이메일 발송 실패 시뮬레이션
        if random.random() < 0.1:
            self._log("ERROR", f"'{recipient_email}'에게 이메일 발송 실패 (모의 네트워크 오류 발생 시뮬레이션).")
            return False
        
        # 실제 이메일 본문은 너무 길 수 있으므로 디버그 목적으로는 일부만 출력하거나 확인 메시지로 대체합니다.
        self._log("DEBUG", f"--- 이메일 내용 (수신자: {recipient_email}) ---")
        self._log("DEBUG", body.split('\n')[0] + "...") # 본문의 첫 줄만 출력
        self._log("DEBUG", "-----------------------------------")
        self._log("INFO", f"'{recipient_email}'에게 이메일 발송 성공.")
        return True

    # --- Bot Core Functions (now methods) ---

    def add_subscriber(self, email: str) -> None:
        """
        모의 구독자를 추가하고 봇의 현재 수익을 업데이트합니다.
        이메일 형식 유효성 검사를 수행합니다.
        Args:
            email (str): 추가할 구독자의 이메일 주소.
        """
        # 간단한 이메일 유효성 검사 (정규식)
        if not re.match(self.EMAIL_REGEX, email):
            self._log("WARN", f"유효하지 않은 이메일 형식입니다: '{email}'. 구독자를 추가할 수 없습니다.")
            return

        if email not in self.subscribers:
            self.subscribers[email] = {'is_active': True, 'subscribed_date': datetime.date.today()}
            self.current_profit += 1.0 # 구독료 $1 시뮬레이션 (LLM API 비용 충당 등)
            self._log("INFO", f"새로운 모의 구독자 '{email}' 추가 완료. 현재 순수익: ${self.current_profit:.2f}")
        else:
            # 이미 구독 중인 경우, 상태를 활성으로 변경 (재구독 시나리오)
            if not self.subscribers[email]['is_active']:
                self.subscribers[email]['is_active'] = True
                self.subscribers[email]['subscribed_date'] = datetime.date.today() # 재구독일 업데이트
                self.current_profit += 1.0 # 재구독 시에도 수익 발생 시뮬레이션
                self._log("INFO", f"구독자 '{email}' 재활성화 완료. 현재 순수익: ${self.current_profit:.2f}")
            else:
                self._log("INFO", f"구독자 '{email}'는 이미 활성 상태입니다. 수익 변동 없음.")

    def _get_dashboard_status(self) -> str:
        """
        봇의 현재 상태를 포함하는 포맷팅된 대시보드 문자열을 반환합니다.
        Returns:
            str: 봇의 현재 상태 대시보드 문자열.
        """
        active_subscribers = sum(1 for sub in self.subscribers.values() if sub['is_active'])
        
        status = (
            f"--- {self.BOT_NAME} 대시보드 ---\n"
            f"현재 순수익: ${self.current_profit:.2f} (목표: ${self.target_profit:.2f})\n"
            f"활성 구독자 수: {active_subscribers}명 (총 구독자: {len(self.subscribers)}명)\n"
            f"다음 뉴스레터 발송 예정 시간: 매일 오전 {self.newsletter_send_hour}시 (현지 시간)\n"
            f"마지막 뉴스레터 발송일: {self.last_sent_date.strftime('%Y-%m-%d') if self.last_sent_date else '없음'}\n"
            f"------------------------------"
        )
        return status

    def _generate_newsletter_content(self, summary: str, current_date: datetime.date) -> str:
        """
        뉴스레터의 전체 본문 내용을 생성합니다.
        Args:
            summary (str): LLM이 생성한 시장 요약.
            current_date (datetime.date): 현재 날짜.
        Returns:
            str: 뉴스레터 본문 내용.
        """
        newsletter_body = (
            f"안녕하세요, {self.BOT_NAME}입니다!\n\n"
            f"매일 아침, 인공지능 눈으로 스캔한 글로벌 경제 뉴스와 시장 지표를 바탕으로\n"
            f"가장 핫한 주식/코인 동향을 딱 세 줄로 요약해 드립니다.\n\n"
            f"--- {current_date.strftime('%Y년 %m월 %d일')} 오늘의 AI 시황 ---\n"
            f"{summary}\n\n"
            f"오늘도 성공적인 투자를 기원합니다!\n\n"
            f"Powered by Otto's AI"
        )
        return newsletter_body

    def _send_daily_newsletter(self) -> None:
        """
        금융 뉴스를 가져오고, LLM으로 요약하고, 모든 활성 구독자에게 뉴스레터를 발송합니다.
        하루에 한 번만 발송되도록 제어합니다.
        """
        current_date = datetime.date.today()

        # 뉴스레터 중복 발송 방지
        if self.last_sent_date == current_date:
            self._log("INFO", f"뉴스레터는 이미 오늘({current_date.strftime('%Y-%m-%d')}) 발송되었습니다. 재발송을 건너뜕니다.")
            return

        self._log("INFO", f"===== {current_date.strftime('%Y-%m-%d')} 일일 뉴스레터 발송 절차 시작 =====")

        try:
            # 1. 금융 뉴스 및 시장 데이터 수집
            self._log("INFO", "1/4단계: 모의 금융 뉴스 데이터 수집 중...")
            news_data = self._get_mock_financial_news()
            self._log("INFO", "1/4단계: 뉴스 데이터 수집 완료.")

            # 2. LLM (모의)을 이용한 분석 및 요약
            self._log("INFO", "2/4단계: 모의 LLM을 이용한 시장 분석 및 3줄 요약 중...")
            market_summary = self._mock_llm_analysis_and_summarization(news_data)
            self._log("INFO", "2/4단계: 시장 요약 완료.")

            # 3. 뉴스레터 콘텐츠 생성
            self._log("INFO", "3/4단계: 뉴스레터 콘텐츠 생성 중...")
            newsletter_subject = f"[{self.BOT_NAME}] {current_date.strftime('%Y-%m-%d')} AI 시황 분석: 딱 3줄 요약!"
            newsletter_body = self._generate_newsletter_content(market_summary, current_date)
            self._log("INFO", "3/4단계: 뉴스레터 콘텐츠 생성 완료.")

            # 4. 활성 구독자에게 발송
            self._log("INFO", "4/4단계: 활성 구독자에게 뉴스레터 발송 중...")
            sent_count = 0
            failed_count = 0

            active_subscribers_list = [email for email, data in self.subscribers.items() if data['is_active']]
            
            if not active_subscribers_list:
                self._log("WARN", "현재 활성 상태인 구독자가 없습니다. 뉴스레터가 발송되지 않습니다.")
                self.last_sent_date = current_date # 구독자가 없어도 오늘 발송 시도했음을 기록
                self._log("INFO", f"===== 일일 뉴스레터 발송 절차 완료 (활성 구독자 없음) =====")
                return

            self._log("INFO", f"총 {len(active_subscribers_list)}명의 활성 구독자에게 발송을 시도합니다.")
            for i, email in enumerate(active_subscribers_list):
                self._log("DEBUG", f"({i+1}/{len(active_subscribers_list)}) '{email}'에게 이메일 발송 시도...")
                try:
                    if self._mock_send_email(email, newsletter_subject, newsletter_body):
                        sent_count += 1
                    else:
                        failed_count += 1
                        # _mock_send_email 내부에서 이미 오류 로그를 출력함
                except Exception as send_err:
                    failed_count += 1
                    self._log("CRITICAL ERROR", f"'{email}'에게 이메일 발송 중 예외 발생: {send_err}")
                    self._log("DEBUG", traceback.format_exc()) # 스택 트레이스는 DEBUG 레벨로 출력
            
            self.last_sent_date = current_date # 오늘 뉴스레터 발송 완료로 기록
            self._log("INFO", f"4/4단계: 일일 뉴스레터 발송 완료. 총 {len(active_subscribers_list)}명 중 {sent_count}명에게 성공, {failed_count}명에게 실패.")
            self._log("INFO", f"===== 일일 뉴스레터 발송 절차 종료 =====")

        except Exception as e:
            self._log("CRITICAL ERROR", f"일일 뉴스레터 발송 절차 중 치명적인 오류 발생: {e}")
            self._log("DEBUG", traceback.format_exc())
            self._log("CRITICAL ERROR", f"===== 일일 뉴스레터 발송 절차 비정상 종료 =====")

    def _initialize_mock_subscribers(self) -> None:
        """
        봇 시작 시 설정된 수만큼의 모의 구독자를 생성합니다.
        """
        self._log("INFO", f"초기 모의 구독자 {self.mock_subscribers_count}명 생성 중...")
        try:
            for i in range(self.mock_subscribers_count):
                mock_email = f"user{i+1}@{random.choice(self.mock_email_domains)}"
                self.add_subscriber(mock_email) # add_subscriber 메서드 사용
            self._log("INFO", "초기 모의 구독자 생성 완료.")
        except Exception as e:
            self._log("ERROR", f"초기 모의 구독자 생성 중 오류 발생: {e}")
            self._log("DEBUG", traceback.format_exc())

    def run(self) -> None:
        """
        오또의 1$ Bull & Bear 봇의 메인 실행 루프입니다.
        정해진 시간에 뉴스레터를 발송하고 목표 수익 달성 여부를 확인합니다.
        """
        self._running = True
        self._log("INFO", f"--- {self.BOT_NAME} 서비스 시작 ---")
        self._log("INFO", f"목표 순수익: ${self.target_profit:.2f}를 달성하기 위해 봇이 작동합니다.")

        self._initialize_mock_subscribers() # 초기 구독자 생성

        # 봇 시작 대시보드 출력
        print("\n" + self._get_dashboard_status() + "\n")
        self._log("INFO", f"봇이 백그라운드에서 실행됩니다. 매일 오전 {self.newsletter_send_hour}시에 뉴스레터 발송을 확인합니다.")

        # 봇이 시작될 때 첫 뉴스레터 발송을 유도하기 위해 last_sent_date를 과거로 설정합니다.
        # (실제 환경에서는 영구 저장소에서 마지막 발송일을 로드하여 연속성 유지)
        if self.last_sent_date is None:
            self.last_sent_date = datetime.date.today() - datetime.timedelta(days=1)
            self._log("INFO", f"Last sent date를 {self.last_sent_date.strftime('%Y-%m-%d')}로 설정하여 봇 시작 시 뉴스레터 발송을 유도합니다.")

        try:
            while self._running:
                now = datetime.datetime.now()
                
                # 뉴스레터 발송 시간 확인 및 발송 (하루 한 번)
                # 조건: 현재 시각이 NEWSLETTER_SEND_HOUR 이고, 오늘 아직 발송되지 않았을 경우
                if now.hour == self.newsletter_send_hour and (self.last_sent_date is None or self.last_sent_date < now.date()):
                    self._log("INFO", f"현재 시각 {now.strftime('%H:%M:%S')}. 오전 {self.newsletter_send_hour}시, 일일 뉴스레터 발송 트리거 조건 충족!")
                    self._send_daily_newsletter()
                    print("\n" + self._get_dashboard_status() + "\n") # 발송 후 업데이트된 대시보드 출력

                    # 목표 수익 달성 확인
                    if self.current_profit >= self.target_profit:
                        self._log("INFO", f"!!!! 축하합니다! 목표 순수익 ${self.target_profit:.2f}를 달성했습니다! !!!!")
                        self._log("INFO", "봇이 목표를 달성했으므로, 더 이상의 작동을 중지합니다.")
                        self.stop() # 목표 달성 시 봇 작동 중지
                        break
                    else:
                        self._log("INFO", f"현재 순수익 ${self.current_profit:.2f}. 목표 ${self.target_profit:.2f} 미달성. 계속 운영합니다.")
                
                # 다음 확인까지 대기
                # 데모 목적상 5분 대기. 실제 운영 시 대기 시간을 60분 (60*60 초) 등으로 조정할 수 있습니다.
                self._log("INFO", f"현재 시각: {now.strftime('%Y-%m-%d %H:%M:%S')}. 다음 뉴스레터 발송 확인까지 대기 중 (5분 간격).")
                
                # 짧은 주기로 봇 종료 요청을 확인하면서 대기
                wait_interval_seconds = 5 * 60 # 5분
                check_interval_seconds = 10 # 10초마다 종료 요청 확인
                
                for _ in range(wait_interval_seconds // check_interval_seconds):
                    if not self._running or self._shutdown_event:
                        break # 종료 요청이 있으면 대기 루프 탈출
                    time.sleep(check_interval_seconds)
                else: # 루프가 정상적으로 끝까지 실행된 경우 (종료 요청 없었음)
                    if not self._running or self._shutdown_event:
                        continue # 마지막 대기 중 종료 요청이 들어왔을 수 있으므로 다시 확인
                
                if not self._running or self._shutdown_event:
                    self._log("INFO", "봇 종료 요청을 감지하여 메인 루프를 종료합니다.")
                    break


        except KeyboardInterrupt:
            self._log("INFO", "사용자 요청(Ctrl+C)에 의해 봇이 안전하게 중지됩니다.")
            self._shutdown_event = True # 종료 이벤트 설정
        except Exception as e:
            self._log("CRITICAL ERROR", f"봇 메인 루프에서 예상치 못한 치명적인 오류 발생: {e}")
            self._log("DEBUG", traceback.format_exc())
            self._shutdown_event = True # 오류 발생 시 종료 요청

        finally:
            self._log("INFO", f"--- {self.BOT_NAME} 서비스 종료 ---")
            self._log("INFO", f"최종 순수익: ${self.current_profit:.2f}")

    def stop(self) -> None:
        """
        봇의 실행을 안전하게 중지하도록 요청합니다.
        """
        self._log("INFO", "봇 중지 요청이 수신되었습니다.")
        self._running = False
        self._shutdown_event = True

if __name__ == "__main__":
    # 봇 인스턴스 생성 및 실행
    otto_bot = OttoBullBearBot(
        target_profit=5.0, # 테스트를 위해 목표 수익을 5달러로 상향
        mock_subscribers_count=5 # 초기 구독자 수를 5명으로 늘림
    )
    otto_bot.run()
