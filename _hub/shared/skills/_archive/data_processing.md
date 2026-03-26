---
name: data_processing
description: 處理大型數據集，生成互動式視覺化儀表板，用於分析 Threads 數據和內容表現。
type: composite-skill
sources:
  - _hub/skills_library/vizro/
  - _hub/skills_library/toonify-mcp/
allowed-tools:
  - Read
  - Write
  - Bash
---

# Data Processing — 數據處理與視覺化技能

## 使用時機

- 有大量 Threads 數據需要視覺化
- 需要生成互動式報告（不只是靜態圖表）
- 受眾洞察數據需要深度分析

---

## Vizro 快速使用

```python
import vizro.plotly.express as px
from vizro import Vizro
import vizro.models as vm

page = vm.Page(
    title="AntiClaude 數據分析",
    components=[
        vm.Graph(figure=px.line(df, x="date", y="likes")),
    ]
)

dashboard = vm.Dashboard(pages=[page])
Vizro().build(dashboard).run()
```

安裝：`pip install vizro`

---

## AntiClaude 數據結構

SQLite 主要表格：
- `posts`：Threads 貼文記錄
- `articles`：抓取的文章
- `audience_insights`：受眾分析結果
- `post_stats`：互動數據

---

## Antigravity 補充

（此區塊由 Antigravity 填寫更詳細的數據處理流程）
