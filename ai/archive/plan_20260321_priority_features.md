# Plan: Priority Features 2026-03-21
> 觸發條件：用戶確認以下 3 項為「蠻重要的」，命令持續執行直到完成

## 執行順序

### Item A — CEO Deliberation → AI Office UI 面板
**目標**：在 `/office` 頁面加入「深度分析」觸發面板，顯示每個 agent 的個別輸出摘要 + 最終建議
**範圍**：
- `dashboard/src/app/office/page.tsx` — 新增 DeliberationPanel 區塊
  - 文字輸入框 + 觸發按鈕
  - 顯示 per-agent 輸出（Ori/Lala/Sage 各自的 summary + success/fail badge）
  - 顯示 CEO 綜合結論（consensus, key_insights, recommendation, confidence）
- `dashboard/src/lib/api.ts` — 新增 `callDeliberate(question)` helper（POST /api/chat/deliberate）
**預計工時**：30 分鐘

### Item B — Real-time SSE Deliberation Streaming
**目標**：deliberation 改為串流，每個 agent 完成就即時推送到前端，不用等全部完成
**範圍**：
- `src/api/routes/chat.py` — 新增 `GET /api/chat/deliberate/stream` SSE endpoint
  - asyncio 逐一執行 agent（保留 gather 但改 as_completed 模式）
  - 每完成一個 agent 推送 `data: {agent, summary, success}`
  - 全部完成後推送 CEO 綜合結果 `data: {type:"synthesis", ...}`
  - 最後推送 `data: [DONE]`
- `dashboard/src/app/chat/page.tsx` — Brain 按鈕改用 EventSource 消費 SSE
  - 每收到 agent event → append to 同一訊息 bubble
  - 收到 synthesis → render 完整結論
**預計工時**：45 分鐘

### Item C — Figma → Design Feedback Loop（設計→建議）
**目標**：讓 Pixel agent 能接收 Figma 截圖並給出 UX/設計建議，完整閉環
**範圍**：
- `dashboard/src/app/figma/page.tsx` — 在「截圖匯出」tab 加「發送給 Pixel 分析」按鈕
  - 將 export 出來的 image URL POST 到 CEO chat with "ux_review" intent
  - 結果顯示在同頁面的分析區塊
- `src/agents/ceo.py` CEO_SYSTEM_PROMPT — 確保 ux_review task_type 正確路由到 pixel
**預計工時**：20 分鐘

### Item D — Codex 任務（同步進行）
- `tests/test_deliberation_sse.py` — SSE endpoint 測試（mock asyncio）
- `tests/test_deliberation_api.py` — POST /api/chat/deliberate 端到端測試
- 更新 sprint.md / progress-log.md（英文）

---

## 執行規則
- Claude Code 負責：A、B、C（跨檔案功能實作）
- Codex 負責：D（測試、記錄）
- 每項完成後立即更新 sprint.md + progress-log.md
- 全部完成後跑 pytest 確認無回歸，build 確認無 TS error

## 完成標準
- [ ] Office UI 有 deliberation panel，可輸入問題、看到 per-agent + 綜合結果
- [ ] SSE streaming 正常，Chat UI Brain 按鈕改為串流顯示
- [ ] Figma UI 可一鍵把設計截圖送 Pixel 分析
- [ ] pytest 全 pass（目前 327）
- [ ] sprint.md + progress-log.md 更新完成
