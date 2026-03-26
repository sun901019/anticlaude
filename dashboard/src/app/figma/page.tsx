"use client";

import { useState } from "react";
import { BACKEND, sendCeoMessage } from "@/lib/api";

type FigmaPage = { id: string; name: string };
type FigmaComponent = { id: string; name: string; type: string; page: string };
type FigmaComment = {
  id: string;
  message: string;
  user?: string;
  created_at?: string;
  resolved_at?: string;
};

type Tab = "overview" | "components" | "comments" | "images";

const API = BACKEND;

async function apiFetch(path: string) {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.json();
}

export default function FigmaPage() {
  const [fileKey, setFileKey] = useState("");
  const [tab, setTab] = useState<Tab>("overview");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connected, setConnected] = useState<boolean | null>(null);
  const [fileInfo, setFileInfo] = useState<{
    name: string; last_modified: string; page_count: number; pages: FigmaPage[];
  } | null>(null);
  const [components, setComponents] = useState<FigmaComponent[]>([]);
  const [comments, setComments] = useState<FigmaComment[]>([]);
  const [imageNodeIds, setImageNodeIds] = useState("");
  const [imageUrls, setImageUrls] = useState<Record<string, string>>({});
  const [imageLoading, setImageLoading] = useState(false);
  const [pixelAnalyzing, setPixelAnalyzing] = useState(false);
  const [pixelResult, setPixelResult] = useState<string | null>(null);

  async function handlePing() {
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch("/api/figma/ping");
      setConnected(data.connected);
      if (!data.ok) setError(data.error ?? "無法連接 Figma API");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
      setConnected(false);
    } finally {
      setLoading(false);
    }
  }

  async function handleLoad() {
    if (!fileKey.trim()) return;
    setLoading(true);
    setError(null);
    setFileInfo(null);
    setComponents([]);
    setComments([]);
    setImageUrls({});
    try {
      const [fileData, compData] = await Promise.all([
        apiFetch(`/api/figma/file?file_key=${encodeURIComponent(fileKey)}`),
        apiFetch(`/api/figma/components?file_key=${encodeURIComponent(fileKey)}`),
      ]);
      setFileInfo({
        name: fileData.name,
        last_modified: fileData.last_modified,
        page_count: fileData.page_count,
        pages: fileData.pages ?? [],
      });
      setComponents(compData.components ?? []);
      setConnected(true);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  async function handleLoadComments() {
    if (!fileKey.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch(`/api/figma/comments?file_key=${encodeURIComponent(fileKey)}`);
      setComments(data.comments ?? []);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  async function handleRenderImages() {
    if (!fileKey.trim() || !imageNodeIds.trim()) return;
    setImageLoading(true);
    setError(null);
    try {
      const ids = encodeURIComponent(imageNodeIds.trim());
      const data = await apiFetch(`/api/figma/images?file_key=${encodeURIComponent(fileKey)}&ids=${ids}`);
      setImageUrls(data.images ?? {});
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setImageLoading(false);
    }
  }

  const tabs: { id: Tab; label: string }[] = [
    { id: "overview", label: "總覽" },
    { id: "components", label: `元件 (${components.length})` },
    { id: "comments", label: `留言 (${comments.length})` },
    { id: "images", label: "截圖匯出" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-stone-800">Figma 整合</h1>
          <p className="mt-1 text-sm text-stone-500">
            讀取 Figma 檔案結構、元件列表、留言與圖像匯出
          </p>
        </div>
        <button
          onClick={handlePing}
          disabled={loading}
          className="rounded-lg border border-stone-200 bg-white px-4 py-2 text-sm font-medium text-stone-600 transition hover:bg-stone-50 disabled:opacity-50"
        >
          {loading ? "測試中..." : "測試連線"}
        </button>
      </div>

      {/* Connection status */}
      {connected !== null && (
        <div className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm ${
          connected ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"
        }`}>
          <span className={`h-2 w-2 rounded-full ${connected ? "bg-emerald-500" : "bg-red-500"}`} />
          {connected ? "Figma API 連線正常" : "無法連接 Figma API — 請確認 FIGMA_API_TOKEN 是否設定"}
        </div>
      )}

      {/* File key input */}
      <div className="flex gap-2">
        <input
          value={fileKey}
          onChange={(e) => setFileKey(e.target.value)}
          placeholder="Figma file key（URL 中 /design/ 後面的字串）"
          className="flex-1 rounded-lg border border-stone-200 px-4 py-2 text-sm focus:border-[#7c5cbf] focus:outline-none"
          onKeyDown={(e) => e.key === "Enter" && handleLoad()}
        />
        <button
          onClick={handleLoad}
          disabled={loading || !fileKey.trim()}
          className="rounded-lg bg-[#7c5cbf] px-5 py-2 text-sm font-medium text-white transition hover:bg-[#6a4daa] disabled:opacity-50"
        >
          {loading ? "讀取中..." : "載入檔案"}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* File info */}
      {fileInfo && (
        <>
          <div className="rounded-xl border border-stone-200 bg-white p-5">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-lg font-bold text-stone-800">{fileInfo.name}</h2>
                <p className="text-xs text-stone-400 mt-1">
                  最後修改：{fileInfo.last_modified ? new Date(fileInfo.last_modified).toLocaleString("zh-TW") : "—"}
                </p>
              </div>
              <span className="rounded-full bg-stone-100 px-3 py-1 text-xs text-stone-600">
                {fileInfo.page_count} 個頁面
              </span>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {fileInfo.pages.map((p) => (
                <span key={p.id} className="rounded-full bg-purple-50 px-3 py-1 text-xs text-purple-700">
                  {p.name}
                </span>
              ))}
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 border-b border-stone-200">
            {tabs.map((t) => (
              <button
                key={t.id}
                onClick={() => {
                  setTab(t.id);
                  if (t.id === "comments" && comments.length === 0) handleLoadComments();
                }}
                className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
                  tab === t.id
                    ? "border-[#7c5cbf] text-[#7c5cbf]"
                    : "border-transparent text-stone-500 hover:text-stone-700"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          {tab === "overview" && (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {[
                { label: "頁面數", value: fileInfo.page_count },
                { label: "元件 / 框架", value: components.length },
                { label: "留言", value: comments.length > 0 ? comments.length : "—" },
                { label: "Token 狀態", value: connected ? "已連線" : "未連線" },
              ].map(({ label, value }) => (
                <div key={label} className="rounded-xl border border-stone-200 bg-white p-4 text-center">
                  <p className="text-2xl font-bold text-stone-800">{value}</p>
                  <p className="mt-1 text-xs text-stone-400">{label}</p>
                </div>
              ))}
            </div>
          )}

          {tab === "components" && (
            <div className="space-y-2">
              {components.length === 0 ? (
                <p className="py-8 text-center text-stone-400">沒有元件資料</p>
              ) : (
                <>
                  <p className="text-xs text-stone-400">顯示前 50 個頂層元件 / 框架</p>
                  <div className="overflow-hidden rounded-xl border border-stone-200 bg-white">
                    <table className="w-full text-sm">
                      <thead className="border-b border-stone-100 bg-stone-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-stone-500">名稱</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-stone-500">類型</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-stone-500">頁面</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-stone-500">ID</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-stone-100">
                        {components.map((c) => (
                          <tr key={c.id} className="hover:bg-stone-50">
                            <td className="px-4 py-3 font-medium text-stone-800">{c.name}</td>
                            <td className="px-4 py-3">
                              <span className="rounded bg-stone-100 px-1.5 py-0.5 text-xs text-stone-500">
                                {c.type}
                              </span>
                            </td>
                            <td className="px-4 py-3 text-stone-500">{c.page}</td>
                            <td className="px-4 py-3 font-mono text-xs text-stone-400">{c.id}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </div>
          )}

          {tab === "comments" && (
            <div className="space-y-3">
              {loading ? (
                <p className="py-8 text-center text-stone-400">載入留言中...</p>
              ) : comments.length === 0 ? (
                <p className="py-8 text-center text-stone-400">沒有留言</p>
              ) : (
                comments.map((c) => (
                  <div
                    key={c.id}
                    className={`rounded-xl border p-4 ${
                      c.resolved_at ? "border-stone-100 bg-stone-50 opacity-60" : "border-stone-200 bg-white"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm text-stone-800">{c.message}</p>
                      {c.resolved_at && (
                        <span className="shrink-0 rounded-full bg-emerald-100 px-2 py-0.5 text-xs text-emerald-700">
                          已解決
                        </span>
                      )}
                    </div>
                    <p className="mt-1 text-xs text-stone-400">
                      {c.user ?? "匿名"} ·{" "}
                      {c.created_at ? new Date(c.created_at).toLocaleString("zh-TW") : ""}
                    </p>
                  </div>
                ))
              )}
            </div>
          )}

          {tab === "images" && (
            <div className="space-y-4">
              <div className="flex gap-2">
                <input
                  value={imageNodeIds}
                  onChange={(e) => setImageNodeIds(e.target.value)}
                  placeholder="Node ID（逗號分隔，例如：1:2,1:3）"
                  className="flex-1 rounded-lg border border-stone-200 px-4 py-2 text-sm focus:border-[#7c5cbf] focus:outline-none"
                />
                <button
                  onClick={handleRenderImages}
                  disabled={imageLoading || !imageNodeIds.trim()}
                  className="rounded-lg bg-[#7c5cbf] px-5 py-2 text-sm font-medium text-white transition hover:bg-[#6a4daa] disabled:opacity-50"
                >
                  {imageLoading ? "渲染中..." : "匯出圖像"}
                </button>
              </div>
              <p className="text-xs text-stone-400">
                在元件列表中複製 Node ID，貼入此處即可渲染為 PNG 圖像。URL 有效期約 30 天。
              </p>
              {Object.keys(imageUrls).length > 0 && (
                <>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    {Object.entries(imageUrls).map(([nodeId, url]) => (
                      <div key={nodeId} className="overflow-hidden rounded-xl border border-stone-200 bg-white">
                        {url ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img src={url} alt={nodeId} className="w-full object-contain" />
                        ) : (
                          <div className="flex h-32 items-center justify-center bg-stone-50 text-sm text-stone-400">
                            渲染失敗
                          </div>
                        )}
                        <p className="px-3 py-2 font-mono text-xs text-stone-400">{nodeId}</p>
                      </div>
                    ))}
                  </div>

                  {/* Pixel UX Review */}
                  <div className="rounded-xl border border-purple-100 bg-purple-50 p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <p className="text-sm font-medium text-purple-800">Pixel 設計審核</p>
                        <p className="text-xs text-purple-500 mt-0.5">
                          將這些 Figma 截圖發送給 Pixel agent 進行 UX/設計分析
                        </p>
                      </div>
                      <button
                        onClick={async () => {
                          setPixelAnalyzing(true);
                          setPixelResult(null);
                          try {
                            const validUrls = Object.values(imageUrls).filter(Boolean);
                            const prompt = `請對以下 Figma 設計截圖進行 UX 審核，分析視覺層次、可用性與設計一致性，並給出具體改善建議。截圖共 ${validUrls.length} 張，URL：${validUrls.join("、")}`;
                            const result = await sendCeoMessage(prompt);
                            setPixelResult(result.response || "Pixel 審核完成");
                          } catch (e: unknown) {
                            setPixelResult(`分析失敗：${e instanceof Error ? e.message : String(e)}`);
                          } finally {
                            setPixelAnalyzing(false);
                          }
                        }}
                        disabled={pixelAnalyzing}
                        className="shrink-0 rounded-lg bg-[#7c5cbf] px-4 py-2 text-sm font-medium text-white transition hover:bg-[#6a4daa] disabled:opacity-50"
                      >
                        {pixelAnalyzing ? "分析中..." : "發送給 Pixel 分析"}
                      </button>
                    </div>
                    {pixelResult && (
                      <div className="mt-3 rounded-lg bg-white border border-purple-100 px-4 py-3">
                        <p className="text-xs text-purple-700 font-medium mb-1">PX Pixel 設計審核結果</p>
                        <p className="text-sm text-stone-700 whitespace-pre-wrap leading-relaxed">{pixelResult}</p>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          )}
        </>
      )}

      {/* Setup guide */}
      {!fileInfo && !loading && (
        <div className="rounded-xl border border-dashed border-stone-200 bg-stone-50 p-8 text-center">
          <p className="text-sm font-medium text-stone-600">如何使用</p>
          <ol className="mt-3 space-y-1 text-xs text-stone-400 text-left max-w-sm mx-auto list-decimal list-inside">
            <li>在 .env 設定 <code className="font-mono bg-stone-200 px-1 rounded">FIGMA_API_TOKEN</code></li>
            <li>開啟 Figma，從 URL 複製 file key（/design/ 後面的字串）</li>
            <li>貼入上方輸入框，點擊「載入檔案」</li>
            <li>瀏覽元件、留言，或匯出節點圖像</li>
          </ol>
        </div>
      )}
    </div>
  );
}
