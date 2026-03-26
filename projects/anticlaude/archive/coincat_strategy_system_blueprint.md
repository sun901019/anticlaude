# CoinCat 籌碼交易系統整合藍圖（給 AI 協作版）

> 目的：把目前的「CoinCat 12 套主力籌碼基礎」整理成一份可討論、可量化、可實作、可回測、可自動化的系統規格草案。  
> 適用對象：你自己、你的 AI 助手、未來的程式架構規劃。  
> 核心定位：**先用 TA 找位置，再用籌碼判真假，最後用劇本決定動作。**

---

## 0. 目前策略總評與升級目標

### 目前評分
- 市場理解：**8.5 / 10**
- 教學框架：**9 / 10**
- 可手動交易性：**7.5 / 10**
- 可量化程度：**4.5 / 10**
- 可自動化程度：**3.5 / 10**

### 評語
你現在的內容，本質上不是「單一交易策略」，而是：

**一套籌碼結構化判斷系統。**

它的強項是：
- 看得懂市場兵力，而不是只看 K 線。
- 有完整劇本分類，不是單點指標亂猜。
- 已經內建心理陷阱提醒，這點很強。
- 很適合做成「人機協作判斷系統」。

它的弱項是：
- 還有很多描述是人看得懂，但電腦看不懂。
- 還缺少明確數值閾值、時間週期、入場 trigger、出場條件、風控公式。
- 還不能直接進回測，也不能直接掛到 OKX / BingX 做自動交易。

### 升級目標
把這套系統從：

**教學型 / 主觀判斷框架**

升級成：

**可量化 + 可回測 + 可 paper trade + 可半自動 + 可逐步自動化 的交易系統。**

---

## 1. 策略核心思想

### 1.1 一句話版本
**技術分析找結構位，籌碼分析判斷真假與兵力，12 套劇本決定開倉 / 平倉 / 觀望。**

### 1.2 核心流程
1. 先看 TA
   - 支撐 / 壓力
   - 前高 / 前低
   - 區間上下緣
   - 突破 / 跌破
   - 高位橫盤 / 低位橫盤
   - 爆量長 K / 震盪整理
2. 再看籌碼
   - OI
   - 多空比 / 大戶多空比
   - 淨多 / 淨空
   - 淨差值
   - 資金費率
   - 清算熱力圖
3. 最後套劇本
   - 真突破 / 假突破
   - 真跌破 / 假跌破
   - 擁擠末期
   - 回補反彈
   - 市場出清
   - 趨勢加速
   - 掃清算 / 獵殺停損
4. 執行動作
   - 開多 / 開空
   - 減碼 / 全出
   - 等回踩 / 等反彈
   - 觀望

---

## 2. 六大核心指標（系統定義版）

### 2.1 OI（Open Interest）持倉量
**定義**：市場中尚未平倉的合約數量。  
**用途**：看槓桿參與度與市場是否在補兵。  
**重點**：OI 上升不代表一定漲跌，只代表有人進場。方向要配合價格與淨差看。

### 2.2 多空比（Long / Short Ratio）
**定義**：市場做多與做空的人數或資金比例。  
**用途**：看市場情緒傾斜。  
**重點**：人多的一邊，不一定是對的；散戶極端常反向。

### 2.3 淨多頭 / 淨空頭（Net Long / Net Short）
**定義**：今天多軍 / 空軍新增多少兵力。  
**用途**：看哪一邊在補兵、哪一邊在撤退。

### 2.4 淨差值（Net Difference）
**定義**：淨多頭 - 淨空頭。  
**用途**：兵力總結，判斷主導權屬於誰。  
**重點**：比單看淨多 / 淨空更準。

### 2.5 資金費率（Funding Rate）
**定義**：永續合約多空互相支付的平衡費用。  
**用途**：判斷哪一邊擁擠。  
**重點**：要看「連續極端」，不是看單次數值。

### 2.6 清算熱力圖（Liquidation Heatmap）
**定義**：潛在爆倉堆積區。  
**用途**：找價格容易被吸過去掃流動性的區域。  
**重點**：不是必到價，是吸引區。

---

## 3. 十二套劇本（系統分類版）

### 第一層：新手 4 套母型態
1. 真漲推進
2. 真跌壓制
3. 擠空反彈
4. 出清落地

### 第二層：進階 4 套陷阱 / 過擠
5. 假突破（誘多）
6. 假跌破（誘空）
7. 多擁擠末期（易殺多）
8. 空擁擠末期（易軋空）

### 第三層：老手 4 套戰法雛型
9. 掃清算反拉
10. 主力獵殺停損
11. 趨勢加速段（多方）
12. 趨勢加速段（空方）

---

## 4. 這套系統最強的地方

### 4.1 不是只看價格，而是看兵力
同樣破高：
- 破高 + OI 增 + 淨差擴大 = 真突破機率高
- 破高 + OI 不增 + 淨差小正 = 假突破機率高

### 4.2 不迷信單指標
你已經知道：
- OI 不是方向
- funding 不是單次看
- 多空比不能單看人數
- 清算熱圖不是必到點

### 4.3 內建行為金融視角
你不只是看圖，而是已經考慮：
- FOMO
- 恐慌殺低
- 追高殺低
- 群體極端
- 假突破 / 假跌破

這很適合做成：
- AI 陪跑教練
- 交易 checklist
- 人機共同決策儀表板

---

## 5. 目前最不足的地方（低分區診斷）

### 5.1 可量化程度 4.5 / 10 的原因
你現在很多關鍵字還是語意化，不是數值化。

例如：
- OI 高
- OI 停滯
- 費率爆正
- 淨差擴大
- 價高 / 價低
- 長 K 爆量
- 小倉位
- 等回踩

這些對人很清楚，但程式無法直接判斷。

### 5.2 可自動化程度 3.5 / 10 的原因
你現在有：
- 劇本
- 市場理解
- 教學邏輯

但還缺：
- 明確資料欄位
- 明確閾值公式
- 明確時間週期
- 明確入場 trigger
- 明確停損 / 減碼 / 全出條件
- 交易所 API 對接
- paper trade 模式
- log / dashboard / risk manager

---

## 6. 必須補齊的量化規格

### 6.1 把語意改成數值
示例：
- OI 高 → `OI_percentile_24h > 80`
- OI 停滯 → `abs(OI_change_15m) < 1.5%`
- OI 急升 → `OI_change_15m > 4%`
- OI 急降 → `OI_change_15m < -4%`
- 費率爆正 → `funding_rate > 0.01% 且連續 3 次為正`
- 費率爆負 → `funding_rate < -0.01% 且連續 3 次為負`
- 淨差擴大 → `net_diff_slope > threshold`
- 淨差縮小 → `net_diff_slope < -threshold`
- 高位橫盤 → `價格位於近 N 根 80% 分位且 ATR 收縮`
- 爆量長 K → `volume > 1.8 * rolling_avg_volume` 且 `實體 / ATR > threshold`

> 注意：以上閾值是 **v1 起始值**，不是聖杯。你要用回測再調。

### 6.2 固定時間週期
建議三層：
- 大方向：`4H / 1H`
- 劇本判斷：`15m`
- 入場觸發：`5m / 3m`

### 6.3 劇本 ≠ 入場點
每個劇本要再加一層 `trigger`。

例如：
- 真漲推進成立後，不是立刻追。
- 真正入場 trigger：
  - 回踩前高不破
  - 5m 收紅
  - 主動買量 > 主動賣量
  - 買一 / 賣一深度沒有失真

### 6.4 出場條件要制度化
每個劇本至少要有：
- 停損
- 第一減碼
- 全出條件
- 加碼條件
- 失效條件

### 6.5 風控公式化
建議 v1：
- 單筆風險：帳戶資金的 `0.5%`
- 單日最大虧損：帳戶資金的 `2%`
- 同方向連續虧損 3 次停機
- 同時最多 1~2 筆倉位

公式：

```text
單筆風險金額 = 帳戶資金 × 0.5%
倉位大小 = 單筆風險金額 / (入場價 - 停損價)
```

### 6.6 劇本打分制
不要硬判 12 選 1，先做分數模型更穩。

範例：真漲推進分數
- 突破前高：+2
- OI 15m 上升 > 3%：+2
- 淨差擴大：+2
- funding 沒過熱：+1
- 上方有清算吸引：+1
- 大週期方向同向：+2

總分 >= 6 才允許開倉。

---

## 7. 建議先實作的 3 套策略（v1）

這是你最適合先量化的三套：

### 7.1 策略 A：真漲推進
**原因**：最容易量化，也最適合順勢。  
**用途**：先建立第一套可回測的順勢多方系統。

#### v1 規則草案
- 大週期 1H 結構偏多
- 15m 價格突破近 20 根高點
- 15m OI_change > +3%
- 15m net_long_change > 0
- 15m net_short_change < 0
- 15m net_diff 擴大
- funding_rate 未達過熱閾值
- 5m 回踩突破位不破 + 收紅 K

#### 出場
- 停損：跌破回踩低點
- 第一減碼：1R
- 第二減碼：2R
- 若 OI 停滯 + 淨差縮小 → 提前減碼

### 7.2 策略 B：真跌壓制
**原因**：和真漲推進對稱，方便做多空雙邊研究。  
**用途**：建立順勢空方模型。

#### v1 規則草案
- 大週期 1H 結構偏空
- 15m 價格跌破近 20 根低點
- 15m OI_change > +3%
- 15m net_long_change < 0
- 15m net_short_change > 0
- 15m net_diff 負向擴大
- funding_rate 未達過冷閾值
- 5m 反彈不過跌破位 + 收黑 K

#### 出場
- 停損：站回跌破位上方
- 第一減碼：1R
- 第二減碼：2R
- 若 OI 停滯 + 淨差縮小 → 提前減碼

### 7.3 策略 C：假突破反手
**原因**：這是你整套系統最有辨識價值的優勢之一。  
**用途**：建立「過濾假信號」與「反手打臉單」能力。

#### v1 規則草案
- 價格創近 20 根新高
- OI_change < +1%
- net_diff 僅小幅正值，不擴大
- volume 未明顯放大
- 5m 出現長上影或收回前高下方

#### 動作
- 不追多
- 若收回前高下方且 5m 確認轉弱，可輕倉反手空

#### 出場
- 停損：再度站穩前高
- 目標：區間中線 / 區間下緣

---

## 8. 前置作業：你要先準備什麼

### 8.1 交易所與環境
建議先以 **OKX** 為第一版交易所，再保留 BingX 作第二交易所擴充。OKX 官方文件提供 REST 與 WebSocket API，且有 Demo Trading 流程；BingX 官方也提供 API 與 Demo Trading，但版本與文件整合度更需要額外留意。  
來源：OKX API guide、OKX API product page、BingX API、BingX Demo Trading。

你要先準備：
- OKX 帳號
- API Key / Secret / Passphrase
- Demo Trading API Key（先模擬）
- 之後若要雙交易所，再補 BingX API Key
- 一個專用測試子帳戶 / 子資金帳戶

### 8.2 市場資料來源
你的策略不只要價格，還要籌碼資料，所以資料源至少分兩層：

#### A. 交易所原始資料
- K 線
- 最新價
- Order book
- 成交量
- 倉位 / 資金費率（若交易所 API 有）

#### B. 衍生分析資料
- OI
- Funding
- Liquidation heatmap
- 多空比
- 大戶持倉比

這類衍生資料若交易所 API 不足，常需第三方資料服務補。CoinGlass 官方提供衍生品、期權、現貨、L2/L3 訂單簿、清算熱力圖、清算地圖等資料，並且列出 OKX、BingX 等多家交易所覆蓋。  
來源：CoinGlass API / pricing / heatmap pages。

### 8.3 程式與部署環境
建議 v1：
- Python 3.11+
- 虛擬環境（venv / conda）
- Git
- Docker（之後再上）
- SQLite / CSV（第一版）
- VPS（等要 24h 跑再上）

### 8.4 回測 / 模擬 / 實盤三階段
你要分三階段：
1. Backtest
2. Paper Trade / Dry Run
3. Live Small Size

不要直接跳實盤。

---

## 9. 你現在市場上可用的工具 / skills / 框架（調查整合）

> 目標：不是把工具越堆越多，而是把你低分項（可量化 / 可自動化）補起來。

### 9.1 交易所 API 層

#### OKX API
- 提供 REST + WebSocket
- 支援 Demo Trading
- 文件完整
- 適合作為第一版主交易所  
來源：OKX docs-v5、OKX API page。

#### BingX API
- 提供 API 頁面
- 提供 Demo Trading / Virtual USDT
- 可以做第二交易所擴充  
來源：BingX API、BingX Demo Trading、BingX Virtual USDT support article。

**建議用途**
- v1：OKX only
- v2：OKX + BingX

---

### 9.2 統一交易所介面

#### CCXT
CCXT 是常用的多交易所連接庫，支援 Python / JS / PHP，提供統一的交易所介面；官方 wiki 與文件持續更新。  
來源：CCXT wiki、CCXT docs changelog。

**優點**
- 多交易所統一 API 介面
- 適合你未來同時接 OKX / BingX
- 降低 vendor lock-in

**缺點**
- 某些交易所特有欄位還是要寫 exchange-specific adapter
- WebSocket 若需要更深度功能，可能還是要走原生 API

**建議用途**
- v1 可不用先上 CCXT，直接接 OKX 官方 API
- v2 開始做 exchange adapter 時很適合引入

---

### 9.3 回測與 dry-run 框架

#### Freqtrade
Freqtrade 官方文件提供 dry-run、backtesting、hyperopt、data downloading 等功能，也有 FreqAI 文件可延伸做模型測試。  
來源：Freqtrade stable docs、hyperopt docs、utils docs、FreqAI docs。

**優點**
- 很適合快速做可回測 / 可 dry-run 的 MVP
- 有超參數優化與資料下載工具
- 適合把規則策略先跑起來

**缺點**
- 你這套策略偏籌碼 + 第三方資料，整合成本較高
- 若你要高度客製化 order flow / liquidation features，原生框架可能不夠順

**建議用途**
- 若你想快速驗證「量化版本規則」：可作為 v1 回測殼
- 若你想完全自訂資料流：可只借用它的設計思路，不一定整套採用

#### NautilusTrader
NautilusTrader 主打高性能、事件驅動、回測與實盤共用核心，Rust 核心 + Python 使用層，強調 research-to-live parity。官方站也列出 OKX 與 Polymarket 等整合。  
來源：NautilusTrader official site / docs / open-source pages。

**優點**
- 很適合你未來做研究到實盤一致性
- 事件驅動設計很適合籌碼 + 多來源資料
- 若未來想做較高品質基礎設施，值得研究

**缺點**
- 對你目前來說偏重
- 學習成本高於純 Python 輕量框架

**建議用途**
- v1 不必急著上
- v2 / v3 若你真的要做成熟 bot，非常值得考慮

---

### 9.4 自動交易與策略執行框架

#### Hummingbot
Hummingbot 官方定位是開源 Python 框架，用來建立自動化交易 / 做市 / 套利 bot，並提供 pure market making、cross-exchange market making、arbitrage 等策略模板。  
來源：Hummingbot docs、strategies pages、XEMM / PMM / arbitrage docs。

**優點**
- 很適合研究自動化執行架構
- 適合做市、跨市場、套利型系統
- 可以參考它的 connector / executor / strategy 分層

**缺點**
- 你的主策略是籌碼判斷，不是純做市
- 若硬套，會有很多不必要抽象層

**建議用途**
- 拿來學 execution architecture
- 不一定直接當你的第一版主框架

---

### 9.5 訊號輸入 / webhook / 半自動橋接

#### TradingView Webhooks
TradingView 官方支援 webhook alerts，可在警報觸發時對指定 URL 發送 HTTP POST，也支援策略 / alert() / order fill alerts 等觸發方式。  
來源：TradingView webhook support、alerts FAQ、intro to alerts。

**優點**
- 超適合做半自動版本
- 你可以先把 TA 條件放在 TradingView
- 由你的 Python server 接收 webhook，再補籌碼判斷

**缺點**
- TradingView 本身不等於籌碼數據中心
- 你仍要自己補 OI / funding / heatmap 資料

**建議用途**
- 很適合做 v0.5 / v1 半自動版
- 「TV 發 TA 信號 → Python 補籌碼 → 決定要不要下單」

---

### 9.6 籌碼 / 熱力圖 / 衍生資料供應

#### CoinGlass API
CoinGlass 官方頁面顯示，其 API 提供期貨、現貨、期權、ETF、L2/L3 訂單簿、Funding、Liquidation heatmap、Liquidation map 等資料，並列出涵蓋包括 OKX、BingX 在內的多家交易所。  
來源：CoinGlass API、pricing、heatmap、liquidation map pages。

**優點**
- 直接補你的核心資料缺口
- 適合你的 OI / funding / 清算熱圖需求
- 很接近你策略的資料層核心

**缺點**
- 成本可能不是免費
- 需要再做資料清洗與對時

**建議用途**
- 若你真要把 12 套做成系統，這是很值得優先研究的資料來源

---

## 10. 依照低分項，對應該補哪些工具 / skills

### 10.1 可量化程度 4.5 / 10 → 要補什麼

#### 需要補的 skill
- 指標工程（feature engineering）
- 規則數值化（threshold design）
- 多週期資料對齊
- 劇本分類器設計
- 回測評估指標

#### 推薦工具
- Python + pandas
- Freqtrade（做規則回測 / dry-run）
- CoinGlass API（補 OI / funding / liquidation）
- TradingView（做 TA 偵測與 webhook 觸發）

#### 升級目標
把 12 套劇本從自然語言，變成：
- 欄位
- 公式
- 條件
- 分數
- 動作

---

### 10.2 可自動化程度 3.5 / 10 → 要補什麼

#### 需要補的 skill
- API 串接
- WebSocket / REST
- 訂單管理
- 風控模組
- logger / dashboard
- paper trade
- restart / fail-safe

#### 推薦工具
- OKX 官方 API
- CCXT（多交易所時）
- TradingView webhooks（半自動）
- NautilusTrader（中長期）
- Hummingbot（參考 execution architecture）

#### 升級目標
把系統拆成：
- Data Ingestion
- Feature Engine
- Scenario Classifier
- Entry Trigger
- Risk Manager
- Execution Engine
- Logger / Dashboard

---

### 10.3 可手動交易性 7.5 / 10 → 還能怎麼提升

#### 要補的點
- 明確 checklist
- 明確「不能做」規則
- 明確劇本打分
- 明確交易前問答

#### 建議做法
建立一張「交易前檢查表」：
- 大方向是什麼？
- 結構位在哪？
- OI 是否支持？
- 淨差是否擴大？
- funding 是否過熱？
- heatmap 是否在前方有吸引區？
- 目前最像哪一套劇本？
- 是順勢 / 反手 / 觀望？
- 停損設哪？
- 這一筆若錯，虧多少？

---

## 11. 建議的系統架構（v1）

```text
[交易所 / 第三方資料]
  ├─ OKX REST / WS
  ├─ CoinGlass API
  ├─ TradingView webhook
  └─ (未來) BingX API

        ↓

[Data Layer]
  ├─ candles
  ├─ orderbook
  ├─ oi
  ├─ funding
  ├─ liquidation map / heatmap
  └─ ratios / net metrics

        ↓

[Feature Engine]
  ├─ TA 結構特徵
  ├─ OI 變化特徵
  ├─ 淨多 / 淨空 / 淨差特徵
  ├─ funding 極端特徵
  ├─ heatmap 距離特徵
  └─ volume / active buy-sell 特徵

        ↓

[Scenario Classifier]
  ├─ 12 劇本打分
  └─ 選出最像的 1~2 套情境

        ↓

[Trigger Layer]
  ├─ 回踩不破
  ├─ 反彈不過
  ├─ 收盤確認
  └─ order flow 微確認

        ↓

[Risk Manager]
  ├─ position sizing
  ├─ stop loss
  ├─ daily loss cap
  └─ cooldown / halt

        ↓

[Execution Engine]
  ├─ place order
  ├─ amend / cancel
  ├─ position sync
  └─ exchange adapter

        ↓

[Logger / Dashboard]
  ├─ signal log
  ├─ trade log
  ├─ system log
  └─ pnl dashboard
```

---

## 12. 建議的專案資料夾結構

```text
coincat-trading-system/
├─ README.md
├─ requirements.txt
├─ .env.example
├─ config/
│  ├─ settings.yaml
│  ├─ thresholds.yaml
│  └─ exchange.yaml
├─ data/
│  ├─ raw/
│  ├─ processed/
│  └─ cache/
├─ docs/
│  ├─ strategy_spec.md
│  ├─ scenario_rules.md
│  └─ playbook.md
├─ src/
│  ├─ data/
│  │  ├─ okx_client.py
│  │  ├─ bingx_client.py
│  │  ├─ coinglass_client.py
│  │  └─ tv_webhook_server.py
│  ├─ features/
│  │  ├─ ta_features.py
│  │  ├─ oi_features.py
│  │  ├─ funding_features.py
│  │  └─ heatmap_features.py
│  ├─ scenarios/
│  │  ├─ scenario_base.py
│  │  ├─ trend_long.py
│  │  ├─ trend_short.py
│  │  ├─ fake_breakout.py
│  │  └─ scoring.py
│  ├─ signals/
│  │  ├─ trigger_engine.py
│  │  └─ signal_router.py
│  ├─ risk/
│  │  ├─ position_sizer.py
│  │  ├─ stop_manager.py
│  │  └─ risk_manager.py
│  ├─ execution/
│  │  ├─ order_executor.py
│  │  ├─ paper_broker.py
│  │  └─ portfolio.py
│  ├─ monitoring/
│  │  ├─ logger.py
│  │  ├─ dashboard.py
│  │  └─ notifier.py
│  └─ main.py
├─ tests/
└─ notebooks/
```

---

## 13. 建議開發順序

### Phase 0：先做資料與觀測
- 接 OKX 行情
- 接 CoinGlass OI / funding / heatmap
- 存 CSV / SQLite
- 不下單，只看資料對不對

### Phase 1：先做 3 套劇本量化
- 真漲推進
- 真跌壓制
- 假突破

### Phase 2：做 paper trade
- 只產生 signal
- 模擬進出場
- 紀錄 PnL 與劇本分類

### Phase 3：做半自動
- TradingView 發 TA 結構 signal
- Python 補籌碼確認
- Telegram / Dashboard 顯示「可交易 / 不可交易」
- 人手確認後下單

### Phase 4：做小額自動化
- 只跑 OKX Demo
- 再跑小資金 live
- 單筆風險固定極小

### Phase 5：擴充雙交易所 / 更進階底層
- 引入 CCXT 或 exchange adapter
- 再研究 NautilusTrader / 更進階 execution

---

## 14. v1 交易前檢查清單（給 AI / 人共同使用）

### TA 層
- 大週期方向是多還是空？
- 現在位置是突破、跌破、橫盤、高位、低位、還是區間中？
- 是不是接近前高 / 前低 / 區間邊緣？

### 籌碼層
- OI 是增加、減少、停滯、急升、急降？
- 淨多 / 淨空誰在補兵？
- 淨差是擴大還是縮小？
- funding 是正常、過熱、過冷？
- heatmap 前方有沒有吸引區？

### 劇本層
- 現在最像哪一套？
- 打分多少？
- 是否同時符合至少 2 個以上關鍵條件？
- 是順勢、反手、減碼、觀望哪一種？

### 執行層
- 入場 trigger 是否確認？
- 停損設哪？
- 單筆最大可承受虧損是多少？
- 這筆若連錯 3 次，系統會不會停？

---

## 15. 給 AI 的任務清單（你可以直接拿去討論）

### 任務 1：把 12 套劇本數值化
請 AI 幫你把每一套劇本拆成：
- 必要欄位
- 判斷公式
- 時間週期
- 最低成立分數
- 入場 trigger
- 停損 / 出場

### 任務 2：先做 3 套 v1 回測版
請 AI 先只實作：
- 真漲推進
- 真跌壓制
- 假突破

### 任務 3：建立特徵欄位表
請 AI 定義：
- `oi_change_5m`
- `oi_change_15m`
- `net_diff_slope`
- `funding_extreme_score`
- `heatmap_distance`
- `breakout_strength_score`
- `volume_expansion_score`

### 任務 4：設計 scenario scoring engine
請 AI 幫你做一個劇本打分器，而不是硬判規則。

### 任務 5：做 paper trade 系統
請 AI 幫你做：
- signal log
- paper order
- pnl log
- scenario tag

### 任務 6：做半自動橋接
請 AI 設計：
- TradingView webhook → Python server
- Python server 補籌碼資料
- Telegram / dashboard 顯示「通過 / 不通過」

---

## 16. 最後結論

### 你的策略值不值得做？
**值得，而且很值得。**

### 它真正的問題是什麼？
不是市場理解不夠，而是：

**還沒從「交易語言」變成「機器語言」。**

### 最正確的下一步
不是再補更多理論，而是：

1. 先選 3 套劇本
2. 全部數值化
3. 做回測
4. 做 paper trade
5. 先半自動
6. 最後再自動化

### 最務實的路
- 先用 OKX 當主交易所
- 先用 CoinGlass 類資料補籌碼層
- 先用 TradingView 做 TA webhook
- 先把系統做成「AI 輔助判斷 + 人決策」
- 等 log 穩定後，再進一步自動下單

---

## 17. 參考資料（官方 / 一手來源）
- OKX API V5 Docs: https://www.okx.com/docs-v5/en/
- OKX API Product Page: https://www.okx.com/okx-api
- BingX API: https://bingx.com/en/wiki/detail/api
- BingX Demo Trading: https://bingx.com/en/wiki/detail/demo-trading
- BingX Virtual USDT: https://bingx.com/en/support/articles/13277514625039
- CCXT Wiki Manual: https://github.com/ccxt/ccxt/wiki/manual
- CCXT Docs Changelog: https://docs.ccxt.com/CHANGELOG
- Freqtrade Stable Docs: https://www.freqtrade.io/en/stable/configuration/
- Freqtrade Hyperopt: https://docs.freqtrade.io/en/2026.1/hyperopt/
- Freqtrade Utils / Dry-Run / Backtesting: https://docs.freqtrade.io/en/2026.2/utils/
- Freqtrade FreqAI: https://www.freqtrade.io/en/stable/freqai-running/
- Hummingbot Docs: https://hummingbot.org/docs/
- Hummingbot Strategies: https://hummingbot.org/strategies/v1-strategies/
- Hummingbot XEMM: https://hummingbot.org/strategies/v1-strategies/cross-exchange-market-making/
- Hummingbot PMM: https://hummingbot.org/strategies/v1-strategies/pure-market-making/
- NautilusTrader: https://nautilustrader.io/
- NautilusTrader Open Source: https://nautilustrader.io/open-source/
- NautilusTrader Logging: https://nautilustrader.io/docs/latest/concepts/logging/
- TradingView Webhook Alerts: https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/
- TradingView Alerts FAQ: https://www.tradingview.com/pine-script-docs/faq/alerts/
- CoinGlass API / Data: https://www.coinglass.com/CryptoApi
- CoinGlass Pricing / Coverage: https://www.coinglass.com/pricing
- CoinGlass Liquidation Heatmap: https://www.coinglass.com/pro/futures/LiquidationHeatMap
- CoinGlass Liquidation Map: https://www.coinglass.com/pro/futures/LiquidationMap

