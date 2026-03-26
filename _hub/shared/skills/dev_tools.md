---
name: dev_tools
description: 開發工具參考：數據視覺化（Vizro）、HTML 投影片製作（frontend-slides）。開發時用，不是 pipeline 邏輯。
type: reference-skill
sources:
  - _hub/skills_library/vizro/
  - _hub/skills_library/toonify-mcp/
  - _hub/skills_library/frontend-slides/
replaces:
  - data_processing.md
  - presentation_ui.md
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
---

# Dev Tools — 開發工具參考

> 這份文件是開發時的工具說明，不是每日 pipeline 流程的一部分。

---

## 1. Vizro 儀表板（數據視覺化）

### 使用時機
- Threads 數據需要互動式視覺化
- 受眾洞察數據深度分析
- 生成互動式報告

### 快速使用

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
範例：`_hub/visualization/vizro/app.py`

### AntiClaude DB 結構（SQLite）
- `posts`：Threads 貼文記錄
- `articles`：抓取的文章
- `audience_insights`：受眾分析結果
- `post_stats`：互動數據

---

## 2. HTML 投影片（frontend-slides）

### 使用時機
- 系統架構說明
- 功能展示 Demo
- 向他人介紹 AntiClaude 系統

### 使用方式
1. 參考 skill spec：`_hub/skills_library/frontend-slides/SKILL.md`
2. 參考樣式：`_hub/skills_library/frontend-slides/STYLE_PRESETS.md`
3. 輸出：單一 `.html` 檔，瀏覽器直接開啟
4. 現有範例：`_hub/anticlaude-intro.html`

### AntiClaude 設計規範
- 背景：`#080808`，主色：紫色 `#7c3aed`
- 字體：Syne（標題）+ Space Mono（代碼）+ Noto Sans TC（中文）
- 效果：玻璃擬態 `backdrop-filter: blur(20px)`

### 重要注意事項
- viewport 必須 `100vh`，不可滾動
- 字體大小用 `clamp()`，CSS 函數不可直接加負號（要用 `calc(-1 * ...)`）
- 詳見 `_hub/skills_library/frontend-slides/STYLE_PRESETS.md` → CSS Gotchas

---

## 3. toonify-mcp（Token 壓縮）

大型文件需要送給 AI 分析時，用 toonify-mcp 壓縮 token 消耗。
路徑：`_hub/skills_library/toonify-mcp/`
