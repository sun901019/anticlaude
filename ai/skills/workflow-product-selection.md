# Workflow SOP：Flow Lab 選品流程
> 觸發：你在 Dashboard 新增候選商品

## 流程圖
你新增候選 → Ori（抓競品）→ Sage（評分）→ Craft（產報告）→ 你（進 or 不進）

## 詳細步驟

### Step 1：你新增候選
- 在 `/ecommerce` Dashboard → 候選池 tab → 新增
- 填入：商品名稱 / 類別 / 來源平台 / 初步想法

### Step 2：Ori 抓競品資料
- 觸發：新增候選後自動（或手動點「開始分析」）
- 搜尋：Serper API 搜競品、蝦皮熱銷、負評
- 產出：`ai/handoff/ori-to-sage.md`（競品資料 + 市場信號）
- AI Office 狀態：Ori → in_progress → done

### Step 3：Sage 跑評分
- 讀取 `ai/handoff/ori-to-sage.md`
- 執行 `ai/skills/product-scoring.md` SOP
- 產出：評分寫入 `ecommerce_selection_analyses` 表 + `ai/handoff/sage-to-craft.md`
- AI Office 狀態：Sage → in_progress → done

### Step 4：Craft 產報告
- 讀取 `ai/handoff/sage-to-craft.md`
- 整理成可讀報告：商品角色 / 建議售價 / 主要風險 / 差異化機會
- 產出：`ecommerce_selection_reports` 表 + `ai/handoff/craft-to-you.md`
- AI Office 狀態：Craft → awaiting_human

### Step 5：你決策
- 看 AI Office 的 awaiting_human 提示
- 開啟選品報告 tab 查看完整報告
- 按「核准進貨」或「不進（附理由）」
- 系統自動寫入 lesson 到 `ecommerce_selection_lessons`
