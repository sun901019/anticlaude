# 任務給 Claude Code：實作 Mission Control Dashboard 前端

> **發布者**：Antigravity (System Architect)
> **目標**：利用已就位的後端 SSE 串流 (`/api/agents/stream`)，以及新生成的 6 張像素風 Agent 圖檔，建立一個「活著」的 Mission Control 管理介面。
> **參考風格**：暗色主題佈景，加上浮動動畫與發光效果模擬「正在工作」的狀態。

## 1. 任務背景與資源盤點

### 後端 API (已完成，無需修改邏輯)
- `src/api/agent_status.py` 負責狀態管理。
- `src/api/main.py` 提供兩個 endpoint:
  - `GET /api/agents/status` (取得當前快照)
  - `GET /api/agents/stream` (SSE 即時串流)
- 觸發來源：`src/agents/orchestrator.py` 在執行各步驟時已綁定 `_emit("ori", "working", "task name")` 等。

### 圖片素材 (已準備)
Antigravity 已生成 6 張像素小人圖檔，需從 `_hub` 的 `brain` 資料夾複製到前端 `public` 目錄：
- 目標路徑：`dashboard/public/agents/`
- 檔名需要對應 Agent ID：`ori.png`, `lala.png`, `craft.png`, `lumi.png`, `sage.png`, `pixel.png`

---

## 2. 前端實作規格 (Next.js 14 App Router)

### 2.1 建立新頁面 `/office`
- **檔案路徑**：`dashboard/src/app/office/page.tsx`
- **導航更新**：在 `dashboard/src/components/TopNav.tsx` 或 `Sidebar.tsx` 加入「AI Office」的導航連結。

### 2.2 狀態管理與 SSE 串接
- **資料結構**：
  ```typescript
  type AgentStatus = "working" | "idle";
  type AgentData = {
    nickname: string;
    role: string;
    emoji: string;
    status: AgentStatus;
    task: string;
    updated_at: string;
  };
  type AgentMap = Record<string, AgentData>;
  ```
- **SSE 實作**：
  - 使用 `useEffect` 初始化 `EventSource` 連接 `http://localhost:8000/api/agents/stream`。
  - 當收到 message event 時，解析 JSON 並更新 React State (`AgentMap`)。
  - 需妥善處理 component unmount 時的 `eventSource.close()`。

### 2.3 視覺佈局設計 (UI/UX)
參考現有深色主題（`#0a0a0f` 背景），設計包含三個主要區塊的頁面：

#### A. 總覽標題 (Header)
- 標題：「MISSION CONTROL - AI Office」
- 狀態指示燈：顯示 "Gateway Connected" (綠燈)
- 整體統計：計算目前多少 Agent 是 `working`，多少是 `idle`。

#### B. 實體化的 Agent 網格 (2 列 x 3 欄)
- 設計 6 張 Agent 卡片，置中放置每個 Agent 的像素圖（`<img src="/agents/${agentId}.png" />`）。
- **生動的動畫邏輯（Tailwind CSS）**：
  - **當 `status === "working"` 時**：
    - 圖片加上輕微的「上下浮動」動畫（自訂 Tailwind 動畫或修改 `animate-bounce`）。
    - 圖片或卡片加上明顯的 Glowing 特效（例如：`drop-shadow-[0_0_15px_rgba(139,92,246,0.5)]`）。
    - 顯示明顯的 Badge 或懸浮文字：「Working...」。
  - **當 `status === "idle"` 時**：
    - 圖片變暗且略微去色（例如：`opacity-60 grayscale-[50%]`）。
    - 移除浮動與發光動畫。
    - 顯示 Badge：「Idle」。

#### C. 右側資訊面板 (Task Panel & Activity Feed)
- **當前任務 (In Progress)**：
  - 列出所有狀態為 `working` 的 Agent，並顯示其 `task` 字串。
- **實時活動日誌 (Activity Feed)**：
  - 在前端維護一個 Array，每當 SSE 推送某個 Agent 的 `status` 從 `idle` 變為 `working` 時，新增一筆紀錄。
  - 格式範例：`[10:25:31] Ori 開始執行: 抓取 AI 新聞素材`。
  - 限制最多顯示 10-15 筆，新的紀錄可加上漸顯動畫（`animate-in fade-in`）。

---

## 3. 驗收標準
1. 在瀏覽器開啟 `/office` 頁面能正常顯示 6 個 Agent 的 UI。
2. 啟動後端伺服器並執行 `python src/pipeline.py` 時，前端畫面不用重整，就能看到 Agent 依序「亮起來」並上下浮動，同時右側面板顯示正在執行的細部任務。
3. 關閉 pipeline 後，所有 Agent 最終都要回歸暗綠色的 `idle` 狀態。
