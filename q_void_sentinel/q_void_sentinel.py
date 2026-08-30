
# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
#   UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import csv
import datetime
import os
import requests
import re

def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9가-힣\s]', '', text).lower().strip()

def analyze_data_for_gaps(data, topic=None):
    question_patterns = {}
    for item in data:
        question = item.get('question')
        answers = item.get('answers', [])
        if not question:
            continue

        cleaned_question = clean_text(question)
        if topic and topic.lower() not in cleaned_question:
            continue

        if cleaned_question not in question_patterns:
            question_patterns[cleaned_question] = {
                'original_question': question,
                'count': 0,
                'has_clear_answer': False,
                'answers': answers
            }
        question_patterns[cleaned_question]['count'] += 1

        # Simple AI simulation for answer quality: check if any answer is substantial
        # A 'clear' answer is assumed if it's longer than a threshold (e.g., 50 chars)
        # or contains keywords like 'solution', 'resolved'.
        if any(len(clean_text(ans)) > 50 or 'solution' in clean_text(ans) for ans in answers if ans):
            question_patterns[cleaned_question]['has_clear_answer'] = True

    content_opportunities = []
    for q_pattern, details in question_patterns.items():
        if details['count'] > 1 and not details['has_clear_answer']:
            # Calculate opportunity score: higher repetition, no clear answer = higher score
            opportunity_score = details['count'] * 100  # Base score on repetition
            # Further boost if answers are very short or non-existent
            if not details['answers'] or all(len(clean_text(ans)) < 20 for ans in details['answers'] if ans):
                opportunity_score += 50
            
            content_opportunities.append({
                'question': details['original_question'],
                'repetition_count': details['count'],
                'answer_status': 'No clear answer', # More descriptive state for output
                'opportunity_score': opportunity_score,
                'suggested_content_idea': f"Detailed guide on '{details['original_question']}'"
            })

    # Sort by opportunity score descending
    content_opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
    return content_opportunities

def main():
    parser = argparse.ArgumentParser(description="Q-Void Sentinel: Detects content gaps in Q&A data.")
    parser.add_argument('--topic', type=str, help="Specific topic keyword to filter questions.")
    parser.add_argument('--url', type=str, help="URL to fetch Q&A data (expected JSON format).")
    args = parser.parse_args()

    # --- Data Acquisition ---
    data = []
    if args.url:
        print(f"Fetching data from: {args.url}")
        try:
            response = requests.get(args.url, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            data = response.json()
            print(f"Successfully fetched {len(data)} items.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from URL: {e}. Falling back to sample data.")
        except ValueError:
            print(f"Error: The URL did not return valid JSON. Falling back to sample data.")
    
    if not data:
        print("Now demonstrating with sample data. To use your own data, run 'python q_void_sentinel.py --url YOUR_DATA_URL.json' or provide a topic like '--topic Python'.")
        # Sample data structure: list of dicts with 'question' and 'answers'
        data = [
            {"question": "What is the best way to learn Python for beginners?", "answers": ["Start with a good tutorial.", "Practice coding everyday."]},
            {"question": "How to set up a Django project with a virtual environment?", "answers": ["pip install virtualenv"]},
            {"question": "What are the best Python libraries for data analysis?", "answers": ["Pandas and NumPy are essential."]},
            {"question": "What is the best way to learn Python for beginners?", "answers": ["There are many resources, just pick one.", "Try online courses."]},
            {"question": "How do I optimize SQL queries in PostgreSQL?", "answers": []},
            {"question": "Explain the GIL in Python in simple terms.", "answers": ["It's a mutex that protects access to Python objects."]},
            {"question": "How to set up a Django project with a virtual environment?", "answers": ["Virtualenv allows isolated Python environments.", "Use 'python -m venv .venv' and then 'source .venv/bin/activate'."]},
            {"question": "What's the difference between list and tuple in Python?", "answers": ["Lists are mutable, tuples are immutable.", "Lists use brackets, tuples use parentheses."]},
            {"question": "How do I optimize SQL queries in PostgreSQL?", "answers": []},
            {"question": "Best IDE for Python development in 2024?", "answers": ["PyCharm is popular."]},
            {"question": "How do I optimize SQL queries in PostgreSQL?", "answers": ["Analyze your query plans.", "Add indexes to frequently queried columns."]}
        ]

    # --- Analysis ---
    print(f"Analyzing content gaps {f'for topic "{args.topic}"' if args.topic else ''}...")
    opportunities = analyze_data_for_gaps(data, args.topic)

    # --- Output & Reporting ---
    if opportunities:
        print("\n--- Detected Content Opportunities (Q-Void Sentinel) ---")
        for opp in opportunities:
            print(f"Question: {opp['question']}")
            print(f"  Repetitions: {opp['repetition_count']}")
            print(f"  Status: {opp['answer_status']}")
            print(f"  Opportunity Score: {opp['opportunity_score']}")
            print(f"  Content Idea: {opp['suggested_content_idea']}")
            print("-" * 30)
        
        output_filename = f"q_void_sentinel_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        try:
            with open(output_filename, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['question', 'repetition_count', 'answer_status', 'opportunity_score', 'suggested_content_idea']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(opportunities)
            print(f"\nReport saved to {output_filename}")
        except IOError as e:
            print(f"Error saving report to CSV: {e}")

    else:
        print(f"No significant content opportunities found {f'for topic "{args.topic}"' if args.topic else ''}.")
    
    print("\nTip: Schedule this script to run daily to continuously monitor for new content gaps. (e.g., cron job on Linux/macOS or Task Scheduler on Windows)")

if __name__ == "__main__":
    main()
