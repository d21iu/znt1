import tempfile
from pathlib import Path

try:
    import cv2
except ImportError:
    cv2 = None  # type: ignore[assignment]


def extract_frames(
    video_path: Path,
    interval_sec: float = 1.0,
    max_frames: int = 30,
) -> list[tuple[float, bytes, str]]:
    if cv2 is None:
        raise ImportError(
            "视频抽帧需要 opencv-python-headless，请执行: pip install opencv-python-headless"
        )
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError("无法打开视频文件")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_step = max(1, int(fps * interval_sec))
    frames: list[tuple[float, bytes, str]] = []
    index = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if index % frame_step == 0:
            t = index / fps
            ok, buf = cv2.imencode(".jpg", frame)
            if ok:
                frames.append((t, buf.tobytes(), "image/jpeg"))
            if len(frames) >= max_frames:
                break
        index += 1

    cap.release()
    if not frames:
        raise ValueError("视频中未能抽取有效帧")
    return frames


def save_upload_to_temp(data: bytes, suffix: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(data)
    tmp.close()
    return Path(tmp.name)
