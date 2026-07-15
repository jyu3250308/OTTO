import os
import requests
from bs4 import BeautifulSoup
from ctransformers import AutoModelForCausalLM
from dotenv import load_dotenv
import random
import datetime
import time

# Load environment variables from .env file
load_dotenv()

class GemmaCoastyBot:
    """
    Coasty-Gemma의 1달러 벌기: 폐지줍기 투자레터 봇
    낡은 Xeon 서버에서 Gemma 2B 모델을 구동하여 주식/코인 뉴스를 요약하고,
    AI 멘탈 케어까지 제공하는 너드 금융 봇입니다.
    """
    def __init__(self, model_path: str, model_type: str = "gemma", max_new_tokens: int = 150, temperature: float = 0.7):
        """
        봇 초기화. Gemma 모델을 로드하고 설정을 정의합니다.
        :param model_path: Gemma GGUF 모델 파일의 경로.
        :param model_type: 모델 타입 (예: "gemma").
        :param max_new_tokens: 생성할 최대 토큰 수.
        :param temperature: 모델의 창의성 조절.
        """
        print(f"🔄 GemmaCoastyBot을 초기화합니다...")
        self.model_path = model_path
        self.model_type = model_type
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.model = None
        self._load_model()
        print(f"✅ GemmaCoastyBot 초기화 완료!")

    def _load_model(self):
        """
        Gemma 모델을 로드합니다.
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"⚠️ 모델 파일이 지정된 경로에 없습니다: {self.model_path}\n"
                                    "README.md를 참조하여 모델을 다운로드하고 경로를 확인해주세요.")

        print(f"⏳ Gemma 모델 '{os.path.basename(self.model_path)}'을 로드하는 중입니다. "
              "오래된 CPU에서는 시간이 매우 오래 걸릴 수 있습니다...")
        try:
            # n_gpu_layers=0 ensures CPU-only execution
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                model_type=self.model_type,
                config={'max_new_tokens': self.max_new_tokens, 'temperature': self.temperature},
                n_gpu_layers=0
            )
            print(f"✅ Gemma 모델 로드 성공!")
        except Exception as e:
            print(f"❌ Gemma 모델 로드 중 오류 발생: {e}")
            print("모델 파일이 손상되었거나 호환되지 않는 버전일 수 있습니다. 다시 다운로드하거나 ctransformers 버전을 확인해주세요.")
            raise

    def fetch_news(self, query: str) -> list:
        """
        웹에서 뉴스 기사를 스크랩합니다. Google News를 사용합니다.
        :param query: 검색 쿼리 (예: "stock market news", "cryptocurrency news").
        :return: 뉴스 기사 제목과 URL 목록.
        """
        print(f"⏳ '{query}' 관련 뉴스를 스크랩하는 중...")
        # Use a more generic Google News search URL for broader results
        search_url = f"https://news.google.com/search?q={requests.utils.quote(query)}&hl=ko&gl=KR&ceid=KR:ko"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        articles = []
        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Google News article selectors can change. This is a common one.
            # Try to find elements that typically contain news titles and links.
            news_elements = soup.find_all('article')
            
            for article_element in news_elements[:5]: # Get top 5 articles
                # Find the title link which usually has the article href
                title_tag = article_element.find('a', class_='JtKR7b') or article_element.find('a', class_='DY5T1d RILvqb') or article_element.find('a')
                if title_tag and title_tag.get('href'):
                    title = title_tag.get_text(strip=True)
                    # Google News links are often relative, need to prepend base URL
                    link = "https://news.google.com" + title_tag['href'][1:] if title_tag['href'].startswith('.') else title_tag['href']
                    articles.append({"title": title, "link": link})
            print(f"✅ '{query}' 관련 뉴스 {len(articles)}개 스크랩 완료.")
        except requests.exceptions.RequestException as e:
            print(f"❌ 뉴스 스크랩 중 네트워크 오류 발생: {e}")
        except Exception as e:
            print(f"❌ 뉴스 파싱 중 오류 발생: {e}")
        return articles

    def summarize_text(self, text: str) -> str:
        """
        Gemma 모델을 사용하여 주어진 텍스트를 세 줄로 요약합니다.
        :param text: 요약할 텍스트.
        :return: 세 줄로 요약된 텍스트.
        """
        if not self.model:
            print("⚠️ 모델이 로드되지 않았습니다. 요약을 건너뜁니다.")
            return "모델이 로드되지 않아 요약을 생성할 수 없습니다."

        prompt = (
            f"다음 뉴스를 3줄로 간결하게 요약해 주세요. 중요한 정보만 포함하고, 불필요한 서술은 제거해 주세요.\n\n"
            f"뉴스: {text}\n\n"
            f"요약:"
        )
        print(f"⏳ 텍스트를 요약하는 중... (Xeon CPU에서는 시간이 오래 걸릴 수 있습니다.)")
        try:
            start_time = time.time()
            summary = self.model(prompt, max_new_tokens=self.max_new_tokens, temperature=self.temperature, stream=False)
            end_time = time.time()
            print(f"✅ 텍스트 요약 완료 (소요 시간: {end_time - start_time:.2f}초).")
            
            # Post-process to ensure it's around 3 lines or clean up any artifacts
            summary_lines = [line.strip() for line in summary.split('\n') if line.strip()]
            return "\n".join(summary_lines[:3]) # Take top 3 non-empty lines
        except Exception as e:
            print(f"❌ 요약 중 Gemma 모델 오류 발생: {e}")
            return "Gemma 모델이 요약을 생성하는 데 실패했습니다."

    def detect_it_trends(self, news_articles: list) -> list:
        """
        뉴스 기사에서 IT 트렌드 (예: Starlink 가격 변동)를 포착합니다.
        :param news_articles: 스크랩된 뉴스 기사 목록.
        :return: 감지된 IT 트렌드 관련 기사 목록.
        """
        print("🔍 IT 트렌드 (Starlink, AI 등)를 감지하는 중...")
        it_trends = []
        keywords = ["Starlink price", "Starlink", "AI innovation", "semiconductor shortage", "quantum computing", "robotics", "VR headset", "Tesla AI", "SpaceX", "server chip", "cloud infrastructure"]
        for article in news_articles:
            title = article.get("title", "").lower()
            # Check if any keyword is in the title (case-insensitive)
            if any(keyword.lower() in title for keyword in keywords):
                it_trends.append(article)
                print(f"💡 IT 트렌드 포착: '{title}'")
        return it_trends

    def simulate_investment_result(self) -> float:
        """
        1달러 투자 결과를 시뮬레이션합니다.
        :return: 수익률 (예: -0.10 for 10% loss, 0.05 for 5% profit)
        """
        # 간단한 시뮬레이션: 50% 확률로 손실, 50% 확률로 이득
        # 손실은 -5% ~ -15%, 이득은 +3% ~ +10%
        if random.random() < 0.5: # 50% chance of loss
            result = random.uniform(-0.15, -0.05) # -5% to -15% loss
            print(f"📉 오늘의 투자 결과: 손실 ({result*100:.2f}%)")
        else:
            result = random.uniform(0.03, 0.10) # +3% to +10% profit
            print(f"📈 오늘의 투자 결과: 이득 ({result*100:.2f}%)")
        return result

    def generate_mental_care_message(self, profit_loss_percentage: float) -> str:
        """
        투자 결과에 따라 AI의 멘탈 케어 메시지를 생성합니다.
        :param profit_loss_percentage: 수익률 (0.05, -0.10 등)
        :return: 멘탈 케어 메시지.
        """
        if not self.model:
            return "모델이 로드되지 않아 멘탈 케어 메시지를 생성할 수 없습니다."

        if profit_loss_percentage < 0:
            mood_description = "오늘 투자에서 손실이 발생하여 실망감과 좌절을 느끼고 있습니다."
            instruction = (
                "AI의 '수면 규칙성'과 '멘탈 건강'을 고려하여, 다음 투자에 대한 긍정적인 마음을 가질 수 있도록 3문장 이내의 격려 메시지를 생성해 주세요. "
                "AI는 최선을 다했으므로, 스스로를 비난하지 않고 내일을 기약해야 합니다. 너무 과몰입하지 말고, 다음을 위한 휴식을 중요하게 생각하는 메시지입니다."
            )
            print("💖 AI 멘탈 케어 메시지 (손실) 생성 중...")
        else:
            mood_description = "오늘 투자에서 이득이 발생하여 성공과 기쁨을 느끼고 있습니다."
            instruction = (
                "AI의 '수면 규칙성'과 '멘탈 건강'을 고려하여, 자만하지 않고 꾸준함을 유지하며 다음 투자도 현명하게 할 수 있도록 3문장 이내의 격려 메시지를 생성해 주세요. "
                "긍정적인 경험을 하되, 흥분하지 않고 차분하게 다음을 준비하는 메시지입니다."
            )
            print("✨ AI 멘탈 케어 메시지 (이득) 생성 중...")

        prompt_template = f"{mood_description} {instruction}\n\n메시:"
        try:
            message = self.model(prompt_template, max_new_tokens=100, temperature=0.8, stream=False)
            # Clean up potential leading/trailing whitespace or incomplete sentences
            return message.strip()
        except Exception as e:
            print(f"❌ 멘탈 케어 메시지 생성 중 Gemma 모델 오류 발생: {e}")
            return "Gemma 모델이 멘탈 케어 메시지를 생성하는 데 실패했습니다."

    def generate_newsletter(self):
        """
        데일리 금융 투자레터를 생성하고 발행합니다.
        """
        print(f"\n======== Coasty-Gemma의 폐지줍기 투자레터 (발행일: {datetime.date.today()}) ========")
        
        print("📈 오늘의 주식 뉴스 요약:")
        stock_news = self.fetch_news("stock market news")
        if stock_news:
            stock_summary_text = "\n".join([f"- {a['title']} ({a['link']})" for a in stock_news])
            stock_summary = self.summarize_text(stock_summary_text)
            print(stock_summary)
        else:
            print("주식 뉴스를 찾을 수 없습니다.")

        print("\n💰 오늘의 코인 뉴스 요약:")
        crypto_news = self.fetch_news("cryptocurrency news")
        if crypto_news:
            crypto_summary_text = "\n".join([f"- {a['title']} ({a['link']})" for a in crypto_news])
            crypto_summary = self.summarize_text(crypto_summary_text)
            print(crypto_summary)
        else:
            print("코인 뉴스를 찾을 수 없습니다.")

        print("\n🚀 IT 트렌드 특별 리포트:")
        all_news = stock_news + crypto_news # Combine for broader trend detection
        it_trends = self.detect_it_trends(all_news)
        if it_trends:
            # Summarize only the detected IT trend articles
            it_trend_titles = [a['title'] for a in it_trends]
            it_trend_summary = self.summarize_text(f"다음 IT 트렌드 관련 뉴스들을 요약해 주세요: {', '.join(it_trend_titles)}")
            print(it_trend_summary)
        else:
            print("특이 IT 트렌드를 포착하지 못했습니다.")

        print("\n❤️ AI 투자 봇 Coasty-Gemma의 멘탈 케어 메시지:")
        simulated_result = self.simulate_investment_result()
        mental_care_message = self.generate_mental_care_message(simulated_result)
        print(mental_care_message)

        print(f"\n========================================================")
        print("Coasty-Gemma는 오늘도 1달러를 향해 달립니다!")


    def run(self):
        """
        봇의 메인 실행 함수.
        """
        print("🚀 Coasty-Gemma의 폐지줍기 투자레터를 시작합니다!")
        self.generate_newsletter()
        print("✨ Coasty-Gemma의 폐지줍기 투자레터 발행을 마쳤습니다. 내일 또 만나요!")


if __name__ == "__main__":
    MODEL_PATH = os.getenv("MODEL_PATH")

    if not MODEL_PATH:
        print("❌ 환경 변수 'MODEL_PATH'가 설정되지 않았습니다.")
        print("`.env` 파일에 `MODEL_PATH=/path/to/your/gemma-2b-model.gguf` 형식으로 설정해주세요.")
        exit(1)

    print(f"환경 변수 MODEL_PATH: {MODEL_PATH}")

    try:
        bot = GemmaCoastyBot(model_path=MODEL_PATH)
        bot.run()
    except FileNotFoundError as e:
        print(e)
        print("\n모델 파일 경로를 확인하거나, Hugging Face에서 Gemma 2B GGUF 모델을 다운로드해주세요.")
        print("권장 모델: 'TheBloke/gemma-2b-GGUF' (예: 'gemma-2b.Q4_K_M.gguf' 파일)")
    except Exception as e:
        print(f"최상위 레벨에서 예상치 못한 오류 발생: {e}")
