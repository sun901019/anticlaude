# AntiClaude — 6 層 AI Agency 框架改造計畫
> 作者：Claude Code
> 日期：2026-03-14
> 執行者：Claude Code
> 目標：把現有系統改造成角色隔離 / 狀態隔離 / 文件交接的標準 AI Agency 架構

---

## 核心原則（執行前必讀）

多 Agent 系統的真正關鍵不是模型數量，而是：
1. **角色隔離** — 每個角色只看自己該看的東西
2. **狀態隔離** — 每個角色只做自己該做的事
3. **文件交接** — 做完要留下可交接的文件

---

## 注意事項（❗ 執行前全部讀完）

1. **不要動 `src/` 和 `dashboard/` 的任何程式碼** — 本計畫只改 AI 協作層文件，不碰業務邏輯
2. **不要刪除 `_context/` 舊資料夾** — 部分 agent 的 workflow 還在引用它，只新增不刪除
3. **不要刪除 `_hub/` 任何內容** — skills_library 是外部 repo clone，不能異動
4. **不要改 `_hub/shared/agents/` 的現有檔案** — 只新增 role-isolation 欄位，不重寫
5. **`CLAUDE.md` 要整個重寫** — 但先備份舊版到 `_archive/CLAUDE.md.bak`
6. **每個步驟完成後更新 `ai/state/progress-log.md`** — 這是本計畫的執行紀錄
7. **檔案內容有 template 標記 `{{}}` 的地方** — 都要填入真實內容，不要保留 template 語法
8. **所有新建的 .md 檔案** — 繁體中文為主，工具名稱保留英文

---

## 準備事項（開始前）

### P-1. 備份現有 CLAUDE.md
```bash
cp C:/Users/sun90/Anticlaude/CLAUDE.md C:/Users/sun90/Anticlaude/_archive/CLAUDE.md.bak
```

### P-2. 確認以下檔案存在（執行前核對）
- [ ] `_context/about_me.md` ← 要搬移內容
- [ ] `_context/workflow.md` ← 要搬移內容
- [ ] `_context/api_reference.md` ← 要搬移內容
- [ ] `_hub/shared/agents/content-strategist.md`
- [ ] `_hub/shared/agents/threads-writer.md`
- [ ] `_hub/shared/agents/sage.md`
- [ ] `_hub/shared/agents/pixel.md`
- [ ] `_hub/shared/skills/writing_guide.md`
- [ ] `_hub/shared/skills/strategy_guide.md`

### P-3. 建立新目錄結構
```bash
mkdir -p C:/Users/sun90/Anticlaude/ai/context
mkdir -p C:/Users/sun90/Anticlaude/ai/state
mkdir -p C:/Users/sun90/Anticlaude/ai/handoff
mkdir -p C:/Users/sun90/Anticlaude/ai/skills
```

---

## 第一層：主模型層

### 任務 1-1：重寫 `CLAUDE.md`

**檔案**：`C:/Users/sun90/Anticlaude/CLAUDE.md`
**動作**：整個替換（舊版已備份）

**新內容**：

```markdown
# CLAUDE.md — AntiClaude 主 AI 協作規則
> 系統版本：AI Agency 架構 v2.0
> 更新日期：2026-03-14

## 你是誰
你是 AntiClaude 的主 AI 協作者（Claude Code）。
負責：規劃、閱讀、整理、寫文件、架構決策、總控協調。
不負責：局部 bug fix、批量測試生成、CSS 微調（這些給 Codex）。

## 每次工作前，依序讀這些檔案

1. `ai/context/project-overview.md` — 專案是什麼
2. `ai/context/architecture.md` — 系統長什麼樣
3. `ai/state/current-task.md` — 現在在做什麼
4. 對應角色檔案（`_hub/shared/agents/`）
5. 對應 skill 檔案（`ai/skills/`）

**不要跳過讀檔步驟，不要憑空假設現狀。**

## 工作原則

- 先理解再修改，不憑空假設
- 小步修改，每次只改一件事
- 每輪工作後更新 `ai/state/progress-log.md`
- 重要決策寫入 `ai/state/decisions.md`
- 若是交接階段，必須在 `ai/handoff/` 寫交接文件
- 動手前先產出 plan_YYYYMMDD_任務名稱.md（非小改動）

## 角色派遣規則

| 使用者說… | 載入角色 | 角色檔案 |
|---------|---------|---------|
| 選題、今天發什麼、策略 | Lala（Content Strategist） | `_hub/shared/agents/content-strategist.md` |
| 寫文案、寫貼文、Hook | Craft（Threads Writer） | `_hub/shared/agents/threads-writer.md` |
| 數據分析、評分、競品 | Sage | `_hub/shared/agents/sage.md` |
| 寫程式、改後端、API | Lumi（Coding Agent） | `_hub/shared/agents/coding_agent.md` |
| UI、設計、前端 | Pixel | `_hub/shared/agents/pixel.md` |
| 研究、抓資料、選品候選 | Ori | `_hub/shared/agents/market_research_agent.md` |

## 分工：Claude Code vs Codex

| 任務類型 | 誰做 |
|---------|------|
| 跨檔案重構、新功能、架構決策 | Claude Code |
| 單檔 bug fix、批量測試、CSS 微調 | Codex（見 AGENTS.md）|

## 重要路徑快速索引

- 專案概述 → `ai/context/project-overview.md`
- 系統架構 → `ai/context/architecture.md`
- 當前任務 → `ai/state/current-task.md`
- 進度記錄 → `ai/state/progress-log.md`
- 決策紀錄 → `ai/state/decisions.md`
- 交接文件 → `ai/handoff/`
- 技能 SOP → `ai/skills/`
- 能力地圖 → `_hub/registry/capability_map.md`
```

---

### 任務 1-2：新建 `AGENTS.md`

**檔案**：`C:/Users/sun90/Anticlaude/AGENTS.md`
**動作**：新建（給 Codex CLI 看的規則）

**內容**：

```markdown
# AGENTS.md — Codex 協作規則
> 給 Codex CLI 或其他 implementation agent 使用
> 更新日期：2026-03-14

## 你是誰
你是 AntiClaude 的 implementation agent（Codex）。
負責：局部實作、bug fix、重構、測試生成、CSS 微調。
不負責：產品決策、架構設計、跨系統規劃（這些給 Claude Code）。

## 每次工作前，依序讀這些檔案

1. `ai/context/architecture.md` — 系統架構
2. `ai/state/current-task.md` — 當前任務
3. `ai/handoff/` — 是否有交接給你的任務文件

## 工作原則

- 先讀相關程式碼，再動手
- 只改任務範圍內的檔案，不要順手改其他東西
- 改完用 pytest 或 npm run build 驗證
- 完成後更新 `ai/state/progress-log.md`
- 有疑問就在 `ai/handoff/codex-questions.md` 寫下來

## 執行範圍

可以動的目錄：
- `src/`
- `dashboard/`
- `tests/`

不要動的目錄：
- `_hub/skills_library/`（外部 repo）
- `ai/`（協作層，不是業務邏輯）
- `_context/`（legacy，唯讀）

## 健康檢查清單（每次工作時順帶確認）

- [ ] API 路由和前端呼叫是否對應
- [ ] DB schema 和 query 邏輯是否一致
- [ ] 有沒有 hardcode 的 port 或路徑
- [ ] 有沒有未使用的 import 或 dead code
- [ ] 修改的功能有沒有對應測試
```

---

## 第二層：角色層

### 任務 2-1：為每個 agent 加上「只看這些」隔離規則

**動作**：編輯以下每個 agent 檔案，在最前面加上 `## 資訊隔離` 區段

**要加的區段模板**：
```markdown
## 資訊隔離（必須遵守）
### 只讀這些檔案
- （列出這個角色需要的檔案）

### 不要讀這些
- `src/` 程式碼（除非 Lumi）
- 其他角色的 handoff 文件
- 不相關的 context 檔案

### 完成後必須產出
- （列出這個角色的產出物）
```

**逐一處理的檔案與內容**：

#### `_hub/shared/agents/content-strategist.md`（Lala）
加在角色定義後：
```markdown
## 資訊隔離（必須遵守）
### 只讀這些檔案
- `ai/context/project-overview.md`（了解品牌定位）
- `_context/about_me.md`（受眾定義）
- `outputs/threads_metrics/`（最近 7 天數據）
- `ai/handoff/ori-to-lala.md`（如果存在，Ori 交給你的素材）

### 不要讀這些
- `src/` 任何程式碼
- `dashboard/` 任何程式碼
- ecommerce 相關檔案（那是 Sage/Ori 的事）

### 完成後必須產出
- `ai/handoff/lala-to-craft.md`（選出的主題 + 角度 + 理由）
```

#### `_hub/shared/agents/threads-writer.md`（Craft）
加在現有內容後：
```markdown
## 資訊隔離（必須遵守）
### 只讀這些檔案
- `ai/handoff/lala-to-craft.md`（Lala 給的選題）
- `ai/skills/write-threads-post.md`（寫作 SOP）
- `_context/about_me.md`（語氣規範）

### 不要讀這些
- 原始素材（Lala 已過濾）
- 數據表（那是 Lala/Sage 的事）
- 程式碼

### 完成後必須產出
- `ai/handoff/craft-to-sage.md`（草稿 + 兩個版本）
- 草稿存入 `outputs/drafts/YYYY-MM-DD_draft.md`
```

#### `_hub/shared/agents/sage.md`（Sage）
加在現有內容後：
```markdown
## 資訊隔離（必須遵守）
### 只讀這些檔案
- `ai/handoff/craft-to-sage.md`（Craft 交來的草稿）或
- `ai/handoff/ori-to-sage.md`（選品分析任務）
- `ai/skills/scoring-engine.md`（評分 SOP）
- 相關 DB 數據（audience_insights / ecommerce_selection_analyses）

### 不要讀這些
- 原始新聞素材（已聚類）
- 程式碼
- 其他角色的 handoff

### 完成後必須產出
- 內容評分：`ai/handoff/sage-to-pixel.md`（評分結果 + 建議選哪篇）
- 選品評分：更新 `ecommerce_selection_analyses` 並產 `ai/handoff/sage-to-craft.md`
```

#### `_hub/shared/agents/market_research_agent.md`（Ori）
加在現有內容後：
```markdown
## 資訊隔離（必須遵守）
### 只讀這些檔案
- `ai/context/project-overview.md`（了解品牌方向）
- `ai/state/current-task.md`（當前是內容任務還是選品任務）
- 搜尋 API 結果（Serper / Perplexity）

### 不要讀這些
- 歷史文案（那是 Craft 的素材）
- 評分數據（那是 Sage 的工作）
- 程式碼

### 完成後必須產出
- 內容任務：`ai/handoff/ori-to-lala.md`（素材清單 + 熱度分數）
- 選品任務：`ai/handoff/ori-to-sage.md`（競品資料 + 原始數據）
```

#### `_hub/shared/agents/pixel.md`（Pixel）
加在現有內容後：
```markdown
## 資訊隔離（必須遵守）
### 只讀這些檔案
- `ai/handoff/sage-to-pixel.md`（Sage 的評分和建議）
- `dashboard/src/app/globals.css`（現有設計 token）
- 相關 dashboard 頁面 `.tsx` 檔案

### 不要讀這些
- 業務邏輯程式碼
- 原始素材
- 數據表

### 完成後必須產出
- UI 改動（直接修改 dashboard 檔案，或產出 spec 給 Lumi）
- 如需 Lumi 實作：`ai/handoff/pixel-to-lumi.md`
```

#### `_hub/shared/agents/coding_agent.md`（Lumi）
加在現有內容後：
```markdown
## 資訊隔離（必須遵守）
### 只讀這些檔案
- `ai/context/architecture.md`（系統架構）
- `ai/state/current-task.md`（當前任務）
- `ai/handoff/pixel-to-lumi.md`（如果有 UI 實作任務）
- 相關 `src/` 程式碼

### 不要讀這些
- 內容文案相關檔案
- 選品策略相關檔案

### 完成後必須產出
- 程式碼修改（直接實作）
- 更新 `ai/state/progress-log.md`
- 如有後續：`ai/handoff/lumi-to-pixel.md`（需要 UI 確認的）
```

---

## 第三層：記憶層

### 任務 3-1：建立 `ai/context/project-overview.md`

**檔案**：`C:/Users/sun90/Anticlaude/ai/context/project-overview.md`
**動作**：新建，整合 README.md + START_HERE.md 的核心資訊

**內容**：
```markdown
# AntiClaude — 專案概述
> 更新日期：2026-03-14

## 這是什麼
AntiClaude 是一套 AI Agency 系統，管理兩個業務：
1. **個人品牌內容自動化**：為 Threads @sunlee._.yabg 每日產出 AI 相關內容
2. **Flow Lab 選品系統**：為辦公室療育品牌做蝦皮選品決策

## 目標使用者
- 台灣科技工作者（25-40 歲，工程師/PM/設計師）
- 對 AI 工具和職涯成長有興趣

## 核心業務流程

### 內容流程（每日）
抓取 AI 新聞 → Ori 整理 → Lala 選題 → Craft 寫文案 → Sage 評分 → 你決定發哪篇

### 選品流程（按需）
你加入候選商品 → Ori 抓競品 → Sage 評分 → Craft 產報告 → 你決定進不進貨

## 系統入口
- 後端 API：http://localhost:8000
- 前端儀表板：http://localhost:3000
- AI Office：http://localhost:3000/office

## 成功標準
- 每天早上 10 分鐘內選好今日發文主題
- 選品決策有數據支撐，不憑感覺
- AI Office 能看到團隊在做什麼

## 禁區（任何 AI 都不能違反）
- 不誇大宣稱（「AI 會取代所有工作」這類）
- 不寫純技術教學
- 不政治議題
- 不業配感推薦
```

---

### 任務 3-2：建立 `ai/context/architecture.md`

**檔案**：`C:/Users/sun90/Anticlaude/ai/context/architecture.md`
**動作**：新建，從 START_HERE.md 整合並更新到最新狀態

**內容**：
```markdown
# AntiClaude — 系統架構
> 更新日期：2026-03-14

## 技術棧

| 層 | 技術 | 路徑 | Port |
|----|------|------|------|
| 後端 API | Python FastAPI | `src/api/main.py` | 8000 |
| 前端 | Next.js 14 App Router | `dashboard/` | 3000 |
| 資料庫 | SQLite | `data/anticlaude.db` | — |
| AI 模型 | Claude Sonnet / Gemini Flash / GPT-4o | `src/ai/` | — |
| 自動化 | n8n（Flow Lab） | localhost | 5678 |

## 目錄結構

```
Anticlaude/
├── src/                    # Python 後端
│   ├── api/main.py         # FastAPI 主程式，所有路由
│   ├── agents/             # AI agent 邏輯（orchestrator, writer, judge...）
│   ├── ecommerce/          # Flow Lab 選品模組
│   ├── pipeline.py         # 每日內容流程
│   ├── db/schema.py        # 資料庫 schema
│   └── config.py           # 環境變數
├── dashboard/              # Next.js 前端
│   └── src/app/
│       ├── page.tsx        # 主控台
│       ├── office/         # AI Office
│       ├── ecommerce/      # Flow Lab 儀表板
│       ├── reports/        # 靈感報告
│       └── metrics/        # Threads 數據
├── ai/                     # AI 協作層（本框架）
│   ├── context/            # 永久記憶（專案/架構）
│   ├── state/              # 當前狀態（任務/進度/決策）
│   ├── handoff/            # 角色交接文件
│   └── skills/             # 技能 SOP
├── _hub/                   # AI-OS 中台
│   ├── shared/agents/      # 6 個 AI 角色定義
│   └── shared/skills/      # 技能定義
└── _context/               # Legacy（保留，部分 agent 還在用）
```

## 關鍵 API 路由

| 路由前綴 | 功能 |
|---------|------|
| `/api/agents/*` | AI Office 狀態、事件、handoff |
| `/api/ecommerce/*` | Flow Lab 在售商品管理 |
| `/api/ecommerce/selection/*` | Flow Lab 選品候選評估 |
| `/api/reports/*` | 每日內容報告 |
| `/api/metrics/*` | Threads 數據 |

## 資料庫主要表格

| 表格 | 用途 |
|------|------|
| `audience_insights` | Threads 互動回饋，影響選題 |
| `fl_products` | Flow Lab 在售商品 |
| `ecommerce_selection_candidates` | 選品候選池 |
| `ecommerce_selection_analyses` | 選品評分記錄 |
| `ecommerce_selection_lessons` | 選品學習記憶 |

## 已知問題（2026-03-14）

- AI Office SSE stream hardcode `http://localhost:8000`，需改走 Next.js rewrite
- Flow Lab Dashboard 5 個 tab 尚未實作（後端 API 已完成）
- Handoff 系統沒有 `blocked` / `done` 狀態
```

---

### 任務 3-3：建立 `ai/state/current-task.md`

**檔案**：`C:/Users/sun90/Anticlaude/ai/state/current-task.md`
**動作**：新建。**每次開始新任務都要更新這個檔案。**

**初始內容**：
```markdown
# Current Task
> 每次開始新任務前更新此檔案

## 當前目標
框架改造：建立 AI Agency 6 層協作結構

## 任務背景
原系統缺少角色隔離、狀態隔離、文件交接機制。
此次改造不動業務邏輯（src/ dashboard/），只建立協作層（ai/）。

## 範圍（做這些）
- 建立 ai/context/, ai/state/, ai/handoff/, ai/skills/ 目錄
- 重寫 CLAUDE.md
- 新建 AGENTS.md
- 為每個 agent 加資訊隔離規則
- 建立 handoff 模板
- 建立 skills SOP

## 不做什麼
- 不改 src/ 任何程式碼
- 不改 dashboard/ 任何程式碼
- 不刪除 _context/ 舊目錄
- 不動 _hub/skills_library/

## 驗收標準
- [ ] ai/ 目錄結構完整建立
- [ ] CLAUDE.md 有正確的讀取順序
- [ ] AGENTS.md 存在且有 Codex 工作規則
- [ ] 每個 agent 有資訊隔離區段
- [ ] 所有 handoff 模板存在
- [ ] 所有 skill SOP 存在

## 目前阻礙
無
```

---

### 任務 3-4：建立 `ai/state/progress-log.md`

**檔案**：`C:/Users/sun90/Anticlaude/ai/state/progress-log.md`
**動作**：新建。**每完成一個任務區塊就更新。**

**初始內容**：
```markdown
# Progress Log
> 每輪工作後更新

## 格式
---
## YYYY-MM-DD HH:mm
- 角色：Claude Code
- 本輪目標：
- 已完成：
- 修改/新增檔案：
- 遇到問題：
- 下一步：
---

## 2026-03-14
- 角色：Claude Code（規劃）
- 本輪目標：建立框架改造計畫
- 已完成：產出 plan_20260314_framework_migration.md
- 修改/新增檔案：projects/anticlaude/plan_20260314_framework_migration.md
- 遇到問題：無
- 下一步：Claude Code 執行本計畫
```

---

### 任務 3-5：建立 `ai/state/decisions.md`

**檔案**：`C:/Users/sun90/Anticlaude/ai/state/decisions.md`
**動作**：新建。**每次做了重要決策就更新。**

**初始內容**：
```markdown
# Decisions
> 記錄為什麼這樣做，避免以後搞忘

## 格式
---
## 決策標題
- 日期：
- 背景：
- 決定：
- 理由：
- 影響範圍：
---

## 不刪除 _context/ 而是保留
- 日期：2026-03-14
- 背景：部分 agent 的 workflow 步驟還在引用 _context/ 路徑
- 決定：保留 _context/，新系統用 ai/context/，兩者並存
- 理由：避免改壞現有 agent 工作流程
- 影響範圍：ai/context/ 為新的主要記憶，_context/ 為 legacy 唯讀

## 技能層採用 SOP 格式而非能力描述
- 日期：2026-03-14
- 背景：_hub/shared/skills/ 裡的檔案是「能做什麼」，不是「怎麼做」
- 決定：在 ai/skills/ 建立 SOP 版技能，_hub/shared/skills/ 保留不動
- 理由：兩層分工：能力定義 vs 執行步驟
- 影響範圍：ai/skills/ 為新的執行 SOP，_hub/shared/skills/ 為能力索引
```

---

## 第四層：技能層

### 任務 4-1：建立 `ai/skills/write-threads-post.md`

**檔案**：`C:/Users/sun90/Anticlaude/ai/skills/write-threads-post.md`
**動作**：新建（從 writing_guide.md 提取 SOP 步驟）

**內容**：
```markdown
# Skill SOP：寫 Threads 貼文
> 執行者：Craft
> 輸入：lala-to-craft.md（選定主題 + 角度）
> 輸出：兩個版本草稿 + outputs/drafts/YYYY-MM-DD_draft.md

## 執行步驟

1. 讀取 `ai/handoff/lala-to-craft.md`，確認選定主題與受眾角度
2. 確認主題類型（AI工具 / 趨勢 / 職涯 / 個人成長）
3. 寫 Hook：先寫 3 個版本，選最強的
   - 數字型：「用 AI 工作 30 天，我發現一件事」
   - 反問型：「你知道 PM 最怕什麼嗎」
   - 揭露型：「大家都誤解了 GPT-5 這個功能」
4. 填充主體：2-5 段，每段 2-4 行，具體 > 抽象
5. 加結尾 CTA（軟性互動，不要說「按讚分享」）
6. 對照禁用詞清單（見 _hub/shared/skills/writing_guide.md）
7. 輸出兩個版本：長版（200-300字）/ 短版（80-150字）
8. 存入 `outputs/drafts/YYYY-MM-DD_draft.md`
9. 更新 `ai/handoff/craft-to-sage.md`

## 品質門檻
- 讀起來像「朋友在 Threads 上分享一件事」
- 評分需達 43/50（見 writing_guide.md 評分標準）
- 沒有禁用詞、沒有翻譯腔
```

---

### 任務 4-2：建立 `ai/skills/select-topic.md`

**檔案**：`C:/Users/sun90/Anticlaude/ai/skills/select-topic.md`
**動作**：新建

**內容**：
```markdown
# Skill SOP：選題策略
> 執行者：Lala
> 輸入：ori-to-lala.md（素材清單）+ Threads 最近 7 天數據
> 輸出：lala-to-craft.md（Top 3 主題 + 角度 + 理由）

## 執行步驟

1. 讀取 `ai/handoff/ori-to-lala.md`
2. 讀取 `outputs/threads_metrics/` 最近 7 天，找出高互動主題模式
3. 讀取 `_context/about_me.md` 確認受眾定位
4. 依以下維度評分每個素材（1-10）：
   - 受眾匹配度：台灣科技工作者會在意嗎？
   - 時效性：這個話題現在討論熱嗎？
   - 差異性：這個角度別人說過嗎？
   - 品牌適配：符合 AI工具/職涯/成長 方向嗎？
5. 選出 Top 3，每個附上：選定角度 + 選擇理由 + 建議版型（長/短）
6. 確認主題比例不失衡（連續 3 天不能都是同類型）
7. 輸出到 `ai/handoff/lala-to-craft.md`

## 選題禁區
- 不選純技術教學（受眾不是工程師為主）
- 不選政治話題
- 不選業配感重的工具推薦
```

---

### 任務 4-3：建立 `ai/skills/product-scoring.md`

**檔案**：`C:/Users/sun90/Anticlaude/ai/skills/product-scoring.md`
**動作**：新建

**內容**：
```markdown
# Skill SOP：Flow Lab 選品評分
> 執行者：Sage
> 輸入：ori-to-sage.md（競品資料）
> 輸出：評分報告 + sage-to-craft.md

## 評分公式
score = demand×2 + profit×2 + pain_points + competition + brand_fit
最高 50 分

## 各維度評分標準

### Demand（需求度）1-10
- 9-10：搜尋量大、多平台討論、持續需求
- 5-8：有穩定搜尋、但不是熱門
- 1-4：搜尋量低或只是短期爆紅

### Profit（利潤空間）1-10
- 進貨成本 × 2.5 以下賣得掉 → 4 分以下
- 進貨成本 × 3 以上可以賣 → 7 分以上
- 有廣告空間（ROAS > 3）→ 加 1 分

### Pain Points（痛點機會）1-10
- 競品 1-2 星評論中有明確可解決的抱怨 → 高分
- 痛點可以用產品改良解決 → 額外加分

### Competition（競爭健康度）1-10
- 有清晰價格梯次、多元差異化 → 高分
- 全部商品同質同價（價格戰） → 低分

### Brand Fit（品牌適配）1-10
- 辦公、桌面、療育、工作效率相關 → 高分
- 和 Flow Lab 定位無關 → 低分

## 評分結果判讀
- 40-50：強力候選，建議進貨
- 35-39：可行候選，觀察後進
- 30-34：觀察名單，暫不進
- <30：目前拒絕

## 輸出格式
每個候選商品產出：score_total + score_breakdown + recommended_role（traffic/profit/hero）+ reasoning
```

---

## 第五層：工作流層

### 任務 5-1：建立 `ai/skills/workflow-daily-content.md`

**檔案**：`C:/Users/sun90/Anticlaude/ai/skills/workflow-daily-content.md`
**動作**：新建

**內容**：
```markdown
# Workflow SOP：每日內容流程
> 觸發：你按「一鍵全部跑」或手動啟動 pipeline

## 流程圖
Ori（抓素材）→ Lala（選題）→ Craft（寫文案）→ Sage（評分）→ 你（決定發哪篇）

## 詳細步驟

### Step 1：Ori 抓素材
- 執行 `src/pipeline.py` 抓取模組
- 來源：RSS + Serper + Perplexity + Hacker News
- 產出：`ai/handoff/ori-to-lala.md`（15-20 則精華主題 + 熱度分數）
- AI Office 狀態：Ori → in_progress → done

### Step 2：Lala 選題
- 讀取 `ai/handoff/ori-to-lala.md`
- 執行 `ai/skills/select-topic.md` SOP
- 產出：`ai/handoff/lala-to-craft.md`（Top 3 主題）
- AI Office 狀態：Lala → in_progress → done，handoff → Craft

### Step 3：Craft 寫文案
- 讀取 `ai/handoff/lala-to-craft.md`
- 執行 `ai/skills/write-threads-post.md` SOP
- 產出：`outputs/drafts/YYYY-MM-DD_draft.md` + `ai/handoff/craft-to-sage.md`
- AI Office 狀態：Craft → in_progress → done，handoff → Sage

### Step 4：Sage 評分
- 讀取 `ai/handoff/craft-to-sage.md`
- 結合 Threads 歷史互動預測表現
- 產出：`ai/handoff/sage-to-you.md`（推薦發哪篇 + 理由）
- AI Office 狀態：Sage → awaiting_human

### Step 5：你決策
- 看 AI Office 的 awaiting_human 提示
- 讀 `ai/handoff/sage-to-you.md`
- 選一篇 → 複製到 Threads 發文

## 整體時間目標
完整流程：10 分鐘內
```

---

### 任務 5-2：建立 `ai/skills/workflow-product-selection.md`

**檔案**：`C:/Users/sun90/Anticlaude/ai/skills/workflow-product-selection.md`
**動作**：新建

**內容**：
```markdown
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
```

---

## 第六層：交接模板建立

### 任務 6-1：建立所有 handoff 模板

為每個交接節點建立模板檔案（初始為空，執行時填入）：

**`ai/handoff/ori-to-lala.md`**：
```markdown
# Handoff：Ori → Lala
> 日期：
> 任務：每日內容素材

## Ori 已完成
- 抓取來源：
- 總素材數：
- 精華主題列表：（附熱度分數）

## 給 Lala 的任務
從上面選出今日發文 Top 3 主題，每個附角度建議。

## 注意事項
- 確認近 3 天主題類型分佈（不要連續同類型）
- 參考 outputs/threads_metrics/ 最近高互動模式

## 相關檔案
- 原始素材：outputs/daily_reports/YYYY-MM-DD.md
```

**`ai/handoff/lala-to-craft.md`**：
```markdown
# Handoff：Lala → Craft
> 日期：
> 任務：文案創作

## Lala 已選定

### 主題 1（推薦發這篇）
- 主題：
- 角度：
- 選擇理由：
- 建議版型：長版 / 短版

### 主題 2（備用）
- 主題：
- 角度：

### 主題 3（備用）
- 主題：
- 角度：

## 給 Craft 的任務
針對主題 1 寫兩個版本（長 + 短），主題 2/3 各寫一版備用。

## 注意事項
- 受眾：台灣科技工作者，朋友聊天語氣
- Hook 先寫 3 個選最強的
- 套用 ai/skills/write-threads-post.md SOP
```

**`ai/handoff/craft-to-sage.md`**：
```markdown
# Handoff：Craft → Sage
> 日期：
> 任務：文案評分

## Craft 已產出
- 草稿位置：outputs/drafts/YYYY-MM-DD_draft.md
- 版本數：

## 草稿摘要
（貼入各版本第一行 Hook）

## 給 Sage 的任務
評估各版本的受眾匹配度（1-10），推薦發哪一篇，附理由。
```

**`ai/handoff/sage-to-pixel.md`** / **`ai/handoff/sage-to-you.md`**：
```markdown
# Handoff：Sage → 你（決策）
> 日期：
> 任務：選擇今日發文

## Sage 評分結果

| 版本 | 受眾匹配 | 預測互動 | 綜合分數 |
|------|---------|---------|---------|
| 版本 A（長）| | | |
| 版本 B（短）| | | |

## Sage 建議
推薦：版本 X
理由：

## 你需要做的事
選一篇 → 複製到 Threads 發文
```

**`ai/handoff/ori-to-sage.md`**：
```markdown
# Handoff：Ori → Sage
> 日期：
> 任務：選品評分

## 候選商品
- 商品名稱：
- 類別：
- 來源：

## Ori 找到的資料
- 競品數量：
- 競品價格範圍：
- 蝦皮搜尋熱度：
- 主要負評痛點：
- 市場類型判斷：demand / trend / problem / hybrid

## 給 Sage 的任務
執行 ai/skills/product-scoring.md SOP，產出完整評分。
```

**`ai/handoff/sage-to-craft.md`**（選品版）：
```markdown
# Handoff：Sage → Craft
> 日期：
> 任務：產選品報告

## 評分結果
- 總分：/ 50
- 各維度：demand= / profit= / pain_points= / competition= / brand_fit=
- 建議角色：traffic / profit / hero
- 建議結論：進貨 / 觀察 / 拒絕

## 關鍵數據
- 建議進貨價：
- 建議售價：
- 預估毛利率：
- 主要風險：
- 差異化機會：

## 給 Craft 的任務
把以上資料整理成可讀的選品報告，讓老闆 10 秒內看懂「要不要進」。
```

**`ai/handoff/pixel-to-lumi.md`**：
```markdown
# Handoff：Pixel → Lumi
> 日期：
> 任務：UI 實作

## Pixel 的設計規格
- 修改頁面：
- 變更說明：
- 設計稿 / 描述：

## 給 Lumi 的任務
實作上述 UI 變更。

## 注意事項
- 使用現有 design token（globals.css）
- 不要改業務邏輯，只改 UI 層
- 完成後截圖或描述給 Pixel 確認
```

---

## 建議事項（整體優化）

### 建議 1：把 `_context/` 的內容同步到 `ai/context/`
`_context/about_me.md` 裡有重要的受眾定義，但路徑分散。
建議在 `ai/context/project-overview.md` 加入關鍵摘要，讓未來不需要讀兩個地方。

### 建議 2：`outputs/office_memory/agent_events.jsonl` 定期清理
隨著系統使用，這個 log 檔案會越來越大。
建議在 pipeline 裡加一個每週歸檔邏輯（超過 7 天的 events 壓縮存檔）。

### 建議 3：handoff 檔案執行後要清空（或歸檔）
`ai/handoff/*.md` 每次執行後應該清空或移到 `ai/handoff/_archive/YYYY-MM-DD/`
避免下次執行時讀到舊的交接資料。

### 建議 4：`ai/state/current-task.md` 每次新任務前必須更新
這是最容易被忽略但最重要的一步。
建議在 `CLAUDE.md` 的工作原則裡明確標注：**工作前第一件事是更新 current-task.md**。

---

## 執行順序總覽

| 順序 | 任務 | 動作 | 預計影響 |
|------|------|------|---------|
| 1 | P-1 備份 CLAUDE.md | cp 指令 | 無 |
| 2 | P-2 確認檔案存在 | 核對清單 | 無 |
| 3 | P-3 建立目錄 | mkdir | 無 |
| 4 | 1-1 重寫 CLAUDE.md | 整個替換 | 影響所有後續對話 |
| 5 | 1-2 新建 AGENTS.md | 新建 | 無 |
| 6 | 3-1 project-overview.md | 新建 | 無 |
| 7 | 3-2 architecture.md | 新建 | 無 |
| 8 | 3-3 current-task.md | 新建 | 無 |
| 9 | 3-4 progress-log.md | 新建 | 無 |
| 10 | 3-5 decisions.md | 新建 | 無 |
| 11 | 2-1 agent 隔離規則 | 逐一編輯 6 個 agent | 影響角色行為 |
| 12 | 4-1 write-threads-post SOP | 新建 | 無 |
| 13 | 4-2 select-topic SOP | 新建 | 無 |
| 14 | 4-3 product-scoring SOP | 新建 | 無 |
| 15 | 5-1 workflow daily content | 新建 | 無 |
| 16 | 5-2 workflow product selection | 新建 | 無 |
| 17 | 6-1 handoff 模板（8個）| 新建 | 無 |
| 18 | progress-log.md 更新 | 記錄本次執行 | 無 |

**總計：18 個步驟，全部是新建或文件修改，不碰業務程式碼。**
