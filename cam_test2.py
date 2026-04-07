import subprocess
import datetime
import os
import time

# RTSP 주소
RTSP_URL = "rtsp://admin:YOUR_PASSWORD@121.139.190.221:8082/video1"

# 저장 경로
SAVE_DIR = r"D:\video"
LOG_FILE = "record_log.txt"
os.makedirs(SAVE_DIR, exist_ok=True)

RECORD_DURATION = 3600  # 1시간 = 3600초

def log_event(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)

def get_save_path():
    now = datetime.datetime.now()
    return os.path.join(SAVE_DIR, now.strftime("recording_%Y%m%d_%H%M%S.avi"))

def run_ffmpeg_loop():
    while True:
        save_path = get_save_path()
        log_event(f"🎬 녹화 시작: {save_path}")

        ffmpeg_cmd = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", RTSP_URL,
            "-t", str(RECORD_DURATION),
            "-c", "copy",
            "-an",
            "-fflags", "+discardcorrupt",
            "-loglevel", "error",
            save_path
        ]

        try:
            subprocess.run(ffmpeg_cmd, check=True)
            log_event(f"녹화 완료: {save_path}")
        except subprocess.CalledProcessError as e:
            log_event(f"FFmpeg 오류 발생: {e}")
        finally:
            log_event("다음 1시간 녹화")

if __name__ == "__main__":
    run_ffmpeg_loop()
