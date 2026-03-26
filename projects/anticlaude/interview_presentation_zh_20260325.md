# AntiClaude / AITOS / Flow Lab
## 面試簡報大綱

建議長度：10 到 12 張投影片  
建議時間：8 到 12 分鐘

---

## 投影片 1｜標題

**AntiClaude / AITOS / Flow Lab**  
AI 作業系統 + 電商決策工作台

副標：

- FastAPI + Next.js + SQLite
- Workflow、Approval、AI 協作、Flow Lab 電商模組

---

## 投影片 2｜我想解決的問題

真實工作流程分散在太多工具中：

- AI 可生成，但不可治理
- review / approval 很混亂
- 電商定價依賴試算表
- 內容、採購、操作決策彼此斷裂

目標：

> 做出一套可控、可追蹤、可審核的 operator system

---

## 投影片 3｜我做了什麼

這個系統可以分成三塊：

- **AITOS / AI Office**
  - AI routing
  - approval
  - review queue
  - workflow control

- **Media Engine**
  - topic strategy
  - draft generation
  - GEO / SEO
  - content review

- **Flow Lab**
  - 商品建檔
  - landed cost
  - Shopee 定價
  - 採購與 bundle 設計

---

## 投影片 4｜系統架構

分層：

- `api/`
- `workflows/`
- `domains/`
- `adapters/`
- `dashboard/`

核心想法：

> 不讓商業邏輯散落在 UI，而是逐步收斂成可維護的 domain 與 workflow 邏輯

---

## 投影片 5｜AI 作業系統怎麼運作

Human + AI collaboration model：

- Human CEO 在上層
- AI 負責 research / strategy / writing / scoring / execution
- 高風險任務經 approval gate
- 所有結果進 review / artifact / decision package

價值：

- AI 可追蹤
- 可審核
- 可中斷 / 繼續

---

## 投影片 6｜Workflow / Review / Approval

已實作：

- workflow runs
- tasks / events
- approval requests
- review queue
- CEO decision package
- pause / resume

這代表：

- AI 不是直接亂做事
- operator 有最終控制權

---

## 投影片 7｜Flow Lab 電商系統

主要能力：

- Quick Add 商品建檔
- 落地成本估算
- Shopee 定價決策
- QQL 採購模式
- Top-Down 採購天花板
- 補貨 / 週績效 / 組合設計

關鍵價值：

> 把原本靠手算與試算表的決策，變成系統化工作流

---

## 投影片 8｜UX 與產品收斂

我不只做功能，也持續整理 operator UX：

- 簡化新增商品
- 重整商品 detail drawer
- 強化補貨入庫 modal
- 收斂在售商品、組合設計、週績效

學到的事：

> 好系統不是功能越多越好，而是越能減少操作者思考負擔越好

---

## 投影片 9｜我修了哪些真問題

代表性修復：

- 通知 spam 修復
- 測試資料碰到發文鏈路的風險修復
- bundle endpoint schema mismatch 修復
- test DB isolation 修復
- API / frontend 呼叫對齊

目前基線：

- `351 passed, 1 skipped, 1 warning`
- `next build` 通過

---

## 投影片 10｜為什麼這不是展示頁而已

目前可量化狀態：

- 16 個 dashboard routes
- 約 101 個 API handlers
- 44 個 backend test files
- 15 個 Flow Lab 商品
- 1262 個 workflow runs

重點：

> 這是一個真的有資料、有流程、有狀態的系統，不是單頁作品集

---

## 投影片 11｜我在裡面的角色

我做的事情跨四層：

- 產品與流程設計
- backend API 與 domain logic
- frontend operator UX
- reliability / debugging / test recovery

面試 framing：

> 我不是只做某一層，而是可以把產品邏輯、實作、驗證和維護串起來

---

## 投影片 12｜現在做到哪、下一步是什麼

現在：

- 主架構已成立
- 主流程可跑
- build / tests 綠燈
- Flow Lab 已能支撐真實決策流程

下一步：

- 更完整的 backend 單一真相
- family / variant 深化
- 更聰明的 bundle intelligence
- 最後一輪 UX 收斂

結尾：

> 我做的是一套正在變成熟的 AI operator system，而不是只完成一個 demo。
