# Viral Siren (바이럴 사이렌)

쇼츠 제작자들을 위해 AI가 유튜브, 틱톡 등에서 급상승하는 바이럴 사운드를 실시간으로 감지하여, 이 사운드의 예상 도달율 시뮬레이션과 함께 알림을 보냅니다. 오또는 이 AI가 포착한 트렌드 사운드 데이터를 기반으로 특정 콘텐츠의 '예상 도달률 및 참여율 시뮬레이션 데이터'를 콘텐츠 제작 스튜디오에 $1에 판매하여 수익을 창출합니다.

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
3. (API 키 불필요 — 바로 실행됩니다!)
4. 스크립트를 실행합니다.
```bash
python viral_siren.py
```

## ⚠️ 경고 및 주의사항
- 외부 API 연동 시 Rate Limit 및 호출 비용에 주의하십시오.
- 이 도구는 시연 및 교육을 목적으로 모의 구현되었습니다.
