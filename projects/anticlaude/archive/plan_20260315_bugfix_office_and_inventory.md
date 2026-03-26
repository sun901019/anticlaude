# Bug Fix 記錄：AI Office 英文 + 庫存功能
> 作者：Claude Code
> 日期：2026-03-15
> 狀態：部分修復，待後端重啟完全生效

---

## 根本原因

Port 8000 上同時有多個 uvicorn 程序在跑（舊版 + 新版）。
當 requests 打到舊 server（PID: 27836 / 63884 / 69304）時：

- 舊 server 的 `agent_status.py` 仍是英文 role/desc → Agent 卡片顯示英文
- 舊 server 沒有 `PUT /products/{sku}/stock` 路由 → 庫存更新 404

**已在程式碼修好，但舊 server 沒有載入新代碼。**

---

## 已完成修改（本次 session）

### Fix A：AI Office 標題英文
**檔案**：`dashboard/src/app/office/page.tsx`

| 改前 | 改後 |
|------|------|
| `Mission Control` | `任務總控` |
| `Pipeline`（系統健康面板）| `每日 Pipeline` |

### Fix B：Agent 角色卡英文
**檔案**：`src/api/agent_status.py`（已在前次 session 修改）

| Agent | role 改前 | role 改後 |
|-------|---------|---------|
| Ori | Research Lead | 研究主導 |
| Lala | Strategy Lead | 策略主導 |
| Craft | Content Lead | 內容主導 |
| Lumi | Engineering Lead | 工程主導 |
| Sage | Analysis Lead | 分析主導 |
| Pixel | Design Lead | 設計主導 |

desc 欄位同步改為中文（詳見 agent_status.py 第 21-58 行）。

### Fix C：庫存更新 API
**檔案**：`src/ecommerce/router.py`（已在前次 session 加入）

```python
@router.put("/products/{sku}/stock")
def set_stock(sku: str, body: StockSet):
    """直接設定商品總庫存，以差值插入一筆調整記錄。"""
```

路由存在，但舊 server 未載入此版本。

---

## 待執行（需要 AI 執行）

### Step 1：確保後端正確重啟（使用者操作，非 AI）

> 這一步不是 AI 能自動做的，需要使用者手動操作

```
1. 在 Windows 工作管理員（Task Manager）→ 找所有 python.exe 程序 → 全部結束
   或
   在 PowerShell 執行：
   Get-Process python | Stop-Process -Force

2. 在專案根目錄重新啟動：
   python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

3. 確認只有一個 8000 port：
   netstat -ano | findstr ":8000"
   → 應只出現一筆 LISTENING
```

### Step 2：活動流 agentName 顯示優化（AI 執行）

**問題**：活動流歷史記錄顯示 `ori` / `lala`（小寫 agent_id），
但即時 SSE 事件顯示 `Ori` / `Lala`（nickname）。

**檔案**：`dashboard/src/app/office/page.tsx`，第 496-504 行

**改前**：
```typescript
const items: ActivityEvent[] = (response.events || []).map((event: any, index: number) => ({
  id: `${event.agent_id}-${event.task_meta?.id || index}-${event.recorded_at}`,
  time: formatClock(event.recorded_at),
  agentId: event.agent_id,
  agentName: event.agent_id,          // ← 顯示 "ori" 小寫
  agentEmoji: event.agent_id.slice(0, 2).toUpperCase(),
  title: event.task_meta?.title || event.task || STATUS_LABELS[event.status] || "狀態更新",
  taskType: TASK_TYPE_LABELS[event.task_meta?.task_type || ""] || event.task_meta?.task_type || "一般",
  nextOwner: event.task_meta?.target_agent_id || "",
}));
```

**改後**：
```typescript
// 在 map 之前，用 agents state 對應 nickname（useEffect 外需傳入 agents）
// 簡單方案：直接 capitalize 首字母
const toDisplay = (id: string) => id.charAt(0).toUpperCase() + id.slice(1);

const items: ActivityEvent[] = (response.events || []).map((event: any, index: number) => ({
  id: `${event.agent_id}-${event.task_meta?.id || index}-${event.recorded_at}`,
  time: formatClock(event.recorded_at),
  agentId: event.agent_id,
  agentName: toDisplay(event.agent_id),   // ← "Ori" 大寫
  agentEmoji: event.agent_id.slice(0, 2).toUpperCase(),
  title: event.task_meta?.title || event.task || STATUS_LABELS[event.status] || "狀態更新",
  taskType: TASK_TYPE_LABELS[event.task_meta?.task_type || ""] || event.task_meta?.task_type || "一般",
  nextOwner: event.task_meta?.target_agent_id || "",
}));
```

**實作位置**：`dashboard/src/app/office/page.tsx`，`loadEvents` 函數內

---

## 驗證清單（修復後確認）

- [ ] `curl http://localhost:8000/api/agents/status` → role 欄位為中文（研究主導）
- [ ] `curl -X PUT http://localhost:8000/api/ecommerce/products/FL-01/stock -H "Content-Type: application/json" -d '{"quantity":30}'` → 回傳 `{"ok":true}`
- [ ] AI Office 頁面標題顯示「任務總控」
- [ ] Agent 卡片 role 顯示中文
- [ ] Agent 卡片 desc 顯示中文
- [ ] 活動流歷史顯示 `Ori` 而非 `ori`
- [ ] 電商頁面更改庫存數量後儲存成功

---

## 給 Claude Code 的執行備註

1. Step 1（後端重啟）是使用者手動操作，不要嘗試自動執行
2. Step 2（agentName capitalize）是小改動，AI 直接修改 page.tsx 即可
3. 修完後執行 `npm run build` 確認無 TS 錯誤
4. 完成後更新 `ai/state/progress-log.md`
