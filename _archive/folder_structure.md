# 資料夾結構說明

```
Anticlaude/
│
├── _context/                  ← 給 AI 的記憶檔（寫一次，長期沿用）
│   ├── about_me.md            ← 你的定位、受眾、語氣規範
│   ├── workflow.md            ← 每日/每週自動化流程
│   └── api_reference.md       ← 所有 API endpoint 對照表
│
├── uploads/                   ← 你丟進來的原始素材
│   ├── screenshots/           ← 截圖、靈感圖片
│   ├── bookmarks/             ← 手動收藏的連結
│   └── voice_notes/           ← 語音備忘錄
│
├── outputs/                   ← 系統幫你做好的成品
│   ├── daily_reports/         ← 每日素材報告 + 評分
│   │   └── YYYY-MM-DD.md
│   ├── drafts/                ← AI 生成的貼文草稿
│   │   └── YYYY-MM-DD.md
│   ├── threads_metrics/       ← Threads 貼文數據
│   │   └── YYYY-MM-DD.json
│   └── weekly_reports/        ← 每週策略報告
│       └── week_YYYY-WW.md
│
├── projects/                  ← 長期項目（各自有 uploads + outputs）
│   └── <專案名稱>/
│       ├── uploads/
│       └── outputs/
│
├── skills/                    ← 後續安裝的 AI skills
│   └── (預留空間)
│
├── README.md                  ← 本文件
├── folder_structure.md        ← 資料夾結構說明
├── system_architecture.md     ← 系統架構文件
└── api_reference.md           ← → 連結到 _context/api_reference.md
```

## 命名規則
- **日期檔案**：`YYYY-MM-DD` 格式（例：`2026-03-10.md`）
- **週報檔案**：`week_YYYY-WW` 格式（例：`week_2026-11.md`）
- **專案資料夾**：全小寫，用底線分隔（例：`ai_tools_series`）
