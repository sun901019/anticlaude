# Video Ingestion Spec — AITOS Multimodal Workflow
> 狀態：規劃中（不進入實作直到 Flow Lab Phase 2 成熟）
> 更新：2026-03-20

---

## 目標

讓 CEO 可以上傳一段影片（商品開箱、競品拍攝、直播片段），
AI 自動提取關鍵幀 + 轉錄字幕，產出選品洞察或 Threads 草稿，等待 CEO 審核後發布。

---

## Upload Path

```
POST /api/flowlab/video-upload
  → multipart/form-data: file (mp4/mov/webm, max 100MB)
  → 儲存至 data/uploads/videos/{uuid}.{ext}
  → 建立 flowlab_video_analyses 記錄（status="processing"）
  → 觸發背景任務：VideoAnalysisPipeline
```

---

## VideoInsightArtifact Schema

```python
class VideoInsightArtifact(BaseModel):
    id: str
    video_path: str                  # 上傳路徑
    duration_secs: float | None      # 影片秒數
    keyframe_paths: list[str]        # 提取的關鍵幀圖片路徑
    transcript: str | None           # 字幕全文（若有音軌）
    extracted_products: list[dict]   # [{name, price_hint, platform_hint}]
    threads_draft: str | None        # AI 產出草稿
    approval_id: str | None          # 對應 approval_request
    artifact_id: str | None          # 對應 workflow artifact
    status: str                      # processing | ready | approved | rejected
    created_at: datetime
```

---

## Frame Extractor 介面

```python
# src/adapters/video_adapter.py (stub)
class VideoFrameAdapter(AdapterBase):
    name = "video_frame_extractor"
    risk_level = "low"
    requires_approval = False

    async def execute(self, context: dict) -> AdapterResult:
        # 輸入：video_path, max_frames=8, interval_secs=None
        # 輸出：keyframe_paths: list[str]
        # 實作選項：
        #   - ffmpeg subprocess（本機）
        #   - Google Video Intelligence API（雲端，需 approval for PII risk）
        raise NotImplementedError("video_frame_extractor not yet implemented")
```

---

## Analysis Pipeline

```
VideoAnalysisPipeline (GraphRunner)
  Node 1: extract_frames  (video_adapter → keyframe_paths)
  Node 2: transcribe      (optional, whisper local or Google STT)
  Node 3: analyze_frames  (claude_vision → extracted_products + scene_context)
  Node 4: draft_from_video (craft → Threads draft based on insights)
  Node 5: video_approval  (approval gate, risk=medium)
  Node 6: save_video_artifact (record VideoInsightArtifact)
```

---

## Review UI（mockup）

```
Flow Lab > Video Analysis
┌─────────────────────────────────────────┐
│  [Video thumbnail]  duration: 2:34      │
│  Keyframes: [frame1] [frame2] [frame3]  │
│  Transcript: "這個商品真的很好用..."     │
│                                          │
│  Extracted products:                     │
│    - 玻尿酸精華液 (NT$599?)             │
│    - 防曬乳 SPF50                        │
│                                          │
│  Draft:                                  │
│    "你有沒有發現 skincare 界的..."       │
│                                          │
│  [核准並發布]  [拒絕]  [手動編輯]       │
└─────────────────────────────────────────┘
```

---

## 前置條件（未達到就不實作）

1. ffmpeg 在本機可用，或 Google Cloud credentials 已設定
2. Flow Lab Phase 1（截圖 workflow）穩定運行 > 2 週
3. VideoInsightArtifact 加入 DB schema + artifact taxonomy
4. approval gate 對 video 類型的風險定義清楚

---

## 里程碑

| 里程碑 | 條件 |
|--------|------|
| M1 上傳路徑 | ffmpeg 確認可用後 |
| M2 幀提取 + 分析 | M1 完成後 |
| M3 草稿 + approval gate | M2 完成後 |
| M4 Review UI | M3 完成後 |
