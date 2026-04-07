import cv2
import time
import numpy as np
from datetime import datetime

# RTSP 주소
RTSP_URL = "rtsp://admin:YOUR_PASSWORD@192.168.0.180:443/video1"

# 로그 파일
LOG_FILE = "rtsp_disconnect_log.txt"

# 끊김/검은 화면 감지 기준
MAX_FAIL_COUNT = 2
MAX_BLACK_FRAMES = 30 * 2  # 약 2분 (30fps 기준)

def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def is_black_frame(frame, threshold=10):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return np.mean(gray) < threshold

def connect_to_stream():
    cap = cv2.VideoCapture(RTSP_URL)
    if cap.isOpened():
        log_event("RTSP 연결 성공")
        return cap
    else:
        log_event("RTSP 연결 실패")
        return None

def test_rtsp_stream():
    while True:
        cap = connect_to_stream()
        if cap is None:
            time.sleep(5)
            continue

        # 프레임 설정
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0 or fps is None or np.isnan(fps):
            fps = 30  # 기본값

        # 비디오 저장 (MP4, H.264)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 혹은 'avc1' 또는 'H264' 사용 가능
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = cv2.VideoWriter(f"record_{timestamp}.mp4", fourcc, fps, (width, height))

        fail_count = 0
        black_frame_count = 0

        log_event("프레임 수신 및 MP4 녹화 시작")

        while True:
            ret, frame = cap.read()

            if not ret:
                fail_count += 1
                log_event(f"프레임 수신 실패 ({fail_count})")

                if fail_count >= MAX_FAIL_COUNT:
                    log_event("연속 프레임 수신 실패. 재연결 시도.")
                    break

                time.sleep(0.2)
                continue

            fail_count = 0

            if is_black_frame(frame):
                black_frame_count += 1
                log_event(f"검은 화면 감지 ({black_frame_count} 프레임)")
            else:
                black_frame_count = 0

            if black_frame_count >= MAX_BLACK_FRAMES:
                log_event("지속적인 검은 화면 감지됨 (약 2분간).")
                black_frame_count = 0

            out.write(frame)
            time.sleep(1 / fps)

        cap.release()
        out.release()
        log_event("녹화 종료. 재연결 대기 중...")
        time.sleep(5)

if __name__ == "__main__":
    test_rtsp_stream()
