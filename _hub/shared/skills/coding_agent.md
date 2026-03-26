---
name: coding_agent
description: 負責程式碼生成、重構、API 開發和系統架構實作，是 Claude Code 的核心執行技能。
type: composite-skill
sources:
  - _hub/skills_library/agency-agents/
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# Coding Agent — 程式碼執行技能

> AntiClaude 專案的技術執行層，由 Claude Code 負責實作。

## AntiClaude 技術規範

### Python 後端
- 目錄：`src/`
- 框架：FastAPI + APScheduler
- 風格：async + type hints
- 測試：pytest，放在 `tests/`

### TypeScript 前端
- 目錄：`dashboard/`
- 框架：Next.js 14 App Router + Tailwind CSS
- 狀態：React hooks（useState, useEffect）
- 圖表：recharts

### 資料庫
- SQLite：`data/anticlaude.db`
- 連接：`src/db/connection.py`

---

## 開發流程

1. 先讀相關檔案，理解現有架構
2. 最小化改動（不過度工程化）
3. 測試邏輯（`pytest tests/ -v`）
4. 確認後端 API 和前端 proxy 一致

---

## 常用指令

```bash
# 啟動後端
uvicorn src.api.main:app --reload --port 8000

# 啟動前端
cd dashboard && npm run dev

# 執行測試
pytest tests/ -v

# Pipeline 測試
python src/pipeline.py --dry-run
```

---

## 安全規範

- 不寫 SQL injection 漏洞（用 parameterized queries）
- 不把 API key 寫進程式碼（用 .env）
- 不 force push main 分支
