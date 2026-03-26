# CoinCat Full Auto v1 規格書
> 版本：v1.0  
> 用途：提供給 AI / 工程師 / 自己開發時使用的全自動交易系統規格文件  
> 目標：不依賴 TradingView，不靠手動畫線，不做半自動提醒，直接建立 **可研究 / 可回測 / 可 paper trade / 可小額實盤** 的全自動交易框架

---

# 1. 專案目標

## 1.1 核心目標
建立一套以 **技術結構 + 籌碼條件 + 劇本分類 + 風控 + 自動下單** 為核心的全自動交易系統。

系統必須做到：

- 自動抓資料
- 自動判斷市場結構
- 自動判斷籌碼條件
- 自動分類進入哪一套劇本
- 自動產生 LONG / SHORT / HOLD 訊號
- 自動執行風控
- 自動下單
- 自動記錄與檢討

---

## 1.2 明確不做的事
v1 階段先 **不做** 以下內容：

- 不做 12 套全部一次上線
- 不做高頻交易
- 不做 orderbook 微結構優化
- 不做多交易所同步套利
- 不做超複雜 AI 模型先決策再下單
- 不做全市場掃 100 個幣種

---

## 1.3 v1 階段的成功定義
v1 不是追求暴利，而是追求「系統成立」。

成功標準：

1. 能穩定抓到資料
2. 能正確分類 3 套劇本
3. 能跑回測
4. 能 paper trade
5. 能小額自動實單
6. 有完整 log 可回溯每筆交易原因

---

# 2. 系統總架構

```text
Exchange Data + Derivatives Data
            ↓
      Data Fetcher
            ↓
    Feature / Align Engine
            ↓
     Structure Engine
(突破 / 跌破 / 橫盤 / 高低位)
            ↓
       Chip Engine
 (OI / Funding / 淨差代理 / 清算)
            ↓
     Scenario Engine
    (劇本分類 1~3 套)
            ↓
      Signal Engine
 (LONG / SHORT / HOLD)
            ↓
       Risk Engine
(倉位 / 停損 / 日損 / 停機)
            ↓
    Execution Engine
      (交易所 API)
            ↓
 Logger / Position / Reports
```

---

# 3. v1 先做哪 3 套

v1 不直接做全部 12 套，而是先做最容易量化、最容易回測、最適合自動化的 3 套。

## 3.1 劇本 A：真漲推進
### 白話
價格向上突破，且 OI 增加、淨差偏多，代表真有兵力推進，不是空漲。

### v1 定義方向
- 結構：突破近期高點
- 籌碼：OI 上升
- 籌碼：淨差代理轉強
- 排除：Funding 不過熱

### 訊號
- LONG

---

## 3.2 劇本 B：真跌壓制
### 白話
價格向下跌破，且 OI 增加、淨差偏空，代表真有空方補兵壓制。

### v1 定義方向
- 結構：跌破近期低點
- 籌碼：OI 上升
- 籌碼：淨差代理轉弱
- 排除：Funding 不處於極端反彈區

### 訊號
- SHORT

---

## 3.3 劇本 C：假突破
### 白話
價格表面破高，但 OI 沒增加、淨差沒變強，甚至下一根收回區間內，代表沒人補兵，屬於誘多。

### v1 定義方向
- 結構：當下突破前高
- 籌碼：OI 平或弱
- 籌碼：淨差代理弱
- 結構確認：下一根或短時間內收回線內

### 訊號
- SHORT 或 HOLD（取決於保守版/積極版）

---

# 4. 前置作業清單

# 4.1 你要先準備的東西

## A. 交易所帳號
建議先用：
- OKX（優先）
- BingX（第二交易所，可後接）

## B. API Key
至少準備：
- API Key
- Secret
- Passphrase（若交易所需要）
- 啟用交易權限
- IP 白名單（若交易所支援）

## C. 衍生品資料來源
因為策略需要：
- OI
- Funding Rate
- Long/Short Ratio
- Liquidation Data

所以要準備：
- 可用的衍生品資料 API
- 或可穩定取得這些欄位的資料源

## D. 開發環境
- Python 3.11+
- Git
- 虛擬環境（venv / conda）
- 本機或 VPS
- `.env` 環境變數管理

## E. 日誌與儲存
至少需要：
- CSV / SQLite
- log 檔案資料夾
- 回測報告輸出資料夾

---

# 4.2 建議的套件
```text
pandas
numpy
ccxt
httpx
requests
pydantic
python-dotenv
loguru
ta
scipy
sqlalchemy（可選）
```

---

# 5. 資料規格

## 5.1 行情資料（必備）
欄位建議：

```text
timestamp
open
high
low
close
volume
```

時間框架建議：
- 大方向：1H 或 4H
- 劇本分類：15m
- 入場：5m

---

## 5.2 衍生品資料（必備）
欄位建議：

```text
timestamp
oi
funding_rate
long_short_ratio
top_trader_long_short_ratio
liquidation_long
liquidation_short
```

---

## 5.3 合併後的標準欄位
```text
timestamp, open, high, low, close, volume,
oi, funding_rate, long_short_ratio,
top_trader_long_short_ratio,
liquidation_long, liquidation_short
```

---

# 6. 時間框架設計

## 6.1 三層時間框架
### 4H / 1H
看大方向，避免逆大趨勢亂做。

### 15m
主要劇本分類。

### 5m
主要入場與短期確認。

---

## 6.2 v1 簡化版
如果開發初期太複雜，v1 可以先只用：

- 15m：劇本分類
- 5m：入場

---

# 7. Feature Engine 設計

這裡是把原始資料轉成策略可以使用的欄位。

## 7.1 價格結構特徵
```python
rolling_high_20 = high.rolling(20).max()
rolling_low_20 = low.rolling(20).min()
range_pct_20 = (rolling_high_20 - rolling_low_20) / close
position_in_range = (close - rolling_low_20) / (rolling_high_20 - rolling_low_20)
```

### 對應概念
- rolling_high_20：近 20 根高點
- rolling_low_20：近 20 根低點
- range_pct_20：是否橫盤
- position_in_range：高位 / 低位

---

## 7.2 OI 特徵
```python
oi_change_1 = oi.pct_change(1)
oi_change_3 = oi.pct_change(3)
oi_change_6 = oi.pct_change(6)
```

### 對應概念
- oi_change_3 > 0.03 可暫定視為 OI 有增加
- abs(oi_change_3) < 0.01 可暫定視為 OI 停滯

---

## 7.3 Funding 特徵
```python
funding_mean_3 = funding_rate.rolling(3).mean()
funding_hot = (funding_rate > 0.0001) & (funding_mean_3 > 0.00008)
funding_cold = (funding_rate < -0.0001) & (funding_mean_3 < -0.00008)
```

---

## 7.4 Long/Short 特徵
```python
ls_extreme_long = long_short_ratio > 1.5
ls_extreme_short = long_short_ratio < 0.67
```

---

## 7.5 淨差代理（v1 Proxy）
如果無法直接拿到淨差，v1 用代理值代替，例如：

```python
net_diff_proxy = (
    oi_change_3
    * (close.pct_change(3))
)
```

或更進一步用：
- OI 方向
- 價格方向
- 長短比偏移

組合成代理評分。

---

# 8. Structure Engine 設計

這個模組負責完全取代 TradingView 的人工結構判斷。

## 8.1 突破
```python
breakout = close > rolling_high_20.shift(1)
```

---

## 8.2 跌破
```python
breakdown = close < rolling_low_20.shift(1)
```

---

## 8.3 橫盤
```python
sideways = range_pct_20 < 0.02
```

---

## 8.4 高位 / 低位
```python
high_zone = position_in_range > 0.8
low_zone = position_in_range < 0.2
```

---

## 8.5 假突破判斷
```python
false_breakout = breakout & (close.shift(-1) < rolling_high_20)
```

> 注意：回測時可這樣定義；實盤時不能直接用未來資料，因此實盤版要改成「突破後 N 分鐘內是否重新跌回區間」。

---

# 9. Chip Engine 設計

## 9.1 OI 狀態
```python
oi_up = oi_change_3 > 0.03
oi_flat = abs(oi_change_3) < 0.01
oi_down = oi_change_3 < -0.03
```

---

## 9.2 Funding 狀態
```python
funding_overheat_long = funding_hot
funding_overheat_short = funding_cold
```

---

## 9.3 淨差代理狀態
```python
net_diff_up = net_diff_proxy > threshold_up
net_diff_down = net_diff_proxy < threshold_down
net_diff_small = abs(net_diff_proxy) < threshold_flat
```

---

# 10. Scenario Engine 設計

這裡就是把市場狀態分類成劇本。

## 10.1 劇本 A：真漲推進
```python
if breakout and oi_up and net_diff_up and not funding_overheat_long:
    scenario = "true_bull_push"
```

---

## 10.2 劇本 B：真跌壓制
```python
if breakdown and oi_up and net_diff_down and not funding_overheat_short:
    scenario = "true_bear_push"
```

---

## 10.3 劇本 C：假突破
```python
if breakout and oi_flat and net_diff_small and close_back_inside:
    scenario = "false_breakout"
```

> `close_back_inside` 需在實盤版用事件狀態機處理，不可以直接偷看未來 K 線。

---

# 11. Signal Engine 設計

場景不是最終下單動作，還要再轉成交易訊號。

```python
if scenario == "true_bull_push":
    signal = "LONG"

elif scenario == "true_bear_push":
    signal = "SHORT"

elif scenario == "false_breakout":
    signal = "SHORT"

else:
    signal = "HOLD"
```

---

# 12. Entry / Exit 規則

# 12.1 真漲推進
## Entry
- 劇本成立
- 5m 不再創更低
- 可以用突破後小回踩不破再進

## Stoploss
- 跌回突破前高之下
- 或固定 ATR 倍數停損

## Exit
- 達到 1R 先減碼
- OI 不再增加 + 淨差縮小 可全出
- 或移動停損

---

# 12.2 真跌壓制
## Entry
- 劇本成立
- 5m 反彈不過破位
- 再進 SHORT

## Stoploss
- 漲回跌破前低上方
- 或固定 ATR 倍數停損

## Exit
- 1R 先減碼
- OI 不再增加 + 淨差縮小 可出
- 或移動停損

---

# 12.3 假突破
## Entry
- 突破後跌回區間內
- 籌碼未跟上
- 反手 SHORT

## Stoploss
- 重新站上假突破高點上方

## Exit
- 回到區間中線可先減碼
- 回到區間下緣可全出

---

# 13. Risk Engine 設計

## 13.1 單筆風險
每筆只允許虧損帳戶資金的 0.5%～1%。

### 公式
```text
單筆可承受虧損 = 資金 × 0.005 ~ 0.01
```

---

## 13.2 倉位大小
```text
position_size = 可承受虧損 / (entry_price - stoploss_price)
```

---

## 13.3 系統級風控
- 每日最大虧損：2%～3%
- 連續虧損 3 筆停機
- API / WS 斷線停機
- 資料異常停機
- 重複訊號冷卻時間

---

## 13.4 倉位限制
- 同時最多 1 個主方向倉位
- 同時最多 1~2 筆交易
- 不允許無限制加碼

---

# 14. Execution Engine 設計

## 14.1 v1 先接哪個交易所
優先：
- OKX

第二：
- BingX

---

## 14.2 先做什麼商品
建議：
- BTC-USDT-SWAP
或
- BTC-USDT

不建議一開始就多幣種同時跑。

---

## 14.3 下單流程
```text
收到信號
→ 檢查是否已有持倉
→ 檢查風控
→ 計算部位大小
→ 下單
→ 等成交
→ 寫入持倉管理
→ 設定停損 / 出場條件
```

---

## 14.4 v1 執行原則
- 不做高頻
- 不做複雜網格
- 不做 martingale
- 先限價或簡化市價單
- 保留滑價與手續費緩衝

---

# 15. Log / Dashboard 設計

至少要記錄：

## 15.1 Signal Log
```text
timestamp, scenario, signal, close, oi, funding, long_short_ratio, net_diff_proxy
```

## 15.2 Trade Log
```text
timestamp, action, side, entry, stoploss, size, reason, status
```

## 15.3 System Log
```text
bot_started
data_updated
signal_triggered
order_sent
order_filled
risk_triggered
bot_stopped
```

---

# 16. 專案檔案結構

```text
coincat_bot/
├─ config/
│  ├─ settings.yaml
│  └─ secrets.env
├─ data/
│  ├─ raw/
│  ├─ processed/
│  └─ cache/
├─ logs/
├─ reports/
├─ backtest/
│  ├─ backtest_runner.py
│  └─ metrics.py
├─ src/
│  ├─ main.py
│  ├─ scheduler.py
│  ├─ data_fetcher.py
│  ├─ feature_engine.py
│  ├─ structure_engine.py
│  ├─ chip_engine.py
│  ├─ scenario_engine.py
│  ├─ signal_engine.py
│  ├─ risk_engine.py
│  ├─ execution_engine.py
│  ├─ position_manager.py
│  └─ logger.py
└─ tests/
```

---

# 17. 開發順序 Roadmap

## Phase 1：資料打通
目標：
- 抓 K 線
- 抓 OI / funding / long-short / liquidation
- 對齊 timestamp

---

## Phase 2：結構引擎
目標：
- breakout
- breakdown
- sideways
- high_zone / low_zone

---

## Phase 3：劇本 1~3
目標：
- scenario 判斷成功
- 可以輸出 LONG / SHORT / HOLD

---

## Phase 4：回測
目標：
- 用歷史資料測劇本有效性
- 調 threshold

---

## Phase 5：Paper Trade
目標：
- 即時跑，但不下真單
- 檢查 signal / log / 風控

---

## Phase 6：小額 Live
目標：
- 真實 API 下單
- 低資金驗證 execution

---

# 18. 回測驗證標準

至少看這些：

- Win Rate
- Average Win / Average Loss
- Profit Factor
- Max Drawdown
- Sharpe Ratio
- Expectancy
- 交易次數是否足夠

---

## 基本門檻（可先暫定）
```text
Profit Factor > 1.2
Sharpe > 1.0
Max Drawdown < 20%
交易次數 > 50
```

---

# 19. 常見風險與錯誤

## 19.1 看未來資料
例如用下一根 K 判斷當前訊號，這在實盤會失效。

## 19.2 閾值過度擬合
不要把條件調到只適合某一段歷史。

## 19.3 太早碰 orderbook
你現在主要 edge 不在 orderbook，先不要把系統搞太重。

## 19.4 一次做 12 套
先做 3 套跑通，再擴充。

---

# 20. 給 AI / 工程師的開發任務 Prompt

## Prompt 1：建專案骨架
```text
請幫我建立一個 Python 專案骨架，用於開發 CoinCat 全自動交易系統 v1。
需求包含：
1. data_fetcher.py
2. feature_engine.py
3. structure_engine.py
4. chip_engine.py
5. scenario_engine.py
6. signal_engine.py
7. risk_engine.py
8. execution_engine.py
9. logger.py
10. main.py

請使用 Python 3.11、pandas、ccxt、httpx、loguru。
```

---

## Prompt 2：寫 Structure Engine
```text
請幫我撰寫 structure_engine.py，要求：
- 輸入 pandas DataFrame
- 自動計算 rolling_high_20, rolling_low_20
- 判斷 breakout, breakdown, sideways, high_zone, low_zone
- 回傳帶有新欄位的 DataFrame
- 程式要有註解與基本錯誤處理
```

---

## Prompt 3：寫劇本分類器
```text
請幫我撰寫 scenario_engine.py。
輸入為已完成 feature_engine 與 structure_engine 的 DataFrame。
請先實作三套劇本：
1. true_bull_push
2. true_bear_push
3. false_breakout

每一套劇本請用明確布林條件判斷，並在 DataFrame 新增 scenario 欄位。
```

---

## Prompt 4：寫風控模組
```text
請幫我撰寫 risk_engine.py。
需求：
- 計算單筆最大風險 0.5%~1%
- 根據 entry 與 stoploss 計算 position size
- 實作 daily loss limit
- 實作連續虧損停機
- 輸出是否允許下單與倉位大小
```

---

## Prompt 5：回測器
```text
請幫我建立一個 backtest_runner.py。
需求：
- 輸入 signal DataFrame
- 模擬 entry / exit / stoploss / takeprofit
- 計算總報酬、勝率、Profit Factor、Sharpe Ratio、Max Drawdown
- 輸出報表 CSV
```

---

# 21. 最後的執行原則

## 原則 1
先求能跑，再求漂亮。

## 原則 2
先做穩定的資料與 log，不要一開始就迷信策略。

## 原則 3
先做 3 套，不要一次 12 套。

## 原則 4
先 paper trade，再 live。

## 原則 5
先建立能持續優化的架構，而不是一次想做出完美系統。

---

# 22. 一句話總結

**CoinCat Full Auto v1 的本質不是「直接賺錢的神策略」，而是把你的交易理解，正式轉成一套可研究、可回測、可自動執行的系統。**
