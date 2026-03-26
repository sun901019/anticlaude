# AntiClaude 技術債清理計畫
> 作者：Claude Code
> 日期：2026-03-15
> 優先執行：Fix-1（多重 server 根本原因）

---

## 問題根本原因：多重 Server 堆積

### 為什麼會出現多個 server？

`start.ps1` 第 16-19 行：
```powershell
if (Test-Port 8000) {
    Write-Host "[警告] Port 8000 已被佔用..." -ForegroundColor Yellow
    # ← 只警告，不停止，繼續往下執行
}
# 第 28 行：不管有沒有舊的，直接開新的
Start-Process powershell -ArgumentList "..uvicorn --reload --port 8000"
```

加上 `--reload` 每個 uvicorn 會產生 **2 個 process**（主程序 + 熱重載監控）。
每次執行 `start.ps1` = 再加 2 個。執行 3 次 = 6 個 process 搶同一個 port。

---

## Fix-1：修正 start.ps1（最高優先）

**檔案**：`start.ps1`

**改法**：偵測到 port 占用時，自動 kill 再重啟，而不是只警告。

**改後完整內容**：

```powershell
# AntiClaude 一鍵啟動腳本
# 執行方式：在根目錄執行 .\start.ps1

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "=== AntiClaude 啟動中 ===" -ForegroundColor Cyan

# ── 1. 清除占用 8000 / 3000 的舊程序 ──
function Stop-Port($port) {
    $pids = netstat -ano |
        Select-String ":$port\s.*LISTENING" |
        ForEach-Object { ($_ -split '\s+')[-1] } |
        Select-Object -Unique

    foreach ($p in $pids) {
        if ($p -match '^\d+$' -and $p -ne '0') {
            try {
                Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
                Write-Host "  已停止舊程序 PID $p (port $port)" -ForegroundColor Gray
            } catch {}
        }
    }
}

Write-Host "[清理] 停止舊的後端程序..." -ForegroundColor Yellow
Stop-Port 8000
Start-Sleep -Seconds 1

Write-Host "[清理] 停止舊的前端程序..." -ForegroundColor Yellow
Stop-Port 3000
Start-Sleep -Seconds 1

# ── 2. 啟動後端（新視窗）──
Write-Host ""
Write-Host "[1/2] 啟動後端 API（port 8000）..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ROOT'; python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000" -WindowStyle Normal

Start-Sleep -Seconds 3

# ── 3. 啟動前端（新視窗）──
Write-Host "[2/2] 啟動前端 Dashboard（port 3000）..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ROOT\dashboard'; npm run dev" -WindowStyle Normal

Start-Sleep -Seconds 2

# ── 4. 健康確認 ──
Write-Host ""
Write-Host "等待後端就緒..." -ForegroundColor Gray
$maxRetry = 15
$retry = 0
while ($retry -lt $maxRetry) {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) {
            Write-Host "[OK] 後端已就緒 http://localhost:8000" -ForegroundColor Green
            break
        }
    } catch {}
    $retry++
    Start-Sleep -Seconds 1
}
if ($retry -eq $maxRetry) {
    Write-Host "[!] 後端啟動逾時，請手動確認" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== 系統啟動完成 ===" -ForegroundColor Cyan
Write-Host "  Dashboard : http://localhost:3000" -ForegroundColor White
Write-Host "  API       : http://localhost:8000" -ForegroundColor White
Write-Host "  AI Office : http://localhost:3000/office" -ForegroundColor White
Write-Host ""
```

**關鍵改動**：
1. `Stop-Port` 函數：自動 kill 占用 port 的舊程序
2. 移除 `--reload`（開發時需要熱重載可手動加）
3. 加 `--host 0.0.0.0`（統一與手動啟動指令一致）
4. sleep 時間加長（給清除程序足夠時間）

---

## Fix-2：新增 stop.ps1（乾淨關閉）

**檔案**：`stop.ps1`（新建）

```powershell
# AntiClaude 關閉腳本
Write-Host "=== AntiClaude 關閉中 ===" -ForegroundColor Cyan

function Stop-Port($port) {
    $pids = netstat -ano |
        Select-String ":$port\s.*LISTENING" |
        ForEach-Object { ($_ -split '\s+')[-1] } |
        Select-Object -Unique

    foreach ($p in $pids) {
        if ($p -match '^\d+$' -and $p -ne '0') {
            try {
                Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
                Write-Host "  已停止 PID $p (port $port)" -ForegroundColor Gray
            } catch {}
        }
    }
}

Stop-Port 8000
Stop-Port 3000
Write-Host "[OK] 所有服務已停止" -ForegroundColor Green
```

---

## Fix-3：移除 --reload（統一啟動方式）

**問題**：`start.ps1` 用 `--reload`，手動啟動時用 `--host 0.0.0.0`，不一致。

**統一規則**（寫進 CLAUDE.md）：
```
開發模式：python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
正式啟動：python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
一鍵啟動：.\start.ps1（不帶 --reload）
```

---

## 技術債清單（其他）

### TD-1：`_archive/` 目錄（低優先）
**狀態**：存在 10+ 個舊文件
**處理**：保留，不動。已有 `_archive/` 命名清楚區分。

### TD-2：`flowlab-selection/` 外部目錄（低優先）
**位置**：`C:\Users\sun90\flowlab-selection\`
**狀態**：已有 DEPRECATED.md
**處理**：保留，不動。歷史參考用。

### TD-3：全局狀態 flag（中優先）
**位置**：`src/api/main.py`
```python
_pipeline_running = False
_tracker_running = False
_weekly_running = False
_feedback_running = False
```
**問題**：全局可變狀態，APScheduler 多工時可能 race condition。
**建議**：改成 asyncio.Lock() 或 asyncio.Event()
**當下影響**：低（排程是序列的，不太會真的 race）

### TD-4：CORS 只允許 localhost:3000（中優先）
**位置**：`src/api/main.py`
```python
allow_origins=["http://localhost:3000"]
```
**問題**：雲端部署後前端 URL 不同，CORS 會擋。
**建議**：改成環境變數 `ALLOWED_ORIGINS`
**當下影響**：無（本機開發不影響）

### TD-5：`google.generativeai` 廢棄警告（低優先）
**位置**：`src/ai/competitor_analyzer.py`、`src/ai/gemini_cluster.py`
**問題**：`google.generativeai` 官方宣告廢棄，建議換 `google.genai`
**當下影響**：只是 warning，功能正常

---

## 執行順序

```
本週立即
└── Fix-1：修正 start.ps1（讓 ./start.ps1 能乾淨重啟）  ✅ 完成
└── Fix-2：新增 stop.ps1                                ✅ 完成

下週可做
└── Fix-3：CLAUDE.md 補充啟動指令說明                  ✅ 完成

未來（雲端部署前必做）
└── TD-4：CORS 改環境變數                              ⏸ 升級 H 跳過，暫緩

不急
└── TD-3：global flag 改 asyncio.Lock
└── TD-5：google.genai 遷移
└── TD-1 / TD-2：保留不動
```

---

## 完成後驗證

```powershell
# 1. 關閉所有
.\stop.ps1

# 2. 確認 port 清空
netstat -ano | findstr ":8000"
# → 應無結果

# 3. 重新啟動
.\start.ps1

# 4. 確認只有一個 server
netstat -ano | findstr ":8000"
# → 應只有 1-2 筆（uvicorn 主程序）

# 5. 測試庫存 API
curl -X PUT http://localhost:8000/api/ecommerce/products/FL-01/stock -H "Content-Type: application/json" -d '{"quantity":30}'
# → {"ok":true,"sku":"FL-01","total":30}
```
