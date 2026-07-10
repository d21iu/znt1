import base64
import json
import logging
import re
from pathlib import Path

import httpx

from app.config import api_key, base_url, request_timeout, text_model, vision_model
from app.exceptions import LLMServiceError

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).resolve().parents[3] / "prompts"


def _load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.md"
    return path.read_text(encoding="utf-8")


def _render(template: str, **kwargs: str) -> str:
    result = template
    for key, value in kwargs.items():
        result = result.replace(f"{{{{{key}}}}}", value)
    return result


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
        raise LLMServiceError("大模型返回内容不是有效 JSON，请检查提示词或换用指令能力更强的模型。")


async def call_text_ai(
    content: str,
    grade: str,
    experiment_name: str,
) -> dict:
    template = _load_prompt("text")
    prompt = _render(
        template,
        content=content,
        grade=grade,
        experiment_name=experiment_name or "未指定",
    )
    return await _chat_completion(prompt, kind="文本")


async def call_image_ai(
    image_bytes: bytes,
    mime: str,
    experiment_type: str,
    grade: str,
) -> dict:
    template = _load_prompt("image")
    text_part = _render(
        template,
        experiment_type=experiment_type,
        grade=grade,
    )
    b64 = base64.standard_b64encode(image_bytes).decode("ascii")
    data_url = f"data:{mime};base64,{b64}"
    return await _vision_completion(text_part, data_url, kind="图片")


async def call_video_ai(
    frames: list[tuple[float, bytes, str]],
    experiment_type: str,
    frame_interval: float,
) -> dict:
    template = _load_prompt("video")
    desc = "\n".join(f"{t:.1f}s | 实验操作画面" for t, _, _ in frames[:12])
    text_part = _render(
        template,
        experiment_type=experiment_type,
        frame_interval=str(frame_interval),
        frames_description=desc,
    )

    image_urls = []
    for t, data, mime in frames[:8]:
        b64 = base64.standard_b64encode(data).decode("ascii")
        image_urls.append((t, f"data:{mime};base64,{b64}"))

    return await _vision_multi(text_part, image_urls, kind="视频")


async def _chat_completion(prompt: str, kind: str = "") -> dict:
    try:
        payload = {
            "model": text_model(),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        data = await _post_openai("/chat/completions", payload)
        content = data["choices"][0]["message"]["content"]
        return _extract_json(content)
    except LLMServiceError:
        raise
    except Exception as exc:
        logger.exception("%s大模型调用失败", kind)
        raise LLMServiceError(
            f"{kind}检测失败：{exc}。请确认 Ollama/vLLM 已启动，且 .env 中模型名称正确。"
        ) from exc


async def _vision_completion(text: str, image_url: str, kind: str = "") -> dict:
    try:
        payload = {
            "model": vision_model(),
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            "temperature": 0.2,
        }
        data = await _post_openai("/chat/completions", payload)
        content = data["choices"][0]["message"]["content"]
        return _extract_json(content)
    except LLMServiceError:
        raise
    except Exception as exc:
        logger.exception("%s视觉大模型调用失败", kind)
        raise LLMServiceError(
            f"{kind}检测失败：{exc}。请安装并选用支持视觉的 Qwen 模型（如 qwen2.5vl:7b）。"
        ) from exc


async def _vision_multi(text: str, images: list[tuple[float, str]], kind: str = "") -> dict:
    try:
        parts: list[dict] = [{"type": "text", "text": text}]
        for t, url in images:
            parts.append({"type": "text", "text": f"时间点 {t:.1f} 秒："})
            parts.append({"type": "image_url", "image_url": {"url": url}})

        payload = {
            "model": vision_model(),
            "messages": [{"role": "user", "content": parts}],
            "temperature": 0.2,
        }
        data = await _post_openai("/chat/completions", payload)
        content = data["choices"][0]["message"]["content"]
        return _extract_json(content)
    except LLMServiceError:
        raise
    except Exception as exc:
        logger.exception("%s视觉大模型调用失败", kind)
        raise LLMServiceError(
            f"{kind}检测失败：{exc}。请确认视觉模型可用（qwen2.5vl 等）。"
        ) from exc


async def _post_openai(path: str, payload: dict) -> dict:
    url = f"{base_url()}{path}"
    headers = {"Authorization": f"Bearer {api_key()}"}
    try:
        async with httpx.AsyncClient(timeout=request_timeout()) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()
    except httpx.ConnectError as exc:
        raise LLMServiceError(
            f"无法连接大模型服务 {base_url()}，请先启动 Ollama 或 vLLM。"
        ) from exc
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text[:200] if exc.response else str(exc)
        raise LLMServiceError(f"大模型接口错误 {exc.response.status_code}：{detail}") from exc
