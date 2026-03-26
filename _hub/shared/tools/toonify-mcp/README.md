# Toonify MCP — Claude API Token 省錢神器

> 來源：https://github.com/PCIRCLE-AI/toonify-mcp
> 自動壓縮結構化資料，省 50-60% token 費用

## 這是什麼
一個 MCP server + Claude Code plugin，自動把傳給 Claude 的結構化資料（JSON、表格等）壓縮成 TOON 格式，省下大量 token。

## 為什麼需要
AntiClaude 每天呼叫 Claude API 做評分和文案，累積下來 token 費不少。裝了這個後每月大約省 $1.5-2。

## 安裝方式

### 方法 A：Claude Code Plugin（推薦）
```
claude plugin add PCIRCLE-AI/toonify-mcp
```

### 方法 B：MCP Server
```bash
npx -y toonify-mcp
```

在 `.claude.json` 中加入：
```json
{
  "mcpServers": {
    "toonify": {
      "command": "npx",
      "args": ["-y", "toonify-mcp"]
    }
  }
}
```

## 預估省多少
| 資料類型 | 壓縮率 |
|---------|--------|
| JSON | 50-55% |
| 表格 | 55-65% |
| 純文字 | 10-20% |

## 適用場景
- AntiClaude 的 Claude API 呼叫
- 任何大量使用 Claude 的專案
