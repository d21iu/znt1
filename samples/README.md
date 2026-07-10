# 测试样例说明

## 文本样例（`samples/text/`）

| 文件 | 用途 |
|------|------|
| `01_complete_report.txt` | 较完整报告，期望高分 pass |
| `02_missing_purpose.txt` | 缺少实验目的/原理，规则应命中 |
| `03_missing_units.txt` | 数据无单位 |
| `04_no_error_analysis.txt` | 缺少误差分析 |
| `05_unreasonable_conclusion.txt` | 结论与数据矛盾，供 AI 判断 |

## 图片样例

请自行准备并放入 `samples/images/`：

1. 规范液压实验台照片
2. 台面杂乱、油污多
3. 软管扭曲/接头可疑松动
4. 气动 F.R.L 回路照片
5. 模糊无法辨认的照片

## 视频样例

请自行准备并放入 `samples/videos/`：

1. 正常启停与测压流程
2. 操作步骤不完整（未排气即加压等）
3. 含疑似带压拆装片段
4. 画面严重模糊

## 快速测试（文本）

```bash
curl -X POST http://127.0.0.1:8000/api/hydraulic-lab/check-text \
  -H "Content-Type: application/json" \
  -d "{\"grade\":\"2024级\",\"experiment_name\":\"泵性能测试\",\"content\":\"$(cat samples/text/02_missing_purpose.txt | sed 's/\"/\\\"/g')\"}"
```

Windows PowerShell 可用前端页面或 `Invoke-RestMethod` 提交 JSON。
