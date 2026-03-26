# Flow Lab 選品引擎 整合狀態

Last updated: 2026-03-14
Source of truth: `projects/anticlaude/`
Executable truth: `src/ecommerce/`

---

## Integration Status

| 系統區域 | Specified | Implemented | Verified |
|---------|-----------|-------------|---------|
| Schema: ecommerce_selection_candidates | ✅ | ✅ | ✅ |
| Schema: ecommerce_selection_analyses | ✅ | ✅ | ✅ |
| Schema: ecommerce_selection_reports | ✅ | ✅ | ✅ |
| Schema: ecommerce_selection_lessons | ✅ | ✅ | ✅ |
| API: /selection/candidates CRUD | ✅ | ✅ | ✅ (import OK) |
| API: /selection/analyze | ✅ | ✅ | ✅ (import OK) |
| API: /selection/reports | ✅ | ✅ | ✅ (import OK) |
| API: /selection/portfolio | ✅ | ✅ | ✅ (import OK) |
| API: /selection/shortlist | ✅ | ✅ | ✅ (import OK) |
| API: /selection/lessons | ✅ | ✅ | ✅ (import OK) |
| Dashboard: 候選池 tab | ✅ | ❌ | ❌ |
| Dashboard: 評分分析 tab | ✅ | ❌ | ❌ |
| Dashboard: 組合設計 tab | ✅ | ❌ | ❌ |
| Dashboard: 選品報告 tab | ✅ | ❌ | ❌ |
| Dashboard: 學習記憶 tab | ✅ | ❌ | ❌ |
| Dashboard: 在售商品 (rename) | ✅ | ❌ | ❌ |
| Phase 4: 負評智能（Claude API）| ✅ | ❌ | ❌ |
| Phase 6: 報告輸出到 outputs/ | ✅ | ❌ | ❌ |
| Phase 7: AI Office domain 標籤 | ✅ | ❌ | ❌ |

---

## 現有路由總覽

```
/api/ecommerce/*           ← 已上架 SKU 運營（fl_products / fl_performance / fl_decisions）
/api/ecommerce/selection/* ← 選品候選評估（ecommerce_selection_*）
```

共 25 條路由（12 原有 + 13 選品新增）

---

## 命名對齊（已確認）

| 舊名 | 新名 | 位置 |
|------|------|------|
| 選品庫 tab | 在售商品 | dashboard Phase 5 時改 |
| 智能決策 tab | 定價決策 | dashboard Phase 5 時改 |
| — | 候選池 | 新增 |
| — | 評分分析 | 新增 |
| — | 組合設計 | 新增 |
| — | 選品報告 | 新增 |
| — | 學習記憶 | 新增 |

---

## 下一步（Phase 3）

核心分析引擎：
- 市場類型分類邏輯（手動輸入，AI 輔助標籤）
- 競品環境評分邏輯
- 單位經濟學強化（含廣告成本模擬）

Dashboard Phase 5 同步開始：先加 4 個空 tab，再填充元件。
