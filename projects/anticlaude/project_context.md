# AntiClaude — 專案入口

> 這份文件是 AI-OS 中台系統中，AntiClaude 專案的入口索引。
> 業務代碼保留在根目錄（方案 B：不搬遷，保持穩定運作）。

---

## 專案位置

| 元件 | 路徑 | 說明 |
|------|------|------|
| Python 後端 | `../../src/` | FastAPI + pipeline |
| Next.js 前端 | `../../dashboard/` | 數據儀表板（port 3000）|
| SQLite 資料庫 | `../../data/anticlaude.db` | 所有數據 |
| 輸出報告 | `../../outputs/` | 每日草稿、報告、週報 |
| AI 記憶 | `../../_context/` | about_me, workflow, api_reference |
| 環境變數 | `../../.env` | 所有 API key |

---

## 啟動指令

```bash
# 後端 API（從根目錄執行）
cd c:\Users\sun90\Anticlaude
uvicorn src.api.main:app --reload --port 8000

# 前端儀表板
cd c:\Users\sun90\Anticlaude\dashboard
npm run dev

# Pipeline 測試
python src/pipeline.py --dry-run
```

---

## 使用的 AI-OS 能力

| 任務類型 | Agent | Skill |
|---------|-------|-------|
| 選題策略 | `content-strategist` | `content_creation` + `marketing_strategy` |
| 寫 Threads 文案 | `threads-writer` | `content_creation` + `text_humanization` |
| 數據分析 | `growth-hacker` | `research_analysis` + `data_processing` |
| 系統介紹 | `coding-agent` | `presentation_ui` |

---

## 相關 AI-OS 資源

- 能力地圖 → `../../_hub/registry/capability_map.md`
- Skill 索引 → `../../_hub/registry/skills_registry.md`
- Agent 索引 → `../../_hub/registry/agents_registry.md`
---

## Codex

- Codex 協作規格: `./codex_agent_spec.md`
