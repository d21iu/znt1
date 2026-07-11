# 液压与气压传动 · 实验规范检测（课程 AI 工具）

面向中国农业大学工学院《液压与气压传动》课程的前后端分离原型：文本报告检测、图片上传检测、视频抽帧检测，统一返回 JSON 检测报告。

## 交付信息（神农百晓特色功能）

| 项目 | 内容 |
|------|------|
| 课序号 | 20 |
| app_id | `course-20-hydraulic-f01` |
| 版本 | 1.0.0 |
| host 端口 | 18100 |
| 容器端口 | 8080 |
| 镜像 | `baixiao-tese-deploy.shennong.cc/yuketang/course-20-hydraulic-f01:1.0.0` |

设计说明见 [APP_SPEC.md](APP_SPEC.md)，manifest 草稿见 [manifest.draft.yaml](manifest.draft.yaml)。

## 本地开发（不用容器）

```powershell
cd hydraulic-lab\backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前后端已同源：直接浏览器打开 `http://127.0.0.1:8000/` 即为完整页面，前端「API 地址」留空即用当前站点。

## 容器构建与自测（交付用）

```bash
# 在仓库根目录（含 Dockerfile）
docker build -t course-20-hydraulic-f01:1.0.0 .

# host 端口 18100 → 容器 8080
docker run --rm -p 18100:8080 --env-file backend/.env.example \
  course-20-hydraulic-f01:1.0.0

# 自测：必须 HTTP 200，body 含 status / app_id / version
curl http://127.0.0.1:18100/health
# 浏览器打开 http://127.0.0.1:18100/ 确认首页不白屏
```

## 推送与提 PR（自测通过后）

```bash
docker tag course-20-hydraulic-f01:1.0.0 \
  baixiao-tese-deploy.shennong.cc/yuketang/course-20-hydraulic-f01:1.0.0
docker push baixiao-tese-deploy.shennong.cc/yuketang/course-20-hydraulic-f01:1.0.0
```

然后 Fork `yuketang-tese-deliveries`，把 `manifest.draft.yaml` 内容放到
`courses/20-hydraulic/f01/manifest.yaml`，提 PR 等运维合并。

## 项目结构

```
hydraulic-lab/
├── 液压与气压传动.json    # 课程信息
├── skills/                 # AI Skill 说明书
├── prompts/                # 文本/图/视频提示词
├── samples/                # 测试样例
├── backend/                # FastAPI 后端
├── frontend/               # 静态前端页面
└── docs/功能说明.md
```

## 最小可交付版本（已完成）

- [x] 文本 / 图片 / 视频检测**均由大模型分析**（无规则引擎回退）
- [x] 视频上传并抽帧后送视觉模型
- [x] 统一 JSON 检测报告
- [x] 前端结果展示

## 启用本地 Qwen

默认使用 **Ollama** 的 OpenAI 兼容接口（`backend/.env` 已写好模板）：

```powershell
ollama pull qwen2.5:7b
ollama pull qwen2.5vl:7b
ollama serve
```

若你用 **vLLM / Xinference** 等，只需改 `.env` 里的 `OPENAI_BASE_URL` 和模型名，例如：

```
OPENAI_BASE_URL=http://127.0.0.1:8000/v1
OPENAI_MODEL=Qwen2.5-7B-Instruct
```

访问 `GET /api/health` 可查看当前是否连上本地模型。**大模型不可用时会返回 503**，不会再用规则代替。

## 项目总结

本原型完整走通「教学场景 → 检测标准 → Skill/提示词 → 接口 → 后端流程 → 前端 → 样例测试」链路。后续可扩展：器材目标检测、OCR 读表、更细化的液压元件知识库、与学生成绩系统对接等。

**声明：** 本系统仅辅助教师发现实验问题，不构成安全认证，最终判断由教师完成。
