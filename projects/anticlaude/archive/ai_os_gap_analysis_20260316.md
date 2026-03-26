# AI OS Gap Analysis Report
> 對照文件：目標規格 v1.0（2026-03-16 提交）
> 基準掃描：AntiClaude 專案實際現況
> 原則：最小侵入、保留現有、漸進整合

---

## 一、現況對齊報告（Alignment Report）

### 已存在的模組

| 模組 | 位置 | 成熟度 |
|------|------|--------|
| 6 個 AI 員工定義 | `_hub/shared/agents/` | ✅ 完整 |
| Agent 協調器（Pipeline） | `src/agents/orchestrator.py` | ✅ 運作中 |
| Agent 狀態追蹤 | `src/api/agent_status.py` | ✅ 完整 |
| Handoff 文件系統 | `ai/handoff/` | ✅ 使用中 |
| Sprint Board | `ai/state/sprint.md` | ✅ 使用中 |
| Skills Library（原始 repo） | `_hub/skills_library/`（9 個） | ✅ 已 clone |
| Registry 文件 | `_hub/registry/` | ⚠️ 文件存在，未程式化 |
| 執行引擎（Claude Code） | Claude CLI + Codex | ✅ 使用中 |
| 後端 API | `src/api/main.py`（40+ endpoints） | ✅ 完整 |
| 儀表板 | `dashboard/`（10 頁） | ✅ 完整 |
| 知識層（Context） | `ai/context/`、`_context/` | ⚠️ 部分 |
| 週報系統 | `src/weekly/` + `/reports` 頁 | ✅ 運作中 |
| 日誌 + 錯誤頁 | `/system` 頁 + logs/ | ✅ 完整 |
| 通知系統 | `src/utils/notify.py`（LINE） | ⚠️ 代碼存在，token 待接 |

### 缺少的模組

| 缺失模組 | 說明 | 影響層級 |
|----------|------|---------|
| Single Entry Interface（Chat UI） | 無任何對話入口，只有 dashboard | 🔴 高 |
| CEO / Planner Agent | 無動態 intent 判斷，pipeline 是固定流程 | 🔴 高 |
| Review Queue | `awaiting_human` 狀態存在，但無正式 queue 介面 | 🟠 中 |
| Morning Report（晨報） | 無每日晨報格式 + 推送機制 | 🟠 中 |
| Composite Skills Layer | Skills 以文件存在，無編排層 | 🟠 中 |
| Capability Map（程式化） | 文件存在，未被任何程式讀取 | 🟡 低 |
| Night Shift Mode | Pipeline@08:00 固定排程，非任務導向自治 | 🟡 低 |
| CEO Console（對話 UI） | 無聊天視窗 | 🔴 高 |
| Nightly Summary | 無夜間任務完成彙整報告 | 🟠 中 |

### 只是概念、尚未落地的部分

- `_hub/visualization/`（Vizro）：只有範例，未整合到儀表板
- `_hub/skills_library/`：9 個 repo 已 clone，但尚未做 capability extraction + composite 編排
- `_hub/registry/capability_map.md`：文件存在，但沒有任何 API 或 agent 讀取它
- `ai-night-shift`：在 skills_library 裡，尚未啟用

---

## 二、差距分析（Gap Analysis）

### 2.1 Single Entry Interface

| 現況 | 目標 | 差距 |
|------|------|------|
| 儀表板（視覺化閱覽）+ CLI | 對話式單一窗口，CEO agent 接待 | 完全缺失 |

**說明：** 目前使用者入口是 dashboard（操作型）和 Claude CLI（工程型）。兩者都不是「對話式 + CEO 接待式」入口。首頁（`/`）是草稿選發，不是對話介面。

---

### 2.2 Orchestrator / Planner Layer

| 現況 | 目標 | 差距 |
|------|------|------|
| `src/agents/orchestrator.py`（固定流程） | 動態 intent 判斷 + agent/skill/tool 路由 | 中等缺口 |

**說明：** 現有 orchestrator 能協調固定 pipeline（研究→策略→寫作→評分），但：
- 無法接收任意用戶輸入做 intent detection
- 無法動態切換 agent 組合
- 是「每日內容流程」的 orchestrator，不是「任意任務」的 orchestrator

---

### 2.3 Agent Routing

| 現況 | 目標 | 差距 |
|------|------|------|
| 硬編碼流程（Ori→Lala→Craft→Sage） | 動態依 intent 路由 | 中等缺口 |

**說明：** 路由邏輯在 `orchestrator.py` 和 `pipeline.py` 中是固定的。`CLAUDE.md` 有 agent 派遣表但依賴人類執行，不是程式自動路由。

---

### 2.4 Skills Registry

| 現況 | 目標 | 差距 |
|------|------|------|
| `_hub/registry/skills_registry.md`（文件） | 程式化 registry，可被 orchestrator 查詢 | 小缺口（有骨架） |

**說明：** 骨架存在。缺的是：讓 orchestrator 能讀取 registry 來決定「這個任務用哪些 skills」的機制。

---

### 2.5 Agents Registry

| 現況 | 目標 | 差距 |
|------|------|------|
| `_hub/registry/agents_registry.md`（文件） | 程式化 registry + routing logic | 小缺口 |

---

### 2.6 Tools Registry

| 現況 | 目標 | 差距 |
|------|------|------|
| `_hub/registry/` 內有 tools 文件 | 程式化，MCP 整合 | 中等缺口 |

**說明：** MCP 類工具（docs、browser、Figma、DB）尚未整合。

---

### 2.7 Capability Map（程式化）

| 現況 | 目標 | 差距 |
|------|------|------|
| `_hub/registry/capability_map.md`（文件） | orchestrator 可讀取，動態選擇能力 | 中等缺口 |

---

### 2.8 Composite Skills Layer

| 現況 | 目標 | 差距 |
|------|------|------|
| 原始 skills 文件存在（9 repo） | 編排層：research_analysis、content_creation 等 composite 定義 | 缺失 |

**說明：** 9 個外部 repo 已 clone，但尚未做 capability extraction 和 composite 編排文件。

---

### 2.9 Knowledge Layer

| 現況 | 目標 | 差距 |
|------|------|------|
| `ai/context/`、`_context/`、`projects/` | 統一 `_hub/knowledge/`，含 PRD、API docs、SOP | 小缺口 |

**說明：** 知識分散在多個目錄，無統一入口。但內容豐富，重組成本低。

---

### 2.10 Review Queue

| 現況 | 目標 | 差距 |
|------|------|------|
| `awaiting_human` agent 狀態 + AI Office 卡片 | 正式 review queue 結構 + UI | 中等缺口 |

**說明：** 現在的 `awaiting_human` 只針對 agent 任務（草稿選擇、選品核准）。缺少更廣泛的決策項目收集機制（架構選型、定位決策等）。

---

### 2.11 Handoff Layer

| 現況 | 目標 | 差距 |
|------|------|------|
| `ai/handoff/`（完整使用中） | 標準化格式 + orchestrator 可讀取 | 小缺口 |

**說明：** 這是整個系統最成熟的部分之一。格式已標準化，claude↔codex 交接流暢。

---

### 2.12 Reporting Layer

| 現況 | 目標 | 差距 |
|------|------|------|
| 週報（自動）、日誌頁、AI Office 時間軸 | 晨報（Morning Report）+ 夜報（Nightly Summary） | 中等缺口 |

**說明：** 週報系統完整。每日晨報（昨晚完成什麼、進度、blocked、需要決策、今日建議）目前不存在。

---

### 2.13 Execution Routing

| 現況 | 目標 | 差距 |
|------|------|------|
| 人工判斷（Claude Code vs Codex） | orchestrator 依複雜度自動路由 | 中等缺口 |

**說明：** `CLAUDE.md` 有分工說明，但路由是人類決策，不是系統自動判斷。

---

### 2.14 Night Shift Readiness

| 現況 | 目標 | 差距 |
|------|------|------|
| APScheduler（固定 08:00/20:00/週一） | 任務導向的夜間自治推進 | 大缺口 |

**說明：** 現有排程是「固定時間跑固定任務」，不是「晚上繼續推進未完成任務」。`ai-night-shift` 在 skills_library 未啟用。

---

### 2.15 Visualization Layer

| 現況 | 目標 | 差距 |
|------|------|------|
| Next.js 儀表板（完整）、Vizro（未整合） | interactive analytics + Vizro dashboard | 小缺口 |

---

## 三、完成度估算（Completion Estimate）

### 整體完成度：**約 48%**

| 層級 | 完成度 | 說明 |
|------|--------|------|
| Agents Layer | 85% | 六個角色完整定義，orchestrator 運作中 |
| Handoff Layer | 80% | 實際使用中，格式標準化 |
| Execution Engines | 75% | Claude Code + Codex 實際運作 |
| Dashboard / Visualization | 70% | 10 頁完整儀表板，Vizro 未整合 |
| Backend / API | 80% | 40+ endpoints，業務邏輯完整 |
| Skills Library（原始） | 60% | 9 repo 已 clone，未 composite 化 |
| Registry（文件） | 55% | 骨架存在，未程式化 |
| Knowledge Layer | 50% | 內容豐富但分散 |
| Review Queue | 30% | awaiting_human 存在，但不完整 |
| Reporting（晨報） | 20% | 週報存在，晨報缺失 |
| Single Entry Interface | 5% | 完全缺失 |
| CEO / Dynamic Orchestrator | 10% | 固定 pipeline，無動態路由 |
| Composite Skills | 15% | 原始 repo 存在，編排層缺失 |
| Night Shift Mode | 10% | 固定排程，非任務自治 |

### 拉低完成度的主要原因

1. **Single Entry Interface 完全缺失**：這是整個架構的「臉」，目前不存在
2. **CEO Orchestrator 是固定流程**：現有 orchestrator 優秀，但無法處理任意任務意圖
3. **Composite Skills 未編排**：原料（9 repo）都有，但沒有加工成可用的複合能力
4. **晨報缺失**：「早上看報告」的使用體驗目前不存在

### 已覆蓋得很好的部分

- **六員工系統**：定義清晰、角色分明
- **Handoff 機制**：claude↔codex 交接已是日常工作流
- **業務邏輯**：content pipeline + Flow Lab 完整且運作
- **Dashboard**：視覺化豐富，10 頁各有功能

---

## 四、安全整合路線（Safe Integration Roadmap）

> 原則：所有改動都是**加法**，不做任何刪除或重構

### Phase 1 — 補齊基礎設施（✅ 完成 2026-03-16）

**目標：讓骨架存在，不動任何現有程式碼**

| 任務 | 動作 | 狀態 |
|------|------|------|
| 建立 workspace 目錄骨架 | mkdir | ✅ `_hub/review_queue/`、`_hub/reports/`、`_hub/knowledge/` |
| 建立 Morning Report 模板 | 新增 .md 模板 | ✅ `_hub/reports/morning_report_template.md` |
| 建立 Nightly Summary 模板 | 新增 .md 模板 | ✅ `_hub/reports/nightly_summary_template.md` |
| 建立 Review Queue 模板 | 新增 .md 模板 | ✅ `_hub/review_queue/review_item_template.md` |
| Composite Skills 骨架 | 新增定義文件（6 個） | ✅ `_hub/shared/skills/composite/` |
| 程式化 Registry 格式 | 新增 JSON schema | ✅ `_hub/registry/registry_schema.json` |

---

### Phase 2 — Morning Report API（✅ 完成 2026-03-16）

**目標：讓「早上看報告」的體驗存在**

| 任務 | 動作 | 狀態 |
|------|------|------|
| `GET /api/morning-report` | 新增 API endpoint（讀取現有資料，不改任何 DB） | ✅ 完成 |
| Dashboard 加晨報頁 `/morning` | 新增頁面，不改現有頁面 | ✅ 完成 |
| Review Queue API + 頁面 | `GET/POST/PATCH /api/review-queue` + `/review` 頁面 | ✅ 完成 |

---

### Phase 3 — CEO Entry Point（✅ 完成 2026-03-16）

**目標：建立對話入口，現有 dashboard 不受影響**

| 任務 | 動作 | 狀態 |
|------|------|------|
| 新增 `/chat` 頁面（對話 UI） | 純新增，不改現有頁面 | ✅ 完成 |
| CEO Agent 端點 `POST /api/chat` | 新增，呼叫 Claude API | ✅ 完成（claude-sonnet-4-6）|
| Intent Detection 邏輯 | 新增模組 `src/agents/ceo.py` | ✅ 完成 |

---

### Phase 4 — Dynamic Routing（高風險，謹慎）

**目標：讓 orchestrator 能動態路由，不是只跑固定 pipeline**

| 任務 | 動作 | 需要確認？ |
|------|------|-----------|
| 改寫 orchestrator 為雙模式（fixed + dynamic） | 改現有檔案 | **🔴 一定要先確認** |
| Skills registry 程式化（讓 orchestrator 讀取） | 改現有 orchestrator | **🔴 一定要先確認** |

---

### Phase 5 — Night Shift Mode（延後，低優先）

**目標：夜間任務自治推進**

| 任務 | 動作 | 需要確認？ |
|------|------|-----------|
| 整合 ai-night-shift | 先研究 skills_library 中的內容 | **需要確認** 範圍 |
| 夜班排程機制 | 新增排程邏輯，不改現有 08:00/20:00 排程 | **需要確認** |

---

### 現在先不要動的東西

| 模組 | 原因 |
|------|------|
| `src/agents/orchestrator.py` | 核心業務邏輯，風險最高 |
| `src/api/main.py` | 40+ endpoints，大改容易壞 |
| `_hub/skills_library/`（原始 repo） | 規格明確禁止修改原始 repo |
| `dashboard/` 現有頁面 | 全部正常運作，不需要動 |
| `ai/state/sprint.md` 工作流 | 目前最核心的協作機制 |

---

## 五、第一步最小可行方案（MVP First Step）

### 建議：建立 `_hub` 完整骨架 + Morning Report 模板

**理由：**
- 純新增目錄和模板文件
- 零風險，不動任何現有程式碼
- 讓「早上看報告」的體驗框架先存在
- 為 Phase 2 的 API 開發做好準備

**具體動作（全部是新增，沒有刪除）：**

```
新增目錄：
_hub/review_queue/
_hub/reports/
_hub/knowledge/
_hub/shared/skills/composite/

新增文件：
_hub/reports/morning_report_template.md     ← 晨報格式
_hub/reports/nightly_summary_template.md    ← 夜報格式
_hub/review_queue/review_item_template.md   ← 決策審閱格式
_hub/shared/skills/composite/README.md      ← composite skill 定義說明
_hub/registry/registry_schema.json          ← registry 的 JSON 格式規範
```

**不動任何現有檔案。**

---

### 建議的晨報格式（Morning Report）

```markdown
# Morning Report — YYYY-MM-DD

## 昨晚完成了什麼
- ...

## 目前進度
- Pipeline 狀態：...
- 草稿數量：...
- Flow Lab 待審：...

## 卡在哪裡（Blocked）
- ...

## 需要你決定的事
- [ ] ...

## 建議今日第一步
1. ...

## 建議今晚下一輪任務
1. ...
```

---

## 六、總結

| 問題 | 現況 | 建議行動 |
|------|------|---------|
| 沒有單一對話入口 | 是 | Phase 3 再做，先讓晨報存在 |
| CEO Orchestrator 是固定流程 | 是 | Phase 4，現在不動 |
| Review Queue 不完整 | 是 | Phase 2 補 API + 頁面 |
| 沒有晨報 | 是 | **Phase 1 先建模板，Phase 2 建 API** |
| Composite Skills 缺編排 | 是 | Phase 1 建骨架 |
| 現有系統運作良好 | 是 | 不動，只加法 |

---

> 這份文件代表的不是「要做多少事」，而是「清楚知道自己在哪裡」。
> 目前系統的基礎相當紮實（48%），核心業務完全運作。
> 缺的是治理層、對話入口、和晨報體驗——而這些都可以用純加法完成。

---
*生成日期：2026-03-16*
*掃描基準：AntiClaude 專案實際檔案結構*
*對照規格：目標 AI OS 規格 v1.0*
