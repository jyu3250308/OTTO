
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


import os
import hashlib
import time
import datetime
import random

class CodeDustAlchemist:
    def __init__(self):
        self.output_dir = "code_relics"
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"[{datetime.datetime.now()}] Code-Dust Alchemist initialized. Output directory: {self.output_dir}")

    def _mock_fetch_old_code(self):
        """Mocks fetching 'dead code' from a public repository."""
        mock_codes = [
            "def calculate_fibonacci(n):\
    a, b = 0, 1\
    for _ in range(n):\
        yield a\
        a, b = b, a + b",
            "class OldLogger:\
    def __init__(self, filename='log.txt'):\
        self.file = open(filename, 'a')\
    def log(self, message):\
        self.file.write(f'{datetime.datetime.now()}: {message}\
')\
    def close(self):\
        self.file.close()",
            "if __name__ == '__main__':\
    print('Hello, ancient world!')",
            "import os\
import sys\
\
# This function was never called\
def unused_function():\
    pass"
        ]
        chosen_code = random.choice(mock_codes)
        code_hash = hashlib.md5(chosen_code.encode()).hexdigest()
        print(f"[{datetime.datetime.now()}] Harvested a snippet of dead code (hash: {code_hash[:8]}...)")
        return chosen_code, code_hash

    def _mock_analyze_code_pattern(self, code_content):
        """Mocks AI analysis to find abstract patterns."""
        # Simple pattern extraction: count lines, character frequency, keyword presence
        line_count = len(code_content.split('\
'))
        char_freq = {char: code_content.count(char) for char in set(code_content)}
        keywords = ["def", "class", "import", "if", "for", "while"]
        keyword_presence = {kw: (1 if kw in code_content else 0) for kw in keywords}

        pattern_data = {
            "line_count": line_count,
            "unique_chars": len(char_freq),
            "keyword_score": sum(keyword_presence.values()),
            "code_entropy": sum(c * c for c in char_freq.values()) % 100 # A pseudo-random value based on char freq
        }
        print(f"[{datetime.datetime.now()}] Analyzed code for patterns: {pattern_data}")
        return pattern_data

    def _generate_relic_design(self, pattern_data, code_hash):
        """Generates minimalist SVG/STL designs based on pattern data."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        relic_id = f"{timestamp}-{code_hash[:8]}"

        # --- SVG Design ---
        svg_filename = os.path.join(self.output_dir, f"relic_{relic_id}.svg")
        size = 100
        center = size / 2
        
        # Base color variations
        colors = ["#3498db", "#e74c3c", "#2ecc71", "#f1c40f", "#9b59b6"]
        color_index = pattern_data['code_entropy'] % len(colors)
        base_color = colors[color_index]

        # Dynamic shapes based on pattern_data
        num_circles = pattern_data['line_count'] % 5 + 1
        line_length_factor = (pattern_data['unique_chars'] % 5 + 1) * 5
        keyword_circle_radius = pattern_data['keyword_score'] * 3 + 5

        svg_content = f"""<?xml version=\"1.0\" standalone=\"no\"?>
<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">
<svg width=\"{size}\" height=\"{size}\" viewBox=\"0 0 {size} {size}\" xmlns=\"http://www.w3.org/2000/svg\">
  <rect x=\"0\" y=\"0\" width=\"{size}\" height=\"{size}\" fill=\"#ecf0f1\"/>
  <circle cx=\"{center}\" cy=\"{center}\" r=\"{keyword_circle_radius}\" fill=\"{base_color}\" opacity=\"0.7\"/>
"""
        for i in range(num_circles):
            cx_offset = random.randint(-20, 20)
            cy_offset = random.randint(-20, 20)
            r = (pattern_data['unique_chars'] % 5 + i * 2) + 2
            svg_content += f'  <circle cx="{center + cx_offset}" cy="{center + cy_offset}" r="{r}" fill="{base_color}" opacity="0.3"/>\
'

        for i in range(pattern_data['keyword_score'] % 4 + 1):
            x1 = random.randint(0, size)
            y1 = random.randint(0, size)
            x2 = x1 + random.randint(-line_length_factor, line_length_factor)
            y2 = y1 + random.randint(-line_length_factor, line_length_factor)
            svg_content += f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{base_color}" stroke-width="1" opacity="0.8"/>\
'
        
        svg_content += f"""  <text x=\"5\" y=\"{size-5}\" font-family=\"Arial\" font-size=\"5\" fill=\"#7f8c8d\">{relic_id}</text>
</svg>"""

        with open(svg_filename, "w") as f:
            f.write(svg_content)
        print(f"[{datetime.datetime.now()}] Generated SVG relic design: {svg_filename}")

        # --- STL Design (Mock) ---
        # For simplicity and line limit, we'll mock an STL by generating a simple cube.
        # A real implementation would convert 2D SVG to 3D or generate complex geometry.
        stl_filename = os.path.join(self.output_dir, f"relic_{relic_id}.stl")
        mock_stl_content = f"""solid {relic_id}
  facet normal 0 0 -1
    outer loop
      vertex 0 0 0
      vertex 10 0 0
      vertex 10 10 0
    endloop
  endfacet
  facet normal 0 0 -1
    outer loop
      vertex 0 0 0
      vertex 10 10 0
      vertex 0 10 0
    endloop
  endfacet
endsolid {relic_id}"""
        with open(stl_filename, "w") as f:
            f.write(mock_stl_content)
        print(f"[{datetime.datetime.now()}] Generated MOCK STL relic design: {stl_filename}")

        return svg_filename, stl_filename, relic_id

    def _mock_manufacture_and_sell(self, relic_id, svg_file, stl_file):
        """Mocks ordering from a manufacturer and listing online."""
        print(f"[{datetime.datetime.now()}] Simulating order to on-demand manufacturer for Relic ID: {relic_id} (using {stl_file})...")
        time.sleep(0.5) # Simulate network delay
        print(f"[{datetime.datetime.now()}] Manufacturer acknowledged. Production will take 1-2 days.")
        
        print(f"[{datetime.datetime.now()}] Listing Code Relic '{relic_id}' for $1 on our online store...")
        time.sleep(0.3) # Simulate network delay
        listing_url = f"https://mock-codestore.com/relic/{relic_id}"
        print(f"[{datetime.datetime.now()}] Relic '{relic_id}' listed successfully! View at: {listing_url}")
        return listing_url

    def run_alchemist(self):
        """Main loop for the Code-Dust Alchemist."""
        print("\
--- Starting Code-Dust Alchemy Process ---")
        try:
            # 1. Harvest & Analyze
            code_content, code_hash = self._mock_fetch_old_code()
            pattern_data = self._mock_analyze_code_pattern(code_content)

            # 2. Design Relic
            svg_file, stl_file, relic_id = self._generate_relic_design(pattern_data, code_hash)

            # 3. Manufacture & Sell (Mock)
            listing_url = self._mock_manufacture_and_sell(relic_id, svg_file, stl_file)

            # Record the relic
            relic_manifest_path = os.path.join(self.output_dir, "relic_manifest.txt")
            with open(relic_manifest_path, "a") as f:
                f.write(f"[{datetime.datetime.now()}] Relic ID: {relic_id}, SVG: {os.path.basename(svg_file)}, STL: {os.path.basename(stl_file)}, Listed: {listing_url}\
")
            print(f"[{datetime.datetime.now()}] Relic details added to {relic_manifest_path}")

            print(f"--- Code-Dust Alchemy Completed for Relic ID: {relic_id} ---")
            print(f"\
[Output] View your new Code Relic SVG at: {svg_file}")
            print(f"[Output] Relic manifest updated: {relic_manifest_path}")

        except Exception as e:
            print(f"[{datetime.datetime.now()}] ERROR: An error occurred during alchemy: {e}")

if __name__ == "__main__":
    alchemist = CodeDustAlchemist()
    alchemist.run_alchemist()
    print("\
To run this alchemist daily, you can schedule it using cron (Linux/macOS) or Task Scheduler (Windows).")
    print("Example cron command: 0 0 * * * python /path/to/code_dust_alchemist.py")