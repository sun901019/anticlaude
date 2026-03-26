# 共用 Agents

AI 角色專家，載入後讓 Claude Code 變身為特定領域專家。

## 自建角色
| 角色 | 檔案 | 用途 |
|------|------|------|
| Content Strategist | `content-strategist.md` | 內容策略 + 選題 |
| Threads Writer | `threads-writer.md` | 繁中文案生成 |

## 第三方角色
| 來源 | 資料夾 | 說明 |
|------|--------|------|
| agency-agents | `agency-agents/` | 50+ 專業 AI 角色 |

## 使用方式
對 Claude Code 說：「請以 [角色名] 的身份回應，參考 `_hub/shared/agents/[檔名]`」
