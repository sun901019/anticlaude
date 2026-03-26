# AntiClaude / AITOS / Flow Lab
## 面試作品報告

更新日期：2026-03-25

---

## 1. 專案一句話介紹

這是一套我自行打造的 **AI 作業系統 + 電商決策工作台**，把：

- AI 協作
- workflow 執行
- approval / review 審核
- 內容營運
- 電商定價與採購決策

整合到同一個全端系統中。

它不是單一頁面的展示作品，而是一個可運作、可驗證、可持續擴充的內部操作平台。

目前基線：

- 後端測試：`351 passed, 1 skipped, 1 warning`
- 前端 build：`next build` 通過
- Dashboard 路由：16 個
- 後端 API handler：約 101 個

---

## 2. 我想解決的問題

我一開始要解決的不是「怎麼做一個 AI 聊天介面」，而是：

> 如何把 AI、內容流程、審核流程、選品與定價決策，整合成一個真正能操作的系統。

實際痛點包括：

- AI 可以生成很多東西，但沒有治理與審核機制
- 電商定價、進貨、選品常常依賴手動筆記或試算表
- 內容生產、審核、通知、報表和操作台是分散的
- 使用者很難知道現在最該處理什麼

所以我最後把專案做成一個「可控的 operator system」。

---

## 3. 這個專案包含什麼

### A. AITOS / AI Office

AI 協作與治理系統，核心包含：

- AI 任務路由
- approval gate
- review queue
- CEO decision package
- workflow 狀態追蹤

### B. Media Engine

內容工作流系統，包含：

- topic strategy
- draft generation
- GEO / SEO 強化
- draft review
- 發佈前控制

### C. Flow Lab

電商決策工作台，包含：

- 商品建檔
- 落地成本試算
- Shopee 定價
- QQL 採購模式
- Top-Down 採購天花板
- 補貨與績效檢視
- 組合設計

---

## 4. 技術架構

### 後端

- Python
- FastAPI
- APScheduler
- SQLite
- pytest

### 前端

- Next.js 14 App Router
- TypeScript
- React

### AI / Workflow 層

- workflow graph runtime
- approval / review system
- AI task routing
- skill loading / routing
- debate / judge style AI 協作

### 架構分層

系統主要分成：

- `api/`：對外路由
- `workflows/`：執行與審核 runtime
- `domains/`：商業邏輯
- `adapters/`：外部整合
- `db/`：schema 與 persistence
- `dashboard/`：操作介面

這樣的分層，是為了避免：

- 前端和後端各算一套邏輯
- AI 行為不可控
- ecommerce 規則散落在不同頁面

---

## 5. 我實際做了什麼

### 5.1 Workflow / Approval Runtime

我建立了可追蹤的 workflow 系統，包含：

- workflow runs
- tasks
- events
- artifacts
- approval requests
- pause / resume
- checkpoint store

這讓 AI 執行流程不再是黑箱，而是可以：

- 暫停
- 繼續
- 審核
- 留存決策痕跡

### 5.2 Review Queue / CEO 控制面板

我建立了 review queue 和 decision package 機制，讓高風險行為必須經過 operator 決策，而不是直接執行。

### 5.3 Media / Content Engine

我把內容生產從單純 prompt，收斂成一套有治理的工作流，包含：

- topic strategy
- draft generation
- GEO / SEO 技術導向 skill 使用
- scoring
- review

### 5.4 Flow Lab 電商系統

我把 Flow Lab 做成真正可用的決策系統，而不是單純記帳工具，重點功能有：

- Quick Add 商品建檔
- landed cost 計算
- Shopee 建議售價
- QQL 採購邏輯
- Top-Down 反推採購上限
- weekly performance
- bundle 設計
- family / variant 規劃

---

## 6. 代表性問題與修復

### 問題 1：通知一直重複發

現象：

- LINE 一直收到重複待決策通知

我做的事：

- 找到是同一個 awaiting-human 事件反覆被推送
- 加入 SQLite 持久化 dedup

結果：

- 同一事件短時間內不會重複推送

### 問題 2：測試內容碰到真實發文鏈路

現象：

- 測試文字可能碰到真 Threads/X 發文流程

我做的事：

- 檢查 dual publish 測試路徑
- 把 Threads 腿也 mock 掉

結果：

- 測試資料不會再污染真發文路徑

### 問題 3：Bundle suggestion endpoint 500

現象：

- `/api/ecommerce/selection/bundles/suggest` 因 schema/query mismatch 崩潰

我做的事：

- 對齊真實 schema
- 改從 performance/inventory 取 margin 與 stock

結果：

- 組合建議路由恢復穩定

### 問題 4：測試基線失去可信度

現象：

- test DB isolation 出問題，pytest 無法被信任

我做的事：

- 修 test fixture
- 改成 repo-local test DB isolation

結果：

- full suite 回到綠燈

---

## 7. 我做這個專案時的重要工程選擇

### A. 業務邏輯應該盡量收斂到後端

原因：

- 避免前端一套、後端一套
- 保證數字可信度
- 方便後續調整 Shopee / QQL / bundle 規則

### B. AI 必須可控，不可黑箱

所以我加入：

- review queue
- approval matrix
- checkpoint / resume
- decision package

### C. UX 的重點不是功能多，而是減少操作者思考負擔

這也是為什麼我在電商頁持續做：

- Quick Add 精簡
- product detail drawer 重構
- 補貨 modal 強化
- 警示與下一步更明顯

---

## 8. 這個專案能代表我的哪些能力

如果用面試官能快速理解的方式來說，這個專案代表我有：

### 產品能力

- 能把模糊需求整理成可執行規格
- 能從使用者操作流程去看系統問題

### 後端能力

- API 設計
- schema / query / runtime 修復
- workflow 與 approval 邏輯

### 前端能力

- 操作台設計
- 資訊層級調整
- 電商決策 UX 收斂

### AI 系統能力

- AI task routing
- human-in-the-loop
- skill / role / workflow 治理

### Debug / Reliability 能力

- 能追 runtime failure
- 能修 schema mismatch
- 能修通知污染與測試污染
- 能把測試基線救回來

---

## 9. 專案目前做到哪裡

### 已可展示、可操作的部分

- dashboard build 穩定
- backend tests 穩定
- review / approval 主幹可用
- Flow Lab 電商決策主線可用
- bundle suggestion route 可用
- 通知 spam 已處理

### 仍在持續優化的部分

- 後端單一真相收斂
- family / variant 深化
- bundle intelligence 升級
- operator UX 最後一輪精修

對面試來說，最好的說法是：

> 這個專案已經是能運作的系統，不是停在概念階段；但我也很清楚哪些地方還在持續收斂。

---

## 10. 可量化成果

目前系統狀態：

- 後端 test files：`44`
- 後端測試結果：`351 passed, 1 skipped, 1 warning`
- Frontend routes：`16`
- API handlers：約 `101`
- Flow Lab products：`15`
- Workflow runs：`1262`
- Approval records：`29`
- Review items：`4`

這些數字能幫助面試官理解：

這不是只做一頁前端頁面，而是一個已經累積了資料、流程與操作邏輯的系統。

---

## 11. 面試簡短講法

如果要濃縮成 30 到 60 秒：

> 我做了一套全端 AI 作業系統，後端用 FastAPI，前端用 Next.js，資料層是 SQLite。這個系統把 workflow、approval、review queue、AI 協作、內容工作流，以及 Flow Lab 電商決策平台整合在一起。我不只做功能，也處理了很多可靠性問題，例如通知 spam、測試污染、schema mismatch、workflow 與 bundle endpoint 修復。目前系統測試綠燈、build 綠燈，是一個真正可操作的內部平台。

---

## 12. 面試時我會怎麼呈現

建議順序：

1. 先講問題：為什麼需要一套 operator system
2. 再講架構：FastAPI + Next.js + workflow + approvals
3. 再講 AI：不是聊天，而是可治理的 AI workflow
4. 再講 Flow Lab：定價、採購、bundle、決策
5. 最後講可靠性：測試、build、runtime 修復

---

## 13. 最終定位

這個專案最能代表我的不是單一技術，而是：

> 我能把產品邏輯、全端實作、AI 治理與系統可靠性整合在同一個作品裡。

如果要一句話總結：

> 我不是只做頁面或只寫 prompt，我是在打造一套真正能支撐工作流程的系統。
