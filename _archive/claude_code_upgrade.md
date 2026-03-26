# Claude Code 升級任務 — Dashboard & 數據品質

> ⚠️ 由 **Antigravity** 規劃，由 **Claude Code** 執行  
> 載入角色：**UI Designer + Frontend Developer**（來自 agency-agents）  
> **不要修改 `src/` Python 後端代碼**，只改 `dashboard/` 前端

---

## 角色載入（先做這步）

在開始前，請以以下兩個角色的結合身份執行：

> 我是 **UI Designer + Frontend Developer** 的結合。
> 我的優先順序：視覺衝擊力 > 功能完整 > 代碼整潔。
> 參考：`_hub/shared/agents/agency-agents/README.md`

---

## 現狀分析（Antigravity 已讀完代碼）

| 頁面 | 現狀 | 問題 |
|------|------|------|
| `globals.css` | 只有 3 個 CSS 變數，用系統字體 | 沒有設計系統，字體普通 |
| `layout.tsx` | 功能正常 | 沒有 Google Fonts |
| `Sidebar.tsx` | 簡單，46 行 | 無 logo/avatar、無漸層 active 狀態 |
| `page.tsx` | 功能完整，341 行 | 卡片無玻璃質感，無微動畫 |
| `metrics/page.tsx` | 有折線圖 | 圖表無面積填色，無受眾洞察面板 |
| `library/page.tsx` | 有搜尋過濾 | 卡片 hover 效果太弱，無評分顯示 |

---

## 升級任務

### Task U1 — 設計系統升級（`globals.css`）

完全重寫 `dashboard/src/app/globals.css`，加入：

1. **Google Fonts**：`@import` Inter（界面字體）+ Noto Sans TC（繁中）
2. **設計 token**：
   ```css
   --bg: #080808          /* 更深的黑 */
   --surface: #111111     /* 卡片底色 */
   --surface-2: #1a1a1a   /* 次層 */
   --border: #1f1f1f      /* 邊框更細 */
   --accent: #7c3aed      /* 紫色 accent */
   --accent-glow: rgba(124, 58, 237, 0.15)
   --text-1: #f0f0f0
   --text-2: #888888
   --text-3: #444444
   --green: #10b981
   --red: #ef4444
   ```
3. **玻璃質感 class** `.glass`：`backdrop-blur-md` + 半透明邊框
4. **漸層背景**：sidebar 背景加細微噪點漸層
5. **動畫 keyframes**：`fadeIn`、`slideUp`、`pulse-glow`
6. **字體套用**：body 用 Inter，中文用 Noto Sans TC

---

### Task U2 — Sidebar 升級（`Sidebar.tsx`）

重寫 `dashboard/src/components/Sidebar.tsx`：

1. **Logo 區域**：AntiClaude 品牌名 + 下方 `@sunlee._.yabg` 以小頭像風格顯示
2. **Active 狀態**：改成紫色漸層 + 左側 3px 亮條（`border-l-2 border-violet-500`）
3. **Hover 動畫**：`transform: translateX(2px)` + 0.15s transition
4. **底部狀態**：顯示「系統運行中 🟢」的即時狀態（fetch `/health`）
5. **寬度**：從 224px 改成 220px，加玻璃邊框

---

### Task U3 — 今日總覽升級（`page.tsx`）

針對 `dashboard/src/app/page.tsx` 的視覺升級：

1. **頂部 Hero**：
   - 大標題「🌅 今日焦點」+ 日期
   - 右側三個手動觸發按鈕排成一排，改成 **pill 風格漸層按鈕**，有 loading spinner
   
2. **主題卡片** `TopicCard`：
   - 加 `glass` class（半透明背景 + blur）
   - 上方彩色細條（根據 post_type 不同顏色）
   - 評分改成環形進度條（SVG，不是 badge）
   - 4 個維度分數改成 **mini bar** 橫排更緊湊
   - Hover 時卡片浮起：`transform: translateY(-2px) + box-shadow`

3. **文案草稿** `DraftCard`：
   - 兩版並排顯示（flex gap）
   - 複製按鈕改大，成功後顯示 `✅ 已複製` 1.5 秒
   - 文字區域加淡淡的紫色左邊框

4. **空狀態**：有插畫風格的 empty state，不是純文字「暫無數據」

---

### Task U4 — Threads 數據頁升級（`metrics/page.tsx`）

1. **統計卡片**：3 個 `StatCard` 改為玻璃質感，加 sparkline（小折線圖）或趨勢箭頭
2. **圖表升級**：
   - 折線圖改 **AreaChart**（面積圖），漸層填色（紫→透明）
   - 加 `referenceLine` 顯示平均值虛線
   - tooltip 改客製化樣式（更精美）
3. **🆕 受眾洞察面板**：在圖表下方加一個 panel，fetch `/api/insights`，顯示：
   - 最佳發文日（高亮顯示）
   - 最受歡迎類型（帶 % 進度條）
   - Top Hook 模式（列表）
   - 如果沒有數據：顯示「需要更多數據，按回饋分析生成」的 CTA
4. **貼文表格**：hover 展開顯示全文（accordion 效果）

---

### Task U5 — 素材庫升級（`library/page.tsx`）

1. **卡片密度**：改成更緊湊的 list 風格（類似 HN style）
2. **評分顯示**：如果 `claude_score` 有值，顯示 `◆ 8.5` 在右側
3. **來源 badge**：加 favicon icon（用對應網站 favicon）
4. **動畫**：卡片入場動畫（stagger `fadeIn`，每張延遲 30ms）

---

### Task U6 — 新增受眾洞察頁（`insights/page.tsx`）

新建 `dashboard/src/app/insights/page.tsx`，顯示閉環分析結果：

1. **頁面結構**：
   - 頂部：「🧠 閉環洞察」+ 上次分析日期 + 「重新分析」按鈕
2. **內容卡片**：
   - 類別表現排名（橫向 bar chart）
   - 最佳發文日/時段（熱力圖 grid，7×24）
   - 高互動 Hook 模式 Top 5（帶互動率標籤）
3. **加到 Sidebar**：新增「受眾洞察」頁面到導覽列（Brain icon）

---

## 完成標準

- [ ] `npm run build` 零 TypeScript 錯誤
- [ ] 所有頁面在 localhost:3000 可正常操作
- [ ] 今日總覽：卡片有玻璃質感，按鈕有 loading 狀態
- [ ] Metrics：有面積圖 + 受眾洞察 panel
- [ ] 新增 Insights 頁面
- [ ] 字體改為 Inter + Noto Sans TC
- [ ] 所有 hover 有過渡動畫

## 技術限制
- Next.js 14 App Router
- Tailwind CSS（已安裝）  
- recharts（已安裝）
- lucide-react（已安裝）
- 後端 API 已在 `http://localhost:8000` 運行（FastAPI）
