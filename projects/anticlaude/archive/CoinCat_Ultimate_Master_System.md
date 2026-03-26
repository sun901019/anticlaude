# CoinCat 終極整合版系統規格書（Ultimate Master System）
> 檔案格式：Markdown  
> 用途：提供給 AI / 工程師 / 自己開發時使用  
> 目標：把你的「技術分析 + 籌碼分析 + 12 套劇本」整合成一套 **可研究、可量化、可回測、可自動化、可小額實盤** 的完整系統藍圖  
> 版本：v1.0

---

# 目錄
1. 專案定位  
2. 你目前策略的本質  
3. 你目前能力評分與缺口  
4. 系統總體架構  
5. 前置作業：你要先準備什麼  
6. 市場與資料來源架構  
7. 為什麼一開始不該依賴 TradingView  
8. 策略核心：技術分析 + 籌碼 + 劇本  
9. 六大核心指標完整定義  
10. 12 套劇本總覽  
11. 先做哪 3 套（v1 優先）  
12. 如何把主觀判斷量化  
13. Structure Engine（取代 TradingView）  
14. Chip Engine（籌碼引擎）  
15. Scenario Engine（劇本分類器）  
16. Signal Engine（交易訊號）  
17. Entry / Exit / Stoploss 規格  
18. 風控系統設計  
19. 自動下單與執行系統  
20. 日誌、監控與報表  
21. Freqtrade 實作規劃  
22. 回測與驗證系統  
23. 避免假回測的機制  
24. Paper Trade → Live 路線  
25. 推薦工具與技能庫（補足你低分項）  
26. 專案資料夾結構  
27. Roadmap（開發順序）  
28. 給 AI / 工程師的指令模板  
29. 最終執行原則  
30. 一句話總結

---

# 1. 專案定位

## 1.1 這個專案不是什麼
這不是：
- 單純畫線教學筆記
- 單一技術指標策略
- 喊單系統
- 追求短期暴利的高頻套利系統
- 複製別人 100ms 延遲套利的 bot

## 1.2 這個專案是什麼
這是一套：
- 以 **市場結構 + 籌碼狀態 + 劇本分類** 為核心
- 最終走向 **量化 + 自動化**
- 能做：
  - 研究
  - 回測
  - 優化
  - Paper Trade
  - 小額實盤

## 1.3 核心轉換思維
你真正要做的是這條路：

```text
主觀交易理解
↓
條件化
↓
數值化
↓
可回測
↓
可驗證
↓
可自動化
↓
可放大
```

---

# 2. 你目前策略的本質

## 2.1 你現在不是只有「一套策略」
你現在擁有的其實是：

**一套籌碼結構化判斷系統**

它不是：
- RSI < 30 就買
- MACD 金叉就進

而是：

```text
先看技術位置
↓
再看籌碼是否支持
↓
再判斷屬於哪一套劇本
↓
最後決定做多 / 做空 / 觀望
```

## 2.2 你的優勢
你已經具備：
- 看結構的能力
- 看籌碼的能力
- 用劇本分類的能力
- 風險意識
- 避免心理陷阱的意識

## 2.3 你目前最大缺口
你現在最缺的是：

### A. 可量化
你很多判斷還是：
- 高位
- 停滯
- 爆正
- 擴大
- 縮小
- 急升
- 急降

這些詞對人有意義，對電腦沒有。

### B. 可自動化
你還有部分依賴：
- 人眼看結構
- 圖形直覺
- 主觀判斷

所以系統還不能完全自動跑。

---

# 3. 你目前能力評分與缺口

## 3.1 原始評分
- 市場理解：8.5 / 10
- 教學框架：9 / 10
- 可手動交易性：7.5 / 10
- 可量化程度：4.5 / 10
- 可自動化程度：3.5 / 10

## 3.2 這代表什麼
### 市場理解高
代表你不是亂學指標，你已經看懂：
- 市場兵力
- 擁擠
- 假突破
- 真突破
- 主力獵殺與清算

### 教學框架高
代表你的內容已經很適合：
- 當系統規格書
- 當 AI 訓練說明
- 當開發需求文件

### 可量化低
代表還沒做到：
- 明確閾值
- 明確公式
- 明確條件判斷
- 回測級規則

### 可自動化低
代表還沒做到：
- 不靠 TradingView
- 不靠人工判結構
- 不靠手動 alert
- 不靠人決定是否進場

## 3.3 本文件的目的
這份文件就是要把你補到這個方向：

- 市場理解：9.5
- 教學框架：9.5
- 可手動交易：8
- 可量化：8.5~9
- 可自動化：8.5~9

---

# 4. 系統總體架構

```text
Exchange Market Data
+ Derivatives Data
        ↓
Data Fetcher
        ↓
Feature Engine
        ↓
Structure Engine
(突破 / 跌破 / 橫盤 / 高低位)
        ↓
Chip Engine
(OI / Funding / Long-Short / Liquidation / Net Diff Proxy)
        ↓
Scenario Engine
(12 套劇本分類，v1 先做 3 套)
        ↓
Signal Engine
(LONG / SHORT / HOLD)
        ↓
Risk Engine
(倉位 / 停損 / 日損 / 連虧停機 / API停機)
        ↓
Execution Engine
(OKX / BingX)
        ↓
Logger / Position Manager / Reports
        ↓
Backtest / Paper Trade / Live
```

---

# 5. 前置作業：你要先準備什麼

## 5.1 交易所帳戶
建議：
- 主：OKX
- 備：BingX

### 為什麼先用 OKX
- API 文件與結構通常較清楚
- 生態工具較多
- 適合第一版開發

### 為什麼 BingX 可保留
- 可當第二交易所
- 可做後續擴充與比較

## 5.2 API 金鑰
至少要準備：
- API Key
- Secret
- Passphrase（若交易所需要）
- 交易權限
- IP 白名單（能設就設）

## 5.3 衍生品資料來源
你的策略不是只吃 K 線，所以一定要準備：
- OI
- Funding Rate
- Long/Short Ratio
- Liquidation Data

## 5.4 開發環境
- Python 3.11+
- Git
- VS Code 或你熟悉的 IDE
- 虛擬環境（venv / conda）
- `.env` 管理密鑰
- 本機 + 後續 VPS

## 5.5 儲存與記錄
先準備：
- CSV / SQLite
- logs 資料夾
- reports 資料夾
- 可視情況加入 PostgreSQL（後期）

---

# 6. 市場與資料來源架構

## 6.1 你策略需要的資料層

### A. 現貨 / 合約行情
- open
- high
- low
- close
- volume

### B. 衍生品資料
- oi
- funding_rate
- long_short_ratio
- top_trader_long_short_ratio
- liquidation_long
- liquidation_short

## 6.2 標準資料表欄位
建議統一成：

```text
timestamp, open, high, low, close, volume,
oi, funding_rate, long_short_ratio,
top_trader_long_short_ratio,
liquidation_long, liquidation_short
```

## 6.3 時間框架
### 大方向
- 4H / 1H

### 劇本分類
- 15m

### 入場精細化
- 5m

## 6.4 v1 簡化版
如果一開始複雜度太高，先做：
- 15m：劇本分類
- 5m：入場

---

# 7. 為什麼一開始不該依賴 TradingView

## 7.1 TradingView 不是不能用
它可以用來：
- 看圖
- 畫結構
- 設 alert
- 做半自動流程

## 7.2 但你現在要的是全自動
所以你不能把第一步永遠交給人工。

你原本流程是：

```text
TA 找位置
↓
籌碼判真假
↓
劇本決策
```

其中第一步如果還要靠人眼：
- 就不是真正自動
- 就不能 24 小時自己跑
- 就不能完整回測

## 7.3 正確做法
把 TradingView 的工作轉進系統：

- 畫線 → rolling high / rolling low
- 看突破 → breakout 條件
- 看跌破 → breakdown 條件
- 看橫盤 → range_pct 條件
- 看高位 / 低位 → position_in_range

---

# 8. 策略核心：技術分析 + 籌碼 + 劇本

## 8.1 正確流程
```text
先用技術分析找候選位置
↓
用籌碼分析判真假
↓
套用劇本分類
↓
決定開倉 / 平倉 / 觀望
```

## 8.2 這套系統的核心不是預測未來
而是：

**在當下判斷這個位置背後有沒有真實兵力支持**

## 8.3 你真正的 edge
不是來自單一指標，而是來自：

- 結構位置
- OI 變化
- 淨差方向
- funding 擁擠度
- long/short 極端
- 清算區域

這些一起組合。

---

# 9. 六大核心指標完整定義

## 9.1 OI（Open Interest）
### 定義
市場裡尚未平倉的槓桿合約數量。

### 解讀
- OI 上升：市場參與槓桿增加
- OI 下降：市場退潮
- OI 高：爆倉風險高

### 常見錯誤
OI 上升不等於必漲或必跌，只代表更多人進場。

---

## 9.2 多空比（Long / Short Ratio）
### 定義
多方與空方的人數 / 資金比例。

### 解讀
- > 1：偏多
- < 1：偏空

### 常見錯誤
人多的方向不一定正確，尤其散戶多數時常是反向參考。

---

## 9.3 淨多 / 淨空
### 定義
今天多軍 / 空軍實際補了多少兵。

### 解讀
- 淨多 > 0：多軍補兵
- 淨空 > 0：空軍補兵

### 意義
能看誰在主動加強力量。

---

## 9.4 淨差值（Net Difference）
### 定義
淨多頭 - 淨空頭

### 解讀
- > 0：多方佔優
- < 0：空方佔優
- 翻正 / 翻負：主導權換邊

### 為何重要
它比單看淨多或淨空更接近「總結戰況」。

---

## 9.5 資金費率（Funding Rate）
### 定義
永續合約多空雙方為維持價格平衡互相支付的費用。

### 解讀
- 正值：做多擁擠，多方付費
- 負值：做空擁擠，空方付費

### 常見錯誤
單次值沒意義，要看持續極端。

---

## 9.6 清算熱力圖（Liquidation Heatmap）
### 定義
潛在爆倉集中區域。

### 解讀
- 是吸引區
- 不是必到價
- 容易先被掃，再反向

---

# 10. 12 套劇本總覽

## 第一層：新手 4 套母型態
1. 真漲推進  
2. 真跌壓制  
3. 擠空反彈  
4. 出清落地  

## 第二層：進階 4 套陷阱 / 過擠
5. 假突破  
6. 假跌破  
7. 多擁擠末期  
8. 空擁擠末期  

## 第三層：老手 4 套戰法
9. 掃清算反拉  
10. 主力獵殺停損  
11. 趨勢加速（多）  
12. 趨勢加速（空）  

---

# 11. 先做哪 3 套（v1 優先）

## 11.1 為什麼不一次做 12 套
因為：
- 條件太多
- 開發太重
- 容易亂
- 回測難解釋
- 自動化風險太高

## 11.2 v1 優先 3 套
### A. 真漲推進
最直觀、最好量化、最適合順勢。

### B. 真跌壓制
和真漲推進對稱，好做、好測。

### C. 假突破
價值很高，因為它是「過濾器」與「反手邏輯」。

---

# 12. 如何把主觀判斷量化

## 12.1 原則
把這些字全部改成明確條件：
- 高
- 低
- 停滯
- 爆正
- 擴大
- 縮小
- 急升
- 急降

## 12.2 例子
### 原本
OI 高停滯

### 改成
- OI 位於近 24h 百分位 > 80%
- 過去 3 根 oi_change 絕對值 < 1%

### 原本
高位橫盤

### 改成
- position_in_range > 0.8
- range_pct_20 < 0.02

### 原本
Funding 爆正

### 改成
- funding_rate > 0.0001
- funding_mean_3 > 0.00008

---

# 13. Structure Engine（取代 TradingView）

## 13.1 目的
用數學取代人工畫線。

## 13.2 核心特徵
```python
rolling_high_20 = high.rolling(20).max()
rolling_low_20 = low.rolling(20).min()
range_pct_20 = (rolling_high_20 - rolling_low_20) / close
position_in_range = (close - rolling_low_20) / (rolling_high_20 - rolling_low_20)
```

## 13.3 判斷條件

### 突破
```python
breakout = close > rolling_high_20.shift(1)
```

### 跌破
```python
breakdown = close < rolling_low_20.shift(1)
```

### 橫盤
```python
sideways = range_pct_20 < 0.02
```

### 高位 / 低位
```python
high_zone = position_in_range > 0.8
low_zone = position_in_range < 0.2
```

### 假突破（回測版）
```python
false_breakout = breakout & (close.shift(-1) < rolling_high_20)
```

> 注意：實盤不能偷看未來資料，所以實盤版要用事件狀態機處理。

---

# 14. Chip Engine（籌碼引擎）

## 14.1 OI 特徵
```python
oi_change_1 = oi.pct_change(1)
oi_change_3 = oi.pct_change(3)
oi_change_6 = oi.pct_change(6)

oi_up = oi_change_3 > 0.03
oi_flat = abs(oi_change_3) < 0.01
oi_down = oi_change_3 < -0.03
```

## 14.2 Funding 特徵
```python
funding_mean_3 = funding_rate.rolling(3).mean()
funding_hot = (funding_rate > 0.0001) & (funding_mean_3 > 0.00008)
funding_cold = (funding_rate < -0.0001) & (funding_mean_3 < -0.00008)
```

## 14.3 多空比極端
```python
ls_extreme_long = long_short_ratio > 1.5
ls_extreme_short = long_short_ratio < 0.67
```

## 14.4 淨差代理（v1）
如果你暫時拿不到真正淨差，可先用 proxy：

```python
net_diff_proxy = oi_change_3 * close.pct_change(3)
```

再配合長短比與價格方向做綜合評分。

---

# 15. Scenario Engine（劇本分類器）

## 15.1 劇本 A：真漲推進
```python
if breakout and oi_up and net_diff_proxy > threshold_up and not funding_hot:
    scenario = "true_bull_push"
```

## 15.2 劇本 B：真跌壓制
```python
if breakdown and oi_up and net_diff_proxy < threshold_down and not funding_cold:
    scenario = "true_bear_push"
```

## 15.3 劇本 C：假突破
```python
if breakout and oi_flat and abs(net_diff_proxy) < threshold_flat and close_back_inside:
    scenario = "false_breakout"
```

---

# 16. Signal Engine（交易訊號）

## 16.1 劇本不等於直接下單
劇本是市場狀態分類，交易訊號要再轉。

## 16.2 基本規則
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

# 17. Entry / Exit / Stoploss 規格

## 17.1 真漲推進
### Entry
- 劇本成立
- 5m 回踩不破突破前高
- 或 5m 出現確認 K

### Stoploss
- 跌回突破前高之下
- 或 ATR 倍數停損

### Exit
- 1R 先減碼
- OI 不再增加 + 淨差縮小時出場
- 或移動停損

---

## 17.2 真跌壓制
### Entry
- 劇本成立
- 5m 反彈不過跌破位
- 再進 SHORT

### Stoploss
- 站回跌破前低上方
- 或 ATR 停損

### Exit
- 1R 先減碼
- OI 不再增加 + 淨差縮小出場
- 或移動停損

---

## 17.3 假突破
### Entry
- 價格突破後快速收回區間內
- OI 未增加
- 籌碼未跟上

### Stoploss
- 重新站上假突破高點

### Exit
- 區間中線先減碼
- 區間下緣全出

---

# 18. 風控系統設計

## 18.1 單筆風險
每筆交易只允許虧損：
- 帳戶資金的 0.5% ~ 1%

### 公式
```text
單筆可承受虧損 = 資金 × 0.005 ~ 0.01
```

## 18.2 倉位大小
```text
position_size = 可承受虧損 / (entry - stoploss)
```

## 18.3 系統級風控
- 每日最大虧損：2% ~ 3%
- 連續虧損 3 筆停機
- API 失敗停機
- 資料中斷停機
- 重複訊號冷卻
- 同時最多 1 個主倉位

## 18.4 v1 原則
不要：
- martingale
- 無限加碼
- 滿倉
- 無停損

---

# 19. 自動下單與執行系統

## 19.1 v1 優先交易所
- OKX

## 19.2 v1 建議商品
- BTC-USDT-SWAP
或
- BTC-USDT

## 19.3 執行流程
```text
收到 signal
↓
檢查是否已有持倉
↓
檢查風控是否允許
↓
計算 position size
↓
送出訂單
↓
確認成交
↓
寫入 log
↓
監控停損 / 出場
```

## 19.4 v1 執行原則
- 不做高頻
- 不做 grid
- 不做 martingale
- 先用簡單單一策略單
- 先以低資金驗證執行是否正常

---

# 20. 日誌、監控與報表

## 20.1 Signal Log
```text
timestamp, scenario, signal, close, oi, funding_rate, long_short_ratio, net_diff_proxy
```

## 20.2 Trade Log
```text
timestamp, side, entry, stoploss, size, scenario, reason, status
```

## 20.3 System Log
```text
bot_started
data_updated
signal_triggered
order_sent
order_filled
risk_triggered
bot_stopped
```

## 20.4 Dashboard（後期）
可以顯示：
- 今日 PnL
- 當前持倉
- 最近 10 筆交易
- 最近 10 筆信號
- 哪一套劇本勝率最好

---

# 21. Freqtrade 實作規劃

## 21.1 為什麼用 Freqtrade
它適合你用來：
- 回測
- Hyperopt
- Dry-run
- 自動交易

## 21.2 專案結構
```text
freqtrade/
├── user_data/
│   ├── strategies/
│   ├── config.json
│   ├── data/
│   ├── logs/
```

## 21.3 Strategy 基本框架
```python
from freqtrade.strategy import IStrategy
import pandas as pd

class CoinCatStrategy(IStrategy):
    timeframe = '5m'

    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe['rolling_high'] = dataframe['high'].rolling(20).max()
        dataframe['rolling_low'] = dataframe['low'].rolling(20).min()
        dataframe['breakout'] = dataframe['close'] > dataframe['rolling_high'].shift(1)
        dataframe['breakdown'] = dataframe['close'] < dataframe['rolling_low'].shift(1)
        return dataframe
```

## 21.4 外部籌碼資料
Freqtrade 預設沒有：
- OI
- funding
- liquidation

你要自己把外部資料 merge 進 DataFrame。

## 21.5 例子：真漲
```python
dataframe.loc[
    (
        (dataframe['breakout']) &
        (dataframe['oi_up'])
    ),
    'enter_long'
] = 1
```

## 21.6 例子：真跌
```python
dataframe.loc[
    (
        (dataframe['breakdown']) &
        (dataframe['oi_up'])
    ),
    'enter_short'
] = 1
```

## 21.7 例子：假突破
```python
dataframe['false_breakout'] = (
    dataframe['breakout'] &
    dataframe['oi_flat'] &
    (dataframe['close'] < dataframe['rolling_high'])
)

dataframe.loc[
    dataframe['false_breakout'],
    'enter_short'
] = 1
```

---

# 22. 回測與驗證系統

## 22.1 你要驗證什麼
### A. 策略有沒有 edge
### B. 條件是不是過度擬合
### C. 不同市場環境有沒有失效
### D. 執行成本會不會吃掉利潤

## 22.2 基本指標
- Win Rate
- Average Win / Average Loss
- Profit Factor
- Max Drawdown
- Sharpe Ratio
- Expectancy
- 交易次數

## 22.3 基本門檻
```text
Profit Factor > 1.2
Sharpe > 1.0
Max Drawdown < 20%
交易次數 > 50
```

## 22.4 回測流程
### Step 1
先跑最簡單版本，不加太多條件

### Step 2
逐步加入 OI / funding 條件

### Step 3
做 time split

### Step 4
做 walk-forward

### Step 5
再做 Dry-run

---

# 23. 避免假回測的機制

## 23.1 Lookahead Bias
不能用未來資料判斷當下。

錯誤例子：
```python
false_breakout = breakout and close.shift(-1) < rolling_high
```

這只能作研究參考，不能直接作 live 條件。

## 23.2 Data Leakage
特徵不能偷偷帶入未來資訊。

## 23.3 Overfitting
不要把閾值調到只適合某一段歷史。

## 23.4 沒算交易成本
回測一定要算：
- fee
- slippage
- latency buffer

---

# 24. Paper Trade → Live 路線

## 24.1 純回測
目標：
- 看策略有沒有基本形狀
- 找出明顯錯誤條件

## 24.2 Dry Run / Paper Trade
目標：
- 看即時資料有沒有正常
- 看 signal 是否與預期一致
- 看 log 是否完整

## 24.3 小額 Live
目標：
- 驗證 API 與 execution
- 驗證停損與平倉
- 驗證 bot 是否穩定

---

# 25. 推薦工具與技能庫（補足你低分項）

## 25.1 直接必備
### CCXT
用途：
- 抓交易所資料
- 下單
- 查帳戶

### pandas
用途：
- 資料整理
- 特徵工程
- 合併 OI / funding

### Freqtrade
用途：
- 回測
- Hyperopt
- Dry-run
- 自動交易

## 25.2 很適合你後續補強的工具
### VectorBT
用途：
- 高速回測
- 參數掃描

### Backtrader
用途：
- 自訂回測架構

### Hummingbot
用途：
- 做市、掛單策略
> 不是你 v1 重點

### NautilusTrader
用途：
- 低延遲、專業級系統
> 現在先不用

## 25.3 你最需要補的「skills」
### Skill A：Feature Engineering
把主觀語言轉成欄位。

### Skill B：Backtest Validation
不只是看勝率，要看整體策略穩定性。

### Skill C：Execution & Risk
很多系統不是輸在策略，而是死在執行與風控。

### Skill D：Data Engineering
資料抓得不穩，系統一定死。

---

# 26. 專案資料夾結構

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

# 27. Roadmap（開發順序）

## Phase 1：資料打通
- 抓 K 線
- 抓 OI / funding / long-short / liquidation
- 對齊 timestamp

## Phase 2：Structure Engine
- breakout
- breakdown
- sideways
- high_zone / low_zone

## Phase 3：Chip Engine
- OI 狀態
- funding 狀態
- long-short 狀態
- net_diff_proxy

## Phase 4：Scenario Engine
先完成 3 套：
- true_bull_push
- true_bear_push
- false_breakout

## Phase 5：Backtest
- 看基本有效性
- 調參數

## Phase 6：Dry-run
- 即時訊號
- 不下真單

## Phase 7：Live 小額
- 低本金測 execution

---

# 28. 給 AI / 工程師的指令模板

## 28.1 建專案骨架
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

## 28.2 寫 Structure Engine
```text
請幫我撰寫 structure_engine.py，要求：
- 輸入 pandas DataFrame
- 自動計算 rolling_high_20, rolling_low_20
- 判斷 breakout, breakdown, sideways, high_zone, low_zone
- 回傳帶有新欄位的 DataFrame
- 程式要有註解與基本錯誤處理
```

## 28.3 寫 Scenario Engine
```text
請幫我撰寫 scenario_engine.py。
輸入為已完成 feature_engine 與 structure_engine 的 DataFrame。
請先實作三套劇本：
1. true_bull_push
2. true_bear_push
3. false_breakout

每一套劇本請用明確布林條件判斷，並在 DataFrame 新增 scenario 欄位。
```

## 28.4 寫 Risk Engine
```text
請幫我撰寫 risk_engine.py。
需求：
- 計算單筆最大風險 0.5%~1%
- 根據 entry 與 stoploss 計算 position size
- 實作 daily loss limit
- 實作連續虧損停機
- 輸出是否允許下單與倉位大小
```

## 28.5 寫回測器
```text
請幫我建立一個 backtest_runner.py。
需求：
- 輸入 signal DataFrame
- 模擬 entry / exit / stoploss / takeprofit
- 計算總報酬、勝率、Profit Factor、Sharpe Ratio、Max Drawdown
- 輸出報表 CSV
```

## 28.6 寫 Freqtrade 版本
```text
請幫我把 CoinCat v1 的三套劇本，轉成 Freqtrade strategy class。
條件如下：
- 真漲推進
- 真跌壓制
- 假突破
請在 populate_indicators 中計算：
rolling_high, rolling_low, breakout, breakdown, oi_change, oi_up, oi_flat, funding_hot, net_diff_proxy
並在 populate_entry_trend / populate_exit_trend 中加入買賣邏輯。
```

---

# 29. 最終執行原則

## 原則 1
先求能跑，再求漂亮。

## 原則 2
先做好資料與 log，再追求花俏策略。

## 原則 3
先做 3 套，不要一次 12 套。

## 原則 4
先回測，再 Dry-run，再 Live。

## 原則 5
先做低頻穩定版本，不要一開始碰高頻。

## 原則 6
全自動 = 放棄模糊、接受近似、換取可驗證與可複製。

---

# 30. 一句話總結

**CoinCat Ultimate Master System 的本質，不是做出一個神奇喊單器，而是把你現在已經很強的市場理解，正式轉成一台可研究、可回測、可優化、可自動執行的交易機器。**
