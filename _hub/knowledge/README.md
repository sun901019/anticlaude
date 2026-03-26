# _hub/knowledge/ — 統一知識層

> 建立日期：2026-03-16
> 目的：整合分散在多個目錄的知識，建立統一入口

---

## 知識來源對照表

| 知識類型 | 現有位置 | 遷移狀態 |
|---------|---------|---------|
| 專案概述 | `ai/context/project-overview.md` | 已存在，未遷移 |
| 系統架構 | `ai/context/architecture.md` | 已存在，未遷移 |
| 品牌身份 | `_context/about_me.md` | 已存在，未遷移 |
| 工作流程 | `_context/workflow.md` | 已存在，未遷移 |
| API 文件 | `src/api/main.py`（inline docs） | 程式碼內嵌 |
| 選品規則 | `_hub/ecommerce_engine_spec.md` | 已存在 |
| Agent 定義 | `_hub/shared/agents/` | 已存在 |
| Composite Skills | `_hub/shared/skills/composite/` | 已建立（2026-03-16）|

## 優先順序（衝突解決規則）

當多個來源對同一主題有不同說明時，依以下優先順序判斷：

1. **`projects/anticlaude/`** — 此專案當前操作規則（最高優先）
2. **`src/` 和 `dashboard/`** — 實際執行的程式碼
3. **`_hub/registry/`** — 能力庫的全局定義
4. **`_hub/shared/`** — 共享能力定義
5. **`_context/`** — 更廣泛的背景記憶

## 計畫中的知識整合（Phase 5）

- [ ] API schema 文件化到 `_hub/knowledge/api_contracts/`
- [ ] 工作流程 SOP 整合到 `_hub/knowledge/workflows/`
- [ ] 決策歷史整合到 `_hub/knowledge/decisions/`

---
*此目錄目前是骨架，Phase 5 完整建立*
