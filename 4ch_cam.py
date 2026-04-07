import cv2
import numpy as np

# 4대 카메라 RTSP 주소를 차례로 넣어주세요.
RTSP_URLS = [
    "rtsp://admin:YOUR_PASSWORD@192.168.0.235:554/video1",  # CH1
    "rtsp://admin:YOUR_PASSWORD@192.168.0.245:554/video1",  # CH2
    "rtsp://admin:YOUR_PASSWORD@192.168.0.230:554/video1",  # CH3
    "rtsp://admin:YOUR_PASSWORD@192.168.0.240:554/video1",  # CH4
]

WINDOW_NAME = "4-Split (Multi-Source)"
TARGET_WIDTH = 1280   # 전체 모자이크 가로
TARGET_HEIGHT = 720   # 전체 모자이크 세로
SHOW_LABELS = True

def put_label(img, text):
    cv2.rectangle(img, (0, 0), (140, 28), (0, 0, 0), -1)
    cv2.putText(img, text, (8, 20), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 1, cv2.LINE_AA)

def main():
    # 4개 캡처 열기
    caps = [cv2.VideoCapture(url, cv2.CAP_FFMPEG) for url in RTSP_URLS]
    for cap in caps:
        # 지연 줄이기 위해 버퍼 크기 최소화 시도(플랫폼에 따라 무시될 수 있음)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # 각 타일 크기
    tile_w = TARGET_WIDTH // 2
    tile_h = TARGET_HEIGHT // 2

    def read_or_placeholder(cap, label_text):
        ok, frame = cap.read()
        if ok and frame is not None:
            tile = cv2.resize(frame, (tile_w, tile_h), interpolation=cv2.INTER_AREA)
        else:
            # 실패 시 검은 타일
            tile = np.zeros((tile_h, tile_w, 3), dtype=np.uint8)
            cv2.putText(tile, "N/A", (tile_w//2 - 35, tile_h//2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2, cv2.LINE_AA)
        if SHOW_LABELS:
            put_label(tile, label_text)
        return tile

    if not any(cap.isOpened() for cap in caps):
        print("4개 카메라 모두 열기에 실패했습니다.")
        for cap in caps:
            cap.release()
        return

    while True:
        # CH1, CH2, CH3, CH4 순서로 읽기
        tl = read_or_placeholder(caps[0], "CH1")
        tr = read_or_placeholder(caps[1], "CH2")
        bl = read_or_placeholder(caps[2], "CH3")
        br = read_or_placeholder(caps[3], "CH4")

        # 2x2 모자이크 결합
        top = np.hstack((tl, tr))
        bottom = np.hstack((bl, br))
        mosaic = np.vstack((top, bottom))

        cv2.imshow(WINDOW_NAME, mosaic)

        key = cv2.waitKey(1) & 0xFF
        if key in (27, ord('q'), ord('Q')):  # ESC 또는 Q 종료
            break

    # 리소스 해제
    for cap in caps:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
