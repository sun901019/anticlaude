# AntiClaude × Flow Lab — 優化路線圖
> 作者：Claude Code 分析建議
> 日期：2026-03-14
> 用途：提交給 Claude Code 執行的任務規劃

---

## 系統現狀快照

```
AntiClaude（根目錄）
├── 內容自動化（src/ pipeline）         → 已運作
├── AI Office（dashboard/office）       → 雛形完成，缺關鍵功能
├── Flow Lab 電商（src/ecommerce）      → 後端 ✅，Dashboard 5 個 tab ❌
└── flowlab-selection/（舊原型）        → 廢棄中，應正式標記
```

---

## 一、最高優先：AI Office 完成度

> **現況問題**：AI Office 畫面存在，但底層流程沒有真正接入，看起來像控制台、實際是空殼。

### 1-A. 修復啟動穩定性
**目標**：每次開機後 30 秒內可靠地把系統跑起來

**任務**：
- 在根目錄新增 `start.sh`（或 `start.ps1`），一鍵啟動前端 + 後端
- 在 `CLAUDE.md` 補充 Windows 環境下 uvicorn 的正確啟動命令（避免 `--reload` 權限問題）
- 統一 AI Office 所有 API 呼叫路徑（目前混用 `/api/...` relative 和 `http://localhost:8000/...` absolute）

**負責**：Lumi

---

### 1-B. 持久化 Timeline 完成
**目標**：重整頁面後仍能看到近期團隊活動，不是空白

**任務**：
- 讓 `dashboard/office/page.tsx` 的右側 activity feed 完全從 `GET /api/agents/events` 讀取（現在是 UI-local）
- 修正 `/api/agents/events` 回傳 `count` 為實際筆數（不是 limit 值）
- 加上按 agent / task type / 時間篩選

**負責**：Lumi（後端）+ Pixel（前端 UI）

---

### 1-C. Handoff 生命週期補全
**目標**：讓任務在 AI Office 裡有完整的狀態流

**任務**：
- 在 `src/api/agent_status.py` 的 task model 新增狀態：`blocked`、`done`、`handoff_pending`
- 前端 office card 渲染對應狀態顏色（blocked=橘、done=綠、handoff=藍）

**負責**：Lumi + Pixel

---

### 1-D. Artifact 可點擊
**目標**：agent 卡片上的產出物可以直接開啟

**任務**：
- `artifact_refs` 欄位已存在，但 UI 沒渲染
- 前端 office page 把 artifact_refs 顯示為可點擊連結（daily report / draft / DB record）

**負責**：Pixel

---

### 1-E. 真實 Workflow 接入 AI Office
**目標**：Ori/Lala/Craft/Sage 在真實工作時自動反映到 AI Office，不再靠 demo handoff

**任務**：
- `src/agents/orchestrator.py` 在每個步驟呼叫 `agent_status.py` 的 emit 函數
- 接入順序：daily pipeline → feedback 分析 → tracker 回收 → ecommerce 分析
- 每個接入點在規格文件標記 ✅

**負責**：Lumi

---

## 二、Flow Lab Dashboard 5 個 Tab

> **現況問題**：後端 API 全部完成，但前端 5 個 tab 尚未實作，功能無法使用。

**文件來源**：`ecommerce_selection_integration_status.md`

### 2-A. 候選池 Tab（Candidate Pool）
- 顯示完整商品候選清單（product_name / market_type / source_platform / category / status）
- 支援按類別、market_type、status 篩選
- 快速操作：送入分析 / 標記廢棄

### 2-B. 評分分析 Tab
- 選定候選商品後，顯示完整評分 breakdown（demand / competition / profit / pain_point / brand_fit）
- 顯示財務摘要（landed_cost / gross_margin / break_even_roas）
- 顯示競品環境說明

### 2-C. 組合設計 Tab（Portfolio Roles）
- 顯示目前商品組合中 traffic / profit / hero 分佈
- 視覺化缺口（e.g. 目前缺 hero 商品）
- 建議下一步應補哪類角色

### 2-D. 選品報告 Tab
- 列出所有已生成報告（`ecommerce_selection_reports` 表）
- 可開啟 markdown 格式報告
- 可下載或複製

### 2-E. 學習記憶 Tab
- 顯示 `ecommerce_selection_lessons` 表累積的選品教訓
- 按 lesson_type 分類（pattern / rule / warning）
- 顯示來源 analysis_id 和 confidence

**負責**：Pixel（UI 設計）+ Lumi（API 串接）

---

## 三、智能閉環強化

> **現況問題**：系統收集數據，但沒有真正形成「越用越準」的回饋循環。

### 3-A. 每日記憶摘要（Agent Memory Summary）
**目標**：每天 pipeline 跑完後，自動產生一份摘要存入長期記憶

**任務**：
- `src/agents/orchestrator.py` 跑完後，讓 Sage 摘要當天事件到 `outputs/office_memory/daily_summary_YYYY-MM-DD.md`
- 摘要內容：誰做了什麼、產出了什麼、哪裡卡住、學到了什麼
- 這份摘要未來可以注入 prompt

**負責**：Sage（摘要邏輯）+ Lumi（觸發機制）

---

### 3-B. Threads 數據 → 選題影響
**目標**：讓上週貼文表現直接影響本週選題建議

**任務**：
- Lala 在選題時，自動讀取 `audience_insights` 表最新 3 筆數據
- 在 `content-strategist` 的 prompt 加入「高互動主題模式」注入
- 把「哪類主題互動率高」存入 `_context/` 長期記憶

**負責**：Lala（策略邏輯）+ Lumi（數據串接）

---

### 3-C. Flow Lab 選品學習回路
**目標**：每次選品決策後，系統自動學習（不只是記錄）

**任務**：
- 當 `decision_status` 更新為 `approved` 或 `rejected` 時，觸發 Sage 生成 1 筆 lesson
- lesson 格式：主題 / 類型（why_approved / why_rejected）/ 關鍵因素 / confidence
- 累積 10 筆後，Sage 整合成「選品規則更新」推送給 Lala

**負責**：Sage

---

## 四、技術債清理

### 4-A. 廢棄 flowlab-selection/ 舊目錄
**任務**：
- 在 `C:\Users\sun90\flowlab-selection\` 根目錄加一個 `DEPRECATED.md`，說明主系統已移至 `Anticlaude/src/ecommerce/`
- 不刪除（保留歷史），但清楚標記

### 4-B. 文件同步
**現況問題**：`ai_office_vision.md` 仍把已完成的項目寫成「未來計畫」，誤導後續 agent

**任務**：
- 更新 `ai_office_vision.md` 的 Current State 區段，標記 ✅ / ❌ 對應實際狀態
- 同步 `ai_office_remaining_work.md` 移除已完成項目

### 4-C. API access pattern 統一
**任務**：
- `dashboard/src/app/office/page.tsx` 中的 `http://localhost:8000/api/agents/stream` 改為走 Next.js rewrite
- 確保 `next.config.js` 有對應的 rewrite rule

---

## 執行優先順序

| 優先 | 任務 | 原因 |
|------|------|------|
| P0 | 1-A 啟動穩定性 | 其他一切的前提 |
| P1 | 1-B 持久化 Timeline | AI Office 可信度關鍵 |
| P1 | 2-A~2-E Flow Lab Dashboard | 後端已完成，前端缺口最明確 |
| P2 | 1-C Handoff 狀態 | 讓協作可見 |
| P2 | 1-D Artifact 可點擊 | 讓產出可溯源 |
| P2 | 3-A 記憶摘要 | 系統越來越聰明的基礎 |
| P3 | 1-E 真實 Workflow 接入 | 最複雜，需要 P0-P2 穩定後再做 |
| P3 | 3-B Threads 數據→選題 | 需要 3-A 打底 |
| P3 | 3-C Flow Lab 學習回路 | 需要 2-A~2-E 完成後才有意義 |
| 清理 | 4-A~4-C | 隨時可做 |

---

## 給 Claude Code 的執行備註

1. 每個任務開始前先確認服務是否在跑（`curl http://localhost:8000/api/agents/status`）
2. 資料庫改動（schema）務必先讀 `src/db/schema.py` 確認現狀
3. 前端改動後用 `npm run build` 確認無 TypeScript 錯誤
4. 每完成一個任務，更新 `ecommerce_selection_integration_status.md` 對應的 ✅
5. 這份文件本身不需要更新，作為靜態規劃快照保留
