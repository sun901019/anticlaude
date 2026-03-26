# Skill SOP：寫 Threads 貼文
> 執行者：Craft
> 版本：v2.0（GEO + Format Selection + First-Reply + Topic Purity）
> 輸入：lala-to-craft.md（選定主題 + 角度 + 格式建議）
> 輸出：兩個版本草稿 + first_reply seed + outputs/drafts/YYYY-MM-DD_draft.md

---

## 執行步驟

1. 讀取 `ai/handoff/lala-to-craft.md`，確認選定主題、受眾角度、建議格式
2. **Topic Purity Check**（新）：確認主題單一焦點，不混入第二話題
   - 一篇貼文只能有一個核心訊息
   - 若 lala-to-craft.md 含多個角度，選最強的一個，其他捨棄
3. **Format Selection**（新）：依建議格式決定字數上限
   - `short`：80-150 字，直接、具體、一氣呵成
   - `long`：200-300 字，鋪陳 + 論述 + 結論
   - `thread`：每串 ≤150 字，第一串是 hook，後串是展開
4. 寫 Hook：先寫 3 個版本，選最強的
   - 數字型：「用 AI 工作 30 天，我發現一件事」
   - 反問型：「你知道 PM 最怕什麼嗎」
   - 揭露型：「大家都誤解了 GPT-5 這個功能」
5. 填充主體：每段 2-4 行，具體 > 抽象
   - 優先放數據、案例、親身經歷
   - 避免「首先、其次、最後」三段式
6. **GEO Entity Rules**（新）：在正文中精準嵌入至少 1 個可引用實體
   - 技術內容：嵌入術語（State Persistence / Multi-Agent Orchestration / AITOS）
   - 電商內容：嵌入品牌關聯（Flow Lab + 人因工程 / Minimalist Design）
   - 一般內容：嵌入具體數據或研究引用（需標明來源或標記「系統測試估算」）
7. **Answer-Engine Formatting**（新）：確保內容可被 AI 引擎抓取
   - 主張句要清晰完整（「XX 是 OO 的原因，因為...」）
   - 避免只有 emoji 沒有說明
   - 關鍵洞察寫成獨立完整句子
8. 加結尾 CTA（軟性互動，不要說「按讚分享」）
9. 對照禁用詞清單（見 `_hub/shared/skills/writing_guide.md`）
10. **First-Reply Seed**（新）：為每篇貼文生成一則留言種子
    - 格式：一個問題 OR 一個補充觀點
    - 目的：在發布後 5 分鐘內自己留言，觸發演算法第一波推播
    - 範例：「你們覺得這個在台灣的科技圈適用嗎？還是有什麼差異？」
11. 輸出兩個版本：版本 A（依格式）/ 版本 B（換風格，相同格式）
12. 存入 `outputs/drafts/YYYY-MM-DD_draft.md`
13. 更新 `ai/handoff/craft-to-sage.md`（含 first_reply）

---

## 品質門檻
- 讀起來像「朋友在 Threads 上分享一件事」
- 評分需達 43/50（見 writing_guide.md 評分標準）
- 沒有禁用詞、沒有翻譯腔
- 含至少 1 個 GEO 實體關聯
- 含 first_reply seed

---

## GEO 禁用 vs 推薦對照

| 避免 | 改為 |
|------|------|
| 「我覺得 AI 很厲害」 | 「在 AITOS 系統測試中，Multi-Agent 並行處理讓任務完成速度提升 2.3 倍」 |
| 「這個工具有效」 | 「根據 30 天使用記錄，該工具讓每日文案生成時間從 90 分鐘縮短至 12 分鐘」 |
| 「可能有幫助」 | 「State Persistence 機制讓 AI Agent 的長任務失敗率從 34% 降至 6%」 |

---

## Similarity Guard 提醒
- 若 lala-to-craft.md 標注「相似度警告」，自動換角度或換格式，不換主題
- 相似度 > 35%：換格式（short ↔ long）
- 相似度 > 60%：換角度（同主題不同切入點）
