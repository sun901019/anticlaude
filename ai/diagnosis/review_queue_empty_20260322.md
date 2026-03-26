# 診斷報告：審核佇列為空但 LINE 有通知

**日期：** 2026-03-22
**問題：** 草稿已生成、LINE 有收到通知，但 `/review` 審核佇列完全沒有項目

---

## 根本原因

### 排程呼叫的是舊版 orchestrator，不是新版 graph pipeline

`src/api/main.py` 的 08:00 排程這樣寫：

```python
# main.py line 55-56
from src.agents.orchestrator import run_pipeline as orch_run
result = await orch_run()
```

**`orchestrator.py`（舊版）的行為：**
- ✅ 抓文章、分群、評分、生成草稿
- ✅ 呼叫 `mark_agent_awaiting_human()` → 發 LINE 通知
- ❌ **不建立 `approval_requests`**
- ❌ **不建立 `review_items`**（審核佇列永遠空的）

**`pipeline_graph.py`（新版 Phase 7）的行為：**
- ✅ 有 `draft_approval` 審核關卡
- ✅ 呼叫 `request_approval()` → 建立 `approval_requests`
- ✅ 呼叫 `_create_inbox_item()` → 建立 `review_items`
- ✅ pipeline 暫停等待你決策

---

## 資料庫現狀確認

| 表格 | 狀態 |
|------|------|
| `review_items` | 3 筆，全部 `rejected`，最後一筆 2026-03-21 |
| `approval_requests` | 28 筆，全部 `rejected`，多數 `run_id=NULL`（孤兒） |
| `workflow_runs` | 最後成功的是 `d71c839f`（2026-03-21 05:44）—— 沒有 `draft_approval` 任務 |

成功的那次 workflow_run 任務清單：
```
content_research → cluster → score → strategy → draft_generation → save_outputs
```
**`draft_approval` 根本不在其中**，代表整個審核關卡被完全跳過。

---

## 修復方案

將 `main.py` 的排程從舊版 orchestrator 改為呼叫新版 graph pipeline，並帶入 `with_approval_gate=True`。

**修改前：**
```python
from src.agents.orchestrator import run_pipeline as orch_run
result = await orch_run()
```

**修改後：**
```python
from src.domains.media.pipeline_graph import run_content_pipeline
result = await run_content_pipeline(with_approval_gate=True)
```

LINE 通知的 `top3` / `drafts_count` key 名稱需同步調整。

---

## 影響範圍

| 項目 | 影響 |
|------|------|
| LINE 晨報通知 | 仍然發送，key 名稱微調 |
| 審核佇列 | ✅ 修復後每天 08:00 會建立待審項目 |
| X + Threads 發布 | ✅ 核准後才發布（之前是完全跳過審核直接存檔） |
| 舊版 orchestrator | 不刪除，保留供手動測試 |

---

## 修復後的完整流程

```
08:00 排程
  └→ run_content_pipeline(with_approval_gate=True)
       ├→ content_research（抓文章，近3天去重）
       ├→ cluster / score / strategy
       ├→ draft_generation（生成草稿）
       ├→ draft_approval（審核關卡）
       │    ├→ 建立 approval_request
       │    ├→ 建立 review_item（審核佇列出現項目）
       │    ├→ pipeline 暫停
       │    └→ LINE 通知：「草稿已就緒，請審核」
       │
       └→ [你在 /review 核准後]
            └→ save_outputs → 同時發布 X + Threads
```

---

*由 Claude Code 自動診斷 2026-03-22*
