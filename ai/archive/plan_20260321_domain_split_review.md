# Plan: Domain Split Review + Approval Unification
> 觸發：用戶指示「電商放電商、自媒體放自媒體，拆開」
> 日期：2026-03-21

## 背景決策（用戶確認）
- review_items = 只放需要 Sun 手動決策的高風險操作
- 電商審核（promote_product / approve_purchase / approve_screenshot / approve_video_analysis）→ 放在 /ecommerce 和 /flowlab
- 自媒體審核（publish_post / select_draft）→ 放在 /review（主要入口）
- /review 頁面加 domain 分頁 Tab（全部 | 自媒體 | 電商）

## Action Type → Domain 對應表
```
社群媒體（自媒體）：
  publish_post, select_draft, confirm_analysis

電商：
  promote_product, approve_purchase,
  approve_screenshot, approve_video_analysis
```

## 執行項目

### A — /review 頁加 Domain Tab（前端）
- 新增 DOMAIN_MAP: action_type → "social" | "ecommerce" | "system"
- 頁面頂部加 Tab（全部 / 自媒體 / 電商）
- Tab 各自顯示 pending count badge
- 選 Tab 後 visibleItems 只顯示對應 domain

### B — /ecommerce 頁面加「待電商審核」側邊面板
- fetchReviewQueue(status="pending") 在 ecommerce page 也呼叫
- 篩選出 ecommerce domain 項目
- 顯示 mini approval 卡片（名稱 + 操作按鈕）
- 有項目才顯示，無則不佔版面

### C — /flowlab 頁面加「待 Flow Lab 審核」panel
- 同上，篩選 approve_screenshot / approve_video_analysis

### D — Sidebar badge 語意修正
- 現在 badge 數量 = review_items pending + approval_requests pending
- 改為只計算 review_items pending（避免重複計算）

### E — 審核模型語意文件
- 在 src/api/routes/review.py 頂部加清楚的 docstring 說明職責分工
- `review_items` = operator-facing curated inbox（高風險手動決策）
- `approval_requests` = workflow internal gate（自動 / semi-auto）

## Codex 任務
- tests/test_review_domain_split.py — 測試 action_type → domain 邏輯
- 更新 sprint.md + progress-log.md

## 完成標準
- [ ] /review 有 自媒體 / 電商 Tab
- [ ] /ecommerce 有電商待審核面板
- [ ] /flowlab 有 Flow Lab 待審核面板
- [ ] Sidebar badge 只計 review_items
- [ ] TypeScript 0 errors
- [ ] Tests passing
