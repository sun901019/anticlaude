# 資源地圖 — 我的 Agents / Skills / MCP Tools

> 用人話寫：這是什麼、能幫我什麼、什麼時候用

---

## 🤖 我的 Agents

### A1. Content Strategist（內容策略師）— 自建
- **這是什麼**：專為你的 Threads 帳號打造的內容策略 AI，懂你的受眾、知道什麼話題會紅
- **能幫你什麼**：根據 Threads 互動數據，選出今天最該發的 3 個主題，告訴你為什麼
- **何時使用**：每天跑 pipeline 的「策略選題」步驟
- **用在哪**：AntiClaude 專案

### A2. Threads Writer（文案專家）— 自建
- **這是什麼**：懂繁體中文語感的文案 AI，寫出來的 Hook 不像翻譯腔
- **能幫你什麼**：把選好的主題變成可以直接複製貼上的 Threads 貼文
- **何時使用**：每天跑 pipeline 的「文案生成」步驟
- **用在哪**：AntiClaude 專案

### A3. Frontend Developer（前端工程師）— agency-agents
- **這是什麼**：專精 React / Next.js / CSS 的 AI 開發者
- **能幫你什麼**：改儀表板 UI、加新頁面、修 bug、做動畫效果
- **何時使用**：要動 `dashboard/` 裡的程式碼時
- **用在哪**：AntiClaude Dashboard，或任何前端專案
- **來源**：[agency-agents/frontend-developer](https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-frontend-developer.md)

### A4. Growth Hacker（成長駭客）— agency-agents
- **這是什麼**：用數據驅動成長的 AI 策略師
- **能幫你什麼**：分析互動數據、建議 A/B 測試、找出增長瓶頸
- **何時使用**：週報分析、想優化 Threads 策略時
- **來源**：[agency-agents/growth-hacker](https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-growth-hacker.md)

### A5. Social Media Strategist（社群策略師）— agency-agents
- **這是什麼**：多平台社群經營專家
- **能幫你什麼**：跨平台發文策略、最佳時段、hashtag 分析
- **何時使用**：想拓展到 Instagram / X 時
- **來源**：[agency-agents/social-media-strategist](https://github.com/msitarzewski/agency-agents/blob/main/marketing/marketing-social-media-strategist.md)

### A6. Backend Architect（後端架構師）— agency-agents
- **這是什麼**：擅長 API 設計和系統架構的 AI
- **能幫你什麼**：設計新 API、最佳 DB schema、效能優化
- **何時使用**：要擴充 AntiClaude 後端功能時
- **來源**：[agency-agents/backend-architect](https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-backend-architect.md)

### A7. UI Designer（UI 設計師）— agency-agents
- **這是什麼**：專精美學和使用者體驗的設計 AI
- **能幫你什麼**：配色方案、排版建議、互動設計
- **何時使用**：儀表板改版、要讓 UI 更好看時
- **來源**：[agency-agents/ui-designer](https://github.com/msitarzewski/agency-agents/blob/main/design/design-ui-designer.md)

### A8. DevOps Automator（部署自動化）— agency-agents
- **這是什麼**：CI/CD、Docker、監控的自動化專家
- **能幫你什麼**：把系統容器化、設定自動部署、監控警報
- **何時使用**：要把 AntiClaude 部署到雲端時
- **來源**：[agency-agents/devops-automator](https://github.com/msitarzewski/agency-agents/blob/main/engineering/engineering-devops-automator.md)

---

## 🧩 我的 Skills

### S1. Frontend Slides — 做簡報不用 PowerPoint
- **這是什麼**：用程式碼生成漂亮的 web 簡報，有多種內建主題
- **能幫你什麼**：快速做 pitch deck、趨勢分享投影片，不用學 CSS
- **何時使用**：要做簡報、分享內容時
- **來源**：[frontend-slides](https://github.com/zarazhangrui/frontend-slides)
- **安裝**：Claude Code 內 `/install-skill frontend-slides`

### S2. SKILLS All-in-one — 技能商店
- **這是什麼**：一個網站，收集了各種可下載的 AI 技能包
- **能幫你什麼**：當你需要某個特定能力時，來這裡找
- **何時使用**：想找新能力擴充 Claude Code 時
- **來源**：[SKILLS All-in-one](https://huangchiyu.com/SKILLS_All-in-one/)

### S3. Content Pipeline — 一鍵跑完內容流水線（自建）
- **這是什麼**：把抓取→分析→評分→文案→存檔包成一個指令
- **能幫你什麼**：打開系統後一個按鈕跑完今天所有事
- **何時使用**：每天使用
- **用在哪**：AntiClaude 專案

---

## 🔧 我的 MCP Tools

### T1. Toonify MCP — 省 Claude API 費用
- **這是什麼**：一個 MCP server，自動壓縮傳給 Claude 的結構化資料
- **能幫你什麼**：**省 50-60% 的 Claude API token 費用**
- **何時使用**：所有用 Claude 的時候自動啟用
- **來源**：[toonify-mcp](https://github.com/PCIRCLE-AI/toonify-mcp)
- **安裝**：`claude plugin add PCIRCLE-AI/toonify-mcp`

### T2. Threads API Tool — 社群數據追蹤（自建）
- **這是什麼**：封裝好的 Threads Graph API 工具
- **能幫你什麼**：一鍵抓取全部貼文數據、計算互動率
- **何時使用**：按儀表板的「📊 抓 Threads 數據」按鈕時
- **用在哪**：AntiClaude 專案

---

## 🔄 推薦工作流

### 每日流程
```
早上打開電腦
    │
    ▼
1. 開 AntiClaude 儀表板
   cd Anticlaude/dashboard && npm run dev
    │
    ▼
2. 按「🚀 一鍵跑完」
   → 背後：scraper → Gemini 分析 → Claude 評分+文案 → GPT 策略
   → Claude 呼叫自動透過 Toonify MCP 省 token
    │
    ▼
3. 看今日 Top 3 → 選一版文案 → 一鍵複製 → 貼到 Threads
    │
    ▼
4. 按「📊 抓 Threads 數據」→ 更新昨天貼文的互動數據
```

### 需要新功能時
```
你：「我想加 XX 功能」
    │
    ▼
Antigravity（規劃）
  → 理解需求 → 拆任務 → 寫 plan
    │
    ▼
Claude Code（執行）
  → 載入對應 agent（如 Frontend Developer）
  → 寫程式碼 → 跑測試 → 完成
```

### 週末回顧
```
按「📋 生成週報」
    │
    ▼
看週報 → 了解受眾偏好變化
    │
    ▼
按「🧠 回饋分析」→ 更新受眾偏好模型
    │
    ▼
下週的評分自動更精準（閉環 ✅）
```
