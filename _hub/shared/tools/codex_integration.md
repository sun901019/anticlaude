# Codex Integration — 執行引擎整合規範

> Codex 是 AntiClaude AI-OS 的第二執行引擎，與 Claude Code 形成互補分工。
> **最後更新**：2026-03-13（Phase 4 新增）

---

## Codex 的角色定義

Codex 是 OpenAI 的程式碼生成模型，擅長局部、精確的程式碼修改。
在 AntiClaude 中，Codex 作為 Claude Code 的**快速修復層**，處理不需要全局理解的任務。

---

## 使用時機

### 適合 Codex 的任務
```
✅ 單一檔案的 bug fix
✅ 新增重複性測試（相同模式的 pytest 測試）
✅ CSS/Tailwind 樣式微調（單一 .tsx 或 .css 檔）
✅ 函數 Docstring 補充
✅ 程式碼格式化和命名一致化
✅ 簡單的資料轉換邏輯
```

### 不適合 Codex 的任務
```
❌ 跨多個檔案的重構
❌ 新增 API endpoint（需要理解現有路由架構）
❌ 資料庫 schema 變更
❌ Pipeline 邏輯修改（多模組相依）
❌ 需要理解 AntiClaude 業務邏輯的任務
```

---

## 與 Claude Code 的分工邊界

```
Claude Code                    Codex
──────────────────────         ──────────────────────
全局架構理解           ←→      局部精確修改
多檔案協調             ←→      單檔案修復
業務邏輯實作           ←→      重複性程式碼生成
設計決策               ←→      格式/風格統一
新功能開發             ←→      既有功能維護
```

---

## 呼叫方式

### 在 Claude Code 中委派給 Codex
```python
# 標準委派格式（在 claude_code_*.md 任務文件中標注）
# [CODEX] 標記表示此任務適合 Codex 執行

# 範例：
# [CODEX] 為 src/ai/claude_scorer.py 新增 pytest 測試
# [CODEX] 修復 dashboard/src/app/metrics/page.tsx 第 45 行的型別錯誤
```

### Codex CLI 使用（如已安裝）
```bash
# 單檔修復
codex "Fix the type error in line 45 of metrics/page.tsx"

# 生成測試
codex "Generate pytest tests for src/ai/claude_scorer.py"
```

---

## 任務標注規範

在 `claude_code_*.md` 任務文件中，用以下標注區分引擎：

```markdown
### Task 1: [名稱] [CLAUDE CODE]
需要全局理解的任務...

### Task 2: [名稱] [CODEX]
單檔局部修復...
```

---

## 注意事項

1. **Codex 不了解 AntiClaude 架構**：給 Codex 的任務描述需要更完整的上下文
2. **結果需要 Claude Code 審查**：Codex 輸出的程式碼要確認符合專案規範
3. **設計 Token 一致性**：Codex 做前端修改時，需提供 globals.css 的 Token 清單
4. **不要讓 Codex 動 .env**：敏感設定只由 Claude Code 處理
