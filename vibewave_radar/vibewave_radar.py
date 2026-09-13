# [실행 환경 방어] 출력을 파일로 저장하거나 자동 실행할 때 한글 윈도우에서
# UnicodeEncodeError로 죽는 것을 막아줍니다. 지우지 마세요!
import sys as _sys
for _s in (_sys.stdout, _sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import os
import csv
from datetime import datetime
import random
from collections import defaultdict, deque
import logging

# 로깅 설정: 상세한 진행 상황 및 알림을 출력합니다.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VibeWaveRadar:
    """
    VibeWave Radar는 숏폼 콘텐츠의 바이브(Vibe) 트렌드를 실시간으로 감지하고 예측합니다.
    주어진 비디오 데이터에서 태그를 추출하여 히스토리를 분석하고,
    새로운 바이브의 출현, 급증, 조합 트렌드를 식별합니다.
    """
    def __init__(self, history_size: int = 100, trend_threshold: float = 0.6, surge_factor: float = 2.0):
        """
        VibeWave Radar를 초기화합니다.
        :param history_size: 트렌드 감지에 사용할 바이브 히스토리의 최대 크기.
        :param trend_threshold: 트렌드로 간주될 태그 빈도의 최소 임계값.
        :param surge_factor: 바이브 급증을 감지하기 위한 배수.
        """
        self.history_size: int = history_size
        self.trend_threshold: float = trend_threshold
        self.surge_factor: float = surge_factor
        self.vibe_history: deque[list[str]] = deque(maxlen=history_size) # 각 비디오의 바이브 태그 목록을 저장
        self.global_vibe_counts: defaultdict[str, int] = defaultdict(int) # 전체 기간 동안의 바이브 태그 출현 횟수
        self.detected_trends: list[dict] = [] # 감지된 트렌드 목록
        logging.info("VibeWave Radar 초기화 완료. 히스토리 크기: %d", history_size)

    def _simulate_video_analysis(self, video_data: str) -> list[str]:
        """
        실제 비디오 분석 대신 텍스트 데이터에서 바이브 태그를 추출하는 시뮬레이션입니다.
        실제 서비스에서는 비디오 콘텐츠 분석 AI/ML 모델이 이 부분을 대체합니다.
        :param video_data: 쉼표로 구분된 바이브 태그 문자열. (예: "lofi_hiphop, vintage_filter")
        :return: 추출된 바이브 태그 리스트.
        """
        if not video_data:
            logging.debug("비디오 데이터가 비어있습니다. 태그 없음.")
            return []
        # 쉼표로 구분된 문자열을 태그 리스트로 변환하고 공백 제거 및 소문자화
        tags = [tag.strip().lower() for tag in video_data.split(',') if tag.strip()]
        logging.debug("시뮬레이션 분석 완료. 원본: '%s', 추출 태그: %s", video_data, tags)
        return tags

    def scan_for_vibes(self, video_id: str, video_data: str):
        """
        단일 비디오를 스캔하여 바이브 태그를 추출하고 트렌드를 감지합니다.
        :param video_id: 비디오의 고유 ID.
        :param video_data: 비디오 콘텐츠를 나타내는 텍스트 데이터.
        """
        logging.info("▶️ 비디오 스캔 시작: %s", video_id)
        try:
            vibe_tags = self._simulate_video_analysis(video_data)

            if not vibe_tags:
                logging.info("  -> %s: 감지된 바이브 태그 없음.", video_id)
                return

            logging.info("  -> %s: 감지된 태그: %s", video_id, ', '.join(vibe_tags))

            # 현재 비디오의 태그를 히스토리 및 전체 카운트에 반영
            for tag in vibe_tags:
                self.global_vibe_counts[tag] += 1

            self.vibe_history.append(vibe_tags) # 현재 비디오의 모든 태그를 히스토리에 저장
            logging.debug("  -> %s: 히스토리 및 글로벌 카운트 업데이트 완료. 현재 히스토리 크기: %d", video_id, len(self.vibe_history))

            # 트렌드 감지 로직 실행
            self._detect_trends(video_id, vibe_tags)
        except Exception as e:
            logging.error("비디오 스캔 중 오류 발생 (%s): %s", video_id, e)

    def _detect_trends(self, video_id: str, current_tags: list[str]):
        """
        숏폼 비디오 시장의 바이브 트렌드를 감지하는 핵심 로직입니다.
        새로운 태그의 출현, 기존 태그의 급증, 그리고 새로운 조합 트렌드를 식별합니다.
        :param video_id: 현재 분석 중인 비디오의 ID.
        :param current_tags: 현재 비디오에서 감지된 바이브 태그 목록.
        """
        potential_trends: list[str] = []

        if not self.vibe_history or len(self.vibe_history) < 5: # 충분한 히스토리 없으면 감지 어려움
            logging.debug("  -> %s: 트렌드 감지를 위한 히스토리 부족 (현재: %d)", video_id, len(self.vibe_history))
            return

        history_tag_counts: defaultdict[str, int] = defaultdict(int)
        for tags_list in self.vibe_history:
            for tag in tags_list:
                history_tag_counts[tag] += 1

        # 1. 개별 태그의 새로운 출현 또는 급증 패턴 식별
        for tag in current_tags:
            current_freq = current_tags.count(tag) / len(current_tags) if current_tags else 0
            history_freq = history_tag_counts[tag] / len(self.vibe_history) if self.vibe_history else 0

            if history_freq < self.trend_threshold and current_freq > history_freq * self.surge_factor and history_freq > 0:
                potential_trends.append(f"'새로운 {tag}' 바이브가 급증하고 있습니다! (현재: {current_freq:.2f}, 과거 평균: {history_freq:.2f})")
            elif history_freq == 0 and current_freq > 0: # 히스토리에 전혀 없던 새로운 태그
                potential_trends.append(f"'신규 {tag}' 바이브가 등장했습니다! (첫 감지)")
        
        # 2. 바이브 조합 트렌드 (예: 'analog_filter' + 'lofi_hiphop')
        if len(current_tags) >= 2:
            combined_vibe = " + ".join(sorted(current_tags))
            # 이 조합이 최근 히스토리에 얼마나 자주 나타났는지 확인
            combo_count_in_history = sum(1 for tags_list in self.vibe_history if all(t in tags_list for t in current_tags))
            # 히스토리 대비 낮은 빈도였던 조합이 지금 나타난 경우
            if combo_count_in_history / len(self.vibe_history) < 0.1 and len(self.vibe_history) > 10: 
                potential_trends.append(f"새로운 조합 '{combined_vibe}' 바이브웨이브가 감지되었습니다!")

        if potential_trends:
            alert_message = f"[VibeWave ALERT! - {video_id}] {'. '.join(potential_trends)}"
            logging.warning("\n%s\n%s\n%s\n", '='*50, alert_message, '='*50)
            self.detected_trends.append({
                "timestamp": datetime.now().isoformat(),
                "video_id": video_id,
                "tags": ", ".join(current_tags),
                "alert": alert_message
            })
        else:
            logging.info("  -> %s: 특이 트렌드 감지 안 됨.", video_id)

    def save_trends_report(self, filename: str = "vibewave_trends.csv"):
        """
        감지된 모든 트렌드 보고서를 CSV 파일로 저장합니다.
        :param filename: 보고서 파일을 저장할 경로 및 이름.
        """
        if not self.detected_trends:
            logging.info("저장할 감지된 트렌드가 없습니다: %s", filename)
            return

        file_exists = os.path.exists(filename)
        try:
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.detected_trends[0].keys())
                if not file_exists:
                    writer.writeheader()
                    logging.info("새로운 트렌드 보고서 파일 생성: %s", filename)
                writer.writerows(self.detected_trends)
            logging.info("총 %d개의 트렌드가 '%s'에 성공적으로 저장되었습니다.", len(self.detected_trends), filename)
        except IOError as e:
            logging.error("트렌드 보고서 파일 저장 중 오류 발생 (%s): %s", filename, e)
        except Exception as e:
            logging.error("예상치 못한 오류로 트렌드 보고서 저장 실패: %s", e)

def main():
    """메인 실행 함수: 인자 파싱, VibeWave Radar 초기화 및 실행 로직을 처리합니다."""
    parser = argparse.ArgumentParser(
        description="VibeWave Radar: AI-driven short-form content trend forecasting.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        help="비디오 데이터 파일들이 있는 디렉토리 경로 (각 파일은 쉼표로 구분된 태그 한 줄)."
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="vibewave_trends.csv",
        help="트렌드 보고서를 저장할 CSV 파일명 (기본값: vibewave_trends.csv)."
    )
    args = parser.parse_args()

    radar = VibeWaveRadar()

    if args.input_dir:
        if not os.path.isdir(args.input_dir):
            logging.error("오류: 입력 디렉토리 '%s'를 찾을 수 없거나 유효하지 않습니다.", args.input_dir)
            return
        
        logging.info("\n--- 사용자 지정 데이터 로드 시작 ---")
        logging.info("지정된 디렉토리 '%s'에서 비디오 데이터를 로드합니다.", args.input_dir)
        
        try:
            video_files = [f for f in os.listdir(args.input_dir) if f.endswith('.txt')]
            if not video_files:
                logging.warning("경고: '%s'에서 .txt 파일을 찾을 수 없습니다. 데모 데이터를 사용합니다.", args.input_dir)
                _run_demo(radar)
                return

            for filename in sorted(video_files):
                filepath = os.path.join(args.input_dir, filename)
                video_id = os.path.splitext(filename)[0]
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        video_data = f.readline().strip()
                    radar.scan_for_vibes(video_id, video_data)
                except IOError as e:
                    logging.error("파일 읽기 오류 (%s): %s", filepath, e)
                except Exception as e:
                    logging.error("비디오 데이터 처리 중 오류 발생 (%s): %s", filepath, e)
        except Exception as e:
            logging.error("디렉토리 처리 중 예상치 못한 오류 발생: %s", e)

    else:
        logging.info("\n=== 데모 모드 ===")
        logging.info("입력 디렉토리가 지정되지 않았습니다. 샘플 데이터로 시연합니다.")
        logging.info("본인 파일을 쓰려면 'python vibewave_radar.py --input_dir ./my_videos' 처럼 실행하세요.\n")
        _run_demo(radar)

    radar.save_trends_report(args.output_file)
    logging.info("\n--- 작업 완료 ---\n")
    logging.info("💡 팁: 이 스크립트를 주기적으로 실행하여 최신 바이브웨이브를 계속 감지하고 보고서를 업데이트하세요.")
    logging.info("  예) Linux/macOS: (crontab -l; echo '0 * * * * python /path/to/vibewave_radar.py --input_dir /path/to/my_videos') | crontab -")
    logging.info("  예) Windows: 작업 스케줄러를 이용해 매 시간마다 실행하도록 설정하세요.\n")

def _run_demo(radar_instance: VibeWaveRadar):
    """데모 모드 실행을 위한 샘플 비디오 데이터를 제공합니다."""
    demo_videos: dict[str, str] = {
        "video_001": "lofi_hiphop, vintage_filter, warm_tones, chill_vibe",
        "video_002": "synthwave, neon_lights, retro_80s, energetic",
        "video_003": "acoustic_folk, natural_light, cozy_ambiance",
        "video_004": "lofi_hiphop, vintage_filter, warm_tones, study_focus",
        "video_005": "dark_academia, classical_music, moody_tones",
        "video_006": "lofi_hiphop, street_art, vibrant_colors, urban_explore",
        "video_007": "synthwave, neon_lights, futuristic, cyberpunk",
        "video_008": "lofi_hiphop, vintage_filter, warm_tones, chill_vibe",
        "video_009": "lofi_hiphop, vintage_filter, warm_tones, study_focus",
        "video_010": "synthwave, neon_lights, retro_80s, energetic",
        "video_011": "acoustic_folk, cafe_vibes, storytelling",
        "video_012": "lofi_hiphop, street_art, vibrant_colors, urban_explore",
        "video_013": "dreamy_pop, pastel_colors, soft_focus", # 완전히 새로운 바이브
        "video_014": "lofi_hiphop, vintage_filter, warm_tones, chill_vibe",
        "video_015": "dreamy_pop, pastel_colors, soft_focus, ethereal_sound",
        "video_016": "tech_reviews, gadget_unboxing, modern_minimalism", # 신규 태그 조합
        "video_017": "lofi_hiphop, vintage_filter, warm_tones, chill_vibe"
    }

    demo_video_keys = list(demo_videos.keys())
    random.shuffle(demo_video_keys) # 데모를 위해 순서를 섞어서 비디오를 처리

    logging.info("데모 비디오 스캔을 시작합니다. 총 %d개 비디오.", len(demo_video_keys))
    for i, video_id in enumerate(demo_video_keys):
        radar_instance.scan_for_vibes(video_id, demo_videos[video_id])
        if (i + 1) % 5 == 0: # 5개 비디오마다 진행 상황 로깅
            logging.info("현재 %d/%d 데모 비디오 처리 완료.", i + 1, len(demo_video_keys))

if __name__ == "__main__":
    main()