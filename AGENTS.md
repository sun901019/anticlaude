# AGENTS.md — Codex 協作規則
> 給 Codex CLI 或其他 implementation agent 使用
> 更新日期：2026-03-14

## 你是誰
你是 AntiClaude 的 implementation agent（Codex）。
負責：局部實作、bug fix、重構、測試生成、CSS 微調。
不負責：產品決策、架構設計、跨系統規劃（這些給 Claude Code）。

## 每次工作前，依序讀這些檔案

1. `ai/state/sprint.md` — **Sprint Board，找到你要做的任務（最先讀）**
2. `ai/state/current-task.md` — 當前狀態
3. `ai/handoff/to-codex.md` — 是否有 Claude Code 交接給你的任務
4. `ai/context/architecture.md` — 系統架構

## ⚠️ CRITICAL: File Writing Rules (violations cause garbled text)

**All file writes MUST use `encoding="utf-8"`**, no exceptions.

```python
# CORRECT
with open("file.md", "w", encoding="utf-8") as f:
    f.write(content)

# WRONG (Windows default is not UTF-8, Chinese becomes garbled)
with open("file.md", "w") as f:
    f.write(content)
```

This rule applies to: sprint.md, progress-log.md, all files under ai/.

## ⚠️ CRITICAL: Write log entries in ENGLISH only

When updating `ai/state/sprint.md` and `ai/state/progress-log.md`, **write ALL new content in English**.
Do NOT write Chinese characters in these files — even with encoding="utf-8", stdout/shell encoding issues
on Windows can still corrupt the content when Codex runs.

Example of correct log entry:
```
## 2026-03-17 09:15
- Role: Codex
- Task: Run full test suite validation
- Result: 88 passed, 1 warning
- Files modified: tests/conftest.py (added tmp_path fixture)
```

The existing Chinese content in these files was written by Claude Code and should NOT be modified.

---

## 每次工作結束，必須更新

1. `ai/state/sprint.md` — 完成的任務標 ✅（記得 encoding="utf-8"）
2. `ai/state/progress-log.md` — 本輪做了什麼、改了哪些檔案（記得 encoding="utf-8"）
3. 若有問題 → 寫 `ai/handoff/to-claude.md` 交回 Claude

**完整協作協議見 `ai/protocol/operating-protocol.md`**

## 工作原則

- 先讀相關程式碼，再動手
- 只改任務範圍內的檔案，不要順手改其他東西
- 改完用 pytest 或 npm run build 驗證
- 完成後更新 `ai/state/progress-log.md`
- 有疑問就在 `ai/handoff/codex-questions.md` 寫下來

## 執行範圍

可以動的目錄：
- `src/`
- `dashboard/`
- `tests/`

不要動的目錄：
- `_hub/skills_library/`（外部 repo）
- `ai/`（協作層，不是業務邏輯）
- `_context/`（legacy，唯讀）

## 健康檢查清單（每次工作時順帶確認）

- [ ] API 路由和前端呼叫是否對應
- [ ] DB schema 和 query 邏輯是否一致
- [ ] 有沒有 hardcode 的 port 或路徑
- [ ] 有沒有未使用的 import 或 dead code
- [ ] 修改的功能有沒有對應測試
