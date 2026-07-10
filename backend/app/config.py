"""本地 Qwen 等 OpenAI 兼容接口配置。"""

import os
from pathlib import Path

from dotenv import load_dotenv

_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(_ENV_PATH)


def _flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if raw in ("1", "true", "yes", "on"):
        return True
    if raw in ("0", "false", "no", "off"):
        return False
    return default


def base_url() -> str:
    return (
        os.getenv("OPENAI_BASE_URL")
        or os.getenv("QWEN_BASE_URL")
        or "http://127.0.0.1:11434/v1"
    ).rstrip("/")


def api_key() -> str:
    return os.getenv("OPENAI_API_KEY") or os.getenv("QWEN_API_KEY") or "ollama"


def text_model() -> str:
    return (
        os.getenv("OPENAI_MODEL")
        or os.getenv("QWEN_MODEL")
        or "qwen2.5:7b"
    )


def vision_model() -> str:
    return (
        os.getenv("OPENAI_VISION_MODEL")
        or os.getenv("QWEN_VISION_MODEL")
        or os.getenv("OPENAI_MODEL")
        or os.getenv("QWEN_MODEL")
        or "qwen2.5vl:7b"
    )


def request_timeout() -> float:
    return float(os.getenv("AI_TIMEOUT", "180"))


def ai_enabled() -> bool:
    """检测接口是否允许调用大模型（关闭后所有检测返回 503）。"""
    if os.getenv("AI_ENABLED", "").strip().lower() in ("0", "false", "no", "off"):
        return False
    if _flag("AI_ENABLED", default=True):
        return True
    if os.getenv("OPENAI_API_KEY") or os.getenv("QWEN_API_KEY"):
        return True
    url = base_url()
    return "127.0.0.1" in url or "localhost" in url
