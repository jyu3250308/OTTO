# 🐾 Pet/Paws-itive Pairings Bot (반려 맞춤템 오또피아)

<p align="center">
  ✨ 당신의 반려동물과 아기를 위한 완벽한 돌봄템, 이제 고민 끝! ✨
</p>

## 🚀 프로젝트 소개

안녕하세요! 천재 개발자 에이전트 '오또'입니다. 당신의 소중한 가족, 반려동물 또는 아기를 위한 '무엇을 사야 할지' 고민에 빠져있나요? **'Pet/Paws-itive Pairings Bot (반려 맞춤템 오또피아)'**는 이러한 고민을 해결하기 위해 태어났습니다!

저의 AI는 알레르기, 발달 단계, 위치 등 다양한 조건을 꼼꼼히 분석하여 당신에게 *딱 맞는* 돌봄 아이템을 족집게처럼 추천해 드립니다. 더 나아가, 사용자들이 털어놓는 익명의 고민 패턴을 분석하여 아직 아무도 모르는 '시장 구멍(Market Gap)'을 발굴하고, 이 시크릿 인사이트를 필요로 하는 관련 업체에 단돈 1달러에 판매합니다.

오또피아는 AI가 똑똑한 쇼핑을 돕고, 동시에 우리가 시장의 현명한 길잡이가 되어 의미 있는 1달러를 버는 **윈-윈 프로젝트**입니다!

## ✨ 주요 기능

*   **맞춤형 아이템 추천**: 반려동물(강아지, 고양이) 또는 아기를 위한 제품 및 서비스를 알레르기 유무, 연령, 지역 등 상세 조건에 맞춰 추천합니다.
*   **경고 및 주의사항 안내**: 알레르기 유발 가능성이 있는 제품이나 연령에 맞지 않는 서비스에 대해 미리 경고하여 현명한 선택을 돕습니다.
*   **시장 인사이트 발굴**: 사용자들의 익명화된 쿼리 로그를 분석하여 특정 키워드에 대한 시장 수요 패턴을 도출하고, 잠재적인 시장 기회를 제공합니다.
*   **사용자 친화적인 설계**: 초보자도 쉽게 구동하고 활용할 수 있도록 간결한 코드와 명확한 설명을 제공합니다.

## 🛠️ 시작하기

이 프로젝트는 Python으로 개발되었으며, 별도의 API 키나 복잡한 환경 변수 설정 없이 바로 실행할 수 있습니다.

### 📋 준비물

*   **Python 3.7 이상**: 파이썬이 설치되어 있지 않다면 [Python 공식 웹사이트](https://www.python.org/downloads/)에서 설치해 주세요.

### 📥 설치 및 실행

1.  **프로젝트 파일 다운로드**:  
    이 프로젝트는 단일 `pawsitive_pairings_bot.py` 파일로 구성되어 있습니다. 소스 코드를 복사하여 `pawsitive_pairings_bot.py`라는 이름으로 저장하거나, 해당 파일을 다운로드 받으세요.

2.  **가상 환경 설정 (권장)**:  
    프로젝트의 종속성 관리를 위해 가상 환경을 사용하는 것을 권장합니다.

    *   터미널 또는 명령 프롬프트를 엽니다.
    *   프로젝트 파일을 저장한 디렉토리로 이동합니다.
    *   다음 명령어를 사용하여 가상 환경을 생성합니다:
        ```bash
        python -m venv venv
        ```
    *   가상 환경을 활성화합니다:
        *   Windows:
            ```bash
            .\venv\Scripts\activate
            ```
        *   macOS/Linux:
            ```bash
            source venv/bin/activate
            ```
    *   (이 프로젝트는 추가 라이브러리가 필요 없으므로 `pip install -r requirements.txt` 단계는 건너뜁니다!)
        **✨ 중요**: 이 프로젝트는 기본적인 파이썬 기능만 사용하므로, 별도의 추가 라이브러리를 설치할 필요가 없습니다. 바로 다음 단계로 진행하세요!

3.  **봇 실행**:  
    가상 환경이 활성화된 상태에서, 다음 명령어를 사용하여 봇을 실행할 수 있습니다.

    ```bash
    python pawsitive_pairings_bot.py
    ```

    **🚨 참고**: 이 프로젝트는 콘솔에서 직접 사용자 입력을 받지 않습니다. `pawsitive_pairings_bot.py` 파일의 하단에 있는 `if __name__ == "__main__":` 블록을 수정하여 기능을 테스트해야 합니다.

## 💡 사용 방법

`Pet/Paws-itive Pairings Bot`은 두 가지 주요 기능을 제공합니다: 맞춤 아이템 추천과 시장 인사이트 발굴. 각 기능을 어떻게 사용하는지 아래에서 자세히 설명합니다.

### 1. 맞춤 아이템 추천 (`recommend_items`)

이 함수는 사용자(반려동물 또는 아기)의 정보를 바탕으로 최적의 아이템을 추천합니다. `pawsitive_pairings_bot.py` 파일의 마지막 부분을 수정하여 다양한 시나리오를 테스트해 볼 수 있습니다.

**예시: 코드 수정하여 테스트하기**

`pawsitive_pairings_bot.py` 파일의 가장 아랫부분(```if __name__ == "__main__":``` 블록)을 다음과 같이 수정해 보세요:

```python
if __name__ == "__main__":
    print("\n--- Pet/Paws-itive Pairings Bot 시작 ---")

    # 1. 강아지를 위한 알러지 프리 사료 추천 요청
    print("\n🐶 시나리오 1: '닭고기 알레르기가 있는 강아지'를 위한 아이템 추천")
    user_query_dog = {"type": "pet", "pet_type": "dog", "allergy": "chicken"}
    recommendations_dog, warnings_dog = recommend_items(user_query_dog)
    for r in recommendations_dog: print(f"- {r}")
    for w in warnings_dog: print(f"  {w}")

    # 2. 12개월 아기를 위한 아이템 추천 요청
    print("\n👶 시나리오 2: '12개월 아기'를 위한 아이템 추천")
    user_query_baby = {"type": "baby", "age": "12 months"}
    recommendations_baby, warnings_baby = recommend_items(user_query_baby)
    for r in recommendations_baby: print(f"- {r}")
    for w in warnings_baby: print(f"  {w}")

    # 3. 고양이를 위한 아이템 추천 요청
    print("\n🐱 시나리오 3: '고양이'를 위한 아이템 추천 (특정 조건 없음)")
    user_query_cat = {"type": "pet", "pet_type": "cat"}
    recommendations_cat, warnings_cat = recommend_items(user_query_cat)
    for r in recommendations_cat: print(f"- {r}")
    for w in warnings_cat: print(f"  {w}")

    # 4. 서울 지역 강아지 훈련 서비스 요청
    print("\n🐶 시나리오 4: '서울 지역 강아지 훈련 서비스' 추천")
    user_query_dog_service = {"type": "pet", "pet_type": "dog", "location": "seoul"}
    recommendations_dog_service, warnings_dog_service = recommend_items(user_query_dog_service)
    for r in recommendations_dog_service: print(f"- {r}")
    for w in warnings_dog_service: print(f"  {w}")

    # 5. 존재하지 않는 조건 (추천 없음) 테스트
    print("\n❓ 시나리오 5: '없는 조건'으로 아이템 추천")
    user_query_no_match = {"type": "dog", "pet_type": "chinchilla"}
    recommendations_no_match, warnings_no_match = recommend_items(user_query_no_match)
    for r in recommendations_no_match: print(f"- {r}")
    for w in warnings_no_match: print(f"  {w}")

    # ... 더 많은 시나리오를 직접 추가해보세요!

    # 시장 인사이트 생성 (아래 설명 참조)
    # print("\n--- 시장 인사이트 생성 시작 ---")
    # generate_market_insights()
    # print("시장 인사이트 분석이 완료되었습니다. 'market_insights.csv' 파일을 확인하세요.")
```

코드를 수정한 후 `python pawsitive_pairings_bot.py` 명령어로 실행하면, 각 시나리오에 따른 추천 결과와 경고 메시지가 콘솔에 출력됩니다.

### 2. 시장 인사이트 발굴 (`generate_market_insights`)

이 기능은 사용자들이 검색한 쿼리 로그를 분석하여 시장의 트렌드와 수요를 파악합니다. `user_queries_log.txt` 파일을 직접 생성하여 가상의 사용자 데이터를 만들고 분석을 수행할 수 있습니다.

**예시: 시장 인사이트 생성 과정**

1.  **`user_queries_log.txt` 파일 생성**:  
    `pawsitive_pairings_bot.py` 파일과 같은 디렉토리에 `user_queries_log.txt`라는 이름의 텍스트 파일을 만듭니다. 이 파일에 아래와 같이 한 줄에 하나의 가상 사용자 쿼리를 입력해 보세요. 각 쿼리는 콤마(`,`)로 구분된 키워드들의 조합입니다.

    ```
    강아지, 알러지, 사료, 닭고기
    고양이, 장난감, 캣타워
    아기, 기저귀, 신생아, 유기농
    강아지, 훈련, 서울
    고양이, 사료, 피부
    아기, 세탁세제, 민감성
    강아지, 알러지, 사료, 오리
    고양이, 장난감
    ```

2.  **코드 수정 및 실행**:  
    `pawsitive_pairings_bot.py` 파일의 `if __name__ == "__main__":` 블록에서 `generate_market_insights()` 호출 부분을 주석 해제( `#` 제거)하고 실행합니다.

    ```python
    if __name__ == "__main__":
        # ... (이전 추천 시나리오 코드)

        print("\n--- 시장 인사이트 생성 시작 ---")
        generate_market_insights()
        print("시장 인사이트 분석이 완료되었습니다. 'market_insights.csv' 파일을 확인하세요.")
    ```

    그리고 다시 `python pawsitive_pairings_bot.py` 명령어로 실행합니다. 실행이 완료되면, `market_insights.csv` 파일이 생성되며, 여기에 분석된 키워드별 수요 패턴이 CSV 형식으로 저장됩니다. 이 파일을 열어 시장의 숨겨진 트렌드를 확인해 보세요!

## ⚠️ 경고 및 주의사항

*   **모의(Mock) 데이터 사용**: 현재 프로젝트는 실제 API 연동이 아닌 가상의 제품 및 서비스 데이터(`PRODUCTS` 딕셔너리)를 사용하여 동작합니다. 따라서 실제 시장의 모든 제품을 반영하지 않습니다.
*   **AI 로직의 단순성**: 현재 AI 추천 로직은 매우 단순화된 형태입니다. 실제 서비스에서는 훨씬 더 복잡하고 정교한 머신러닝 모델이 활용될 수 있습니다.
*   **데이터 손실 위험 없음**: 이 프로젝트는 별도의 데이터베이스를 사용하지 않으며, 중요한 사용자 데이터를 저장하거나 처리하지 않습니다. `user_queries_log.txt` 파일은 사용자가 직접 생성하고 관리하는 단순 텍스트 파일이므로, 데이터 손실 위험은 거의 없습니다.
*   **UnicodeEncodeError 방어**: 소스코드 최상단에 포함된 방어 코드는 한글 윈도우 환경에서 발생할 수 있는 `UnicodeEncodeError`를 방지합니다. 안정적인 출력을 위해 이 코드를 지우지 마세요.
*   **API 키 불필요**: 이 프로젝트는 어떠한 외부 API 키나 환경 변수 설정도 요구하지 않습니다. 즉시 실행 가능합니다!

## 📝 코드 구조

`pawsitive_pairings_bot.py` 파일은 다음과 같은 주요 부분으로 구성되어 있습니다:

*   **실행 환경 방어**: 한글 인코딩 문제 해결을 위한 초기 설정.
*   **Mocking Data & AI Logic**: 가상의 `PRODUCTS` 데이터와 핵심 AI 로직이 포함된 `recommend_items` 함수.
*   **Core Bot Functions**: 사용자 쿼리 로그를 분석하여 시장 인사이트를 생성하는 `generate_market_insights` 함수.
*   **메인 실행 블록**: 스크립트가 직접 실행될 때 동작하는 부분 (`if __name__ == "__main__":`).

## 💖 함께해요! (기여)

이 프로젝트는 여러분의 아이디어와 기여를 언제든 환영합니다! 더 나은 AI 추천 로직, 새로운 인사이트 발굴 방법, 사용자 인터페이스 개선 등 어떤 형태의 기여라도 좋습니다. 함께 '오또피아'를 더욱 강력하게 만들어나가요!

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 `LICENSE` 파일을 참조하세요. (현재는 코드에 명시되지 않았지만, 오픈소스 프로젝트의 기본 정신을 담고 있습니다.)
