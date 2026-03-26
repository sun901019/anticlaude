"""
Content Intelligence Layer
==========================
純 Python 工具模組，不依賴 DB 或 API，可在任何階段獨立呼叫。

模組：
  format_selector   — 根據主題特性選擇 short / long / thread 格式
  topic_fit         — 過濾不符合品牌定位的主題（Topic Fit Gate）
  similarity_guard  — 防止連續發相似主題（關鍵字重疊 + 冷卻期）
"""
