# AntiClaude — 個人品牌內容自動化系統

> 每天打開就能看到 AI 幫你抓好的素材、評好分、寫好文案、追蹤好數據。

## 快速開始
```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 設定 API Key
cp .env.example .env
# 填入你的 Key

# 3. 跑一次
python src/pipeline.py

# 4. 打開儀表板
streamlit run src/dashboard/app.py
```

## 資料夾結構
| 資料夾 | 用途 |
|--------|------|
| `_context/` | AI 記憶檔（你的定位、流程、API 對照） |
| `uploads/` | 原始素材（截圖、連結、語音） |
| `outputs/` | 系統產出（報告、草稿、數據） |
| `projects/` | 長期項目（各自有 uploads + outputs） |
| `skills/` | 後續安裝的 AI skills |

## 文件索引
- [`_context/about_me.md`](./_context/about_me.md) — 個人定位與受眾
- [`_context/workflow.md`](./_context/workflow.md) — 自動化流程
- [`_context/api_reference.md`](./_context/api_reference.md) — API 對照表
- [`folder_structure.md`](./folder_structure.md) — 資料夾結構詳解
- [`system_architecture.md`](./system_architecture.md) — 系統架構
