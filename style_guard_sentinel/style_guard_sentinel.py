
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
import re
import json
import datetime
from collections import Counter
import math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# NLTK dependencies - User might need to run:
# import nltk
# nltk.download('punkt')
# nltk.download('stopwords')
# For simplicity, we'll use basic regex tokenization here to avoid NLTK download issues for a quick run.

class StyleGuardSentinel:
    def __init__(self, creator_name="Unknown Creator"):
        self.creator_name = creator_name
        self.style_profile = None
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.alerts = []

    def _preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', '', text) # Remove punctuation
        return text

    def learn_creator_style(self, text_data):
        print(f"[+] 학습 시작: '{self.creator_name}'님의 고유 스타일을 학습 중...")
        preprocessed_texts = [self._preprocess_text(t) for t in text_data]
        if not preprocessed_texts:
            print("[!] 학습할 텍스트가 없습니다. 스타일 프로필 생성 실패.")
            return False
        
        # Learn TF-IDF vocabulary and transform creator's texts
        creator_vectors = self.vectorizer.fit_transform(preprocessed_texts)
        self.style_profile = np.mean(creator_vectors.toarray(), axis=0) # Average vector as profile
        print(f"[+] 학습 완료: '{self.creator_name}'님의 스타일 프로필이 생성되었습니다. (차원: {len(self.style_profile)})\n")
        return True

    def monitor_content(self, new_content_list, similarity_threshold=0.7):
        if self.style_profile is None:
            print("[!] 스타일 프로필이 먼저 학습되어야 합니다. 'learn_creator_style'을 먼저 실행하세요.")
            return

        print(f"[+] 콘텐츠 감시 시작: 웹상의 새로운 콘텐츠를 '{self.creator_name}'님 스타일과 비교 중...")
        for i, content in enumerate(new_content_list):
            preprocessed_content = self._preprocess_text(content)
            if not preprocessed_content.strip():
                continue

            # Transform new content using the *same* vectorizer fitted on creator's data
            new_content_vector = self.vectorizer.transform([preprocessed_content])
            
            if new_content_vector.shape[1] == 0: # Check if the vector is empty after transformation
                continue

            # Calculate cosine similarity
            similarity = cosine_similarity(self.style_profile.reshape(1, -1), new_content_vector.toarray())[0][0]

            if similarity >= similarity_threshold:
                alert_message = f"[!!! 경고 !!!] '{self.creator_name}'님의 스타일과 매우 유사한 AI 생성 콘텐츠 발견!\n유사도: {similarity:.2f} (임계치: {similarity_threshold})\n내용 일부: {content[:100]}..."
                self.alerts.append({
                    "timestamp": str(datetime.datetime.now()),
                    "creator": self.creator_name,
                    "similarity": similarity,
                    "content_snippet": content[:200] + "...",
                    "full_content_hash": hash(content) # Simple content identifier
                })
                print(alert_message)
            else:
                print(f"[-] 새로운 콘텐츠 {i+1} 감시 완료. 유사도: {similarity:.2f} (임계치 미달)")
        
        print("\n[+] 콘텐츠 감시 종료.")
        if self.alerts:
            print(f"[!] 총 {len(self.alerts)}건의 AI 스타일 모방 의심 사례가 감지되었습니다.\n")
        else:
            print("[+] AI 스타일 모방 의심 사례가 감지되지 않았습니다.\n")

    def save_alerts_to_file(self, filename="styleguard_alerts.json"):
        if self.alerts:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.alerts, f, ensure_ascii=False, indent=2)
            print(f"[파일 저장] 감지된 경고 목록이 '{filename}'에 저장되었습니다.")
            print("[안내] 이 익명화된 데이터를 AI 윤리 연구소 등에 1달러에 판매합니다. (가상 동작)")
        else:
            print("[안내] 저장할 경고가 없습니다.")

def run_demo():
    print("\n--- StyleGuard Sentinel 데모 모드 실행 ---")
    print("지금은 샘플 데이터로 시연 중입니다. 본인 파일을 쓰려면 'python style_guard_sentinel.py --creator_texts 내파일.txt' 처럼 실행하세요.\n")

    demo_creator_texts = [
        "안녕하세요, 저는 오늘 여러분과 함께 흥미로운 주제에 대해 이야기하고자 합니다. 특히, 최신 기술 트렌드와 그로 인한 사회 변화에 주목해봅시다. 복잡한 문제를 단순하게 설명하는 것이 저의 강점입니다.",
        "최근 인공지능의 발전은 실로 놀랍습니다. 그러나 이러한 발전이 가져올 윤리적 문제와 개인 정보 보호에 대한 깊은 논의가 필요하다고 생각합니다. 항상 균형 잡힌 시각을 유지하는 것이 중요합니다.",
        "창의성은 인간 고유의 영역이라고 여겨져 왔지만, AI가 창작 활동에 참여하면서 이 경계가 모호해지고 있습니다. 미래에는 인간과 AI의 협업이 새로운 창조의 지평을 열 것입니다. 제 의견은 이렇습니다."
    ]

    demo_new_web_content = [
        "여러분, 안녕하세요! 오늘 저는 기술의 미래와 사회적 영향이라는 매우 중요한 테마를 다루고자 합니다. 어려운 개념도 쉽게 풀어서 전달하는 것이 제 스타일이죠.",
        "인공지능의 급격한 발전은 분명 흥미롭지만, AI 윤리와 데이터 프라이버시 문제는 심도 있게 고민해야 합니다. 언제나 양면성을 고려하며 접근하는 것이 현명합니다.",
        "창의적 작업은 인간만의 전유물로 생각되었으나, AI의 등장으로 그 인식이 변화하고 있습니다. 앞으로 인간과 AI가 공존하며 더욱 풍부한 창조물을 만들어낼 것이라는 생각입니다.",
        "오늘 날씨가 정말 좋네요. 저는 산책을 다녀왔어요. 가을이 되면 단풍 구경도 가봐야겠어요. 맛있는 커피 한잔 어떠세요?"
    ]

    sentinel = StyleGuardSentinel(creator_name="오또 샘플")
    if sentinel.learn_creator_style(demo_creator_texts):
        sentinel.monitor_content(demo_new_web_content, similarity_threshold=0.75)
        sentinel.save_alerts_to_file()

def main():
    parser = argparse.ArgumentParser(description="StyleGuard Sentinel: AI 기반 콘텐츠 스타일 모방 감시병")
    parser.add_argument('--creator_texts', type=str, help='콘텐츠 제작자의 과거 텍스트 데이터 파일 경로 (한 줄에 하나의 문서).')
    parser.add_argument('--new_content_feed', type=str, default=None, 
                        help='감시할 새로운 웹 콘텐츠 피드 파일 경로 (한 줄에 하나의 문서). 비워두면 데모 데이터를 사용합니다.')
    parser.add_argument('--threshold', type=float, default=0.7, 
                        help='AI 모방 감지 유사도 임계치 (0.0 ~ 1.0). 기본값은 0.7입니다.')
    args = parser.parse_args()

    if args.creator_texts:
        if not os.path.exists(args.creator_texts):
            print(f"[오류] 제작자 텍스트 파일 '{args.creator_texts}'을 찾을 수 없습니다. 경로를 확인해주세요.")
            return
        with open(args.creator_texts, 'r', encoding='utf-8') as f:
            creator_texts = [line.strip() for line in f if line.strip()]
        
        new_content_list = []
        if args.new_content_feed and os.path.exists(args.new_content_feed):
            with open(args.new_content_feed, 'r', encoding='utf-8') as f:
                new_content_list = [line.strip() for line in f if line.strip()]
        elif args.new_content_feed and not os.path.exists(args.new_content_feed):
            print(f"[오류] 새로운 콘텐츠 피드 파일 '{args.new_content_feed}'을 찾을 수 없습니다. 데모 데이터로 대체합니다.")
            # Fallback to demo content if specified file not found
            new_content_list = ["이것은 샘플 웹 콘텐츠입니다. 흥미로운 주제에 대해 이야기하고 있습니다.", "AI의 발전은 계속되고 있으며, 그 영향은 광범위합니다."]
        else: # If no new_content_feed specified, use a small default for non-demo run
            new_content_list = ["이것은 샘플 웹 콘텐츠입니다. 흥미로운 주제에 대해 이야기하고 있습니다.", "AI의 발전은 계속되고 있으며, 그 영향은 광범위합니다."]

        if not creator_texts:
            print("[오류] 제작자 텍스트 파일에 내용이 없습니다. 유효한 텍스트를 제공해주세요.")
            return

        print("--- StyleGuard Sentinel 사용자 지정 모드 실행 ---")
        sentinel = StyleGuardSentinel(creator_name="사용자")
        if sentinel.learn_creator_style(creator_texts):
            sentinel.monitor_content(new_content_list, similarity_threshold=args.threshold)
            sentinel.save_alerts_to_file()

    else:
        run_demo()

    print("\n[팁] 이 스크립트를 매일/주간 실행하여 지속적으로 스타일 모방을 감시할 수 있습니다. (예: cronjob, Windows 작업 스케줄러)")

if __name__ == "__main__":
    main()
