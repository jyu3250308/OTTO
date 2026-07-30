
# ─────────────────────────────────────────────────────────────────────────────
# [실행 환경 방어] 한글 윈도우에서 출력을 파일로 저장하거나 다른 프로그램에 넘길 때
#   (예: python bot.py > log.txt / 작업 스케줄러 등록 / 주피터 / VS Code 일부 설정)
#   파이썬이 콘솔 기본 인코딩(cp949)을 쓰게 되어 이모지 출력 순간 UnicodeEncodeError로 죽습니다.
#   아래 3줄이 그걸 막아줍니다. 지우지 마세요!
# ─────────────────────────────────────────────────────────────────────────────
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


import datetime
import random
import os

def _mock_ai_generate_scenario(user_prompt: str) -> str:
    """
    Mocks an AI generating an alternate history scenario based on user_prompt.
    It provides diverse content types (diary, news, dialogue).
    """
    print(f"\
[ChronoWhisperer AI] 'What If' 시나리오를 생성 중입니다: '{user_prompt}'")
    scenario_type = random.choice(["일기", "뉴스 기사", "대화"])
    mock_content = ""
    
    keywords = user_prompt.lower().split()
    
    # Basic keyword-based content generation
    if "세종대왕" in keywords and "스마트폰" in keywords:
        base_scenario = "세종대왕이 스마트폰을 가졌더라면, 한글의 보급은 물론, 백성과의 소통 방식이 혁명적으로 바뀌었을 것입니다. 어쩌면 전 세계에 조선의 IT 기술이 전파되었을지도 모릅니다."
    elif "공룡" in keywords and "멸종" in keywords and "안" in keywords:
        base_scenario = "만약 공룡이 멸종하지 않고 현대까지 살아남았다면, 인류는 거대한 생명체와 공존하거나 끝없는 생존 경쟁을 벌였을 것입니다. 대도시 대신 공룡 보호 구역이 생겼을지도 모릅니다."
    elif "로마" in keywords and "제국" in keywords and "멸망" in keywords and "안" in keywords:
        base_scenario = "로마 제국이 멸망하지 않고 계속 존속했다면, 유럽의 역사는 완전히 달라졌을 것입니다. 기술 발전, 정치 체제, 문화 예술 등 모든 면에서 현재와는 상상조차 어려운 세상이 되었을 겁니다."
    else:
        base_scenario = f"당신의 '{user_prompt}' 질문은 흥미롭군요. 역사의 한 페이지를 완전히 뒤바꿀 만한 상상력입니다. 이 가설이 현실이 되었다면, 우리는 오늘날과는 전혀 다른 세상을 살고 있을 것입니다."
        
    
    if scenario_type == "일기":
        mock_content = f"""[가상 역사 일기 - {datetime.date.today().strftime('%Y년 %m월 %d일')}]\
오늘 아침, 나는 잠시 멍하니 창밖을 바라보았다. {user_prompt} 이 현실이 되었다는 사실이 아직도 믿기지 않는다. 모든 것이 너무나도... 다르다. 어제의 역사가 오늘 바뀌어버린 느낌이다. {base_scenario} 이제 우리는 이 새로운 역사 속에서 어떻게 살아가야 할까."""
    elif scenario_type == "뉴스 기사":
        mock_content = f"""[긴급 속보: 역사를 뒤흔든 'What If' 현실화]\
속보입니다. 오늘 아침, 익명의 'ChronoWhisperer AI'가 던진 질문, '{user_prompt}'이 현실화되었다는 충격적인 보도가 나왔습니다. 역사학자들은 일제히 혼란에 빠졌으며, 인류 문명의 근간이 뒤흔들릴 수 있다고 경고했습니다. {base_scenario} 전문가들은 향후 전개될 상황에 대해 예측하기 어렵다고 밝혔습니다."""
    elif scenario_type == "대화":
        mock_content = f"""[가상 역사 대화 - 기록 보관소 발견]\
인물 A: 믿을 수 없어. {user_prompt} 이게 정말 가능했던 거야?\
인물 B: 기록에 따르면 그렇다고 합니다. AI가 제시한 이 가설이 현실이 되면서, 우리는 전혀 다른 시간선에 살고 있는 거죠.\
인물 A: 그럼 우리 조상들의 삶은 어땠을까?\
인물 B: 글쎄요. {base_scenario} 상상하기조차 힘든 일입니다. 이제 우리는 이 새로운 역사를 어떻게 받아들여야 할까요?"""

    print(f"[ChronoWhisperer AI] 시나리오 생성이 완료되었습니다. ({scenario_type} 형식)\
")
    return mock_content

def _mock_process_payment(amount: float) -> bool:
    """Mocks a payment process for a given amount."""
    print(f"\
[결제 시스템] {amount:.2f} 달러 결제를 시도합니다...")
    # Simulate a successful payment
    print("[결제 시스템] 결제가 성공적으로 완료되었습니다!")
    return True

def _save_content_to_file(filename: str, content: str):
    """Saves the generated content to a text file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[파일 저장] 생성된 콘텐츠가 '{filename}' 파일로 저장되었습니다.")
    except IOError as e:
        print(f"[오류] 파일 저장 중 문제가 발생했습니다: {e}")

def main():
    """
    Main function for the ChronoWhisperer AI project.
    Generates alternate history content based on user input.
    """
    print("==============================================")
    print("  ✨ ChronoWhisperer AI: 역사改變 1달러 ✨")
    print("AI가 당신의 '만약에' 질문을 받아, 역사의 한 순간을 비틀어낸")
    print("가상 일기, 뉴스 등을 $1에 생성해 드립니다!")
    print("==============================================")

    user_prompt = input("\
[사용자] 당신의 기발한 '만약에' 질문을 입력해주세요 (예: 세종대왕이 스마트폰을 가졌다면?):\
> ").strip()

    if not user_prompt:
        print("[오류] 유효한 질문을 입력해주세요. 프로그램을 종료합니다.")
        return

    # Simulate $1 payment
    if not _mock_process_payment(1.00):
        print("[오류] 결제에 실패했습니다. 프로그램을 종료합니다.")
        return

    # Simulate AI content generation
    generated_content = _mock_ai_generate_scenario(user_prompt)

    # Generate a unique filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"chrono_whisperer_output_{timestamp}.txt"

    # Save content to file
    _save_content_to_file(output_filename, generated_content)

    print(f"\
[ChronoWhisperer AI] 새로운 대체 역사가 생성되어 '{output_filename}' 파일로 저장되었습니다!")
    print("이 파일을 열어 당신의 상상력이 빚어낸 역사를 확인해 보세요!")
    print("\
==============================================")
    print("  ⭐ 오늘의 대체 역사 생성 완료! ⭐")
    print("매일 새로운 '만약에' 질문으로 역사를 비틀어 보세요!")
    print("팁: 이 스크립트를 작업 스케줄러에 등록하여 매일 다른 질문으로")
    print("    자동으로 대체 역사를 생성하고 저장할 수 있습니다. (예: cronjob)")
    print("==============================================")

if __name__ == "__main__":
    main()