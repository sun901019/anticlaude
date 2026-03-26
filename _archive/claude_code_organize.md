# Claude Code 任務 — 檔案整理

> 由 Antigravity 規劃，Claude Code 執行
> **只搬移/建立文件，不修改程式碼邏輯**

---

## 問題

根目錄有 8 個散落的 `.md` 文件，跟代碼資料夾混在一起，不好找：

```
Anticlaude/                  ← 現況（亂）
├── CLAUDE.md               ← 保留（Claude Code 規定放根目錄）
├── README.md               ← 保留（專案入口）
├── claude_code_tasks.md    ← 散落
├── claude_code_upgrade.md  ← 散落
├── database_schema.md      ← 散落
├── folder_structure.md     ← 散落
├── project_record.md       ← 散落
├── resource_map.md         ← 散落
├── system_architecture.md  ← 散落
├── implementation_plan.md.resolved ← 散落
├── requirements.txt
├── pytest.ini
├── src/
├── dashboard/
├── _context/
├── _hub/
└── ...
```

---

## 整理方案

### 新增 `docs/` 資料夾，分 3 個子目錄

```
Anticlaude/                      ← 整理後（乾淨）
│
├── CLAUDE.md                    ← 不動（Claude Code 必須在根目錄）
├── README.md                    ← 不動（專案入口）
├── requirements.txt             ← 不動
├── pytest.ini                   ← 不動
│
├── docs/                        ← 🆕 所有文件集中在這
│   ├── architecture/            ← 架構設計類
│   │   ├── system_architecture.md
│   │   ├── database_schema.md
│   │   └── folder_structure.md
│   │
│   ├── planning/                ← 規劃與任務類
│   │   ├── project_record.md
│   │   ├── resource_map.md
│   │   └── implementation_plan.md
│   │
│   └── tasks/                   ← Claude Code 執行任務
│       ├── claude_code_tasks.md
│       └── claude_code_upgrade.md
│
├── _context/                    ← 不動（AI 記憶）
├── _hub/                        ← 不動（共用資源）
├── src/                         ← 不動（Python 後端）
├── dashboard/                   ← 不動（Next.js 前端）
├── data/                        ← 不動（SQLite）
├── outputs/                     ← 不動（產出）
├── uploads/                     ← 不動（原始素材）
├── tests/                       ← 不動（測試）
├── logs/                        ← 不動（日誌）
├── projects/                    ← 不動（長期項目）
└── skills/                      ← 不動（AI skills）
```

---

## 執行步驟

### Step 1：建立 docs 資料夾

```powershell
cd c:\Users\sun90\Anticlaude
New-Item -ItemType Directory -Force -Path "docs/architecture", "docs/planning", "docs/tasks"
```

### Step 2：搬移檔案

```powershell
# 架構設計類
Move-Item -Path "system_architecture.md" -Destination "docs/architecture/"
Move-Item -Path "database_schema.md" -Destination "docs/architecture/"
Move-Item -Path "folder_structure.md" -Destination "docs/architecture/"

# 規劃與紀錄類
Move-Item -Path "project_record.md" -Destination "docs/planning/"
Move-Item -Path "resource_map.md" -Destination "docs/planning/"

# Claude Code 任務類
Move-Item -Path "claude_code_tasks.md" -Destination "docs/tasks/"
Move-Item -Path "claude_code_upgrade.md" -Destination "docs/tasks/"

# 清理
Remove-Item -Path "implementation_plan.md.resolved" -ErrorAction SilentlyContinue
```

### Step 3：建立 docs/README.md

建立 `docs/README.md`，內容：

```markdown
# 📚 文件索引

## 架構設計 `architecture/`
| 文件 | 內容 |
|------|------|
| `system_architecture.md` | 系統架構圖、6 個模組、技術選型、成本 |
| `database_schema.md` | SQLite 5 張表 schema + 閉環查詢範例 |
| `folder_structure.md` | 資料夾用途與命名規則 |

## 規劃紀錄 `planning/`
| 文件 | 內容 |
|------|------|
| `project_record.md` | 專案現況快照（檔案數、API、DB、時間線） |
| `resource_map.md` | 人話版：我有哪些 agents / skills / tools |

## 執行任務 `tasks/`
| 文件 | 內容 |
|------|------|
| `claude_code_tasks.md` | Hub 整合任務（Step 1-6） |
| `claude_code_upgrade.md` | 儀表板升級任務（U1-U6） |

## 其他重要文件（在根目錄）
| 文件 | 位置 | 內容 |
|------|------|------|
| `CLAUDE.md` | 根目錄 | Claude Code 自動讀取的專案指引 + Agent 派遣規則 |
| `README.md` | 根目錄 | 專案入口 + 快速開始 |

## 其他重要文件（在 _context/）
| 文件 | 內容 |
|------|------|
| `about_me.md` | 品牌定位、受眾、語氣規範 |
| `workflow.md` | 每日/每週流程 |
| `api_reference.md` | 所有 API 對照表 |
```

### Step 4：更新 README.md

把根目錄 `README.md` 的文件索引段落更新為指向 `docs/` 的新路徑：

```markdown
## 文件索引
- [`docs/`](./docs/) — 完整文件目錄
  - [`architecture/`](./docs/architecture/) — 系統架構、DB schema
  - [`planning/`](./docs/planning/) — 專案紀錄、資源地圖
  - [`tasks/`](./docs/tasks/) — Claude Code 執行任務
- [`_context/`](./_context/) — AI 記憶（受眾定位、流程、API）
- [`_hub/`](./_hub/) — 共用 agents / skills / tools
```

### Step 5：更新 CLAUDE.md 的路徑參考

在 CLAUDE.md 中，把「上下文自動載入」表格裡的路徑更新：

| 原本 | 改成 |
|------|------|
| `database_schema.md` | `docs/architecture/database_schema.md` |
| `system_architecture.md` | `docs/architecture/system_architecture.md` |

---

## 整理後的根目錄

```
Anticlaude/
├── CLAUDE.md            ← Claude Code 大腦
├── README.md            ← 專案入口
├── requirements.txt     ← Python 依賴
├── pytest.ini           ← 測試設定
│
├── docs/                ← 📚 所有文件
├── _context/            ← 🧠 AI 記憶
├── _hub/                ← 📦 共用資源
├── src/                 ← ⚙️ Python 後端
├── dashboard/           ← 🖥️ Next.js 前端
├── data/                ← 🗄️ SQLite DB
├── outputs/             ← 📊 系統產出
├── uploads/             ← 📥 原始素材
├── tests/               ← 🧪 測試
├── logs/                ← 📋 日誌
├── projects/            ← 📁 長期項目
└── skills/              ← 🧩 AI skills
```

**根目錄只剩 4 個檔案 + 11 個資料夾，乾淨清楚。**
