# 液压与气压传动 · 特色功能 f01
# app_id: course-20-hydraulic-f01
FROM python:3.11-slim

# opencv-python-headless 运行所需的最小系统库
RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先装依赖，利用层缓存
COPY backend/requirements.txt backend/requirements-video.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt \
    && pip install --no-cache-dir -r backend/requirements-video.txt

# 拷贝后端代码与前端静态页
COPY backend/app ./backend/app
COPY frontend ./frontend

ENV PYTHONUNBUFFERED=1 \
    AI_ENABLED=true

# 容器端口以 catalog.yaml 为准：课20 为 8000
EXPOSE 8000

WORKDIR /app/backend
# 监听 0.0.0.0:8000（catalog.yaml 课20 container 端口）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
