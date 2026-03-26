# AntiClaude AI 協作作業系統 — 標準作業協議
> 版本：v1.0
> 建立日期：2026-03-15
> 適用對象：所有進入此專案的 AI（Claude Code、Codex、GPT、Gemini 等）

---

## 核心原則

**任何 AI 進來，必須：**
1. 讀完 Context（不跳過）
2. 知道現在 Sprint 在做什麼
3. 認領一個任務，做完寫回去
4. 交接給下一個 AI / 下一個階段

---

## 角色地圖（6 個 Agent 對應開發生命週期）

你的 6 個 Agent 不只做內容，他們對應完整的**工作生命週期**：

```
Ori     → 偵察 / 審計 / 研究        → 發現問題、找缺口
Lala    → 策略 / 規劃 / 排優先       → 決定做什麼、怎麼做
Craft   → 文件 / 規格 / 產出文字     → 寫計畫、寫規格、寫 SOP
Lumi    → 工程 / 實作 / 程式碼       → 真正動手改代碼（= Codex 執行者）
Sage    → 分析 / 審核 / 驗證         → 驗收成果、找問題、看數據
Pixel   → 設計 / UI / 視覺           → 前端美化、介面決策
```

**一個完整的工作循環長這樣：**

```
用戶提出需求
    ↓
Ori（Claude Code）   → 審計系統，發現真正的缺口
    ↓
Lala（Claude Code）  → 規劃 Sprint，排優先順序
    ↓
Craft（Claude Code） → 寫成 plan_YYYYMMDD_xxx.md 規格文件
    ↓
Lumi（Codex）        → 讀規格文件，實作程式碼
    ↓
Sage（Claude Code）  → 審查成果，執行測試，確認品質
    ↓
Pixel（Codex）       → 若有前端工作，處理 UI 細節
    ↓
更新 progress-log.md + sprint.md
    ↓
下一個循環
```

---

## 誰做什麼（AI 分工表）

| 任務類型 | 角色 | 執行 AI |
|---------|------|---------|
| 系統審計、找缺口 | Ori | Claude Code |
| 規劃、優先排序 | Lala | Claude Code |
| 寫計畫文件、規格 | Craft | Claude Code |
| 架構決策 | 無特定角色 | Claude Code |
| 後端實作、Bug Fix | Lumi | Codex |
| 前端 UI 實作 | Pixel | Codex |
| 測試生成、驗收 | Sage | Claude Code 或 Codex |
| 數據分析、週報 | Sage | Claude Code |
| 內容選題 | Lala | Claude Code |
| 文案寫作 | Craft | Claude Code |
| 競品/市場研究 | Ori | Claude Code |

---

## Session 標準流程

### 每次工作開始（任何 AI 都要做）

```
Step 1：讀 CLAUDE.md（你是誰、你的規則）
Step 2：讀 ai/state/sprint.md（現在的 Sprint 任務）
Step 3：讀 ai/state/current-task.md（當前最新狀態）
Step 4：確認要認領哪個任務
Step 5：將任務狀態改為「進行中」
```

### 每次工作結束（任何 AI 都要做）

```
Step 1：更新 ai/state/sprint.md（完成的任務 → ✅）
Step 2：更新 ai/state/progress-log.md（寫本輪做了什麼）
Step 3：更新 ai/state/current-task.md（下一步是什麼）
Step 4：若有交接→ 寫 ai/handoff/to-codex.md 或 to-claude.md
Step 5：若有重要決策 → 寫 ai/state/decisions.md
```

---

## Sprint Board 使用規則

**Sprint Board** = `ai/state/sprint.md`

每個任務格式：
```markdown
- [ ] 任務名稱 | 角色：Lumi | 優先：高 | 預計：1h | 計畫文件：plan_xxx.md
- [x] 已完成任務 ✅ 2026-03-15
- [~] 進行中任務 🔄 Claude Code
```

狀態符號：
- `[ ]` = 待做
- `[~]` = 進行中（同時只能有一個進行中）
- `[x]` = 完成
- `[!]` = 阻塞（需要用戶介入）

---

## 交接文件規則

### Claude Code → Codex 交接（要實作時）

寫 `ai/handoff/to-codex.md`：

```markdown
# 交接給 Codex
日期：YYYY-MM-DD
任務：xxx
計畫文件：projects/anticlaude/plan_YYYYMMDD_xxx.md

## 你需要做的事
1. ...
2. ...

## 注意事項
- 不要改 xxx 文件
- 改完跑 pytest 確認

## 完成後
- 更新 sprint.md
- 把 to-codex.md 改名為 done-codex-YYYYMMDD.md
```

### Codex → Claude Code 交接（實作完成後）

寫 `ai/handoff/to-claude.md`：

```markdown
# 交接給 Claude Code
日期：YYYY-MM-DD
完成任務：xxx

## 已完成
- ...

## 需要 Claude 驗收的地方
- ...

## 遇到的問題（若有）
- ...
```

---

## 強制規定（紅線）

❌ **不能做的事：**
- 不讀 sprint.md 就開始工作
- 工作完不更新 progress-log.md
- 寫了計畫文件但沒加到 sprint.md
- 同時有 2 個任務標為「進行中」

✅ **必須做的事：**
- 每個計畫文件都要對應 sprint.md 裡的一個任務
- 每次工作結束都要在 progress-log.md 留下紀錄
- 有阻塞就標 `[!]`，不要自己猜著做

---

## 觸發詞 → 角色派遣

用戶說以下詞時，Claude Code 應該啟動對應角色的工作模式：

| 用戶說… | 派遣角色 | Claude Code 做的事 |
|---------|---------|----------------|
| 「幫我檢查系統」「有什麼問題」| Ori | 執行系統審計 |
| 「規劃一下」「下一步做什麼」| Lala | 更新 sprint.md + 排優先 |
| 「寫成計畫」「規格文件」| Craft | 產出 plan_xxx.md |
| 「幫我分析」「看看數據」| Sage | 分析 DB 或 log |
| 「幫我改 UI」「前端調整」| Pixel | 啟動 Codex 交接 |
| 「幫我實作」「寫代碼」| Lumi | 啟動 Codex 交接 |
