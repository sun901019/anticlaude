# 李政陽
**全端工程師 · AI 系統開發**

📧 _(請填入 email)_　　🔗 [github.com/sun901019](https://github.com/sun901019)　　📍 台灣

---

## 技術能力

### 後端
- **Python** — FastAPI、Django REST Framework、APScheduler、Celery、pytest
- RESTful API 設計、排程任務、非同步任務佇列（Redis）

### 前端
- **TypeScript / JavaScript** — Next.js 14 App Router、React 18、Zustand、TanStack Table
- TailwindCSS、Recharts / Chart.js、SPA 架構設計

### AI / LLM 整合
- **Anthropic Claude API**（claude-sonnet、claude-haiku）：多 agent 協作、prompt engineering
- **Google Gemini API**：聚類分析、fallback 策略
- 自建 skill routing 系統、multi-agent workflow、approval gate 機制

### 資料庫 & 架構
- SQLite（schema 設計、migration、28 資料表）
- 分層架構設計：`api/` `workflows/` `domains/` `adapters/` `db/`

### 開發工具
- **Claude Code CLI** — 主力 AI 編程工具，用於整個 AntiClaude 系統的設計、debug、重構
- **Codex CLI（OpenAI）** — 批次實作任務（Batch 1–7），包含測試生成、UI 元件、bug fix
- **Gemini CLI** — 程式碼輔助與 API 整合驗證
- **AI IDE（Cursor / Windsurf）** — 日常開發輔助
- Git / GitHub — 版本控制、repo 管理

---

## 專案作品

### 1. AntiClaude — AI 作業系統 + 電商決策平台
> 個人獨立開發 · Python / FastAPI + Next.js 14 / TypeScript · 2026

**這是什麼：**
一套我從零自行設計並建構的全端 AI 系統，整合 AI 協作治理、內容自動化工作流、與電商決策工具，是一個可在本機運作的「AI operator platform」。

**技術規模：**
- 後端測試：`351 passed, 1 skipped`（pytest）
- API handler：約 101 個
- 資料庫資料表：28 張
- 前端路由：16 頁（Next.js App Router）
- Python 模組：100+ 個

**核心子系統：**

**① AITOS / AI Office — AI 治理與工作流引擎**
- 自建 `GraphRunner`：支援 retry、依賴追蹤、pause/resume、checkpoint 儲存
- Approval Gate：高風險 AI 行為（如自動發文）需 operator 審核後才執行
- Review Queue + CEO Decision Package：審核佇列 + 決策記錄持久化
- 6 個 AI 角色（Ori/Lala/Craft/Sage/Lumi/Pixel）透過 skill routing 分工協作
- 支援 debate / judge 模式：多個 AI agent 互相辯論後再決策

**② Media Engine — 內容生產工作流**
- 全自動日報 pipeline：抓取 → 聚類 → 評分 → 選題 → 寫稿 → 審核 → 發布
- GEO / SEO skill 自動注入（geo_optimization_engine）
- Orio Scorer：三維評分（topic_fit × persona_fit × source_trust）
- 四維主題評分（timeliness / heat / controversy / audience_fit）
- Threads 發文整合 + LINE 通知

**③ Flow Lab — 電商決策工作台**
- 商品建檔 Quick Add + 系列分組（family / variant）
- 落地成本計算：進貨 + 頭程 + 集運 + 包材 + 平台費率（CCB / 促銷日 / 備貨懲罰情境）
- Top-Down 採購天花板反推：給定市場售價，反算最高可承受進貨成本
- QQL 採購模式整合（含匯率 × 平台費加成）
- Bundle 組合引擎：4 種組合類型、相容性守門、動態折扣計算
- Shopee 週績效管理 + 補貨警示 + 滯銷自動標記

**我實際做了什麼（可驗證）：**
- 所有架構決策、模組設計、API 設計皆由我主導
- 使用 **Claude Code CLI** 進行整個系統的設計、重構與 debug
- 使用 **Codex CLI** 執行 Batch 1–7 的批次實作（UI 元件、測試、bug fix）
- 使用 **Gemini API** 實作 ClusterAgent（Gemini Flash 聚類 + Claude fallback）
- 透過 AI 工具協作完成單人無法在短期內完成的系統規模

---

### 2. Issue Tracker — 全端議題追蹤系統
> 個人作品 · [github.com/sun901019/issue-backend](https://github.com/sun901019/issue-backend) + [issue-frontend](https://github.com/sun901019/issue-frontend) · 2025–2026

**這是什麼：**
仿 GitHub Issues / Jira 設計的全端 issue 追蹤系統，前後端分離，從零獨立完成。

**技術架構：**

| 層 | 技術 |
|---|---|
| 後端 | Python · Django 5.1 + DRF · Celery + Redis |
| 前端 | React 18 + TypeScript · Vite · Zustand · TanStack Table · Chart.js |
| 樣式 | TailwindCSS |
| 路由 | React Router v6 |
| 測試 | pytest |
| 環境管理 | Poetry + `.env` config |

**重點：**
- 前後端分離架構，RESTful API 設計
- 背景任務（Celery + Redis）處理排程工作
- 前端狀態管理（Zustand）+ 表格（TanStack Table）+ 圖表（Chart.js）
- 功能完整：建立、追蹤、分類、狀態管理

---

## AI 輔助開發能力

我以 AI 編程工具作為日常開發的核心工作方式，不只是問答，而是用來做架構設計、跨檔案重構、debug、批次實作。

**使用的工具：** Claude Code CLI · Codex CLI · Gemini CLI · AI IDE（Cursor）· Git / GitHub

**用這些工具做出了什麼：**

AntiClaude 是我用 AI 工具獨自建構出來的系統。整個專案的規模如下：

- 100+ Python 模組
- 101 個 API handler
- 351 個自動化測試（全部通過）
- 28 張資料庫資料表
- 16 個前端頁面

這個規模，一個人在短期內能做到，是因為我知道怎麼用 AI 工具把想法快速實體化，同時保持對系統架構的掌控。

具體工作分工：**Claude Code** 負責架構設計與跨模組重構；**Codex CLI** 負責批次實作（UI 元件、測試生成）；**Gemini** 整合進系統作為 AI agent 的其中一個推理引擎。

---

## 學歷

_(請自行填入學校 / 科系 / 年級 / 預計畢業年份)_

---

## 補充說明

- **獨立建構大型系統的能力**：AntiClaude 是單人從零設計並建構，涵蓋後端、前端、AI 整合、資料庫、工作流引擎，總計超過 100 個 Python 模組、101 個 API handler、351 個測試。
- **有想法，能實體化**：我不只是使用現成工具，而是根據實際需求設計系統，例如自建 GraphRunner workflow engine、approval gate 機制、multi-agent 協作架構。
- **AI 輔助開發實戰能力**：Claude Code CLI、Codex CLI、Gemini CLI 是我日常開發的工具，不是輔助，是工作流程的一部分。我用這些工具獨立建構出超過 100 個模組、351 個測試的系統，這是最直接的能力證明。
