# Visualization Tool

> 生成互動式數據儀表板，用於 AntiClaude 系統的數據分析展示。

## 什麼時候用這個 Tool？

- Threads 數據分析結果需要圖表化
- 受眾洞察報告需要視覺化呈現
- 定期數據報告需要儀表板格式

## 與 recharts 的差異

| | recharts（現有） | Vizro（此 Tool）|
|--|---------|------|
| 位置 | dashboard/ Next.js | 獨立 Python 應用 |
| 適用 | 即時數據、Web 嵌入 | 深度分析、一次性報告 |
| 技術 | React/TypeScript | Python/Plotly |

## AntiClaude 應用場景

- 月度數據報告儀表板
- 受眾洞察深度分析視覺化
- 內容表現熱力圖

## 快速啟動

```bash
pip install vizro
python _hub/visualization/vizro/app.py
# 開啟 http://localhost:8050
```
