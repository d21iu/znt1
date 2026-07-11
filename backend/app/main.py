from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import app.config  # noqa: F401  加载 .env
from app.config import ai_enabled, base_url, text_model, vision_model
from app.routes.check import router as check_router

APP_ID = "course-20-hydraulic-f01"
APP_VERSION = "1.0.3"

# 前端静态目录（容器内为 /app/frontend，本地开发为仓库根 frontend）
_FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

app = FastAPI(
    title="液压与气压传动实验规范检测",
    description="文本、图片、视频检测均由大模型分析，辅助教师发现实验规范与安全问题",
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(check_router)


def _health_payload():
    return {
        "status": "ok",
        "app_id": APP_ID,
        "version": APP_VERSION,
        "course": "液压与气压传动",
        "detection_mode": "llm_only",
        "ai_enabled": ai_enabled(),
        "llm_base_url": base_url(),
        "text_model": text_model(),
        "vision_model": vision_model(),
        "note": "文本/图片/视频检测均依赖大模型，无规则引擎回退。",
    }


# 交付规范要求的健康检查：GET /health 返回 200，含 status / app_id / version
@app.get("/health")
def health():
    return _health_payload()


# 兼容旧路径
@app.get("/api/health")
def api_health():
    return _health_payload()


# 静态前端挂载到根路径，必须放在所有 API 路由之后，避免覆盖 /api、/health
if _FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_DIR), html=True), name="frontend")
