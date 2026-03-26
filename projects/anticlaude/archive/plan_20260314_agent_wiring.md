# AntiClaude AI Agency 接線計畫
> 作者：Claude Code
> 日期：2026-03-14
> 目標：讓 6 個 AI 員工自動傳遞任務，人只做決策與驗收

---

## 終態目標

```
你說「跑今日流程」
    ↓
Ori 抓資料 ──→ Lala 選角度 ──→ Craft 寫文案 ──→ Sage 評分 ──→ Pixel 呈現
                                                              ↓
                                                    你在 AI Office 看結果
                                                    決定發哪一篇

你說「分析這個商品」
    ↓
Ori 抓競品 ──→ Sage 評分計算 ──→ Craft 產報告 ──→ 你看報告決定進不進貨
```

---

## 現在缺什麼（接線清單）

### 缺口 1：沒有統一的任務物件

目前 agent 之間傳的是「文字狀態」，不是結構化任務。

需要一個 `AgentTask` 物件長這樣：

```python
{
  "task_id": "task_20260314_001",
  "title": "今日 AI 新聞聚類分析",
  "task_type": "research",          # research / strategy / write / score / design / implement
  "status": "in_progress",          # pending / in_progress / done / blocked / handoff_pending
  "owner_agent": "ori",
  "source_agent": None,             # 誰交過來的
  "target_agent": "lala",           # 完成後交給誰
  "input_refs": [],                 # 輸入素材（檔案路徑 / DB record id）
  "artifact_refs": [],              # 產出物（完成後填入）
  "started_at": "2026-03-14T08:00",
  "updated_at": "2026-03-14T08:05",
  "notes": ""
}
```

**實作位置**：`src/api/agent_status.py` 擴充現有 task model

---

### 缺口 2：沒有 Handoff 函數

每個 agent 完成工作後，需要一個標準方式把任務交給下一個。

需要新增：

```python
# src/api/agent_status.py
def handoff_task(task_id, from_agent, to_agent, artifact_refs, notes=""):
    """
    把任務從 from_agent 交給 to_agent
    更新 task status → handoff_pending
    寫入 agent_events.jsonl
    通知 to_agent 變成 in_progress
    """
```

**實作位置**：`src/api/agent_status.py`

---

### 缺口 3：Pipeline 沒有發射 Agent 事件

現在 `src/pipeline.py` 跑完是跑完，AI Office 不知道發生了什麼。

需要在每個步驟加上事件發射：

```python
# src/pipeline.py（目前長這樣）
results = await scraper.run()
analysis = await gemini.analyze(results)
drafts = await claude.write(analysis)

# 改成這樣
await agent_status.start_task("ori", "今日素材抓取", task_type="research")
results = await scraper.run()
await agent_status.handoff_task(task_id, "ori", "lala", artifact_refs=[results_path])

await agent_status.start_task("lala", "主題聚類與角度選擇", task_type="strategy")
analysis = await gemini.analyze(results)
await agent_status.handoff_task(task_id, "lala", "craft", artifact_refs=[analysis_path])

# 以此類推...
```

**實作位置**：`src/pipeline.py` + `src/agents/orchestrator.py`

---

### 缺口 4：Flow Lab 選品流程沒有接入 Agent

現在 ecommerce 的分析是直接呼叫 API，不走 Agent 系統。

需要定義 Flow Lab 的 Agent 流：

```
用戶新增候選商品
    ↓
Ori：POST /api/ecommerce/selection/candidates 觸發後
    → Ori 接手：搜尋競品資料（Serper API）
    → handoff → Sage

Sage：跑評分邏輯（demand / competition / profit / brand_fit）
    → handoff → Craft

Craft：產出選品報告（markdown）
    → artifact 存入 ecommerce_selection_reports
    → handoff_pending → 等人決策
```

**實作位置**：`src/ecommerce/selection.py` 加 agent emit 點

---

### 缺口 5：AI Office 沒有「等待人決策」狀態

有些任務完成後需要你來做決定，不是自動繼續。

需要新增一個狀態：`awaiting_human`

```
Craft 產完報告 → status: awaiting_human
AI Office 顯示：「📋 Craft 完成選品報告，等待你的決策」
你看完 → 按「核准進貨」或「棄用」
→ 系統繼續下一步
```

**實作位置**：
- `src/api/agent_status.py` 加 `awaiting_human` 狀態
- `dashboard/src/app/office/page.tsx` 顯示等待決策卡片 + 按鈕

---

## 實作順序

### Phase 1：打地基（prerequisite）
**目標**：建好任務物件和 handoff 函數，其他一切的基礎

| 任務 | 檔案 | 說明 |
|------|------|------|
| 擴充 AgentTask model | `src/api/agent_status.py` | 加 task_type / source_agent / target_agent / artifact_refs |
| 實作 `handoff_task()` | `src/api/agent_status.py` | 標準交接函數 |
| 實作 `await_human()` | `src/api/agent_status.py` | 需要人決策時暫停 |
| 更新 events API 回傳真實筆數 | `src/api/main.py` | 修一行 bug |

**負責**：Lumi

---

### Phase 2：接內容 Pipeline
**目標**：Ori → Lala → Craft → Sage 真實流動，AI Office 全程可見

| 任務 | 檔案 | 說明 |
|------|------|------|
| Pipeline 加 agent emit 點 | `src/pipeline.py` | 每步驟呼叫 handoff_task |
| Orchestrator 接入 | `src/agents/orchestrator.py` | 讓 orchestrator 驅動 handoff |
| AI Office timeline 完整顯示 | `dashboard/src/app/office/page.tsx` | 從 events API 讀取，支援重整後保留 |

**負責**：Lumi（後端）+ Pixel（前端）

---

### Phase 3：接 Flow Lab 選品流程
**目標**：新增商品後 Ori/Sage/Craft 自動跑，產報告等你決策

| 任務 | 檔案 | 說明 |
|------|------|------|
| selection.py 加 agent emit | `src/ecommerce/selection.py` | Ori/Sage/Craft 各自的任務點 |
| awaiting_human 顯示 | `dashboard/src/app/office/page.tsx` | 選品報告完成後顯示決策卡片 |
| 決策按鈕接 API | `dashboard/src/app/ecommerce/page.tsx` | 核准 / 棄用 → 更新 decision_status |

**負責**：Lumi + Pixel

---

### Phase 4：Agent 記憶層
**目標**：每天結束後系統自動學習，下次更準

| 任務 | 檔案 | 說明 |
|------|------|------|
| 每日摘要觸發 | `src/agents/orchestrator.py` | pipeline 結束後 Sage 摘要當天事件 |
| 摘要寫入 | `outputs/office_memory/daily_summary_YYYY-MM-DD.md` | 誰做了什麼、學到了什麼 |
| 選品 lesson 自動生成 | `src/ecommerce/selection.py` | 決策後 Sage 寫入 ecommerce_selection_lessons |
| 摘要注入 prompt | `src/agents/` 各 agent | 下次執行時帶入近期記憶 |

**負責**：Sage（邏輯）+ Lumi（觸發）

---

## 完成後的樣子

```
你：「跑今日流程」
  ↓
AI Office 即時顯示：
  [Ori]   🔵 進行中  「抓取今日 AI 新聞素材」
  [Lala]  ⏳ 等待中
  [Craft] ⏳ 等待中
  [Sage]  ⏳ 等待中

  → 2分鐘後 →

  [Ori]   ✅ 完成    「抓到 23 篇素材」→ 交給 Lala
  [Lala]  🔵 進行中  「聚類分析，選出 Top 3 主題」
  [Craft] ⏳ 等待中

  → 1分鐘後 →

  [Lala]  ✅ 完成    「選出：GPT-5 發布 / Cursor AI / 職涯觀點」→ 交給 Craft
  [Craft] 🔵 進行中  「撰寫 6 篇 Threads 文案」

  → 完成後 →

  [Craft] 📋 等待決策「文案已產出，請選擇發哪篇」
          [開啟文案] [選第1篇] [選第2篇]
```

---

## 給 Claude Code 的執行備註

1. Phase 1 完成前不要動 pipeline，Phase 1 是一切的地基
2. `agent_status.py` 改動前先讀整份文件，現有結構不要破壞
3. Handoff 函數要是 async，避免阻塞 pipeline 主流程
4. `awaiting_human` 狀態在 UI 要明顯區分於其他狀態（建議橘色 border + 行動按鈕）
5. 每個 Phase 完成後跑 `pytest tests/ -v` 確認沒有 regression
