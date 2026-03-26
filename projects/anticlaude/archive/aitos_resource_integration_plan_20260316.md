# AITOS 外部資源整合規劃
> 建立日期：2026-03-16
> 基於：用戶提供資源清單 + Gap Analysis Report（ai_os_gap_analysis_20260316.md）
> 原則：最小侵入、用現有、加新的、不動舊的

---

## 一、資源快速裁決表

| 資源 | 類型 | 對現有系統的用途 | 裁決 | 優先度 |
|------|------|----------------|------|--------|
| **Claude HUD** | Dev 工具 | 顯示 Claude Code 工作狀態（context 用量、todo、agent 活動） | ✅ 有用（開發期） | 低 |
| **Magic UI** | UI 元件庫 | CEO Console / Chat UI 的動態背景、光影特效 | ✅ 有用（Phase 3） | 中 |
| **Aceternity UI** | UI 元件庫 | Agent 狀態動畫、AI Office 升級、Chat UI | ✅ 有用（Phase 3） | 中 |
| **Shadcn UI** | UI 元件庫 | 系統已在用 Tailwind，補充 Command palette、Calendar | ✅ 有用（Phase 2） | 高 |
| **React Aria** | 無障礙庫 | 非同步操作穩定性（Chat UI 輸入框） | 🟡 備用 | 低 |
| **React Bits** | 微互動 | 小動畫點綴 | 🟡 備用 | 低 |
| **OpenAI Agents SDK** | Python 框架 | 參考多 agent handoff 邏輯，強化 CEO Orchestrator | ✅ 有用（Phase 4 參考） | 中 |
| **Figma MCP + Claude Code** | 執行工具 | Lumi 的設計→程式碼自動化 | ✅ 有用（Phase 3） | 中 |
| **GoodUX Skills** | Skill 模板 | Pixel UX 審核 | ✅ 有用（立即可放入） | 高 |
| **Marketing Skills** | Skill 模板 | Craft 電商內容 + Lala 策略 | ✅ 有用（立即可放入） | 高 |
| **Geo-SEO Claude** | Skill 模板 | Sage 品牌搜尋排名分析 | ✅ 有用（立即可放入） | 中 |
| **Awesome Agent Skills (ZH-TW)** | Skill 模板 | 通用技能庫，補充現有 agents | ✅ 有用（立即可放入） | 高 |
| **Awesome Agent Skills (Global)** | Skill 模板 | 通用技能庫，英文版 | 🟡 選擇性使用 | 低 |
| **AI Night Shift 類** | 自治框架 | 夜班模式參考（Phase 5） | 🟡 參考架構 | 低 |

---

## 二、與現有系統的對應關係

### 2.1 已在 _hub/skills_library/ 的資源（確認現況）

以下資源掃描顯示**已 clone 到本地**：

| 資源 | 位置 | 現狀 |
|------|------|------|
| agency-agents | `_hub/skills_library/agency-agents/` | ✅ 已 clone，未 composite 化 |
| marketingskills | `_hub/skills_library/marketingskills/` | ✅ 已 clone，未提取 |
| awesome-agent-skills (ZH-TW) | `_hub/skills_library/` | ✅ 已 clone，未提取 |
| awesome-agent-skills (Global) | `_hub/skills_library/` | ✅ 已 clone，未提取 |
| geo-seo-claude | `_hub/skills_library/` | ✅ 已 clone，未提取 |
| Humanizer-zh | `_hub/skills_library/` | ✅ 已 clone，未提取 |
| SKILLS All-in-one | `_hub/skills_library/` | ✅ 已 clone，未提取 |

**結論：原料都在，缺的是 extraction → composite 編排這一步。**

### 2.2 尚未存在的資源（需要新增）

| 資源 | 需要的動作 |
|------|-----------|
| Claude HUD | 安裝 npm package（開發環境），不影響生產 |
| Magic UI | `npm install` 到 dashboard，僅新增 |
| Aceternity UI | `npm install` 到 dashboard，僅新增 |
| Shadcn UI（補充件） | 補裝 Command、Calendar 元件 |
| Figma MCP | 設定 MCP config，Lumi 使用 |
| GoodUX Skills | 從 skills_library 提取，放入 `_hub/shared/skills/` |

---

## 三、Agent 技能分配表

> 每個 Agent 應調用哪些外部資源

### Ori — 研究主導
| 技能來源 | 用途 | 狀態 |
|---------|------|------|
| `agency-agents` 的 research prompt | 競品研究、市場分析 | 待 composite 化 |
| `awesome-agent-skills` 的 research 模組 | 通用研究 SOP | 待提取 |
| Perplexity scraper（現有） | 自動抓資料 | ✅ 運作中 |

### Lala — 策略主導
| 技能來源 | 用途 | 狀態 |
|---------|------|------|
| `marketingskills` 的 strategy 模組 | 行銷漏斗規劃 | 待提取 |
| `awesome-agent-skills` 的 planning 模組 | 任務拆解 SOP | 待提取 |
| `_hub/shared/skills/strategy_guide.md`（現有） | 策略框架 | ✅ 存在 |

### Craft — 內容主導
| 技能來源 | 用途 | 狀態 |
|---------|------|------|
| `marketingskills` 的 content 模組 | 電商文案 + Threads 貼文 | 待提取 |
| `Humanizer-zh` | 中文人性化改寫 | 待整合 |
| `_hub/shared/skills/writing_guide.md`（現有） | 寫作標準 | ✅ 存在 |
| `SKILLS All-in-one` 的寫作區塊 | 進階寫作技法 | 待提取 |

### Sage — 分析主導
| 技能來源 | 用途 | 狀態 |
|---------|------|------|
| `geo-seo-claude` | 品牌 SEO 分析、搜尋排名優化 | 待整合 |
| `awesome-agent-skills` 的 analytics 模組 | 數據分析 SOP | 待提取 |
| `_hub/shared/skills/seo_optimization.md`（現有） | SEO 框架 | ✅ 存在 |

### Lumi — 工程主導
| 技能來源 | 用途 | 狀態 |
|---------|------|------|
| `Figma MCP + Claude Code` | 設計稿→程式碼 | 待設定 |
| `OpenAI Agents SDK` | 參考 handoff 邏輯 | 待研究 |
| `_hub/shared/skills/dev_tools.md`（現有） | 工程 SOP | ✅ 存在 |

### Pixel — 設計主導
| 技能來源 | 用途 | 狀態 |
|---------|------|------|
| `GoodUX Skills` | UX 審核 checklist | 待提取 |
| `Magic UI` | CEO Console 動態背景 | 待安裝 |
| `Aceternity UI` | Agent 狀態動畫升級 | 待安裝 |
| `React Bits` | 微互動元件 | 待安裝（備用） |

---

## 四、與 Gap Analysis 的對應

> 這些資源能填補哪些已知缺口

| Gap Analysis 缺口 | 對應資源 | 填補程度 |
|------------------|---------|---------|
| Single Entry Interface | Magic UI + Aceternity UI（視覺） | 部分填補（UI 層） |
| CEO Console UI | Shadcn Command palette + Aceternity | 部分填補（UI 層） |
| Composite Skills Layer | 所有 skills_library 內容提取 | 可大幅填補 |
| Morning Report 格式 | `awesome-agent-skills` 的 reporting 模組 | 部分參考 |
| Execution Routing | OpenAI Agents SDK 邏輯參考 | 參考架構用 |
| Figma → Code 自動化 | Figma MCP | 新增能力 |
| Night Shift Mode | ai-night-shift 類框架 | 架構參考 |

---

## 五、Claude HUD 的特殊用途

**Claude HUD 不是生產系統的一部分，而是開發工具。**

用途：
- 開發 CEO Console 時，用來監控 Claude Code 的 context 用量
- Sprint 執行時，顯示 todo list 進度
- 調試 agent handoff 時，看 tool 使用情況

**安裝方式**（開發環境，不影響生產）：
```bash
# 在 Claude Code 設定中加入此 statusline plugin
# 不需要修改任何 AntiClaude 專案程式碼
```

建議：在 Claude Code 環境裡安裝，Lumi 開發時使用。

---

## 六、最終整合優先度路線

### 立即可做（Phase 1，✅ 完成 2026-03-16）

```
_hub/shared/skills/composite/
├── research_analysis.md         ✅ 已建立（Ori 用）
├── content_creation.md          ✅ 已建立 + 注入 claude_writer.py
├── marketing_strategy.md        ✅ 已建立 + 注入 gpt_strategist.py
├── seo_optimization.md          ✅ 已建立 + 注入 claude_scorer.py
├── ux_review.md                 ✅ 已建立（Pixel 用）
└── project_planning.md          ✅ 已建立（Lumi 用）

_hub/registry/
├── composite_skills_registry.md ✅ 已建立
└── registry_schema.json         ✅ 已建立（JSON schema）

src/ai/
└── skill_loader.py              ✅ 已建立（統一載入 + lru_cache）
```

---

### Phase 2 — UI 元件安裝（✅ 完成 2026-03-16）

```bash
# 已完成
npx shadcn@latest add command    ✅ Command palette（CEO Console 快速指令）
npx shadcn@latest add calendar   ✅ /calendar 頁日曆元件
```

---

### Phase 3 — CEO Console UI（✅ 部分完成 2026-03-16）

| 項目 | 狀態 | 備註 |
|------|------|------|
| `/chat` 頁面建立 | ✅ 完成 | 含指令路由 + agent 狀態側欄 |
| `POST /api/chat`（CEO Agent）| ✅ 完成 | claude-sonnet-4-6 意圖偵測 |
| `src/agents/ceo.py` | ✅ 完成 | 路由邏輯 + 對話歷史 |
| Aceternity UI 動畫 | ⏳ Phase 4 | 視覺升級，功能已完整 |
| Magic UI 光影 | ⏳ Phase 4 | 視覺升級，功能已完整 |

---

### Phase 4 — Figma MCP 設定（⏳ 待 Figma Access Token）

```json
// .claude/mcp.json 新增（待用戶提供 token 後執行）
{
  "figma": {
    "command": "figma-mcp",
    "description": "Lumi 的設計→程式碼橋接"
  }
}
```

---

### 延後處理（Phase 5+）

| 資源 | 延後原因 |
|------|---------|
| OpenAI Agents SDK | Phase 4 才需要，現在 orchestrator 夠用 |
| AI Night Shift 整合 | 需要先完成 CEO Orchestrator |
| React Aria | 無障礙需求目前不急 |
| Awesome Agent Skills (Global) | 中文版優先，英文版等有需求再看 |

---

## 七、現有 skills 與新資源的不重疊性確認

> 確保不做重複工作

| 現有 skill 文件 | 對應的新資源 | 關係 |
|----------------|-------------|------|
| `writing_guide.md` | `marketingskills` + `Humanizer-zh` | **補充**（現有保留，新的加強） |
| `strategy_guide.md` | `marketingskills/strategy` | **補充** |
| `seo_optimization.md` | `geo-seo-claude` | **強化**（合併精華） |
| `dev_tools.md` | OpenAI Agents SDK | **參考**（不替換） |
| `project_planning.md` | `awesome-agent-skills/planning` | **補充** |

**結論：沒有重疊衝突，全部是加法關係。**

---

## 八、總結建議

1. **現有 skills_library 裡已有 7 個 repo**，原料充足，現在只差「提取 + composite 化」
2. **UI 元件庫**（Shadcn/Magic/Aceternity）對 CEO Console 非常有用，但要等 Phase 3
3. **Claude HUD** 是給 Lumi 自己用的開發工具，不是系統功能
4. **OpenAI Agents SDK** 值得研究其 handoff 邏輯，作為 Phase 4 Dynamic Orchestrator 的架構參考，但不要現在整合
5. **最有立竿見影效果的動作**：從 skills_library 提取 composite skills 定義文件（純寫 .md，零風險）

---

*最後更新：2026-03-16*
*關聯文件：ai_os_gap_analysis_20260316.md*
