# Bionic_KIMI의 1달러 뉴스: AI 머니 스멜러

AI 에이전트 '키미'가 LM Studio Bionic으로 매일 아침 주식/코인 시장을 냄새 맡아 3줄 요약 뉴스레터를 발행해요. 목표는 단돈 1달러! 혹시 압니까, 1달러가 100달러가 될지?

## 🚀 시작하는 방법
1. 격리된 가상 환경을 생성하고 활성화합니다.
```bash
python -m venv venv
.\venv\Scripts\activate # Windows
source venv/bin/activate # macOS/Linux
```
2. 필요한 라이브러리를 설치합니다.
```bash
pip install -r requirements.txt
```
3. `.env` 파일에 필요한 API 자격 증명을 설정합니다.
4. 스크립트를 실행합니다.
```bash
python bot.py
```

## ⚠️ 경고 및 주의사항
- 외부 API 연동 시 Rate Limit 및 호출 비용에 주의하십시오.
- 이 도구는 시연 및 교육을 목적으로 모의 구현되었습니다.
