# AntiClaude 關閉腳本
# 執行方式：在根目錄執行 .\stop.ps1

Write-Host "=== AntiClaude 關閉中 ===" -ForegroundColor Cyan

function Stop-Port($port) {
    $pids = netstat -ano |
        Select-String ":$port\s.*LISTENING" |
        ForEach-Object { ($_ -split '\s+')[-1] } |
        Select-Object -Unique

    foreach ($p in $pids) {
        if ($p -match '^\d+$' -and $p -ne '0') {
            try {
                Stop-Process -Id ([int]$p) -Force -ErrorAction SilentlyContinue
                Write-Host "  已停止 PID $p (port $port)" -ForegroundColor Gray
            } catch {}
        }
    }
}

Stop-Port 8000
Stop-Port 3000

Write-Host "[OK] 所有服務已停止" -ForegroundColor Green
