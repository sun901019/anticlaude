# START HERE — AntiClaude × AI-OS 系統指南

> 系統版本：AI-OS 中台架構 v1.0（2026-03-12）
> 架構設計：Antigravity | 程式實作：Claude Code

---

## 這套系統是什麼？

AntiClaude 是台灣科技 Threads 帳號 @sunlee._.yabg 的**個人品牌內容自動化系統**。
升級後整合了 AI-OS 中台架構，讓 AI 能力可以被系統性地調度和組合。

```
你說「幫我寫文案」
    ↓
CLAUDE.md 偵測任務類型
    ↓
派遣 Threads Writer Agent
    ↓
Agent 載入 content_creation + text_humanization skills
    ↓
輸出台灣朋友聊天語氣的 Threads 貼文
```

---

## 快速啟動

### 啟動 AntiClaude 系統
```bash
# 後端 API（port 8000）
cd c:\Users\sun90\Anticlaude
uvicorn src.api.main:app --reload --port 8000

# 前端儀表板（port 3000）
cd dashboard && npm run dev

# Pipeline 執行
python src/pipeline.py --dry-run   # 測試
python src/pipeline.py             # 正式執行
```

### 啟動 Vizro 儀表板（選用）
```bash
pip install vizro pandas
python _hub/visualization/vizro/app.py
# 開啟 http://localhost:8050
```

---

## 系統地圖

### AntiClaude 業務層（`src/` + `dashboard/`）

| 元件 | 路徑 | 說明 |
|------|------|------|
| Pipeline | `src/pipeline.py` | 每日自動執行流程 |
| FastAPI | `src/api/main.py` | 所有 API 端點 |
| 儀表板 | `dashboard/` | Next.js 數據面板 |
| 資料庫 | `data/anticlaude.db` | SQLite 所有數據 |

### AI-OS 中台層（`_hub/`）

| 元件 | 路徑 | 說明 |
|------|------|------|
| 能力地圖 | `_hub/registry/capability_map.md` | 任務→Agent→Skill 路由 |
| Skill 索引 | `_hub/registry/skills_registry.md` | 9 個複合技能索引 |
| Agent 索引 | `_hub/registry/agents_registry.md` | 所有 Agent 索引 |
| 外部 Repo | `_hub/skills_library/` | 9 個 clone 的技能庫 |

---

## 9 個 Composite Skills

| Skill | 最主要用途 |
|-------|-----------|
| `text_humanization` | 讓 AI 文案去除 AI 味，更像人說話 |
| `content_creation` | Threads 貼文結構設計 |
| `research_analysis` | 素材篩選與趨勢分析 |
| `marketing_strategy` | 選題策略與發文計畫 |
| `seo_optimization` | GEO + 傳統 SEO 優化 |
| `presentation_ui` | HTML 投影片製作 |
| `data_processing` | 大型數據集視覺化 |
| `project_planning` | 任務拆解與計畫生成 |
| `coding_agent` | 程式碼生成與系統實作 |

---

## 7 個 Agents

| Agent | 觸發場景 |
|-------|---------|
| `content-strategist` | 「選題」「今天發什麼」 |
| `threads-writer` | 「寫文案」「寫貼文」 |
| `market-research-agent` | 「市場調查」「競品分析」 |
| `marketing-strategy-agent` | 「行銷策略」「成長計畫」 |
| `content-agent` | 「多格式內容」「投影片」 |
| `planning-agent` | 「規劃任務」「拆解需求」 |
| `coding-agent` | 「寫程式」「改後端」 |

加上 `_hub/skills_library/agency-agents/` 的 50+ 個外部 agents（UI Designer、Backend Architect 等）

---

## 工作分工

| 角色 | 負責 |
|------|------|
| **Antigravity** | 規劃、架構、決策、補充 skill/agent 內容 |
| **Claude Code** | 程式碼實作、任務執行、skill 調度 |

收到 `claude_code_*.md` 任務檔時，Claude Code 直接按步驟執行。

---

## 相關文件

- `CLAUDE.md` — Claude Code 指引（自動讀取）
- `_hub/registry/capability_map.md` — 完整任務路由表
- `projects/anticlaude/project_context.md` — AntiClaude 專案入口
- `_hub/visualization/vizro/app.py` — Vizro 儀表板範例
