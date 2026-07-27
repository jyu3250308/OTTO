import subprocess
import os
import random
import datetime
import json

# Configuration
OUTPUT_DIR = "cosmic_noise_cartridges"
AUDIO_DURATION_SEC = 10 # seconds
FFMPEG_PATH = "ffmpeg" # Assumes ffmpeg is in PATH, or provide full path

def check_ffmpeg_installed():
    """
    Checks if FFmpeg is installed and accessible in the system's PATH.
    """
    try:
        subprocess.run([FFMPEG_PATH, "-version"], check=True, capture_output=True)
        print("✅ FFmpeg is installed and accessible.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found or not callable. Please install FFmpeg and ensure it's in your PATH.")
        print("   Download from: https://ffmpeg.org/download.html")
        return False

def get_mock_astronomical_data():
    """
    Simulates fetching real-time astronomical/environmental data.
    In a real scenario, this would use APIs (e.g., NASA, USGS) or sensors.
    Values are scaled 0-10 for easy mapping to audio parameters.
    """
    print("📡 Simulating real-time cosmic and environmental data...")
    data = {
        "solar_wind_activity": random.uniform(0.1, 10.0), # e.g., solar flux index
        "seismic_tremor_intensity": random.uniform(0.1, 10.0), # e.g., local seismic activity
        "ambient_noise_level": random.uniform(0.0, 100.0) # e.g., dB level, scaled for a percentage influence
    }
    print(f"   Generated Data: {data}")
    return data

def generate_ffmpeg_command(data, output_filepath, duration):
    """
    Constructs an FFmpeg command based on the simulated data to create unique audio.
    Maps data values to audio filter parameters for a 'retro cassette' noise profile.
    """
    solar_wind = data["solar_wind_activity"]
    seismic_tremor = data["seismic_tremor_intensity"]
    ambient_noise_percent = data["ambient_noise_level"] / 100.0 # Normalized 0-1

    # --- Map data to FFmpeg audio filter parameters ---
    # Base noise amplitude (louder with more ambient noise)
    base_noise_amp = 0.3 + (ambient_noise_percent * 0.7) # 0.3 to 1.0

    # Low-pass filter cutoff (higher solar wind -> higher cutoff, allowing more high frequencies)
    lp_cutoff = 1000 + (solar_wind * 200) # 1kHz to 3kHz

    # High-pass filter cutoff (higher seismic tremor -> lower cutoff, allowing more low frequencies/rumble)
    hp_cutoff = 50 + (seismic_tremor * 10) # 50Hz to 150Hz

    # Compressor for tape saturation/crunch (more solar wind -> more compression)
    comp_ratio = 4 + (solar_wind / 10.0 * 6) # 4:1 to 10:1
    comp_makeup = 2 + (solar_wind / 10.0 * 3) # 2dB to 5dB

    # Chorus/Flanger for 'wow and flutter' (tape speed variations, more with seismic tremor)
    chorus_depth = 0.5 + (seismic_tremor / 10.0 * 0.5) # 0.5 to 1.0

    # Final output volume (overall louder with more ambient noise)
    output_volume = 0.5 + (ambient_noise_percent * 0.5) # 0.5 to 1.0

    # Low drone frequency from seismic tremor (40Hz to 140Hz rumble)
    drone_freq = 40 + (seismic_tremor * 10)

    # Two lavfi audio sources: pink noise (the 'cosmic static') + a low sine drone (the 'engine hum').
    # NOTE: 'noise' is a VIDEO-only filter in FFmpeg — for audio we must use the 'anoisesrc' source.
    noise_src = f"anoisesrc=r=44100:color=pink:amplitude={base_noise_amp:.3f}:duration={duration}"
    drone_src = f"sine=frequency={drone_freq:.1f}:sample_rate=44100:duration={duration}"

    # Audio-only filter chain: mix the two sources, then sculpt with the data-driven parameters.
    filter_complex = (
        f"[1:a]volume=0.35[drone];"
        f"[0:a][drone]amix=inputs=2:duration=first:normalize=0,"
        f"highpass=f={hp_cutoff:.1f},"
        f"lowpass=f={lp_cutoff:.1f},"
        f"acompressor=ratio={comp_ratio:.2f}:attack=20:release=1000:makeup={comp_makeup:.2f},"  # Tape saturation
        f"chorus=0.6:{chorus_depth:.2f}:50|60|40:0.4|0.3|0.3:0.25|0.4|0.3:2|2|2,"  # Wow & Flutter
        f"volume={output_volume:.3f}[out]"
    )

    command = [
        FFMPEG_PATH,
        "-y",                       # Overwrite output files without asking
        "-f", "lavfi", "-i", noise_src,
        "-f", "lavfi", "-i", drone_src,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-ac", "2",                 # Stereo output
        "-t", str(duration),        # Audio duration
        "-c:a", "libmp3lame",       # Audio codec for MP3
        "-q:a", "2",                # VBR quality 2 (good quality for MP3)
        output_filepath
    ]
    print(f"   Generated FFmpeg Command: {' '.join(command)}")
    return command

def main():
    """
    Main function to orchestrate the CosmicNoise Cartridge project.
    """
    if not check_ffmpeg_installed():
        return

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"📁 Output directory '{OUTPUT_DIR}' ensured.")

    # 1. Get simulated real-time data
    cosmic_data = get_mock_astronomical_data()

    # 2. Generate unique filename based on timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"cosmic_noise_cartridge_{timestamp}.mp3"
    output_filepath = os.path.join(OUTPUT_DIR, output_filename)

    # 3. Construct FFmpeg command based on data
    ffmpeg_command = generate_ffmpeg_command(cosmic_data, output_filepath, AUDIO_DURATION_SEC)

    # 4. Execute FFmpeg command to generate audio clip
    print(f"✨ Generating unique audio clip: '{output_filepath}'...")
    try:
        # Run FFmpeg, capture output for debugging but don't print unless error
        subprocess.run(ffmpeg_command, check=True, capture_output=True)
        print(f"✅ Audio clip created successfully!")
        print(f"   Your unique data symphony is ready for a special listening experience.")
        print(f"   File saved to: {os.path.abspath(output_filepath)}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate audio clip.")
        print(f"   Error Code: {e.returncode}")
        print(f"   STDERR: {e.stderr.decode(errors='replace').strip()[-600:]}")
        raise SystemExit(1)  # Fail loudly — a broken run must not look like a success
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        raise SystemExit(1)

    print("\n--- CosmicNoise Cartridge Workflow Complete ---")
    print("To generate new, unique clips daily, consider scheduling this script (e.g., with cron or Task Scheduler).")

if __name__ == "__main__":
    main()
