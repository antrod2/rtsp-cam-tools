# rtsp-cam-tools

RTSP 카메라 스트림 관련 유틸리티 모음 (OpenCV / FFmpeg 기반)

---

## 파일 구성

| 파일 | 설명 |
|------|------|
| `4ch_cam.py` | 4채널 RTSP 카메라 2x2 분할 모니터링 |
| `cam_record_test.py` | RTSP 스트림 녹화 + 끊김/검은화면 감지 및 자동 재연결 |
| `cam_test2.py` | FFmpeg 기반 RTSP 1시간 단위 자동 분할 녹화 |

---

## 파일별 분석

### 4ch_cam.py — 4채널 분할 모니터링

4대의 RTSP 카메라를 동시에 2x2 그리드로 화면에 표시합니다.

**주요 동작:**
- `cv2.VideoCapture`로 4개 RTSP 스트림을 동시에 열기
- 각 프레임을 타일 크기(640x360)로 리사이즈 후 `np.hstack/vstack`으로 2x2 모자이크 합성
- 연결 실패 시 검은 화면 + "N/A" 텍스트로 대체 (전체 앱 중단 없음)
- 각 채널 좌상단에 CH1~CH4 라벨 표시
- ESC 또는 Q 키로 종료

**설정값:**
```python
TARGET_WIDTH = 1280   # 전체 화면 가로
TARGET_HEIGHT = 720   # 전체 화면 세로
SHOW_LABELS = True    # 채널 라벨 표시 여부
```

---

### cam_record_test.py — 녹화 + 끊김 감지 자동 재연결

RTSP 스트림을 MP4로 녹화하면서 끊김과 검은 화면을 감지해 자동으로 재연결합니다.

**주요 동작:**
- 연속 프레임 수신 실패 2회 시 자동 재연결
- 픽셀 평균 밝기 10 이하이면 검은 화면으로 판정
- 검은 화면이 약 2분(30fps 기준 60프레임) 지속되면 경고 로그 기록
- 재연결마다 새 MP4 파일 생성 (`record_YYYYMMDD_HHMMSS.mp4`)
- 모든 이벤트는 `rtsp_disconnect_log.txt`에 타임스탬프와 함께 기록

**설정값:**
```python
MAX_FAIL_COUNT = 2        # 연속 실패 허용 횟수
MAX_BLACK_FRAMES = 60     # 검은 화면 허용 프레임 수 (약 2분)
```

---

### cam_test2.py — FFmpeg 1시간 단위 분할 녹화

FFmpeg를 subprocess로 호출해 RTSP 스트림을 1시간 단위로 분할 녹화합니다.

**주요 동작:**
- FFmpeg를 직접 호출하므로 재인코딩 없이 스트림을 그대로 복사 (`-c copy`)
- 1시간(`3600초`) 단위로 파일 분할, 자동으로 다음 녹화 시작
- 오디오 제외 (`-an`), 손상된 패킷 무시 (`-fflags +discardcorrupt`)
- RTSP 전송은 TCP 사용 (`-rtsp_transport tcp`)
- 저장 경로: `D:\video\recording_YYYYMMDD_HHMMSS.avi`
- 로그: `record_log.txt`

---

## 의존성

```bash
pip install opencv-python numpy
```

FFmpeg는 시스템에 별도 설치 필요 (`cam_test2.py` 사용 시)

---

## 설정 방법

각 파일의 `RTSP_URL` / `RTSP_URLS` 변수에 실제 카메라 주소를 입력하세요:

```python
# 4ch_cam.py
RTSP_URLS = [
    "rtsp://admin:YOUR_PASSWORD@카메라IP:포트/video1",  # CH1
    ...
]

# cam_record_test.py / cam_test2.py
RTSP_URL = "rtsp://admin:YOUR_PASSWORD@카메라IP:포트/video1"
```

> **주의:** RTSP URL에 비밀번호가 포함되므로 코드를 공유하거나 커밋할 때 반드시 마스킹하세요.
