# AntiClaude — 個人品牌與電商自動化平台

> 結合多代理人（Multi-Agent）與自研圖形工作流引擎的 AI 基礎設施。
> 每天幫你：抓素材、聚類選題、評分排序、文案產出、一鍵發文與電商數據分析。

## 系統架構

- **Backend**: Python 3.12 (FastAPI), SQLite, 自研 `GraphRunner` DAG 工作流。
- **Frontend**: Next.js 14 (App Router), Tailwind CSS, Framer Motion。
- **AI 引擎**: Claude Sonnet 4.6 (主力) / GPT-4o / Gemini Flash。

## 快速開始

### 1. 後端 (FastAPI)
```powershell
# 安裝依賴
pip install -r requirements.txt

# 設定環境變數 (.env)
Copy-Item .env.example .env

# 啟動後端伺服器 (包含排程器)
.\start.ps1
```

### 2. 前端 (Next.js Dashboard)
```powershell
cd dashboard
npm install
npm run dev
```

打開 [http://localhost:3000](http://localhost:3000) 即可進入 CEO 儀表板。

## 主要服務層
| 模組/目錄 | 職責 |
|--------|------|
| `src/api/` | FastAPI 路由與自動化排程入口 |
| `src/agents/` | 代理人定義（CEO, Cluster, Score, Strategy） |
| `src/domains/` | 領域業務邏輯（自媒體 `media`、電商視覺 `flow_lab`） |
| `src/workflows/`| 自研圖形化工作流引擎（含 Checkpoint 與人工審核閘門） |
| `dashboard/` | Next.js 14 管理後台（16 個業務與分析指標面板） |
| `ai/` | 開發與協作紀錄（Codex 狀態同步） |

## 核心工作流
本系統主要以 Daily Content Pipeline 為主軸：
1. **內容研究 (Ori)**：整合 RSS, Perplexity, Serper 抓取資訊。
2. **主題聚類 (Ori)**：Claude 語意聚類 + 去重過濾。
3. **評分排序 (Lala)**：以 Orio 三維公式計算最適合的內容。
4. **策略選題與草稿 (Lala/Craft)**：挑選 Top 3 並匯入 GEO Skill 產出 Thread 草稿。
5. **人工決策 (CEO)**：在 Dashboard 進行最後發布或退回審閱。
6. **對外發布與分析**：Threads Graph API 推播與互動追蹤。

---
*詳細專案文件請參閱 `projects/anticlaude/` 目錄。*
