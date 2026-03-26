# AntiClaude 系統狀態確認腳本
# 執行方式：.\check.ps1
# 用途：確認後端 + 前端 + 關鍵 API 都正常運行

$OK   = "[OK]"
$FAIL = "[!!]"
$INFO = "[--]"

function Test-Endpoint {
    param(
        [string]$Label,
        [string]$Url,
        [int]$TimeoutSec = 3
    )
    try {
        $resp = Invoke-WebRequest -Uri $Url -TimeoutSec $TimeoutSec -UseBasicParsing -ErrorAction Stop
        if ($resp.StatusCode -eq 200) {
            Write-Host "  $OK $Label" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  $FAIL $Label — HTTP $($resp.StatusCode)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "  $FAIL $Label — 無法連線" -ForegroundColor Red
        return $false
    }
}

Write-Host ""
Write-Host "=== AntiClaude 系統狀態確認 ===" -ForegroundColor Cyan
Write-Host ""

# ── 後端 ──
Write-Host "[後端 http://localhost:8000]" -ForegroundColor Yellow
$backendOk = Test-Endpoint "Health"            "http://localhost:8000/health"
              Test-Endpoint "API Health"        "http://localhost:8000/api/health"        | Out-Null
              Test-Endpoint "Review Queue"      "http://localhost:8000/api/review-queue"  | Out-Null
              Test-Endpoint "Approvals list"    "http://localhost:8000/api/approvals"     | Out-Null
              Test-Endpoint "Workflow runs"     "http://localhost:8000/api/workflow-runs" | Out-Null

Write-Host ""

# ── 前端 ──
Write-Host "[前端 http://localhost:3000]" -ForegroundColor Yellow
$frontendOk = Test-Endpoint "Dashboard"  "http://localhost:3000"

Write-Host ""

# ── 整體結論 ──
if ($backendOk -and $frontendOk) {
    Write-Host "=== 所有服務正常 ===" -ForegroundColor Green
} elseif ($backendOk) {
    Write-Host "=== 後端正常，前端未就緒（可能仍在啟動中）===" -ForegroundColor Yellow
} else {
    Write-Host "=== 後端離線 — 請執行 .\start.ps1 ===" -ForegroundColor Red
}
Write-Host ""
