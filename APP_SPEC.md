# APP_SPEC · 液压与气压传动实验规范检测（f01）

## 基本信息

| 项目 | 内容 |
|------|------|
| 课序号 | 20 |
| 课程名称 | 液压与气压传动 |
| 负责人（技术开发同学） | 石家霖、马瑞笛 |
| app_id | `course-20-hydraulic-f01` |
| 版本 | 1.0.0 |
| host 端口 | 18100 |
| 容器端口 | 8080 |

## 一句话定位

面向《液压与气压传动》课程的 AI 辅助教学工具：对实验报告文本、实验台照片、操作视频做规范性与安全性检测，输出统一 JSON 报告，**辅助教师发现问题，不替代教师评分**。

## 目标用户与场景

- 授课教师：批改前快速定位报告结构缺失、数据不规范、结论不合理与潜在安全风险。
- 学生：提交前自查实验报告完整性。

## 功能范围（f01）

| 功能 | 输入 | 输出 |
|------|------|------|
| 文本检测 | 实验报告全文 | 统一 JSON 报告 |
| 图片检测 | 实验台照片 | 统一 JSON 报告 |
| 视频检测 | 操作过程视频（OpenCV 抽帧后送视觉模型） | 统一 JSON 报告 + 关键时间段事件 |

三类检测**均由大模型完成**，无规则引擎回退；模型不可用时接口返回 503。

## 统一输出 JSON

| 字段 | 说明 |
|------|------|
| score | 0–100 总分 |
| level | pass / warning / fail |
| issues | 问题列表（category、severity、problem、evidence、suggestion、confidence） |
| teacher_review_required | 是否建议教师复核 |
| summary | 总体评价 |
| key_events | 视频专用时间段事件 |

## 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查，返回 status / app_id / version |
| GET | `/` | 前端首页（可在门户 iframe 打开） |
| POST | `/api/hydraulic-lab/check-text` | 文本报告检测 |
| POST | `/api/hydraulic-lab/check-image` | 图片检测（multipart） |
| POST | `/api/hydraulic-lab/check-video` | 视频抽帧检测（multipart） |
| GET | `/api/health` | 兼容旧路径 |

## 运行与配置

- 监听：`0.0.0.0:8080`
- 前端与后端同源，前端 API 地址留空即用当前站点 origin。
- 所有 LLM 配置从环境变量读取（见 `backend/.env.example`），**密钥不进代码/Git/镜像**。
- 生产环境 `.env` 与 LLM 密钥由运维从 `yuketang/tese` 同步下发。

## 依赖的大模型

默认 OpenAI 兼容接口（本地 Qwen / Ollama）：
- 文本模型：`qwen2.5:7b`
- 视觉模型（图片/视频）：`qwen2.5vl:7b`

可通过 `OPENAI_BASE_URL` / `OPENAI_MODEL` / `OPENAI_VISION_MODEL` 切换到 vLLM、Xinference 等。

## 非目标（本期不做）

- 器材目标检测、OCR 读表
- 与学生成绩系统对接
- f02 第二功能

## 声明

本系统仅辅助教师发现实验问题，不构成安全认证，最终判断由教师完成。
