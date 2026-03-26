# Threads 追蹤修復 + Metrics 頁面建置計畫
> 作者：Claude Code
> 日期：2026-03-15
> 依據：系統審計發現的兩個重要缺口

---

## Part 1：Threads 追蹤問題診斷

### 現況釐清

**好消息**：`threads_client.py` 的程式碼結構沒有問題，import 正確，API 呼叫邏輯合理。

**真正的問題**：需要確認兩件事：

#### 問題 A：環境變數有沒有設定？

檢查 `.env` 是否有這兩行：
```
THREADS_ACCESS_TOKEN=<你的 Threads API Token>
THREADS_USER_ID=<你的 Threads 數字 ID>
```

若沒有 → Tracker 每次跑都只拿到空資料，但不會報錯，靜默失敗。

#### 問題 B：Threads API Token 是否有效？

Threads Graph API Token 有效期約 60 天，需要定期刷新。
若 Token 過期 → `get_me()` 回傳 `{"error": {"code": 190}}`，log 會印出 "Threads Token 已過期"。

#### 問題 C：THREADS_USER_ID 是數字 ID

不是 `@username`，是類似 `12345678901` 的數字。
取得方式：呼叫 `/me` API 就能拿到。

---

### 確認步驟

**Step 1：確認 .env 設定**
```bash
# 在根目錄執行
python -c "from src.config import settings; print('Token:', bool(settings.threads_access_token)); print('UserID:', bool(settings.threads_user_id))"
```

**Step 2：確認 Token 有效**
```bash
python -c "
import asyncio
from src.tracker.threads_client import get_me
result = asyncio.run(get_me())
print(result)
"
```

**Step 3：確認 Tracker 真的有在拿資料**
```bash
# 手動跑一次 Tracker
curl -X POST http://localhost:8000/api/tracker/run
# 然後看 log
```

---

### 如果 Token 沒有（最常見情況）

**取得 Threads API Token 流程**：
1. 前往 Meta Developer Dashboard
2. 建立 App，選 Threads API
3. 設定 Redirect URI
4. 取得 Long-lived Access Token（60 天有效）
5. 填入 `.env`：`THREADS_ACCESS_TOKEN=xxx`

**自動刷新 Token（未實作，建議加）**：
```python
# src/tracker/threads_client.py 加入
async def refresh_token() -> str | None:
    """使用現有 token 刷新為新 token（延長 60 天）"""
    token = _token()
    url = f"{BASE_URL}/refresh_access_token"
    params = {
        "grant_type": "th_refresh_token",
        "access_token": token,
    }
    result = await get(url, params=params)
    if result and "access_token" in result:
        # 寫回 .env 或 DB（建議寫 fl_settings）
        return result["access_token"]
    return None
```

---

### 影響範圍

若 Threads 追蹤從未正確運作：

| 功能 | 影響 |
|------|------|
| `audience_insights` 表 | 互動數據是 0 或舊的 |
| Lala 策略選題 | 無法參考「高互動主題」 |
| Sage 評分 | 無受眾偏好數據輸入 |
| 週報 | 互動率數據可能全是 0 |
| AI Office 系統健康面板 | Threads 那格可能一直是紅色 |

**這是整個「學習記憶 → 越用越準」機制的基礎**。若不修，系統等於一直在空跑。

---

### 修復工作清單

```
Step 1：確認 .env THREADS_ACCESS_TOKEN + THREADS_USER_ID
Step 2：執行 get_me() 確認 Token 有效
Step 3：手動執行 /api/tracker/run，確認能拿到貼文
Step 4：確認 posts 表有真實資料
Step 5：執行 /api/feedback/run，確認 audience_insights 有寫入
Step 6（加功能）：Token 刷新機制（每 50 天自動刷新）
Step 7（加功能）：AI Office 系統健康面板加「Threads 連線狀態」指示燈
```

---

## Part 2：Metrics 頁面現況與建置計畫

### 現況

**`dashboard/src/app/metrics/` 目錄不存在。**

這個頁面完全沒有建。導覽選單上是否有這個連結？如果有，現在點了會 404。

---

### Metrics 頁面應該顯示什麼

根據你的業務需求，Metrics 頁面 = **電商 + 內容的整合績效儀表板**。

#### 區塊 1：Threads 內容績效

| 指標 | 說明 |
|------|------|
| 本月平均互動率 | 本月所有發文的平均值 |
| 互動率趨勢折線圖 | 過去 30 天日趨勢 |
| 各類型文章表現 | 問題型 / 故事型 / 教學型 比較 |
| 粉絲成長曲線 | 追蹤者數量變化（需 Threads API）|
| 最佳發文時段 | 熱力圖（0-24h × 週一-週日）|

#### 區塊 2：Flow Lab 電商績效

| 指標 | 說明 |
|------|------|
| 本月總營收 | 所有 SKU 7 天銷售加總 |
| 各商品毛利率比較 | 橫條圖排序 |
| ROAS 趨勢 | 各商品廣告回報率 |
| 庫存周轉天數 | 每個 SKU 還剩幾天貨 |
| 安全 CPA vs 實際廣告費 | 是否在廣告上限內 |

#### 區塊 3：選品漏斗

```
靈感 (N) → 調查中 (N) → 可進樣 (N) → 已上架 (N) → 放大中 (N)
```
漏斗圖：直觀看到選品轉化率。

---

### 後端需要的 API

現有 API 不足，需要新增：

```python
# 1. Threads 內容月報數據
GET /api/stats/monthly-content
→ { avg_engagement: 0.05, by_category: [...], by_day: [...], ... }

# 2. Flow Lab 月報數據
GET /api/stats/monthly-ecommerce
→ { total_revenue_7d: 12500, products: [{sku, margin, roas, ...}], ... }

# 3. 選品漏斗數據
GET /api/ecommerce/funnel
→ { idea: 3, investigating: 5, sample_pending: 2, listed: 8, scaling: 2 }
```

---

### 前端建置規格

**框架**：Next.js + Recharts（已在 package.json，可直接用）

**頁面結構**：
```
/metrics
  ├── 頁籤：內容績效 | 電商績效 | 選品漏斗
  ├── 日期範圍選擇器（本週 / 本月 / 近 90 天）
  └── 圖表區塊（詳見上方）
```

**優先實作**：
1. 電商績效（Flow Lab 數據在 DB 裡，不依賴 Threads API）
2. 選品漏斗（需要 Part 1 的生命週期狀態流）
3. 內容績效（依賴 Threads 追蹤正常運作）

---

## 實作優先順序

```
立即（本週）
└── Part 1 Step 1-4：確認 Threads 追蹤是否正常

近期（1-2 週）
├── Metrics 頁面電商績效 Tab
└── Threads Token 刷新機制

中期（1 個月）
├── Metrics 頁面內容績效 Tab（依賴 Threads 正常）
└── 選品漏斗 Tab（依賴生命週期狀態流）
```
