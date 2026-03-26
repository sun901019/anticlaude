# Tools Registry

> Tools 與 Skills 的差異：Tools 是獨立的可執行程式，需要額外安裝或設定。

---

## 已整合 Tools

| Tool | 類型 | 狀態 | 用途 | 安裝 |
|------|------|------|------|------|
| `toonify-mcp` | MCP Server | 可用（需設定） | 圖片卡通化、省 Token | `_hub/skills_library/toonify-mcp/` |
| `vizro` | Python Dashboard | 可用（需 pip） | 互動式數據視覺化 | `pip install vizro` |

---

## 已整合 Tools（Phase 4 更新）

| Tool | 類型 | 狀態 | 用途 | 安裝 |
|------|------|------|------|------|
| `toonify-mcp` | MCP Server | 可用（需設定） | 圖片卡通化、省 Token | `_hub/skills_library/toonify-mcp/` |
| `vizro` | Python Dashboard | 可用（需 pip） | 互動式數據視覺化 | `pip install vizro` |
| `codex` | AI 執行引擎 | 可用（需 OpenAI API key） | 局部程式碼修復、批量生成 | `pip install openai` |

## Tool 使用規則

1. **只有在必要時才啟動 Tool**，不要為了用而用
2. **大數據集處理** → `vizro`
3. **圖片處理需求** → `toonify-mcp`
4. **局部程式碼修復** → `codex`（單檔、不需上下文）
5. **一般分析** → 直接用 Skill，不需要 Tool

---

## toonify-mcp 設定

來源：`https://github.com/PCIRCLE-AI/toonify-mcp`
本地路徑：`_hub/skills_library/toonify-mcp/`

功能：將圖片轉為卡通風格，可節省 Claude API token 用量（約 60%）

安裝步驟：
```bash
cd _hub/skills_library/toonify-mcp
npm install  # 或 pip install，視 repo 語言而定
```

---

## vizro 設定

來源：`https://github.com/mckinsey/vizro`
本地路徑：`_hub/skills_library/vizro/`
Demo：`_hub/visualization/vizro/app.py`

功能：用 Python 快速建立互動式儀表板

安裝：
```bash
pip install vizro
python _hub/visualization/vizro/app.py
```
