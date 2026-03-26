# AntiClaude — 專案概述
> 更新日期：2026-03-17

## 這是什麼
AntiClaude 是 Sun Lee 的虛擬帝國施工藍圖：一台 24 小時運轉的 AI 資產創造機。
管理兩個業務，目標是讓 Sun Lee 只做決策，其餘全部自動化。

**完整願景：** `projects/anticlaude/vision_sun_lee_empire.md`

## 兩大核心業務

### 1. Flow Lab — 電商印鈔機
- 極簡辦公與療癒風格品牌，在蝦皮販售
- Sun Lee 只決定「賣什麼」，其餘 AI 處理：市調 / 文案 / 競品追蹤 / 定價建議
- 目標：被動收入穩定成長，不需要每天盯後台

### 2. Threads @sunlee._.yabg — 毫不費力的影響力
- 快樂程式鴨人設，記錄 AI 學習與轉職旅程
- AI 幫 Sun Lee 每天找最新技術話題、寫好草稿、等他 Approve 發布
- GEO 優化：讓 Perplexity / ChatGPT / Gemini 主動引用 Sun Lee 的內容

## 核心業務流程

### 內容流程（每日自動）
Ori 搜尋 AI 最新動態（Google/Dcard/IG/FB）
→ Lala 選題（依受眾數據）
→ Craft 寫文案（含 GEO 優化）
→ Sage 評分
→ 送 Review Queue
→ Sun Lee 花 5 分鐘 Approve
→ 自動發布 Threads

### 選品流程（按需 + 夜班自動）
Sun Lee 加入候選商品 or 夜班 Ori 自動找候選
→ Ori 抓競品 + Sage 評分
→ Craft 寫 GEO 電商文案
→ Review Queue 送審
→ Sun Lee 決定進不進貨

### 競品監控（每週自動）
每週一 Ori 掃描在售商品競品均價
→ 跌幅 > 10%：LINE 通知 Sun Lee
→ 滯銷超過 14 天：自動標記警示

## 系統入口
- **主要入口：** http://localhost:3000/chat（CEO Console）
- **晨報：** http://localhost:3000/morning
- **審核：** http://localhost:3000/review
- **後端 API：** http://localhost:8000

## 成功標準（已升級）
- 每天 10 分鐘：看晨報 → 點 Approve → 走人
- Flow Lab 競品追蹤全自動，降價就收 LINE
- 貼文開始被 AI 引擎引用（GEO 生效）
- 夜班 AI 不需要指揮，自動推進任務

## Sun Lee 的禁區（任何 AI 都不能違反）
- 不誇大宣稱（「AI 會取代所有工作」這類）
- 不寫純技術教學（要有觀點，不是翻譯文件）
- 不政治議題
- 不業配感推薦
