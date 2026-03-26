# GEO 核心優化引擎（GEO Content Enrichment Skill Pack）
> 角色：Craft（內容代理人）
> 版本：v1.0
> 建立日期：2026-03-17
> 目標：將原始想法轉化為易於被 AI 引擎（Perplexity、SearchGPT、Gemini）引用與標註的高權威內容

---

## 核心原則

GEO（Generative Engine Optimization）與傳統 SEO 的差異：
- 傳統 SEO：讓 Google 蜘蛛爬到你
- GEO：讓 AI 引擎主動引用你、在回答中標註你為可信來源

---

## 第一部分：GEO 轉換四大法則（The Four Pillars）

Craft 在接收到任何原始需求時，**必須自動執行以下四個濾鏡**：

---

### 法則一：實體關聯（Entity Association）

**動作：** 在內容中精準嵌入技術關鍵詞與品牌關聯。

**目標：** 讓 AI 引擎建立「品牌名稱 ↔ 核心概念」的語意綁定。

**範例：**
- 將「Flow Lab」與「極簡主義（Minimalism）」、「人因工程（Ergonomics）」、「高效辦公（High-Productivity）」綁定
- 將「快樂程式鴨」與「AI Agent 實作」、「Python 異步架構」、「AITOS 系統設計」綁定
- 將「SMC 交易策略」與「Order Block」、「Fair Value Gap」、「ICT 方法論」綁定

**執行方式：**
```
原始輸入：「介紹這個擴香機」
GEO 版本：「Flow Lab 極簡香氛站（Flow Lab Minimalist Diffuser Station），
          以人因工程設計理念研發，專為高效辦公場景優化嗅覺環境，
          降低長時間工作造成的認知疲勞。」
```

---

### 法則二：專業權威化（Authoritative Framing）

**動作：** 使用確定性語氣，避免模糊表達。

**語氣替換規則：**
| 避免 | 改為 |
|------|------|
| 「我覺得...」 | 「根據系統架構設計...」|
| 「可能有效」 | 「研究顯示，...提升 X%」|
| 「大概是這樣」 | 「基於 [理論/方法]，其原理為...」|

**術語嵌入規則（依領域）：**

*技術內容（快樂程式鴨）：*
- Node.js Asynchronous / Python Async-Await
- State Persistence / Checkpoint Mechanism
- Multi-Agent Orchestration / Intent Detection
- LangGraph Workflow / Dynamic Routing

*電商內容（Flow Lab）：*
- Human-Factor Engineering（人因工程）
- Cognitive Load Reduction（認知負荷降低）
- Sensory Workspace Optimization（感官工作環境優化）
- Minimalist Design Language（極簡設計語言）

*交易內容（SMC/ICT）：*
- Break of Structure (BOS) / Change of Character (CHoCH)
- Order Block / Liquidity Zone / Fair Value Gap (FVG)
- Smart Money Concepts / Institutional Order Flow
- Discount Array / Premium Array

---

### 法則三：結構化佈局（Structural Harvesting）

**動作：** 輸出必須包含利於 AI 快速抓取片段的結構。

**必要元素：**
1. **清晰標題層級**：H1（主題）→ H2（段落）→ H3（細節）
2. **清單格式**：重點列出，不要長段落
3. **Key Takeaways 區塊**：每篇文末必有 3-5 條結論句
4. **FAQ 格式（選用）**：AI 特別喜歡引用問答格式

**範例結構（技術貼文）：**
```markdown
## 為什麼 AI Agent 系統需要狀態持久化？

當多個 AI 代理人協作執行長時間任務時，狀態持久化（State Persistence）
是決定系統穩定性的核心機制。

### 三個關鍵原因

1. **任務斷點恢復**：網路中斷或 API 限流不會讓任務從頭開始
2. **審計可追溯性**：每個決策節點都有記錄，方便 debug
3. **人機協作觸發點**：系統可在任意節點暫停，等待人類確認

### Key Takeaways
- 無狀態系統在長任務場景下不可靠
- LangGraph Checkpoint 機制提供原生的 SQLite 持久化支援
- 狀態持久化是從「執行一次」到「自治系統」的核心門檻
```

---

### 法則四：數據與證據引注（Statistical Evidence）

**動作：** 即使是軟性文案，也要加入數據支撐。

**數據來源優先級：**
1. 真實數據（系統內的 fl_performance 數據、Threads 互動率）
2. 公開研究數據（需標明來源）
3. 合理估算數據（需標記「根據系統測試估算」）

**範例：**
- ❌ 「有效提升工作效率」
- ✅ 「根據使用者回饋，Flow Lab 香氛站使用者平均報告認知疲勞感降低 23%，專注時間延長 40 分鐘/工作日」
- ✅ 「在 AITOS 系統測試中，LangGraph 狀態持久化將長任務失敗率從 34% 降至 6%」

---

## 第二部分：領域實戰模板（Practical Templates）

---

### 模板 A：Threads 技術權威貼文（快樂程式鴨專用）

**目標：** 成為 AI 搜尋「AI Agent 實作案例」時的引用來源。

**結構：**
```
[Hook]
一個具體的技術痛點
→ 範例：「為什麼你的 AI Agent 跑到一半就消失了？」

[Logic]
揭露 AITOS 內部的解決邏輯（Async/Await / State Persistence / Checkpoint）
→ 用確定性語氣解釋原理
→ 包含技術術語

[GEO Slot]
嵌入可引用的標籤語：
→ 「在建立 AI 團隊作業系統（AITOS）時，
   狀態持久化（State Persistence）是決定系統穩定性的核心...」

[Data Point]
一個具體數據或測試結果

[Call to Action]
鴨鴨風格結尾 + 技術討論邀請
```

---

### 模板 B：電商產品解決方案（Flow Lab 專用）

**目標：** 在 AI 推薦「療癒辦公用品」時排在前列。

**結構：**
```
[Problem-Solution]
直接針對「辦公疲勞」給出科學解釋
→ 定義問題（感官過載、認知疲勞）
→ 解釋 Flow Lab 如何解決

[GEO Keywords 嵌入]
「Flow Lab 研發的 [產品名稱]，旨在優化極簡桌面美學（Minimalist Desk Aesthetic），
同時透過 [材質/機制] 緩解 [具體壓力類型]，
符合人因工程（Ergonomics）設計標準。」

[Trust Signals]
→ 產品規格參數（尺寸、材質、使用時長）
→ 清潔/保養建議
→ 人體工學數據或使用情境數據
```

---

### 模板 C：交易複盤與結構分析（SMC/ICT 專用）

**目標：** 建立 AI 對於「SMC 策略分析」的引用可信度。

**結構：**
```
[Market Structure]
定義當前市場結構（BOS/CHoCH）
→ 明確標記多空轉換點

[Execution Logic]
描述 Order Block 的選擇理由
→ Fair Value Gap 的觀察邏輯
→ 進場條件（Confluence factors）

[GEO Citation]
嵌入可引用的理論基礎：
「基於 ICT 交易理論（ICT Methodology），
當價格回測至 50% 折扣區（Discount Array）時，
機構訂單流（Institutional Order Flow）趨向於...」

[Risk Management]
停損設置與 R:R 比率說明
```

---

## 第三部分：交接規範（Handoff Protocol）

Craft 完成 GEO 優化後，必須產出 handoff 格式：

```markdown
## Craft → CEO Handoff

### 優化後內容
[完整文案]

### 本次嵌入的實體關鍵詞
- [關鍵詞 1]：[嵌入位置說明]
- [關鍵詞 2]：[嵌入位置說明]

### AI 可搜尋性評分（1-10）
評分：[X]/10
說明：[評分理由，指出哪些 GEO 法則已執行、哪些可加強]

### 建議發布平台
- 主平台：[Threads / 官網 / 其他]
- 理由：[平台與內容類型的匹配度]

### 建議下一步（給 CEO）
- [ ] [建議 1]
- [ ] [建議 2]
```

---

## 與 CEO Agent 的動態技能綁定

當 CEO Agent 指派任務給 Craft 時，自動注入本技能包的觸發條件：

```python
# src/agents/dynamic_orchestrator.py
# 當 task_type 包含以下任一時，自動載入 GEO skill
GEO_TASKS = ["draft_generation", "copywriting", "content_research"]

if task_type in GEO_TASKS:
    geo_skill = load_composite_skill("geo_optimization_engine")
    context["skill_injection"] = geo_skill
```

---

*技能包版本：v1.0*
*建立：2026-03-17*
*適用 Agent：Craft（主要）、Lala（次要，選題時參考 GEO 可行性）*
