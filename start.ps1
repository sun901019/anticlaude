# AntiClaude 一鍵啟動腳本
# 執行方式：在根目錄執行 .\start.ps1
# 會自動清除舊程序，再啟動後端（port 8000）與前端（port 3000）

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
                Stop-Process -Id ([int]$p) -Force -ErrorAction SilentlyContinue
                Write-Host "  已停止舊程序 PID $p (port $port)" -ForegroundColor Gray
            } catch {}
        }
    }
}

Write-Host "[清理] 停止舊的後端程序（port 8000）..." -ForegroundColor Yellow
Stop-Port 8000
Start-Sleep -Seconds 1

Write-Host "[清理] 停止舊的前端程序（port 3000）..." -ForegroundColor Yellow
Stop-Port 3000
Start-Sleep -Seconds 1

# ── 2. 啟動後端（新視窗）──
Write-Host ""
Write-Host "[1/2] 啟動後端 API（port 8000）..." -ForegroundColor Green
# PYTHONIOENCODING=utf-8 防止 Windows CP950 控制台亂碼
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONIOENCODING='utf-8'; cd '$ROOT'; python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000" -WindowStyle Normal

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
