"""
AntiClaude Vizro Dashboard — Hello World 模板

安裝：pip install vizro pandas
執行：python _hub/visualization/vizro/app.py
開啟：http://localhost:8050
"""

import pandas as pd
import vizro.plotly.express as px
import vizro.models as vm
from vizro import Vizro

# === 範例數據（替換為真實的 anticlaude.db 數據）===
sample_data = pd.DataFrame({
    "date": pd.date_range("2026-03-01", periods=12, freq="D"),
    "likes": [12, 28, 15, 45, 32, 67, 23, 89, 54, 43, 71, 95],
    "replies": [3, 8, 5, 12, 9, 18, 7, 24, 15, 11, 19, 28],
    "post_type": ["AI工具", "趨勢", "職涯", "AI工具", "個人成長",
                  "AI工具", "趨勢", "AI工具", "職涯", "趨勢", "AI工具", "AI工具"],
})

# === 頁面 1：互動率趨勢 ===
page_trend = vm.Page(
    title="📈 互動率趨勢",
    components=[
        vm.Graph(
            figure=px.line(
                sample_data,
                x="date",
                y=["likes", "replies"],
                title="每日按讚數 vs 回覆數",
                labels={"value": "數量", "date": "日期"},
            )
        ),
    ],
)

# === 頁面 2：內容類型分析 ===
type_summary = sample_data.groupby("post_type")[["likes", "replies"]].mean().reset_index()

page_type = vm.Page(
    title="📊 內容類型分析",
    components=[
        vm.Graph(
            figure=px.bar(
                type_summary,
                x="post_type",
                y="likes",
                title="各類型平均按讚數",
                color="post_type",
                labels={"post_type": "內容類型", "likes": "平均按讚"},
            )
        ),
    ],
)

# === 建立 Dashboard ===
dashboard = vm.Dashboard(
    title="🤖 AntiClaude Analytics",
    pages=[page_trend, page_type],
)

if __name__ == "__main__":
    print("啟動 AntiClaude Vizro Dashboard...")
    print("請開啟瀏覽器：http://localhost:8050")
    Vizro().build(dashboard).run(port=8050)
