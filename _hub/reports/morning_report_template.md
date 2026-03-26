# Morning Report — {{DATE}}
> 生成時間：{{GENERATED_AT}}
> 生成者：AntiClaude System

---

## 昨晚完成了什麼
- Pipeline 狀態：{{PIPELINE_STATUS}}
- 草稿生成：{{DRAFTS_COUNT}} 篇（主題：{{TOPICS_COUNT}} 個）
- 發布情況：{{POSTS_PUBLISHED}} 篇已發布
- Threads 同步：{{TRACKER_STATUS}}

## 昨日數據
- 平均互動率：{{YESTERDAY_AVG_ENGAGEMENT}}%
- 最高互動貼文：{{YESTERDAY_BEST_POST}}
- 瀏覽數：{{YESTERDAY_VIEWS}}

## 目前進度
- Pipeline 狀態：{{CURRENT_PIPELINE_STATUS}}
- Flow Lab 待審：{{PENDING_CANDIDATES}} 個候選商品
- 週報狀態：{{WEEKLY_STATUS}}
- 下次 Pipeline：{{NEXT_PIPELINE_COUNTDOWN}}

## 卡在哪裡（Blocked）
{{#BLOCKED_ITEMS}}
- [ ] {{ITEM}}
{{/BLOCKED_ITEMS}}
{{^BLOCKED_ITEMS}}
- 無阻塞事項
{{/BLOCKED_ITEMS}}

## 需要你決定的事
{{#AWAITING_HUMAN}}
- [ ] {{DECISION_ITEM}}（by {{AGENT}}）
{{/AWAITING_HUMAN}}
{{^AWAITING_HUMAN}}
- 目前無待決策事項
{{/AWAITING_HUMAN}}

## 建議今日第一步
1. {{SUGGESTED_FIRST_ACTION}}

## 系統健康
- 後端 API：{{API_STATUS}}
- 資料庫：{{DB_STATUS}}
- 排程器：{{SCHEDULER_STATUS}}
- 有無錯誤：{{ERROR_SUMMARY}}

---
*此模板由 `GET /api/morning/briefing` 端點填充*
*格式版本：1.0 | 建立日期：2026-03-16*
