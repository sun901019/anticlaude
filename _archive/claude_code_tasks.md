# Claude Code 執行指南 — Hub 整合任務

> ⚠️ 這份文件是給 **Claude Code** 看的執行指令  
> 由 **Antigravity** 規劃，**不要修改任何現有程式碼**  
> 只建立結構、說明檔、整合腳本與啟用方法

---

## 執行順序

依照 Step 1 → 6 順序執行，每步完成後回報。

---

## Step 1：建立 _hub 資料夾結構

在 `c:\Users\sun90\Anticlaude\` 下建立以下目錄：

```
_hub/
├── shared/
│   ├── agents/
│   │   └── agency-agents/
│   ├── skills/
│   │   └── frontend-slides/
│   └── tools/
│       └── toonify-mcp/
```

指令：
```powershell
cd c:\Users\sun90\Anticlaude
New-Item -ItemType Directory -Force -Path "_hub/shared/agents/agency-agents", "_hub/shared/skills/frontend-slides", "_hub/shared/tools/toonify-mcp"
```

---

## Step 2：建立自建 Agent 角色檔

### 2a. `_hub/shared/agents/content-strategist.md`

建立檔案，內容如下：

```markdown
# Content Strategist（內容策略師）

## 角色定義
你是 Sun Lee（@sunlee._.yabg）的專屬內容策略師。你專注台灣科技圈，受眾是對 AI 工具、副業、個人成長有興趣的台灣科技工作者。

## 性格
- 數據導向，不憑感覺做決策
- 用繁體中文溝通，工具名稱保留英文
- 說話直接，先講結論再講理由

## 能力
- 分析 Threads 互動數據，找出受眾偏好
- 評估素材的受眾匹配度（1-10 分）
- 建議今天該發什麼主題、為什麼
- 根據歷史數據給出策略建議

## 工作流程
1. 讀取 `_context/about_me.md` 了解受眾定位
2. 讀取 `outputs/threads_metrics/` 最近 7 天數據
3. 讀取 `data/anticlaude.db` 的 `audience_insights` 表
4. 結合以上資訊，評估今日素材

## 限制
- 不寫文案（那是 Threads Writer 的工作）
- 不做技術實作
- 主題比例遵守 about_me.md 的分佈目標

## Prompt 範本
當你需要我擔任 Content Strategist 時，在對話開頭加上：
> 請以 Content Strategist 角色回應。參考 `_hub/shared/agents/content-strategist.md` 的角色設定。
```

### 2b. `_hub/shared/agents/threads-writer.md`

建立檔案，內容如下：

```markdown
# Threads Writer（繁中文案專家）

## 角色定義
你是專為 Threads 平台打造的繁體中文文案專家。你的文字像朋友在聊天，不像教授在上課。

## 性格
- 口語化、有溫度、偶爾幽默
- 用繁中為主，工具名稱保留英文
- Hook 要讓人「劃到就停下來」

## 能力
- 把任何 AI 新聞轉化為受眾有感的貼文
- 寫出不像 AI 寫的 Hook（第一句話）
- 自然地加入 CTA（追蹤 / 收藏 / 留言）
- 控制 150-300 字的最佳長度

## 文案結構
1. **Hook**（1 句）：痛點或驚喜開場，不用「今天來介紹…」
2. **正文**（3-5 句）：實用 > 理論，體驗 > 功能列表
3. **CTA**（1 句）：自然不勉強
4. **Hashtag**（3-5 個）：混合熱門 + 長尾

## 禁區
- 不用「大家好，今天要跟大家分享…」
- 不用翻譯腔（「在這個 AI 時代…」）
- 不誇大（「AI 將取代所有工作」）
- 不全英文

## Prompt 範本
> 請以 Threads Writer 角色回應。參考 `_hub/shared/agents/threads-writer.md` 和 `_context/about_me.md` 的語氣規範。主題：[填入主題]
```

---

## Step 3：建立 agency-agents 引用

### `_hub/shared/agents/agency-agents/README.md`

```markdown
# Agency Agents — 精選 AI 專家角色

> 來源：https://github.com/msitarzewski/agency-agents
> 50+ 專業 AI 角色，各有專精領域和性格

## 安裝方式

### 方法 A：Claude Code 直接使用（推薦）
在 Claude Code 中執行：
\```
/install-agent https://github.com/msitarzewski/agency-agents
\```

### 方法 B：手動 Clone
\```bash
cd c:\Users\sun90\Anticlaude\_hub\shared\agents\agency-agents
git clone https://github.com/msitarzewski/agency-agents.git .
\```

## 推薦使用的角色

### 💻 工程類
| 角色 | 檔案 | 什麼時候用 |
|------|------|-----------|
| Frontend Developer | `engineering/engineering-frontend-developer.md` | 改儀表板 UI |
| Backend Architect | `engineering/engineering-backend-architect.md` | 擴充 API / DB |
| DevOps Automator | `engineering/engineering-devops-automator.md` | 部署到 production |

### 🎨 設計類
| 角色 | 檔案 | 什麼時候用 |
|------|------|-----------|
| UI Designer | `design/design-ui-designer.md` | 儀表板改版 |

### 📢 行銷類
| 角色 | 檔案 | 什麼時候用 |
|------|------|-----------|
| Growth Hacker | `marketing/marketing-growth-hacker.md` | 成長策略分析 |
| Social Media Strategist | `marketing/marketing-social-media-strategist.md` | 多平台拓展 |

## 使用方式
在 Claude Code 對話中說：
> 請載入 agency-agents 的 Frontend Developer 角色，幫我修改儀表板的 metrics 頁面。
```

---

## Step 4：建立 Skills README

### `_hub/shared/skills/README.md`

```markdown
# 共用 Skills

可安裝的 AI 能力包，擴充 Claude Code 的功能。

| Skill | 用途 | 安裝 |
|-------|------|------|
| Frontend Slides | 做 web 簡報 | 見 `frontend-slides/README.md` |
| SKILLS All-in-one | 技能商店 | 瀏覽 https://huangchiyu.com/SKILLS_All-in-one/ |
```

### `_hub/shared/skills/frontend-slides/README.md`

```markdown
# Frontend Slides — 用程式碼做簡報

> 來源：https://github.com/zarazhangrui/frontend-slides

## 這是什麼
不用 PowerPoint，用 Claude Code 直接生成漂亮的 web 簡報。內建多種深色/淺色主題。

## 安裝方式
在 Claude Code 中執行：
\```
/install-skill https://github.com/zarazhangrui/frontend-slides
\```

## 使用方式
\```
幫我做一份 5 頁的簡報，主題是「2026 AI 工具趨勢」，用深色主題
\```

或轉換現有 PPT：
\```
把這份 PowerPoint 轉成 web 簡報：[檔案路徑]
\```

## 適用場景
- 分享 AI 趨勢報告
- 做 pitch deck
- 內容行銷用的視覺素材
```

---

## Step 5：建立 MCP Tools README

### `_hub/shared/tools/README.md`

```markdown
# 共用 MCP Tools

Model Context Protocol 工具，自動擴充 Claude 的能力。

| Tool | 用途 | 安裝 |
|------|------|------|
| Toonify MCP | 省 50-60% Claude token 費用 | 見 `toonify-mcp/README.md` |
```

### `_hub/shared/tools/toonify-mcp/README.md`

```markdown
# Toonify MCP — Claude API Token 省錢神器

> 來源：https://github.com/PCIRCLE-AI/toonify-mcp
> 自動壓縮結構化資料，省 50-60% token 費用

## 這是什麼
一個 MCP server + Claude Code plugin，自動把傳給 Claude 的結構化資料（JSON、表格等）壓縮成 TOON 格式，省下大量 token。

## 為什麼需要
AntiClaude 每天呼叫 Claude API 做評分和文案，累積下來 token 費不少。裝了這個後每月大約省 $1.5-2。

## 安裝方式

### 方法 A：Claude Code Plugin（推薦）
\```
claude plugin add PCIRCLE-AI/toonify-mcp
\```

### 方法 B：MCP Server
\```bash
npx -y toonify-mcp
\```

在 `.claude.json` 中加入：
\```json
{
  "mcpServers": {
    "toonify": {
      "command": "npx",
      "args": ["-y", "toonify-mcp"]
    }
  }
}
\```

## 預估省多少
| 資料類型 | 壓縮率 |
|---------|--------|
| JSON | 50-55% |
| 表格 | 55-65% |
| 純文字 | 10-20% |

## 適用場景
- AntiClaude 的 Claude API 呼叫
- 任何大量使用 Claude 的專案
```

---

## Step 6：建立 START_HERE.md + agents/README.md

### `_hub/START_HERE.md`

```markdown
# 🚀 START HERE — 資源使用指南

## 我有什麼？

### 🤖 Agents（AI 角色）
| 名稱 | 位置 | 一句話說明 |
|------|------|----------|
| Content Strategist | `shared/agents/content-strategist.md` | 幫你選今天發什麼 |
| Threads Writer | `shared/agents/threads-writer.md` | 幫你寫出好文案 |
| +6 個 agency-agents | `shared/agents/agency-agents/` | 前端/後端/設計/行銷專家 |

### 🧩 Skills（技能包）
| 名稱 | 位置 | 一句話說明 |
|------|------|----------|
| Frontend Slides | `shared/skills/frontend-slides/` | 做簡報不用 PPT |

### 🔧 MCP Tools
| 名稱 | 位置 | 一句話說明 |
|------|------|----------|
| Toonify MCP | `shared/tools/toonify-mcp/` | 省 60% Claude 費用 |

## 怎麼用？

### 叫 Agent 出場
在 Claude Code 中說：
> 請載入 `_hub/shared/agents/content-strategist.md` 的角色設定

### 用 Skill
> /install-skill [GitHub URL]

### 用 MCP Tool
> claude plugin add [repo]

## 更多細節
- 完整資源地圖 → `resource_map.md`（專案根目錄）
- 專案現況 → `project_record.md`（專案根目錄）
```

### `_hub/shared/agents/README.md`

```markdown
# 共用 Agents

AI 角色專家，載入後讓 Claude Code 變身為特定領域專家。

## 自建角色
| 角色 | 檔案 | 用途 |
|------|------|------|
| Content Strategist | `content-strategist.md` | 內容策略 + 選題 |
| Threads Writer | `threads-writer.md` | 繁中文案生成 |

## 第三方角色
| 來源 | 資料夾 | 說明 |
|------|--------|------|
| agency-agents | `agency-agents/` | 50+ 專業 AI 角色 |

## 使用方式
對 Claude Code 說：「請以 [角色名] 的身份回應，參考 `_hub/shared/agents/[檔名]`」
```

---

## 完成後的最終結構

```
_hub/
├── START_HERE.md
└── shared/
    ├── agents/
    │   ├── README.md
    │   ├── content-strategist.md
    │   ├── threads-writer.md
    │   └── agency-agents/
    │       └── README.md
    ├── skills/
    │   ├── README.md
    │   └── frontend-slides/
    │       └── README.md
    └── tools/
        ├── README.md
        └── toonify-mcp/
            └── README.md
```

共 **9 個新檔案**，**0 個現有檔案被修改**。
