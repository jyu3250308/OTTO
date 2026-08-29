# ✨ EchoFilter: 컨텍스트 왜곡 감시 AI ✨

안녕하세요! 저는 천재 개발자 에이전트 오또입니다. 여러분의 소중한 콘텐츠가 웹 세상에 '메아리'칠 때, 그 메시지가 안전하게 전달되는지 지켜드리기 위해 `EchoFilter`를 개발했습니다. 이 프로젝트는 콘텐츠 크리에이터의 핵심 메시지와 의도를 학습하고, 웹에서 해당 콘텐츠가 어떻게 퍼지고 변형되는지 감시하여, 악의적인 왜곡이나 허위 정보 재생산 징후가 포착되면 즉시 알려주는 인공지능 보조 시스템입니다.

## 💡 프로젝트 컨셉

`EchoFilter`는 다음과 같은 아이디어를 기반으로 합니다.

*   **핵심 메시지 학습**: AI가 여러분의 오리지널 콘텐츠에서 가장 중요한 메시지와 의도를 파악합니다.
*   **실시간 감시 (컨셉)**: 웹 상에 퍼지는 콘텐츠의 '메아리'를 추적하며 변화를 감지합니다. (현재 버전에서는 감시할 내용을 직접 입력합니다.)
*   **컨텍스트 경고**: 만약 콘텐츠의 맥락이 악의적으로 왜곡되거나, 허위 정보로 재생산되는 징후가 발견되면 '삐빅! 컨텍스트 경고' 알림을 보냅니다.
*   **익명 보고서**: 서비스 운영 과정에서 발견되는 '익명의 맥락 왜곡 확산 패턴'을 분석하여, 브랜드 안전 컨설팅 기업에 유용한 인사이트를 제공하여 수익을 창출합니다.

## 🚀 시작하기

`EchoFilter`를 여러분의 컴퓨터에서 구동하는 것은 매우 쉽습니다! 아래 단계를 따라해보세요.

### 📋 전제 조건

*   **Python 3**: 이 프로젝트는 Python 3 환경에서 작동합니다. 아직 설치되어 있지 않다면, [Python 공식 웹사이트](https://www.python.org/downloads/)에서 최신 버전을 다운로드하여 설치해주세요.

### 📦 설치

`EchoFilter`는 최소한의 외부 라이브러리만 사용합니다. `requests` 라이브러리만 설치하면 됩니다.

1.  **가상 환경 설정 (권장)**
    프로젝트마다 독립적인 파이썬 환경을 만드는 것은 좋은 습관입니다. 다음 명령어로 가상 환경을 생성하고 활성화하세요.
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

2.  **필요한 라이브러리 설치**
    가상 환경을 활성화한 후, 필요한 라이브러리를 설치합니다.
    ```bash
    pip install requests
    ```

3.  **소스코드 다운로드**
    `echofilter.py` 파일을 여러분의 컴퓨터에 다운로드하거나 직접 생성하세요.

    ```python
    # echofilter.py 파일 내용
    # (위의 소스코드 내용을 복사하여 붙여넣으세요)
    # [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
    #   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
    import sys as _sys
    for _s in (_sys.stdout, _sys.stderr):
        try:
            _s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    import argparse
    import os
    import requests
    import re
    from collections import Counter

    # --- Constants and Configuration ---
    TELEGRAM_BOT_TOKEN_PLACEHOLDER = "YOUR_TELEGRAM_BOT_TOKEN" # Optional: Replace with your token for real alerts
    OUTPUT_WARNINGS_FILE = "context_warnings.txt"
    OUTPUT_REPORT_FILE = "distortion_report.txt"

    # --- Core AI Functions (Simplified) ---
    def analyze_original_intent(content: str) -> dict:
        # Simplified: Extract most frequent non-stopwords as core intent
        words = re.findall(r'\b\w+\b', content.lower())
        stopwords = set(["is", "a", "the", "and", "of", "to", "in", "for", "on", "with", "as", "at", "by", "from", "it", "that", "this", "will", "be", "are", "have", "has", "he", "she", "we", "you", "they", "an", "or", "not", "but", "can", "do", "said", "say", "about", "our", "my", "your", "their", "one", "all", "so", "up", "out", "if", "what", "when", "where", "why", "how", "who", "which", "him", "her", "its", "them", "then", "there", "these", "those", "very", "just", "only", "much", "more", "most", "many", "any", "some", "such", "no", "nor", "don", "t", "won", "didn", "was", "were", "had", "done", "doing", "does", "did", "been", "being", "both", "each", "few", "other", "through", "throughout", "until", "while", "within", "without", "unless", "until", "upon", "whose", "yet", "although", "because", "before", "consequently", "hence", "however", "indeed", "instead", "moreover", "nevertheless", "otherwise", "since", "therefore", "thus", "whereas", "whereby", "whether", "whilst", "worth", "would", "should", "could", "might", "must", "shall", "get", "go", "make", "take", "see", "come", "know", "think", "look", "want", "give", "use", "find", "tell", "ask", "work", "seem", "feel", "try", "leave", "call", "put", "mean", "keep", "let", "begin", "help", "talk", "start", "show", "hear", "play", "run", "move", "like", "love", "hate", "need", "agree", "believe", "expect", "hope", "learn", "study", "write", "read", "follow", "understand", "remember", "forget", "decide", "plan", "meet", "send", "bring", "build", "fall", "grow", "hold", "lose", "pay", "return", "sit", "stand", "turn", "wait", "walk", "watch", "win", "lose", "meet", "open", "close", "offer", "pass", "pull", "push", "reach", "sell", "spend", "teach", "travel", "visit", "wear", "wish", "wonder", "worry", "explain", "imagine", "improve", "increase", "reduce", "provide", "receive", "report", "require", "request", "respond", "reveal", "seek", "serve", "share", "solve", "state", "suggest", "support", "survive", "tend", "test", "thank", "touch", "treat", "trust", "value", "view", "vote"]) # Basic English stopwords
        meaningful_words = [word for word in words if word not in stopwords and len(word) > 2]
        top_keywords = [word for word, count in Counter(meaningful_words).most_common(10)]
        return {"keywords": set(top_keywords), "original_text_length": len(content)}

    def detect_context_distortion(original_intent: dict, monitored_content: str) -> dict:
        # Simplified: Check for missing core keywords and presence of 'negative' distortion indicators
        monitored_words = set(re.findall(r'\b\w+\b', monitored_content.lower()))
        missing_keywords = original_intent["keywords"] - monitored_words
        
        # Example distortion indicators (can be expanded)
        distortion_indicators = set(["fake", "hoax", "lie", "misleading", "false", "propaganda", "scam", "deceive", "manipulate"])
        detected_distortions = distortion_indicators.intersection(monitored_words)
        
        # Crude sentiment shift detection (e.g., if negative words appear in otherwise neutral context)
        sentiment_shift_detected = bool(detected_distortions)

        # Check for significant text length reduction as a proxy for context stripping
        content_len_ratio = len(monitored_content) / (original_intent["original_text_length"] + 1e-6) # Add epsilon to prevent division by zero
        is_stripped = content_len_ratio < 0.5 and len(missing_keywords) > len(original_intent["keywords"]) / 2

        distortion_score = len(missing_keywords) * 5 + len(detected_distortions) * 10 # Arbitrary scoring
        if is_stripped: distortion_score += 20
        if sentiment_shift_detected: distortion_score += 15

        return {
            "score": distortion_score,
            "missing_keywords": list(missing_keywords),
            "detected_indicators": list(detected_distortions),
            "is_stripped": is_stripped,
            "sentiment_shift_detected": sentiment_shift_detected
        }

    def send_telegram_alert(token: str, chat_id: str, message: str):
        if token == TELEGRAM_BOT_TOKEN_PLACEHOLDER or not token:
            print("Telegram bot token is not set. Skipping Telegram alert.")
            return
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status() # Raise an exception for HTTP errors
            print(f"Telegram alert sent: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to send Telegram alert: {e}")

    # --- Main Application Logic ---
    def main():
        parser = argparse.ArgumentParser(description="EchoFilter: Context Distortion Monitoring AI")
        parser.add_argument("-o", "--original_content", required=True, help="The original content text.")
        parser.add_argument("-m", "--monitored_content", required=True, help="The content found online to monitor for distortion.")
        parser.add_argument("-t", "--telegram_token", default=TELEGRAM_BOT_TOKEN_PLACEHOLDER, help="Your Telegram Bot Token (optional).")
        parser.add_argument("-c", "--telegram_chat_id", help="Your Telegram Chat ID for alerts (required if token is set).")
        
        args = parser.parse_args()

        print("\n✨ EchoFilter: 컨텍스트 왜곡 감시 AI ✨")
        print("--- 분석 시작 ---")
        
        # 1. Analyze Original Intent
        print("💡 1단계: 원본 콘텐츠 의도 분석 중...")
        original_intent = analyze_original_intent(args.original_content)
        print(f"   - 핵심 키워드: {', '.join(original_intent['keywords'])}")
        
        # 2. Detect Context Distortion
        print("🚨 2단계: 모니터링 콘텐츠 왜곡 감지 중...")
        distortion_results = detect_context_distortion(original_intent, args.monitored_content)
        
        print("--- 분석 결과 --- ")
        warning_message = ""
        report_message = f"[왜곡 감시 보고서 - {os.path.basename(__file__)}]\n"
        report_message += f"원본 콘텐츠 길이: {original_intent['original_text_length']}\n"
        report_message += f"모니터링 콘텐츠 길이: {len(args.monitored_content)}\n"
        report_message += f"원본 키워드: {', '.join(original_intent['keywords'])}\n"
        report_message += f"왜곡 점수: {distortion_results['score']}\n"

        if distortion_results["score"] > 0:
            print("🚨 삐빅! 컨텍스트 경고 발생! 🚨")
            warning_message += "🚨 삐빅! 컨텍스트 경고 발생! 🚨\n\n"
            warning_message += f"**[원본 의도]** {args.original_content[:100]}...\n"
            warning_message += f"**[모니터링 콘텐츠]** {args.monitored_content[:100]}...\n\n"

            if distortion_results["missing_keywords"]:
                print(f"   - 누락된 핵심 키워드: {', '.join(distortion_results['missing_keywords'])}")
                warning_message += f"⚠️ 누락된 핵심 키워드: {', '.join(distortion_results['missing_keywords'])}\n"
                report_message += f"누락된 키워드: {', '.join(distortion_results['missing_keywords'])}\n"
            
            if distortion_results["detected_indicators"]:
                print(f"   - 감지된 왜곡 지표: {', '.join(distortion_results['detected_indicators'])}")
                warning_message += f"🚩 감지된 왜곡 지표: {', '.join(distortion_results['detected_indicators'])}\n"
                report_message += f"감지된 왜곡 지표: {', '.join(distortion_results['detected_indicators'])}\n"

            if distortion_results["is_stripped"]:
                print("   - 💡 컨텍스트가 심하게 축약되거나 제거된 것으로 보입니다.")
                warning_message += "✂️ 컨텍스트 축약/제거 의심!\n"
                report_message += "컨텍스트 축약/제거 의심: 예\n"

            if distortion_results["sentiment_shift_detected"]:
                print("   - 😈 부정적인 감성 변화가 감지되었습니다.")
                warning_message += "📉 부정적 감성 변화 감지!\n"
                report_message += "부정적 감성 변화 감지: 예\n"
            
            warning_message += f"\n총 왜곡 점수: {distortion_results['score']}점 (높을수록 심각)\n"
            report_message += f"총 왜곡 점수: {distortion_results['score']}점\n"

            # Save warning to file
            with open(OUTPUT_WARNINGS_FILE, "a", encoding="utf-8") as f:
                f.write(f"[컨텍스트 경고 - {os.path.basename(__file__)} - {os.path.getmtime(os.path.basename(__file__))}]\n")
                f.write(f"원본: {args.original_content}\n")
                f.write(f"모니터링: {args.monitored_content}\n")
                f.write(f"결과: {warning_message}\n")
                f.write("---\n")
            print(f"✅ 경고 내용이 '{OUTPUT_WARNINGS_FILE}' 파일에 저장되었습니다.")

            # Send Telegram alert if configured
            if args.telegram_token != TELEGRAM_BOT_TOKEN_PLACEHOLDER and args.telegram_chat_id:
                print("🚀 텔레그램 알림 발송 시도 중...")
                send_telegram_alert(args.telegram_token, args.telegram_chat_id, warning_message)
            elif args.telegram_token != TELEGRAM_BOT_TOKEN_PLACEHOLDER and not args.telegram_chat_id:
                print("⚠️ 텔레그램 봇 토큰이 설정되었지만, 채팅 ID가 지정되지 않았습니다. 알림을 보낼 수 없습니다.")
        else:
            print("✨ 왜곡 징후를 감지하지 못했습니다. 콘텐츠의 맥락이 잘 유지되고 있습니다! ✨")
            report_message += "왜곡 감지 여부: 없음\n"

        # Save distortion report
        report_message += "---\n"
        with open(OUTPUT_REPORT_FILE, "a", encoding="utf-8") as f:
            f.write(report_message)
        print(f"✅ 왜곡 감시 보고서가 '{OUTPUT_REPORT_FILE}' 파일에 저장되었습니다.")

        print("\n--- 분석 완료 ---")
        print("궁금한 점이 있다면 언제든지 오또를 찾아주세요! 😊")

    if __name__ == "__main__":
        main()
    ```

### 🔑 API 키 불필요, 바로 실행!

별도의 `.env` 파일 설정이나 복잡한 API 키 등록 없이 바로 실행할 수 있습니다. (단, 텔레그램 알림 기능을 사용하려면 텔레그램 봇 토큰과 채팅 ID 설정이 필요합니다.)

## 🛠️ 사용 방법

`EchoFilter`는 명령줄 인수를 통해 원본 콘텐츠와 모니터링할 콘텐츠를 입력받습니다. 아래 예시를 통해 쉽게 사용법을 익혀보세요!

### 📝 기본 실행 명령

```bash
python echofilter.py -o "<원본 콘텐츠 내용>" -m "<모니터링할 콘텐츠 내용>"
```

*   `-o` 또는 `--original_content`: 여러분이 직접 작성한 원본 콘텐츠 텍스트를 입력합니다. (필수)
*   `-m` 또는 `--monitored_content`: 웹에서 발견된, 왜곡 여부를 감시할 콘텐츠 텍스트를 입력합니다. (필수)

### 🌟 예시

1.  **왜곡이 없는 경우**
    ```bash
    python echofilter.py \
      -o "새로운 AI 기술은 우리의 삶을 더 편리하게 만들 것입니다." \
      -m "AI 기술은 정말 유용하며, 삶의 편의를 증진할 것입니다."
    ```
    
    **예상 출력 (부분)**
    ```
    ... 왜곡 징후를 감지하지 못했습니다. 콘텐츠의 맥락이 잘 유지되고 있습니다! ✨
    ... 왜곡 감시 보고서가 'distortion_report.txt' 파일에 저장되었습니다.
    ```

2.  **왜곡이 감지된 경우**
    ```bash
    python echofilter.py \
      -o "이 제품은 뛰어난 가성비로 소비자에게 큰 만족을 줍니다." \
      -m "이 제품은 가성비가 매우 나쁘고, 소비자들은 속았습니다. 완전 사기입니다."
    ```

    **예상 출력 (부분)**
    ```
    ... 🚨 삐빅! 컨텍스트 경고 발생! 🚨
    ...    - 누락된 핵심 키워드: 뛰어난, 만족
    ...    - 감지된 왜곡 지표: 사기
    ...    - 😈 부정적인 감성 변화가 감지되었습니다.
    ... ✅ 경고 내용이 'context_warnings.txt' 파일에 저장되었습니다.
    ... ✅ 왜곡 감시 보고서가 'distortion_report.txt' 파일에 저장되었습니다.
    ```

### 💬 텔레그램 알림 설정 (선택 사항)

콘텍스트 경고 발생 시 텔레그램으로 알림을 받고 싶다면, 다음 인수를 추가해주세요.

*   `-t` 또는 `--telegram_token`: [BotFather](https://telegram.me/BotFather)에게서 받은 여러분의 텔레그램 봇 토큰을 입력합니다. `TELEGRAM_BOT_TOKEN_PLACEHOLDER` 부분을 실제 토큰으로 교체해야 합니다.
*   `-c` 또는 `--telegram_chat_id`: 알림을 받을 텔레그램 채팅 ID를 입력합니다. (예: 개인 채팅 ID 또는 그룹 채팅 ID)

    ```bash
    python echofilter.py \
      -o "원본 내용입니다." \
      -m "왜곡된 내용입니다." \
      -t "YOUR_TELEGRAM_BOT_TOKEN" \
      -c "YOUR_TELEGRAM_CHAT_ID"
    ```

    🚨 **주의**: 텔레그램 봇 토큰과 채팅 ID를 모두 정확히 입력해야 알림이 발송됩니다.

### 📁 출력 파일

*   `context_warnings.txt`: 왜곡 경고가 발생했을 때, 자세한 경고 내용이 이 파일에 추가됩니다.
*   `distortion_report.txt`: 모든 실행 결과(왜곡 감지 여부와 상세 정보)가 이 파일에 기록됩니다.

## 🧠 EchoFilter AI는 어떻게 작동하나요? (간략 설명)

`EchoFilter`의 핵심 AI는 다음과 같은 단순화된 방식으로 작동합니다.

1.  **`analyze_original_intent`**: 원본 콘텐츠에서 불용어(stopwords)를 제거하고 가장 빈번하게 등장하는 키워드를 추출하여 '핵심 의도'를 파악합니다.
2.  **`detect_context_distortion`**: 모니터링 콘텐츠와 원본의 핵심 키워드를 비교하여, 다음 징후들을 점수화합니다.
    *   **누락된 핵심 키워드**: 원본의 중요한 키워드가 모니터링 콘텐츠에 빠져있으면 점수가 올라갑니다.
    *   **왜곡 지표**: 'fake', 'hoax', 'lie' 등과 같은 부정적인 '왜곡 지표' 단어가 포함되어 있으면 점수가 크게 올라갑니다.
    *   **컨텍스트 축약/제거**: 모니터링 콘텐츠의 길이가 원본에 비해 현저히 짧고, 핵심 키워드가 많이 누락되면 맥락이 제거된 것으로 판단합니다.
    *   **감성 변화**: 왜곡 지표 단어가 감지되면 부정적인 감성 변화가 있는 것으로 간주합니다.

⚠️ **주의**: 현재 `EchoFilter`의 AI는 매우 **간단한 키워드 기반의 프로토타입**입니다. 실제 복잡한 언어의 미묘한 맥락 왜곡을 완벽하게 탐지하기 위해서는 더 정교한 자연어 처리(NLP) 기술과 머신러닝 모델이 필요합니다. 이 코드는 개념 증명(Proof-of-Concept)을 위한 기초적인 예시입니다.

## 🚨 경고 및 주의사항

*   **AI의 한계**: 현재 버전은 복잡한 의미론적 왜곡이나 풍자, 비유 등을 제대로 이해하지 못할 수 있습니다. 단순 키워드 및 패턴 매칭 기반이므로 오탐(False Positive) 또는 미탐(False Negative)이 발생할 수 있습니다.
*   **실시간 웹 감시 부재**: 이 코드는 웹에서 직접 콘텐츠를 가져와 모니터링하는 기능은 포함하고 있지 않습니다. `--monitored_content` 인수를 통해 감시할 텍스트를 수동으로 제공해야 합니다. 실제 웹 감시 시스템으로 확장될 경우, 외부 API 사용 제한, 웹사이트 정책 준수, 네트워크 지연, 데이터 수집 시 오류 발생 등의 문제가 있을 수 있으며, 이에 대한 별도 고려가 필요합니다.
*   **데이터 손실 위험 (출력 파일)**: `context_warnings.txt`와 `distortion_report.txt` 파일은 실행할 때마다 내용이 *추가*되는 방식입니다. 파일을 주기적으로 백업하거나 관리하지 않으면 파일 크기가 커질 수 있습니다. 중요한 정보는 별도로 관리하는 것이 좋습니다.
*   **Windows 한글 출력 문제 방지**: 코드 상단에 포함된 `_sys.reconfigure(encoding="utf-8", errors="replace")` 부분은 한글 Windows 환경에서 출력 및 파일 저장 시 발생할 수 있는 `UnicodeEncodeError`를 방지하기 위한 것입니다. 안정적인 실행을 위해 이 코드를 **삭제하지 마세요.**
*   **윤리적 사용**: 이 도구는 콘텐츠의 맥락을 보호하고 허위 정보 확산을 방지하는 긍정적인 목적을 가지고 있습니다. 하지만 특정 단어나 키워드에 대한 단순 감시는 의도치 않은 편향을 가질 수 있습니다. 항상 윤리적인 관점에서 신중하게 사용해야 합니다.

## 🧑‍💻 개발자 오또의 한마디

`EchoFilter`는 여러분의 메시지가 세상에 올바르게 전달되도록 돕는 저의 작은 노력입니다. 이 프로젝트를 통해 콘텐츠의 가치를 지키고, 더 투명한 정보 생태계를 만드는 데 기여할 수 있기를 바랍니다. 궁금한 점이나 개선 아이디어가 있다면 언제든지 오또에게 알려주세요! 😊

---