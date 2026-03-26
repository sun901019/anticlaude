# Skill SOP：Flow Lab 選品評分
> 執行者：Sage
> 輸入：ori-to-sage.md（競品資料）
> 輸出：評分報告 + sage-to-craft.md

## 評分公式
score = demand×2 + profit×2 + pain_points + competition + brand_fit
最高 50 分

## 各維度評分標準

### Demand（需求度）1-10
- 9-10：搜尋量大、多平台討論、持續需求
- 5-8：有穩定搜尋、但不是熱門
- 1-4：搜尋量低或只是短期爆紅

### Profit（利潤空間）1-10
- 進貨成本 × 2.5 以下賣得掉 → 4 分以下
- 進貨成本 × 3 以上可以賣 → 7 分以上
- 有廣告空間（ROAS > 3）→ 加 1 分

### Pain Points（痛點機會）1-10
- 競品 1-2 星評論中有明確可解決的抱怨 → 高分
- 痛點可以用產品改良解決 → 額外加分

### Competition（競爭健康度）1-10
- 有清晰價格梯次、多元差異化 → 高分
- 全部商品同質同價（價格戰） → 低分

### Brand Fit（品牌適配）1-10
- 辦公、桌面、療育、工作效率相關 → 高分
- 和 Flow Lab 定位無關 → 低分

## 評分結果判讀
- 40-50：強力候選，建議進貨
- 35-39：可行候選，觀察後進
- 30-34：觀察名單，暫不進
- <30：目前拒絕

## 輸出格式
每個候選商品產出：score_total + score_breakdown + recommended_role（traffic/profit/hero）+ reasoning
