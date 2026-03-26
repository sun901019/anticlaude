# 任務給 Claude Code：實作 Mission Control Dashboard 前端

> **發布者**：Antigravity
> **目標**：利用已就位的後端 SSE 串流，以及新生成的 6 張像素風 Agent 圖檔，建立一個「活著」的 Mission Control 管理介面。
> **參考風格**：暗色主題佈景，加上浮動動畫與發光效果模擬「正在工作」的狀態。

## 任務背景與資源

1. **後端資料流（已完成）**：`src/api/agent_status.py` 已經建好，且 FastAPI 在 `main.py` 提供了 `/api/agents/stream` (SSE) 端點。
2. **觸發來源（已完成）**：`src/agents/orchestrator.py` 在執行各步驟時已綁定 `_emit("ori", "working", "task name")`。
3. **圖片素材（已準備）**：我已經將 6 張生成的像素小人放到 `dashboard/public/agents/` 下：
   - `ori.png`, `lala.png`, `craft.png`, `lumi.png`, `sage.png`, `pixel.png`

## 實作步驟

### Step 1: 建立新頁面 `/office`
- 路徑：`dashboard/src/app/office/page.tsx`
- 在 `TopNav.tsx` 或 `Sidebar.tsx` 加入「AI Office」的導航連結。

### Step 2: 串接 SSE (Server-Sent Events)
- 使用 `useEffect` 和原生 `EventSource` 連結到 `http://localhost:8000/api/agents/stream`。
- State 儲存格式對應後端的 `AGENTS` 字典： `{ ori: { status: "working", task: "xxx", nickname: "Ori"... }, ... }`

### Step 3: 設計實體化的 Agent 網格
設計一個 2 列 3 欄的網格，顯示 6 個小人。
- **背景與圖片**：用深色漸層卡片當每個 Agent 的背景，正中央放入 `<img src="/agents/ori.png" />`。
- **生動的動畫邏輯（CSS/Tailwind）**：
  - **當 `status === "working"` 時**：
    - 給圖片加上輕微的「上下浮動」動畫（`animate-bounce` 改寫成慢速浮動，例如 Y 軸位移 8px）。
    - 圖片加上明顯的 Drop Shadow 或 Glow 特效（例如紫色的 `drop-shadow(0 0 15px rgba(139,92,246,0.6))`）。
    - 顯示 Badge：「正在執行...」。
  - **當 `status === "idle"` 時**：
    - 圖片變暗（`opacity-60 grayscale-[50%]`）。
    - 移除浮動動畫。

### Step 4: Task Panel 與 Activity Feed
- **Task Panel (Hover 或右側面板)**：當滑鼠移到正在 Working 的 Agent 上，顯示他目前正在做的 `task` 內容。
- **實時訊息流 (Message Feed)**：在頁面底部或右下角做一個滾動清單。每次 SSE 收到某個 Agent 從 idle 變 working 時，加入一條紀錄：`[10:25:31] Ori 開始執行: 抓取 AI 新聞素材`。只保留最新 10 條，超出自動移除並加上滑動動畫。

## 驗收標準
當我在 dashboard 開啟這個畫面，然後去終端機跑 `python src/pipeline.py` 的時候，我應該要看到畫面上的 Agent 輪流「亮起來」浮動，並且顯示他們正在做的任務。
