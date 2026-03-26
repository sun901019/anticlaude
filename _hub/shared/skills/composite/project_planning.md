---
name: project_planning
description: 通用複合技能：任務拆解 SOP + 交接格式 + Sprint 管理原則
sources:
  - _hub/skills_library/agency-agents/strategy/nexus-strategy.md
  - AntiClaude operating-protocol
agents: [全體 agents，主要 Lumi]
version: 1.0.0
created: 2026-03-16
---

# Project Planning 複合技能

## 用途

任何 agent 在需要拆解任務、規劃工作步驟、與其他 agent 交接時調用。
Lumi 在接到複雜工程任務時特別依賴此技能。

---

## 一、任務拆解原則（NEXUS 方法）

### 好的任務拆解
- **每個子任務獨立可執行**（不依賴同時進行的任務）
- **輸出明確**（知道做完長什麼樣）
- **可驗證**（有方法確認是否完成）
- **範圍清楚**（不含糊，不重疊）

### 拆解框架
```
大任務
  ├── 子任務 A（獨立）
  │     ├── 步驟 1
  │     └── 步驟 2
  ├── 子任務 B（可並行）
  └── 子任務 C（依賴 A 完成後）
```

### 任務規模判斷
| 規模 | 特徵 | 處理方式 |
|------|------|---------|
| 小（< 30 分鐘）| 單一檔案改動 | 直接執行 |
| 中（1-2 小時）| 跨 2-3 個檔案 | 先確認範圍再執行 |
| 大（> 半天）| 架構性改動 | 先寫計畫文件再執行 |

---

## 二、AntiClaude 任務優先級框架

### P0 — 緊急修復
系統無法正常運作、數據錯誤、用戶看到錯誤
→ 立刻修，不需批准

### P1 — 本週必做
Sprint board 上的核心任務
→ 按 sprint 計畫執行

### P2 — 本週希望完成
nice-to-have，如果 P1 完成了就做
→ Sprint board 次要任務

### P3 — 下次 Sprint
好主意，但現在沒空
→ 記到 sprint.md 待辦

---

## 三、工作前確認清單

```
□ 讀過 ai/state/sprint.md（知道現在的優先級）
□ 確認任務範圍（只改需要改的，不做額外優化）
□ 確認影響範圍（這個改動會影響哪些其他功能？）
□ 有沒有需要先備份的東西？
□ 如果出錯，如何還原？
```

---

## 四、交接文件格式（給 Codex）

當 Claude Code 要把任務交給 Codex 實作時：

```markdown
# Codex 任務：[任務名稱]
日期：YYYY-MM-DD
優先級：P[0-3]

## 任務說明
[一句話描述要做什麼]

## 背景
[為什麼要做這個，上下文]

## 具體要求
1. [要改的檔案 + 具體改法]
2. [要新增的功能]
3. [不要動的東西]

## 驗收標準
- [ ] [如何確認完成]
- [ ] [有沒有測試需求]

## 注意事項
- 所有 .md 檔案寫入必須加 encoding="utf-8"（Windows 避免亂碼）
- 不要修改任何沒有在上面列出的檔案
```

---

## 五、工作後更新清單

```
□ 更新 ai/state/sprint.md（完成的任務打 ✅）
□ 更新 ai/state/progress-log.md（本輪做了什麼）
□ 更新 ai/state/current-task.md（下一步是什麼）
□ 如果有決策記錄 → 寫入 ai/state/decisions.md
□ 如果需要 Codex → 寫 ai/handoff/to-codex.md
□ 如果有新 bug 發現 → 加入 sprint.md 的下一個 P 級
```

---

## 六、Pipeline 完整性原則

來自 NEXUS 方法論，適用 AntiClaude：

| 原則 | 意義 |
|------|------|
| 沒有 context 不執行 | Agent 開始工作前必須讀背景文件 |
| 交接要完整 | 接手的 agent 不應該要問「這是什麼？」 |
| 並行優先 | 獨立的任務同時執行，不要排隊 |
| 失敗快速修復 | 同一個問題最多嘗試 3 次，超過要升級 |
| 單一事實來源 | sprint.md 是現在要做什麼的唯一依據 |
