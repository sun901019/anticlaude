# Workflow SOP：每日內容流程
> 版本：v2.0（GEO + Format Selection + First-Reply + Memory Fabric）
> 觸發：你按「一鍵全部跑」或手動啟動 pipeline

## 流程圖
Ori（抓素材）→ Lala（選題 + Topic Fit Gate + Similarity Guard）→ Craft（寫文案 + GEO + First-Reply）→ Sage（評分）→ 你（決定發哪篇）

---

## 詳細步驟

### Step 1：Ori 抓素材
- 執行 `src/pipeline.py` 抓取模組
- 來源：RSS + Serper + Perplexity + Hacker News
- 產出：`ai/handoff/ori-to-lala.md`（15-20 則精華主題 + 熱度分數）
- **Memory Fabric**：抓取結果自動記錄至 `workflow_events`（event_type=content_fetched）
- AI Office 狀態：Ori → in_progress → done

### Step 2：Lala 選題
- 讀取 `ai/handoff/ori-to-lala.md`
- 執行 `ai/skills/select-topic.md` v2.0 SOP（含 Topic Fit Gate + Similarity Guard）
- **Topic Fit Gate**：剔除品牌適配分數 < 0.5 的主題
- **Similarity Guard**：對照近 7 天貼文，標注重疊率警告
- **Breakout Cooldown**：若昨日貼文互動率 > 5%，冷卻同類型 48 小時
- 產出：`ai/handoff/lala-to-craft.md`（Top 3 主題 + 格式建議 + GEO 實體建議）
- AI Office 狀態：Lala → in_progress → done，handoff → Craft

### Step 3：Craft 寫文案
- 讀取 `ai/handoff/lala-to-craft.md`
- 執行 `ai/skills/write-threads-post.md` v2.0 SOP
- **Format Selection**：依 Lala 建議格式（short / long / thread）決定字數
- **GEO Auto-inject**：系統自動注入 `geo_optimization_engine` skill（via dynamic_orchestrator）
- **GEO Entity Rules**：每篇正文嵌入 ≥1 個可引用實體
- **First-Reply Seed**：每篇生成一則 first_reply 留言種子
- **品質驗證**：Claude Haiku 二次審核，AI 痕跡分數 < 7 自動修正
- 產出：`outputs/drafts/YYYY-MM-DD_draft.md` + `ai/handoff/craft-to-sage.md`
- **Memory Fabric**：draft 自動記錄至 `artifacts` 表（producer=craft, type=draft）
- AI Office 狀態：Craft → in_progress → done，handoff → Sage

### Step 4：Sage 評分
- 讀取 `ai/handoff/craft-to-sage.md`
- 結合 Threads 歷史互動預測表現
- **First-Hour Engagement Plan**：為每篇草稿建議最佳發文時段 + first_reply 發送時機
- 產出：`ai/handoff/sage-to-you.md`（推薦發哪篇 + 理由 + 建議發文時段）
- AI Office 狀態：Sage → awaiting_human

### Step 5：你決策
- 看 AI Office 的 awaiting_human 提示
- 讀 `ai/handoff/sage-to-you.md`
- 選一篇 → 複製到 Threads 發文
- 發文後 5 分鐘內：發送 first_reply seed 留言

---

## 整體時間目標
完整流程：10 分鐘內

---

## 新增系統能力（v2.0）

| 能力 | 位置 | 效果 |
|------|------|------|
| Topic Fit Gate | Step 2（Lala） | 過濾品牌不匹配主題，保護受眾定位 |
| Similarity Guard | Step 2（Lala） | 防止 7 天內發相似主題，維持多樣性 |
| Breakout Cooldown | Step 2（Lala） | 保護高表現貼文的長尾流量 |
| GEO Auto-inject | Step 3（系統） | 自動注入 GEO skill，提升 AI 引擎可引用性 |
| First-Reply Seed | Step 3（Craft） | 觸發演算法第一波推播 |
| Memory Fabric | Step 1 + 3 | 所有產出自動記錄至 DB，可追溯 |
