import os
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import ai_enabled, base_url, text_model, vision_model
from app.exceptions import LLMServiceError
from app.models import TextCheckRequest
from app.services.ai_client import call_image_ai, call_text_ai, call_video_ai
from app.services.ai_report import build_ai_report
from app.services.video_frames import extract_frames, save_upload_to_temp

router = APIRouter(prefix="/api/hydraulic-lab", tags=["hydraulic-lab"])

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_llm_ready() -> None:
    if not ai_enabled():
        raise HTTPException(
            status_code=503,
            detail=(
                "大模型未配置。请在 backend/.env 设置 OPENAI_BASE_URL 与模型名，"
                "并启动本地 Qwen（如 ollama serve）。"
            ),
        )


def _llm_http_error(exc: LLMServiceError) -> HTTPException:
    return HTTPException(status_code=503, detail=exc.message)


@router.post("/check-text")
async def check_text(body: TextCheckRequest):
    _ensure_llm_ready()
    if not body.content.strip():
        raise HTTPException(status_code=400, detail="实验报告内容不能为空。")

    try:
        ai_result = await call_text_ai(
            body.content,
            body.grade,
            body.experiment_name,
        )
    except LLMServiceError as exc:
        raise _llm_http_error(exc) from exc

    return build_ai_report(ai_result, suffix="文本检测由大模型完成。")


@router.post("/check-image")
async def check_image(
    image: UploadFile = File(...),
    experiment_type: str = Form("hydraulic"),
    grade: str = Form("2024级本科"),
):
    _ensure_llm_ready()
    data = await image.read()
    if not data:
        raise HTTPException(status_code=400, detail="图片文件为空。")

    suffix = Path(image.filename or "img.jpg").suffix or ".jpg"
    save_path = UPLOAD_DIR / f"img_{os.urandom(4).hex()}{suffix}"
    save_path.write_bytes(data)

    mime = image.content_type or "image/jpeg"
    try:
        ai_result = await call_image_ai(data, mime, experiment_type, grade)
    except LLMServiceError as exc:
        raise _llm_http_error(exc) from exc

    report = build_ai_report(
        ai_result,
        suffix="图片检测由大模型完成，建议教师结合现场复核。",
    )
    report.teacher_review_required = True
    return report


@router.post("/check-video")
async def check_video(
    video: UploadFile = File(...),
    experiment_type: str = Form("hydraulic"),
    frame_interval: float = Form(1.0),
    grade: str = Form("2024级本科"),
):
    _ensure_llm_ready()
    raw = await video.read()
    if not raw:
        raise HTTPException(status_code=400, detail="视频文件为空。")

    suffix = Path(video.filename or "vid.mp4").suffix or ".mp4"
    tmp_path = save_upload_to_temp(raw, suffix)

    try:
        try:
            frames = extract_frames(tmp_path, interval_sec=frame_interval)
        except ImportError as exc:
            raise HTTPException(
                status_code=503,
                detail="视频抽帧需要安装 opencv-python-headless：pip install -r requirements-video.txt",
            ) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        try:
            ai_result = await call_video_ai(frames, experiment_type, frame_interval)
        except LLMServiceError as exc:
            raise _llm_http_error(exc) from exc

        report = build_ai_report(
            ai_result,
            suffix=f"视频检测由大模型完成（共抽取 {len(frames)} 帧）。",
        )
        report.teacher_review_required = True
        return report
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
