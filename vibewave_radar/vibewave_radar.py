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
    def __init__(self, history_size: int = 100, trend_threshold: float = 0.05, surge_factor: float = 2.0):
        """
        VibeWave Radar를 초기화합니다. 각 파라미터는 트렌드 감지 로직의 민감도를 조절합니다.
        :param history_size: 트렌드 감지에 사용할 바이브 히스토리의 최대 크기. (이전 100개 비디오)
        :param trend_threshold: '신규' 트렌드로 간주될 태그 빈도의 최소 임계값. (전체 히스토리에서 5% 미만)
        :param surge_factor: 바이브 급증을 감지하기 위한 배수. (과거 평균 대비 2배 이상)
        """
        self.history_size: int = history_size
        self.trend_threshold: float = trend_threshold
        self.surge_factor: float = surge_factor
        self.vibe_history: deque[list[str]] = deque(maxlen=history_size) # 각 비디오의 바이브 태그 목록 저장
        self.global_vibe_counts: defaultdict[str, int] = defaultdict(int) # 전체 기간 동안의 바이브 태그 출현 횟수
        self.detected_trends: list[dict] = [] # 감지된 트렌드 목록
        logging.info("VibeWave Radar 초기화 완료. 히스토리 크기: %d, 트렌드 임계값: %.2f, 급증 배수: %.1f",
                     history_size, trend_threshold, surge_factor)

    def _extract_tags_from_video_data(self, video_data: str) -> list[str]:
        """
        비디오 콘텐츠 텍스트 데이터에서 바이브 태그를 추출하는 시뮬레이션 함수입니다.
        실제 서비스에서는 AI/ML 모델이 이 부분을 대체하여 비디오에서 직접 태그를 추출합니다.
        :param video_data: 쉼표로 구분된 바이브 태그 문자열 (예: "lofi_hiphop, vintage_filter").
        :return: 추출된 바이브 태그 리스트.
        """
        if not video_data: # 비디오 데이터가 비어있으면 태그 없음
            logging.debug("비디오 데이터가 비어있어 추출된 태그가 없습니다.")
            return []
        # 쉼표로 구분된 문자열을 태그 리스트로 변환하고 공백 제거 및 소문자화
        tags = [tag.strip().lower() for tag in video_data.split(',') if tag.strip()]
        logging.debug("태그 추출 완료. 원본: '%s', 추출 태그: %s", video_data, tags)
        return tags

    def scan_video(self, video_id: str, video_data: str):
        """
        단일 비디오를 스캔하여 바이브 태그를 추출하고 실시간 트렌드를 감지합니다.
        :param video_id: 비디오의 고유 ID.
        :param video_data: 비디오 콘텐츠를 나타내는 텍스트 데이터 (시뮬레이션용).
        """
        logging.info("▶️ 비디오 스캔 시작: ID '%s'", video_id)
        try:
            vibe_tags = self._extract_tags_from_video_data(video_data)

            if not vibe_tags:
                logging.info("  -> %s: 감지된 바이브 태그 없음. 스캔 종료.", video_id)
                return

            logging.info("  -> %s: 감지된 태그: %s", video_id, ', '.join(vibe_tags))

            # 현재 비디오의 태그를 히스토리 및 전체 카운트에 반영
            for tag in vibe_tags:
                self.global_vibe_counts[tag] += 1
            self.vibe_history.append(vibe_tags) # 현재 비디오의 모든 태그를 히스토리에 저장
            logging.debug("  -> %s: 히스토리 및 글로벌 카운트 업데이트 완료. 현재 히스토리 크기: %d", video_id, len(self.vibe_history))

            # 업데이트된 히스토리를 기반으로 트렌드 감지 로직 실행
            self._detect_and_report_trends(video_id, vibe_tags)

        except Exception as e:
            logging.error("❌ 비디오 스캔 중 예상치 못한 오류 발생 (%s): %s", video_id, e, exc_info=True)

    def _detect_and_report_trends(self, video_id: str, current_tags: list[str]):
        """
        숏폼 비디오 시장의 바이브 트렌드 (새로운 출현, 급증, 새로운 조합)를 감지하고 보고합니다.
        :param video_id: 현재 분석 중인 비디오의 ID.
        :param current_tags: 현재 비디오에서 감지된 바이브 태그 목록.
        """
        potential_trend_alerts: list[str] = []

        # 충분한 히스토리 데이터가 쌓여야 트렌드 감지 가능
        if len(self.vibe_history) < self.history_size * 0.1: # 최소 10%의 히스토리가 채워져야 감지 시작
            logging.debug("  -> %s: 트렌드 감지를 위한 히스토리 부족 (현재: %d/%d). 감지 생략.", video_id, len(self.vibe_history), self.history_size)
            return

        # 1. 히스토리 내 태그 빈도 계산 (전체 히스토리 내에서 각 태그가 얼마나 자주 나타났는지)
        history_tag_counts: defaultdict[str, int] = defaultdict(int)
        total_history_tags = 0
        for tags_list in self.vibe_history:
            for tag in tags_list:
                history_tag_counts[tag] += 1
                total_history_tags += 1

        # 2. 개별 태그의 새로운 출현 또는 급증 패턴 식별
        for tag in current_tags:
            history_tag_freq = history_tag_counts[tag] / total_history_tags if total_history_tags else 0
            # 완전히 새로운 태그의 등장
            if history_tag_freq == 0: 
                potential_trend_alerts.append(f"'신규 {tag}' 바이브가 등장했습니다! (첫 감지)")
            # 기존에 존재했지만 빈도가 낮았던 태그의 급격한 증가
            elif history_tag_freq < self.trend_threshold and (current_tags.count(tag) / len(current_tags)) > history_tag_freq * self.surge_factor:
                potential_trend_alerts.append(f"'새로운 {tag}' 바이브가 급증하고 있습니다! (현재: {current_tags.count(tag)/len(current_tags):.2f}, 과거 평균: {history_tag_freq:.2f})")
        
        # 3. 바이브 조합 트렌드 (예: 'analog_filter' + 'lofi_hiphop')
        if len(current_tags) >= 2:
            combined_vibe = " + ".join(sorted(current_tags))
            # 현재 비디오의 태그 조합이 히스토리에서 얼마나 자주 나타났는지 확인
            combo_count_in_history = sum(1 for tags_list in self.vibe_history if all(t in tags_list for t in current_tags))
            # 해당 조합이 히스토리에서 거의 나타나지 않다가 지금 등장한 경우
            if combo_count_in_history / len(self.vibe_history) < 0.02 and len(self.vibe_history) > self.history_size * 0.2: # 최소 20% 히스토리 필요, 2% 미만 빈도
                potential_trend_alerts.append(f"새로운 조합 '{combined_vibe}' 바이브웨이브가 감지되었습니다!")

        # 감지된 트렌드가 있을 경우 경고 로그 및 저장
        if potential_trend_alerts:
            alert_message = f"[VibeWave ALERT! - {video_id}] {'. '.join(potential_trend_alerts)}"
            logging.warning("\n%s\n%s\n%s\n", '='*50, alert_message, '='*50)
            self.detected_trends.append({
                "timestamp": datetime.now().isoformat(),
                "video_id": video_id,
                "tags": ", ".join(current_tags),
                "alert": alert_message
            })
        else:
            logging.info("  -> %s: 특이 트렌드 감지 안 됨. (현재 히스토리: %d)", video_id, len(self.vibe_history))

    def save_trends_report(self, filename: str = "vibewave_trends.csv"):
        """
        감지된 모든 트렌드 보고서를 CSV 파일로 저장합니다.
        :param filename: 보고서 파일을 저장할 경로 및 이름.
        """
        if not self.detected_trends:
            logging.info("✔️ 저장할 감지된 트렌드가 없습니다: '%s'", filename)
            return

        file_exists = os.path.exists(filename)
        try:
            with open(filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.detected_trends[0].keys() if self.detected_trends else [])
                if not file_exists:
                    writer.writeheader()
                    logging.info("새로운 트렌드 보고서 파일 '%s'을(를) 생성했습니다.", filename)
                writer.writerows(self.detected_trends)
            logging.info("총 %d개의 트렌드가 '%s'에 성공적으로 저장되었습니다.", len(self.detected_trends), filename)
        except IOError as e:
            logging.error("❌ 트렌드 보고서 파일 저장 중 오류 발생 (%s): %s", filename, e, exc_info=True)
        except Exception as e:
            logging.error("❌ 예상치 못한 오류로 트렌드 보고서 저장 실패: %s", e, exc_info=True)

def main():
    """메인 실행 함수: 인자 파싱, VibeWave Radar 초기화 및 실행 로직을 처리합니다."""
    parser = argparse.ArgumentParser(
        description="VibeWave Radar: AI 기반 숏폼 콘텐츠 바이브 트렌드 예측 시스템.",
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
        if not os.path.isdir(args.input_dir): # 입력 디렉토리 유효성 검사
            logging.error("❌ 오류: 입력 디렉토리 '%s'를 찾을 수 없거나 유효하지 않습니다. 프로그램을 종료합니다.", args.input_dir)
            return
        
        logging.info("\n--- 사용자 지정 데이터 로드 시작 ---")
        logging.info("✅ 지정된 디렉토리 '%s'에서 비디오 데이터를 로드합니다.", args.input_dir)
        
        try:
            video_files = [f for f in os.listdir(args.input_dir) if f.endswith('.txt')] # .txt 파일만 필터링
            if not video_files:
                logging.warning("⚠️ 경고: '%s'에서 .txt 파일을 찾을 수 없습니다. 데모 데이터를 사용합니다.\n", args.input_dir)
                _run_demo(radar)
            else:
                for filename in sorted(video_files): # 파일명 순서대로 처리
                    filepath = os.path.join(args.input_dir, filename)
                    video_id = os.path.splitext(filename)[0]
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            video_data = f.readline().strip()
                        radar.scan_video(video_id, video_data)
                    except IOError as e:
                        logging.error("❌ 파일 읽기 오류 (%s): %s", filepath, e, exc_info=True)
                    except Exception as e:
                        logging.error("❌ 비디오 데이터 처리 중 예상치 못한 오류 발생 (%s): %s", filepath, e, exc_info=True)
        except Exception as e:
            logging.error("❌ 디렉토리 '%s' 처리 중 예상치 못한 오류 발생: %s", args.input_dir, e, exc_info=True)

    else:
        logging.info("\n=== 데모 모드 ===")
        logging.info("입력 디렉토리가 지정되지 않았습니다. 샘플 데이터로 시연합니다.")
        logging.info("💡 팁: 본인 파일을 사용하려면 'python vibewave_radar.py --input_dir ./my_videos' 처럼 실행하세요.\n")
        _run_demo(radar)

    radar.save_trends_report(args.output_file)
    logging.info("\n--- 모든 작업 완료 ---\n")
    logging.info("💡 팁: 이 스크립트를 주기적으로 실행하여 최신 바이브웨이브를 계속 감지하고 보고서를 업데이트하세요.")
    logging.info("  예) Linux/macOS: (crontab -l; echo '0 * * * * python /path/to/vibewave_radar.py --input_dir /path/to/my_videos') | crontab - ")
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
        radar_instance.scan_video(video_id, demo_videos[video_id])
        if (i + 1) % 5 == 0: # 5개 비디오마다 진행 상황 로깅
            logging.info("📊 현재 %d/%d 데모 비디오 처리 완료.", i + 1, len(demo_video_keys))

if __name__ == "__main__":
    main()
