# AITOS 技能武器庫（Skills Arsenal）
> 版本：v1.0
> 建立：2026-03-17
> 概念：技能就像武器裝備，隨時可以安裝到 Agent 身上，讓他們更強
> 擴充原則：新增技能只需要加一個 .md 檔 + 在 skill_loader.py 登記

---

## 武器庫架構

```
_hub/shared/skills/
├── composite/              ← 複合技能（已安裝，Agent 自動使用）
│   ├── content_creation.md          ✅ Craft
│   ├── marketing_strategy.md        ✅ Lala
│   ├── seo_optimization.md          ✅ Sage
│   ├── research_analysis.md         ✅ Ori
│   ├── geo_optimization_engine.md   ✅ Craft（新）
│   ├── ux_review.md                 ⚠️ Pixel（未自動化）
│   └── project_planning.md          ⚠️ Lumi（手動）
│
├── domain/                 ← 領域技能（待開發）
│   ├── threads_viral_hooks.md       📋 規劃中
│   ├── shopee_listing_optimizer.md  📋 規劃中
│   ├── smc_trade_analysis.md        📋 規劃中
│   └── notebooklm_synthesis.md      📋 規劃中
│
└── tools/                  ← 工具整合技能（待開發）
    ├── perplexity_deep_search.md    ✅ 已整合（Ori）
    ├── notebooklm_integration.md    📋 規劃中
    ├── figma_mcp.md                 📋 待 token
    └── line_messaging.md            ✅ 已整合
```

---

## 已安裝的武器（Active）

### content_creation — Craft 的核心武器
- **效果：** 讓貼文有人味、有 Hook、有鴨鴨風格
- **自動觸發：** task_type = draft_generation, copywriting
- **強化版：** + geo_optimization_engine = GEO 貼文

### marketing_strategy — Lala 的戰略武器
- **效果：** 讓選題有市場邏輯、有受眾精準度
- **自動觸發：** task_type = topic_strategy, audience_analysis

### seo_optimization — Sage 的分析武器
- **效果：** 讓內容有搜尋曝光度
- **自動觸發：** task_type = seo_analysis, product_evaluation

### research_analysis — Ori 的情報武器
- **效果：** 讓市調深入、競品分析精準
- **自動觸發：** task_type = content_research, market_analysis

### geo_optimization_engine — Craft 的升級武器（新）
- **效果：** 讓內容被 Perplexity/ChatGPT/Gemini 引用
- **自動觸發：** task_type = draft_generation, copywriting, content_research
- **三個模板：** 技術貼文（快樂程式鴨）/ 電商文案（Flow Lab）/ 交易複盤（SMC）

---

## 規劃中的武器（Planned）

---

### threads_viral_hooks — Craft 的病毒傳播武器

**目標：** 讓每篇貼文的前兩行就能讓人停下來看完

**內容：**
- Hook 公式庫（問題型 / 反直覺型 / 故事型 / 數字型）
- 鴨鴨風格語氣校準器
- A/B 測試學習記憶（哪種 Hook 在你的受眾裡最有效）

**安裝方式：**
```
新增：_hub/shared/skills/composite/threads_viral_hooks.md
修改：src/ai/claude_writer.py 加入 load_composite_skill("threads_viral_hooks")
```

---

### shopee_listing_optimizer — Craft 的電商文案武器

**目標：** 讓 Flow Lab 的每個蝦皮商品頁都能轉換

**內容：**
- 蝦皮標題 SEO 公式（含關鍵字密度）
- 商品描述結構（痛點 → 解方 → 規格 → 信任信號）
- Flow Lab 品牌語氣：極簡、療癒、有質感、不過度推銷
- GEO 版本：讓 AI 推薦「辦公療癒用品」時出現 Flow Lab

**安裝方式：**
```
新增：_hub/shared/skills/domain/shopee_listing_optimizer.md
觸發條件：CEO 路由到 copywriting + 上下文包含 "Flow Lab" or "蝦皮"
```

---

### smc_trade_analysis — Sage 的交易分析武器

**目標：** 讓交易複盤有結構、有 ICT 術語、可被 AI 引用

**內容：**
- SMC 市場結構分析框架（BOS / CHoCH / MSS）
- Order Block 選擇邏輯
- Fair Value Gap 觀察方法
- ICT 理論術語庫（供 GEO 嵌入）
- R:R 與停損設置標準

**安裝方式：**
```
新增：_hub/shared/skills/domain/smc_trade_analysis.md
觸發條件：CEO 路由到 data_analysis + 上下文包含交易相關詞
```

---

### notebooklm_synthesis — Ori 的深度研究武器

**目標：** 讓 Ori 不只是「找資料」，而是「合成洞見」

**背景：**
Google NotebookLM 可以把多個來源（PDF / 文章 / 筆記）合成成互動式知識庫。
Ori 目前用 Perplexity 搜尋 + Gemini 分析，可以升級成三層研究：

```
Layer 1：Perplexity 抓當天最新資訊（已有）
Layer 2：Gemini Deep Research 深度分析（已有）
Layer 3：NotebookLM 跨來源合成洞見（待整合）
         → 把多篇文章/技術文件上傳
         → 生成「今日技術快報 + 可用角度」
         → 直接餵給 Craft 寫貼文
```

**整合路線：**
- 短期：Ori 的 research prompt 加入「多來源對比分析」指令（不需要 API）
- 中期：NotebookLM API 開放後直接串接（2025 年預計開放）

---

### lightweight_model_routing — CEO 的省錢武器

**目標：** 不是所有任務都需要最強的模型，用對模型省 80% 成本

**路由邏輯：**
```
任務複雜度高（架構設計、多步驟分析）→ Claude Sonnet 4.6（現有）
任務中等（文案寫作、選題）→ Claude Haiku 4.5（快 3x，省 80%）
任務簡單（狀態查詢、格式化）→ Gemini Flash（幾乎免費）
圖片分析 → Claude Sonnet 4.6（視覺能力最強）
```

**效益：**
- 目前每次 Pipeline 全用 Sonnet，月成本 $X
- 加入模型路由後，預計降低 60-70% API 費用

---

## 安裝新技能的 SOP

任何時候你想讓 AI 學會新東西，只需要三步：

```
步驟 1：在 _hub/shared/skills/composite/ 建一個 .md 檔
        說清楚：這個技能是什麼、怎麼用、什麼時候觸發

步驟 2：在 skills_arsenal.md（本文件）登記

步驟 3：告訴 Claude Code：
        「幫我把 [技能名] 注入到 [Agent 名] 的 [任務類型]」
        → 修改 dynamic_orchestrator.py 或對應的 AI 模組
```

**這套系統的設計保證：永遠不需要重寫核心代碼，只加法。**

---

## 外部工具整合地圖

| 工具 | 現況 | 整合後能做什麼 | 難度 |
|------|------|-------------|------|
| Perplexity API | ✅ 已整合（Ori）| 即時聯網搜尋 | — |
| Claude API | ✅ 已整合（主要 LLM）| 寫作、分析、路由 | — |
| Gemini API | ✅ 已整合（Ori 聚類）| 深度研究、圖片分析 | — |
| GPT-4o | ✅ 已整合（Lala）| 行銷策略 | — |
| LINE Messaging | ✅ 已整合 | 即時通知 | — |
| NotebookLM | 📋 規劃中（API 待開放）| Ori 多來源合成洞見 | 低（API 開放後）|
| Figma MCP | 📋 待 token | Pixel 直接讀設計稿 | 低（有 token 後）|
| Threads API | ✅ 已整合（自動發文）| Craft 直接發布 | — |
| Google Search API | 📋 規劃中 | Ori 搜尋 Dcard/Google 趨勢 | 低 |
| Dcard API | 📋 規劃中 | Ori 抓 Dcard 熱門話題 | 中（非官方）|

---

## 願景完成度（對照 vision_sun_lee_empire.md）

### Flow Lab 電商印鈔機

| 功能 | 狀態 | 還差什麼 |
|------|------|---------|
| Ori 自動市調 | ✅ 完成 | — |
| Sage 選品評分 | ✅ 完成 | — |
| 競品降價 LINE 通知 | 🔄 進行中 | LINE API 測試通後上線 |
| GEO 電商文案 | ✅ 技能建好 | 需注入 Craft 觸發條件 |
| 蝦皮文案優化器 | 📋 規劃中 | shopee_listing_optimizer.md |
| 商品生命週期警示 | 📋 規劃中 | 電商 Phase |

**完成度：55%**

---

### Threads 毫不費力的影響力

| 功能 | 狀態 | 還差什麼 |
|------|------|---------|
| Ori 抓 AI 新聞 | ✅ 完成 | — |
| Craft 寫鴨鴨風格貼文 | ✅ 完成 | — |
| GEO 讓 AI 引擎引用 | ✅ 技能建好 | 需注入 + 實際測試 |
| Ori 搜 Dcard/IG/FB 趨勢 | 📋 規劃中 | Google Search API |
| A/B 測試機制 | 📋 規劃中 | drafts 表加欄位 |
| 自動發布 Threads | ✅ 完成 | — |

**完成度：65%**

---

### 你的時間解放

| 功能 | 狀態 | 還差什麼 |
|------|------|---------|
| 晨報（早上看昨晚成果）| ✅ 完成 | — |
| Review Queue（點核准）| ✅ 完成 | — |
| CEO Console（單一入口）| ✅ 完成 | — |
| Night Shift（夜間自治）| ✅ 完成 | — |
| LangGraph 多步驟自動接力 | 📋 規劃中 | Phase B |
| 首頁改版為極簡入口 | 📋 規劃中 | Phase C 後 |

**完成度：70%**

---

### 整體願景完成度：**約 63%**

核心功能都已到位，剩下的是「讓它更自動、更精準、更聰明」。

---

*武器庫版本：v1.0*
*更新原則：每次新增技能後在此登記*
