---
name: project_planning
description: 將複雜任務拆解為可執行步驟，生成清晰的實作計畫和任務追蹤文件。
type: composite-skill
sources:
  - _hub/skills_library/awesome-agent-skills/
  - _hub/skills_library/aws-agent-skills-libukai/
allowed-tools:
  - Read
  - Write
  - TodoWrite
---

# Project Planning — 專案規劃技能

## 任務拆解框架

1. **澄清目標**：要達成什麼結果？
2. **識別相依性**：哪些任務需要先完成？
3. **評估風險**：哪裡最容易出問題？
4. **輸出任務清單**：具體、可執行、有優先順序

---

## AntiClaude 專用：任務文件格式

```markdown
# 任務：[任務名稱]
> 建立日期：YYYY-MM-DD
> 負責人：Claude Code（執行）/ Antigravity（規劃）

## 目標
[一句話說明這個任務要達成什麼]

## Phase 清單
- [ ] Phase 1：[描述]
- [ ] Phase 2：[描述]

## 注意事項
- [重要限制或風險]
```

---

## Antigravity 補充

（此區塊由 Antigravity 填寫更詳細的規劃方法論）
