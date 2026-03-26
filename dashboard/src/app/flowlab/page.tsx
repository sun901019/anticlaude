"use client";
import { useCallback, useRef, useState, useEffect } from "react";
import { Upload, ImageIcon, Package, FileText, Check, X, ChevronDown, ChevronUp, Loader2, FileVideo, ClipboardCheck } from "lucide-react";
import { uploadVideo, fetchVideoAnalyses, fetchReviewQueue, decideReviewItem } from "@/lib/api";

type Extraction = {
  product_name?: string;
  category?: string;
  specs?: string[];
  selling_points?: string[];
  buyer_pain_points?: string[];
  suggested_price_range?: string;
  platform_origin?: string;
  extraction_confidence?: number;
  notes?: string;
};

type ShopeeDraft = {
  title?: string;
  description?: string;
  hashtags?: string[];
  geo_keywords?: string[];
};

type ThreadsDraft = {
  hook?: string;
  content?: string;
  first_reply?: string;
  format?: string;
};

type AnalysisResult = {
  ok: boolean;
  analysis_id?: string;
  product_name?: string;
  extraction?: Extraction;
  shopee_draft?: ShopeeDraft;
  threads_draft?: ThreadsDraft;
  approval_id?: string;
  artifact_id?: string;
  error?: string;
};

type HistoryItem = {
  id: string;
  product_name: string;
  category: string;
  confidence: number;
  status: string;
  created_at: string;
};

type VideoAnalysisItem = {
  id: string;
  filename: string;
  status: string;
  created_at: string;
};

type VideoUploadResult = {
  ok?: boolean;
  video_id?: string;
  error?: string;
};

export default function FlowLabPage() {
  const [activeTab, setActiveTab] = useState<"screenshot" | "video">("screenshot");

  // ── Screenshot tab state ──────────────────────────────────────────────────
  const [dragging, setDragging] = useState(false);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [context, setContext] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({ extraction: true, shopee: true, threads: true });
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ── Video tab state ───────────────────────────────────────────────────────
  const [videoDragging, setVideoDragging] = useState(false);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoUploading, setVideoUploading] = useState(false);
  const [videoUploadResult, setVideoUploadResult] = useState<VideoUploadResult | null>(null);
  const [videoUploadError, setVideoUploadError] = useState<string | null>(null);
  const [videoHistory, setVideoHistory] = useState<VideoAnalysisItem[]>([]);
  const [videoHistoryLoading, setVideoHistoryLoading] = useState(false);
  const videoFileInputRef = useRef<HTMLInputElement>(null);

  // ── Screenshot helpers ────────────────────────────────────────────────────
  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const res = await fetch("/api/flowlab/screenshots?limit=10");
      const data = await res.json();
      setHistory(data.screenshots || []);
    } catch {
      setHistory([]);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  // 初次載入歷史記錄
  useState(() => { loadHistory(); });

  const handleFile = (file: File) => {
    if (!file.type.startsWith("image/")) return;
    setImageFile(file);
    const reader = new FileReader();
    reader.onload = (e) => setImagePreview(e.target?.result as string);
    reader.readAsDataURL(file);
    setResult(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleAnalyze = async () => {
    if (!imageFile || !imagePreview) return;
    setLoading(true);
    setResult(null);
    try {
      // imagePreview is data:image/xxx;base64,<data>
      const [header, base64] = imagePreview.split(",");
      const mimeMatch = header.match(/data:(image\/\w+);base64/);
      const mimeType = mimeMatch ? mimeMatch[1] : "image/jpeg";
      const res = await fetch("/api/flowlab/screenshot-analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_base64: base64, image_type: mimeType, context }),
      });
      const data = await res.json();
      setResult(data);
      if (data.ok) loadHistory();
    } catch (e) {
      setResult({ ok: false, error: String(e) });
    } finally {
      setLoading(false);
    }
  };

  const handleDecide = async (analysisId: string, decision: "approved" | "rejected") => {
    await fetch(`/api/flowlab/screenshots/${analysisId}/decide`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision }),
    });
    loadHistory();
    if (result?.analysis_id === analysisId) {
      setResult(prev => prev ? { ...prev, error: undefined } : null);
    }
  };

  const toggle = (key: string) => setExpanded(p => ({ ...p, [key]: !p[key] }));

  // ── Video helpers ─────────────────────────────────────────────────────────
  const ACCEPTED_VIDEO_TYPES = ["video/mp4", "video/quicktime", "video/webm"];

  const loadVideoHistory = useCallback(async () => {
    setVideoHistoryLoading(true);
    try {
      const data = await fetchVideoAnalyses();
      setVideoHistory(data.videos || data || []);
    } catch {
      setVideoHistory([]);
    } finally {
      setVideoHistoryLoading(false);
    }
  }, []);

  useEffect(() => { loadVideoHistory(); }, [loadVideoHistory]);

  // ── Flow Lab mini review panel ────────────────────────────────────────────
  type MiniReviewItem = { id: number; question: string; context?: string; status: string };
  const [pendingReviews, setPendingReviews] = useState<MiniReviewItem[]>([]);
  const [reviewDeciding, setReviewDeciding] = useState<number | null>(null);
  const FLOWLAB_ACTIONS = new Set(["approve_screenshot", "approve_video_analysis"]);

  const loadPendingReviews = useCallback(async () => {
    try {
      const data = await fetchReviewQueue("pending");
      const items: MiniReviewItem[] = (data.items ?? []).filter((item: MiniReviewItem & { context?: string }) => {
        try { const ctx = JSON.parse(item.context ?? "{}"); return FLOWLAB_ACTIONS.has(ctx.action); }
        catch { return false; }
      });
      setPendingReviews(items);
    } catch { /* silent */ }
  }, []);

  async function handleMiniDecide(id: number, action: "approved" | "rejected") {
    setReviewDeciding(id);
    try { await decideReviewItem(id, action); await loadPendingReviews(); }
    catch { /* silent */ }
    finally { setReviewDeciding(null); }
  }

  useEffect(() => { void loadPendingReviews(); }, [loadPendingReviews]);

  const handleVideoFile = (file: File) => {
    if (!ACCEPTED_VIDEO_TYPES.includes(file.type)) {
      setVideoUploadError("不支援的檔案格式，請上傳 MP4 / MOV / WebM");
      return;
    }
    setVideoFile(file);
    setVideoUploadResult(null);
    setVideoUploadError(null);
  };

  const handleVideoDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setVideoDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleVideoFile(file);
  };

  const handleVideoUpload = async () => {
    if (!videoFile) return;
    setVideoUploading(true);
    setVideoUploadResult(null);
    setVideoUploadError(null);
    try {
      const data = await uploadVideo(videoFile);
      setVideoUploadResult({ ok: true, video_id: data.video_id });
      setVideoFile(null);
      loadVideoHistory();
    } catch (e) {
      setVideoUploadError(String(e));
    } finally {
      setVideoUploading(false);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Flow Lab 視覺選品</h1>
        <p className="text-gray-500 mt-1 text-sm">上傳 1688 / Taobao 截圖 → AI 提取產品資訊 → 自動生成 Shopee + Threads 草稿</p>
      </div>

      {/* Flow Lab 待審核 mini panel */}
      {pendingReviews.length > 0 && (
        <div className="rounded-[14px] border border-blue-200 bg-blue-50 p-4 space-y-3">
          <div className="flex items-center gap-2 text-[13px] font-semibold text-blue-800">
            <ClipboardCheck size={15} />
            待 Flow Lab 審核 <span className="ml-auto text-[12px] font-medium text-blue-600">{pendingReviews.length} 件</span>
          </div>
          <div className="space-y-2">
            {pendingReviews.map(item => {
              let actionLabel = "分析操作";
              try { const ctx = JSON.parse(item.context ?? "{}"); actionLabel = ctx.action === "approve_screenshot" ? "截圖分析" : "影片分析"; } catch {}
              return (
                <div key={item.id} className="flex items-start gap-3 bg-white rounded-[10px] border border-blue-100 px-3 py-2.5">
                  <div className="flex-1 min-w-0">
                    <div className="text-[12px] text-blue-700 font-medium mb-0.5">{actionLabel}</div>
                    <div className="text-[13px] text-gray-800 leading-snug line-clamp-2">{item.question}</div>
                  </div>
                  <div className="flex gap-1.5 shrink-0">
                    <button
                      disabled={reviewDeciding === item.id}
                      onClick={() => void handleMiniDecide(item.id, "approved")}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-[8px] text-[12px] font-medium bg-emerald-100 text-emerald-700 hover:bg-emerald-200 disabled:opacity-50">
                      <Check size={12} /> 核准
                    </button>
                    <button
                      disabled={reviewDeciding === item.id}
                      onClick={() => void handleMiniDecide(item.id, "rejected")}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-[8px] text-[12px] font-medium bg-red-100 text-red-600 hover:bg-red-200 disabled:opacity-50">
                      <X size={12} /> 拒絕
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab Bar */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex gap-6">
          <button
            onClick={() => setActiveTab("screenshot")}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "screenshot"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            截圖分析
          </button>
          <button
            onClick={() => setActiveTab("video")}
            className={`pb-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-1.5 ${
              activeTab === "video"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            <FileVideo className="w-4 h-4" />
            影片分析
          </button>
        </nav>
      </div>

      {/* ── Tab 1: Screenshot Analysis ── */}
      {activeTab === "screenshot" && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 上傳區 */}
            <div className="space-y-4">
              <div
                className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${dragging ? "border-blue-400 bg-blue-50" : "border-gray-300 hover:border-gray-400"}`}
                onDragOver={e => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
              >
                {imagePreview ? (
                  <img src={imagePreview} alt="preview" className="max-h-64 mx-auto rounded-lg object-contain" />
                ) : (
                  <div className="space-y-2">
                    <Upload className="w-10 h-10 text-gray-400 mx-auto" />
                    <p className="text-gray-600 font-medium">拖拉截圖至此，或點擊上傳</p>
                    <p className="text-gray-400 text-sm">支援 JPG / PNG / WebP</p>
                  </div>
                )}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])}
                />
              </div>

              {imagePreview && (
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-gray-700">補充說明（選填）</label>
                  <textarea
                    className="w-full border border-gray-200 rounded-lg p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="例：目標客群是台灣上班族、定位中高端、主攻辦公桌面美學..."
                    value={context}
                    onChange={e => setContext(e.target.value)}
                  />
                  <button
                    onClick={handleAnalyze}
                    disabled={loading}
                    className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {loading ? <><Loader2 className="w-4 h-4 animate-spin" />分析中...</> : <><ImageIcon className="w-4 h-4" />開始分析</>}
                  </button>
                </div>
              )}
            </div>

            {/* 分析結果 */}
            <div className="space-y-4">
              {result?.error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
                  {result.error}
                </div>
              )}

              {result?.ok && (
                <>
                  {/* 提取結果 */}
                  <div className="border border-gray-200 rounded-xl overflow-hidden">
                    <button
                      onClick={() => toggle("extraction")}
                      className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100"
                    >
                      <div className="flex items-center gap-2 font-medium text-gray-800">
                        <Package className="w-4 h-4 text-blue-600" />
                        {result.extraction?.product_name || "產品資訊"}
                        <span className="text-xs text-gray-500 font-normal">
                          信心度 {Math.round((result.extraction?.extraction_confidence || 0) * 100)}%
                        </span>
                      </div>
                      {expanded.extraction ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                    </button>
                    {expanded.extraction && result.extraction && (
                      <div className="p-4 space-y-3 text-sm">
                        <InfoRow label="品類" value={result.extraction.category} />
                        <InfoRow label="建議定價" value={result.extraction.suggested_price_range} />
                        <ListRow label="賣點" items={result.extraction.selling_points} color="green" />
                        <ListRow label="買家痛點" items={result.extraction.buyer_pain_points} color="orange" />
                        <ListRow label="規格" items={result.extraction.specs} color="blue" />
                        {result.extraction.notes && (
                          <p className="text-gray-500 text-xs bg-gray-50 rounded p-2">{result.extraction.notes}</p>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Shopee 草稿 */}
                  {result.shopee_draft?.title && (
                    <div className="border border-gray-200 rounded-xl overflow-hidden">
                      <button
                        onClick={() => toggle("shopee")}
                        className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100"
                      >
                        <span className="font-medium text-gray-800 flex items-center gap-2">
                          Shopee 草稿
                        </span>
                        {expanded.shopee ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                      </button>
                      {expanded.shopee && (
                        <div className="p-4 space-y-3 text-sm">
                          <div>
                            <p className="text-xs text-gray-500 mb-1">標題</p>
                            <p className="font-medium">{result.shopee_draft.title}</p>
                          </div>
                          <div>
                            <p className="text-xs text-gray-500 mb-1">商品描述</p>
                            <p className="whitespace-pre-wrap text-gray-700">{result.shopee_draft.description}</p>
                          </div>
                          {result.shopee_draft.hashtags && (
                            <div className="flex flex-wrap gap-1">
                              {result.shopee_draft.hashtags.map(t => (
                                <span key={t} className="bg-blue-100 text-blue-700 text-xs px-2 py-0.5 rounded-full">{t}</span>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Threads 草稿 */}
                  {result.threads_draft?.content && (
                    <div className="border border-gray-200 rounded-xl overflow-hidden">
                      <button
                        onClick={() => toggle("threads")}
                        className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100"
                      >
                        <span className="font-medium text-gray-800 flex items-center gap-2">
                          <FileText className="w-4 h-4 text-purple-600" />Threads 草稿
                        </span>
                        {expanded.threads ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                      </button>
                      {expanded.threads && (
                        <div className="p-4 space-y-3 text-sm">
                          {result.threads_draft.hook && (
                            <div>
                              <p className="text-xs text-gray-500 mb-1">Hook（第一行）</p>
                              <p className="font-semibold text-gray-800">{result.threads_draft.hook}</p>
                            </div>
                          )}
                          <div>
                            <p className="text-xs text-gray-500 mb-1">正文</p>
                            <p className="whitespace-pre-wrap text-gray-700">{result.threads_draft.content}</p>
                          </div>
                          {result.threads_draft.first_reply && (
                            <div className="bg-purple-50 rounded-lg p-3">
                              <p className="text-xs text-purple-600 mb-1">First Reply（發文後 5 分鐘內留言）</p>
                              <p className="text-gray-700">{result.threads_draft.first_reply}</p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  {/* 審核按鈕 */}
                  {result.analysis_id && (
                    <div className="flex gap-3">
                      <button
                        onClick={() => handleDecide(result.analysis_id!, "approved")}
                        className="flex-1 bg-green-600 text-white py-2.5 rounded-lg font-medium hover:bg-green-700 flex items-center justify-center gap-2"
                      >
                        <Check className="w-4 h-4" />核准草稿
                      </button>
                      <button
                        onClick={() => handleDecide(result.analysis_id!, "rejected")}
                        className="flex-1 bg-gray-200 text-gray-700 py-2.5 rounded-lg font-medium hover:bg-gray-300 flex items-center justify-center gap-2"
                      >
                        <X className="w-4 h-4" />拒絕
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>

          {/* 歷史記錄 */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-3">分析記錄</h2>
            {historyLoading ? (
              <div className="text-center py-8 text-gray-400"><Loader2 className="w-5 h-5 animate-spin mx-auto" /></div>
            ) : history.length === 0 ? (
              <p className="text-gray-400 text-sm text-center py-8">尚無分析記錄</p>
            ) : (
              <div className="divide-y border border-gray-200 rounded-xl overflow-hidden">
                {history.map(item => (
                  <div key={item.id} className="flex items-center justify-between p-4 hover:bg-gray-50">
                    <div>
                      <p className="font-medium text-gray-800">{item.product_name}</p>
                      <p className="text-xs text-gray-400">{item.category} · 信心度 {Math.round(item.confidence * 100)}% · {item.created_at?.slice(0, 16)}</p>
                    </div>
                    <StatusBadge status={item.status} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {/* ── Tab 2: Video Analysis ── */}
      {activeTab === "video" && (
        <>
          {/* 上傳區 */}
          <div className="space-y-4 max-w-xl">
            <div
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${videoDragging ? "border-blue-400 bg-blue-50" : "border-gray-300 hover:border-gray-400"}`}
              onDragOver={e => { e.preventDefault(); setVideoDragging(true); }}
              onDragLeave={() => setVideoDragging(false)}
              onDrop={handleVideoDrop}
              onClick={() => videoFileInputRef.current?.click()}
            >
              <div className="space-y-2">
                <FileVideo className="w-10 h-10 text-gray-400 mx-auto" />
                {videoFile ? (
                  <p className="text-gray-700 font-medium">{videoFile.name}</p>
                ) : (
                  <>
                    <p className="text-gray-600 font-medium">拖拉影片至此，或點擊上傳</p>
                    <p className="text-gray-400 text-sm">支援 MP4 / MOV / WebM</p>
                  </>
                )}
              </div>
              <input
                ref={videoFileInputRef}
                type="file"
                accept="video/mp4,video/quicktime,video/webm"
                className="hidden"
                onChange={e => e.target.files?.[0] && handleVideoFile(e.target.files[0])}
              />
            </div>

            {videoUploadError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
                {videoUploadError}
              </div>
            )}

            {videoUploadResult?.ok && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-green-700 text-sm">
                影片已上傳，等待 AI 分析核准
                {videoUploadResult.video_id && (
                  <span className="ml-1 text-green-500 text-xs">(ID: {videoUploadResult.video_id})</span>
                )}
              </div>
            )}

            <button
              onClick={handleVideoUpload}
              disabled={!videoFile || videoUploading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {videoUploading
                ? <><Loader2 className="w-4 h-4 animate-spin" />上傳中...</>
                : <><FileVideo className="w-4 h-4" />上傳影片</>
              }
            </button>

            <p className="text-xs text-gray-400 leading-relaxed">
              目前 AI 影片分析功能開發中（需 ffmpeg），上傳後系統會建立審核請求
            </p>
          </div>

          {/* 影片分析記錄 */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-3">影片分析記錄</h2>
            {videoHistoryLoading ? (
              <div className="text-center py-8 text-gray-400"><Loader2 className="w-5 h-5 animate-spin mx-auto" /></div>
            ) : videoHistory.length === 0 ? (
              <p className="text-gray-400 text-sm text-center py-8">尚無影片分析記錄</p>
            ) : (
              <div className="border border-gray-200 rounded-xl overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 text-gray-500 text-xs">
                    <tr>
                      <th className="text-left px-4 py-3 font-medium">檔名</th>
                      <th className="text-left px-4 py-3 font-medium">狀態</th>
                      <th className="text-left px-4 py-3 font-medium">上傳時間</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {videoHistory.map(item => (
                      <tr key={item.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-gray-800 font-medium">{item.filename}</td>
                        <td className="px-4 py-3"><VideoStatusBadge status={item.status} /></td>
                        <td className="px-4 py-3 text-gray-400">{item.created_at?.slice(0, 16)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value?: string }) {
  if (!value) return null;
  return (
    <div className="flex gap-2">
      <span className="text-gray-400 w-16 shrink-0">{label}</span>
      <span className="text-gray-700">{value}</span>
    </div>
  );
}

function ListRow({ label, items, color }: { label: string; items?: string[]; color: "green" | "orange" | "blue" }) {
  if (!items?.length) return null;
  const cls = { green: "bg-green-100 text-green-700", orange: "bg-orange-100 text-orange-700", blue: "bg-blue-100 text-blue-700" }[color];
  return (
    <div>
      <p className="text-gray-400 text-xs mb-1">{label}</p>
      <div className="flex flex-wrap gap-1">
        {items.map((item, i) => <span key={i} className={`text-xs px-2 py-0.5 rounded-full ${cls}`}>{item}</span>)}
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { cls: string; label: string }> = {
    pending:  { cls: "bg-yellow-100 text-yellow-700", label: "待審核" },
    approved: { cls: "bg-green-100 text-green-700",   label: "已核准" },
    rejected: { cls: "bg-red-100 text-red-700",       label: "已拒絕" },
  };
  const { cls, label } = map[status] || { cls: "bg-gray-100 text-gray-600", label: status };
  return <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${cls}`}>{label}</span>;
}

function VideoStatusBadge({ status }: { status: string }) {
  const map: Record<string, { cls: string; label: string }> = {
    processing: { cls: "bg-gray-100 text-gray-600",   label: "處理中" },
    ready:      { cls: "bg-blue-100 text-blue-700",   label: "就緒" },
    approved:   { cls: "bg-green-100 text-green-700", label: "已核准" },
    rejected:   { cls: "bg-red-100 text-red-700",     label: "已拒絕" },
  };
  const { cls, label } = map[status] || { cls: "bg-gray-100 text-gray-600", label: status };
  return <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${cls}`}>{label}</span>;
}
