# Capability Map — 任務 → Agent → Skill 對照表

> AI-OS 的核心路由邏輯。收到任務時，按此地圖選擇正確的 Agent 和 Skill。
> **最後更新**：2026-03-12（Skills 整合後版本）

---

## 快速路由表

| 使用者說... | 偵測關鍵字 | Agent | Skills |
|-----------|-----------|-------|--------|
| 「選題」「今天發什麼」「主題策略」 | 選題, 策略, 主題, 受眾 | `content-strategist` | `strategy_guide` |
| 「寫文案」「寫貼文」「寫 Hook」 | 文案, 貼文, Hook, 寫, Threads | `threads-writer` | `writing_guide` |
| 「改 UI」「更好看」「調整畫面」 | ui, 設計, 配色, 動畫, CSS | agency-agents: UI Designer | `dev_tools` |
| 「寫 API」「加 endpoint」「改後端」 | api, backend, endpoint, DB | agency-agents: Backend Architect | `coding_agent` |
| 「成長」「互動率」「數據分析」 | 成長, 分析, 互動, 報告 | agency-agents: Growth Hacker | `strategy_guide` + `dev_tools` |
| 「SEO」「搜尋排名」「關鍵字」 | seo, 排名, 關鍵字, 搜尋 | `market-research-agent` | `seo_optimization` + `strategy_guide` |
| 「做簡報」「投影片」「slides」 | 簡報, slides, 投影片, HTML | `content-agent` | `dev_tools` |
| 「市場調查」「競品」「趨勢」 | 市場, 競品, 趨勢, 調查 | `market-research-agent` | `strategy_guide` |
| 「部署」「Docker」「CI/CD」 | deploy, docker, ci, 部署 | agency-agents: DevOps Automator | `coding_agent` |

---

## Skill 索引（整合後）

| Skill 檔案 | 用途 | 使用時機 |
|-----------|------|---------|
| `writing_guide.md` | Threads 貼文結構 + 去 AI 痕跡 | 寫文案、改文案 |
| `strategy_guide.md` | 素材評估 + 選題策略 + 受眾成長 | 選題、分析、策略規劃 |
| `dev_tools.md` | Vizro 視覺化 + HTML 投影片 | 開發工具需求 |
| `seo_optimization.md` | GEO + SEO 優化 | 有 SEO 需求時 |
| `project_planning.md` | 任務拆解 + 規劃 | 規劃複雜任務 |
| `coding_agent.md` | 程式碼生成 | 寫後端/前端程式 |

> 原有的 `content_creation`, `text_humanization`, `research_analysis`, `marketing_strategy`, `data_processing`, `presentation_ui` 已合併，備份在 `_hub/shared/skills/_archive/`

---

## AntiClaude Pipeline 路由

```
pipeline 執行
  └─ 抓取新聞 → aggregator.py（RSS + Serper + HN + Perplexity）
  └─ Claude 聚類 → claude_cluster.py
  └─ Claude 評分 → claude_scorer.py（注入 strategy_guide 規則）
  └─ GPT 選題 → gpt_strategist.py（注入 strategy_guide 多樣性規則）
  └─ 文案生成 → claude_writer.py（注入 writing_guide 規則）
  └─ 品質驗證 → claude_writer.py → _verify_and_fix_draft()
  └─ 數據追蹤 → metrics_collector.py → audience_insights → 閉環
```

---

## 能力群組

### Content 群組（最常用）
- **Skills**: `writing_guide`, `strategy_guide`
- **Agents**: `threads-writer`, `content-strategist`, `content-agent`
- **來源**: marketingskills, Humanizer-zh, awesome-agent-skills

### Dev 群組
- **Skills**: `dev_tools`, `coding_agent`
- **Tools**: Vizro, toonify-mcp, frontend-slides
- **Agents**: agency-agents (UI Designer, Backend Architect, DevOps)

### Planning 群組
- **Skills**: `project_planning`
- **Agents**: `planning-agent`

---

## 執行工具層

- **Claude Code CLI** — 讀寫檔案、執行指令、調度任務
- **Vizro Dashboard** — `dev_tools.md` 的視覺化實作
- **Toonify MCP** — Token 壓縮與快取

## 執行工具層（更新版）

| 工具 | 適用任務 | 原因 |
|-----|---------|------|
| **Claude Code CLI** | 跨檔案重構、新功能開發、Pipeline 修改 | 需要全局理解和上下文 |
| **Codex** | 簡單 bug fix、生成測試、CSS 微調、Docstring | 快速局部修復，不需上下文 |
| **Vizro Dashboard** | 互動式數據視覺化 | `dev_tools.md` 的視覺化實作 |
| **Toonify MCP** | 圖片處理、Token 壓縮 | 節省 API Token 用量約 60% |

### Claude Code vs Codex 決策樹
```
任務涉及 3+ 個檔案？         → Claude Code
任務涉及資料庫 schema？      → Claude Code
任務需要理解整體架構？        → Claude Code
單檔案局部修改？              → Codex 可考慮
重複性批量工作（測試/doc）？  → Codex
```

> 詳細規範見 `_hub/shared/tools/codex_integration.md`
