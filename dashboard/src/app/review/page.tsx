"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  cleanupReviewQueue,
  decideReviewItem,
  fetchApprovalPackage,
  fetchPublishableDrafts,
  fetchReviewQueue,
  regenerateDraft,
  updateDraft,
} from "@/lib/api";

type ReviewStatus = "pending" | "approved" | "rejected" | "deferred";

type ReviewItem = {
  id: number;
  item_type: string;
  question: string;
  context?: string;
  options_json?: string;
  recommended?: string;
  reason?: string;
  related_agents?: string;
  deadline?: string;
  default_action?: string;
  status: ReviewStatus;
  created_by?: string;
  created_at: string;
  decision_by?: string;
  decision_at?: string;
  decision_note?: string;
};

const TYPE_LABELS: Record<string, string> = {
  content: "內容",
  product: "商品",
  architecture: "架構",
  strategy: "策略",
  integration: "整合",
};

const ACTION_LABELS: Record<string, string> = {
  publish_post:           "發布貼文",
  promote_product:        "推廣商品",
  approve_screenshot:     "截圖分析",
  approve_video_analysis: "影片分析",
  approve_purchase:       "採購決策",
};

// Domain category for each action — shows WHERE the request comes from
type ActionCategory = "content" | "flow_lab" | "external" | "system";

const ACTION_CATEGORY: Record<string, ActionCategory> = {
  publish_post:           "content",
  select_draft:           "content",
  confirm_analysis:       "content",
  promote_product:        "external",
  approve_screenshot:     "flow_lab",
  approve_video_analysis: "flow_lab",
  approve_purchase:       "flow_lab",
};

const CATEGORY_LABELS: Record<ActionCategory, string> = {
  content:  "內容",
  flow_lab: "選品",
  external: "外部",
  system:   "系統",
};

const CATEGORY_COLORS: Record<ActionCategory, string> = {
  content:  "bg-purple-100 text-purple-700",
  flow_lab: "bg-blue-100 text-blue-700",
  external: "bg-orange-100 text-orange-700",
  system:   "bg-stone-200 text-stone-600",
};

// Top-level domain split: 自媒體 vs 電商
type Domain = "all" | "social" | "ecommerce";

const DOMAIN_LABELS: Record<Domain, string> = {
  all:       "全部",
  social:    "自媒體",
  ecommerce: "電商",
};

const DOMAIN_ICONS: Record<Domain, string> = {
  all:       "📋",
  social:    "✍️",
  ecommerce: "🛍️",
};

// Map ActionCategory → Domain
const CATEGORY_TO_DOMAIN: Record<ActionCategory, Exclude<Domain, "all">> = {
  content:  "social",
  flow_lab: "ecommerce",
  external: "ecommerce",
  system:   "ecommerce",  // system items shown under ecommerce by default
};

// Irreversible actions — warn CEO before approving
const IRREVERSIBLE_ACTIONS = new Set([
  "publish_post", "promote_product", "approve_purchase",
]);

function parseContext(json?: string): { approval_id?: string; run_id?: string; action?: string } {
  if (!json) return {};
  try { return JSON.parse(json); } catch { return {}; }
}

const STATUS_LABELS: Record<ReviewStatus, string> = {
  pending: "待審核",
  approved: "已核准",
  rejected: "已拒絕",
  deferred: "已延後",
};

const STATUS_BADGES: Record<ReviewStatus, string> = {
  pending: "bg-amber-100 text-amber-800",
  approved: "bg-emerald-100 text-emerald-800",
  rejected: "bg-red-100 text-red-800",
  deferred: "bg-stone-200 text-stone-700",
};

function parseOptions(json?: string): { label: string; consequence: string }[] {
  if (!json) return [];
  try {
    return JSON.parse(json);
  } catch {
    return [];
  }
}

function parseAgents(value?: string): string[] {
  if (!value) return [];
  try {
    return JSON.parse(value);
  } catch {
    return value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
  }
}

export default function ReviewPage() {
  const [filter, setFilter] = useState<ReviewStatus | "all">("pending");
  const [domainFilter, setDomainFilter] = useState<Domain>("all");
  const [categoryFilter, setCategoryFilter] = useState<ActionCategory | "all">("all");
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [selected, setSelected] = useState<ReviewItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [deciding, setDeciding] = useState(false);
  const [cleaning, setCleaning] = useState(false);
  const [note, setNote] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  // Draft selection state (publish_post flow)
  const [drafts, setDrafts] = useState<{ id: number; style: string; content: string; hook: string }[]>([]);
  const [selectedDraftId, setSelectedDraftId] = useState<number | null>(null);
  const [editingContent, setEditingContent] = useState<string>("");
  const [isEditing, setIsEditing] = useState(false);
  const [regenerating, setRegenerating] = useState(false);
  const [regenError, setRegenError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [regenHint, setRegenHint] = useState("");
  // Platform selection for publish_post
  const [publishPlatforms, setPublishPlatforms] = useState<{ x: boolean; threads: boolean }>({ x: true, threads: true });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchReviewQueue(filter === "all" ? undefined : filter);
      setItems(data.items ?? []);
    } catch {
      setItems([]);
      setMessage("讀取審核佇列失敗");
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    load();
  }, [load]);

  const cleanupTarget = useMemo<"pending" | "approved" | "rejected" | "deferred" | "decided" | "all" | null>(() => {
    if (filter === "all") return "all";
    return filter;
  }, [filter]);

  // Domain counts for top-level tabs
  const domainCounts = useMemo(() => {
    const counts: Record<Domain, number> = { all: items.length, social: 0, ecommerce: 0 };
    for (const item of items) {
      const ctx = parseContext(item.context);
      const cat: ActionCategory = ctx.action ? (ACTION_CATEGORY[ctx.action] ?? "system") : "system";
      const domain = CATEGORY_TO_DOMAIN[cat];
      counts[domain] = (counts[domain] ?? 0) + 1;
    }
    return counts;
  }, [items]);

  // Apply domain + category filter on top of status filter
  const visibleItems = useMemo(() => {
    return items.filter((item) => {
      const ctx = parseContext(item.context);
      const cat: ActionCategory = ctx.action ? (ACTION_CATEGORY[ctx.action] ?? "system") : "system";
      if (domainFilter !== "all" && CATEGORY_TO_DOMAIN[cat] !== domainFilter) return false;
      if (categoryFilter !== "all" && cat !== categoryFilter) return false;
      return true;
    });
  }, [items, domainFilter, categoryFilter]);

  // Count items per category for sub-filter badges
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const item of items) {
      const ctx = parseContext(item.context);
      const cat = ctx.action ? (ACTION_CATEGORY[ctx.action] ?? "system") : "system";
      counts[cat] = (counts[cat] ?? 0) + 1;
    }
    return counts;
  }, [items]);

  async function handleDecide(status: "approved" | "rejected" | "deferred") {
    if (!selected || selected.status !== "pending") return;
    setDeciding(true);
    setMessage(null);
    try {
      // If approving a publish_post with a selected draft, save edited content first
      const ctx = parseContext(selected.context);
      if (status === "approved" && ctx.action === "publish_post" && selectedDraftId && editingContent) {
        const currentDraft = drafts.find(d => d.id === selectedDraftId);
        if (currentDraft && currentDraft.content !== editingContent) {
          await updateDraft(selectedDraftId, editingContent);
        }
      }
      const platforms = ctx.action === "publish_post"
        ? [publishPlatforms.x && "x", publishPlatforms.threads && "threads"].filter(Boolean) as string[]
        : undefined;
      const draftId = (ctx.action === "publish_post" && selectedDraftId) ? selectedDraftId : undefined;
      await decideReviewItem(selected.id, status, note || undefined, platforms, draftId);
      setSelected(null);
      setNote("");
      setDrafts([]);
      setSelectedDraftId(null);
      setRegenError(null);
      if (status === "approved" && ctx.action === "publish_post") {
        const dest = [publishPlatforms.x && "X", publishPlatforms.threads && "Threads"].filter(Boolean).join(" 和 ");
        setMessage(`已核准 — ${dest || "（未選平台）"} 發文排程中`);
      } else {
        setMessage(`已更新為「${STATUS_LABELS[status]}」`);
      }
      await load();
    } catch {
      setMessage("更新審核結果失敗");
    } finally {
      setDeciding(false);
    }
  }

  async function handleCleanup() {
    if (!cleanupTarget) return;
    const labelMap: Record<string, string> = {
      pending: "全部待審核項目（並取消對應的 Pipeline 等待）",
      decided: "全部已處理項目",
      all: "所有審核項目",
    };
    const label = labelMap[cleanupTarget] ?? STATUS_LABELS[cleanupTarget as keyof typeof STATUS_LABELS];
    if (!window.confirm(`要清除${label}嗎？此動作無法復原。`)) return;

    setCleaning(true);
    setMessage(null);
    try {
      const result = await cleanupReviewQueue(cleanupTarget);
      setSelected(null);
      setMessage(
        `已清除 ${result.review_items_deleted} 筆 review items，${result.approval_requests_deleted} 筆 approvals`
      );
      await load();
    } catch {
      setMessage("清理失敗");
    } finally {
      setCleaning(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-stone-800">審核佇列</h1>
          <p className="mt-1 text-sm text-stone-500">
            只保留需要你判斷的項目。電商審核也可在電商頁直接處理。
          </p>
        </div>
        {cleanupTarget && items.length > 0 && (
          <button
            onClick={handleCleanup}
            disabled={cleaning}
            className="rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm font-medium text-red-700 transition-colors hover:bg-red-100 disabled:opacity-50"
          >
            {cleaning
              ? "清理中..."
              : filter === "pending"
                ? `清除全部待審核 (${items.length})`
                : filter === "all"
                  ? `清除全部 (${items.length})`
                  : `清除目前列表 (${items.length})`}
          </button>
        )}
      </div>

      {message && (
        <div className="rounded-lg bg-stone-100 px-4 py-3 text-sm text-stone-600">
          {message}
        </div>
      )}

      {/* Domain tabs — 自媒體 vs 電商 */}
      <div className="flex gap-2 border-b border-stone-200 -mb-2">
        {(["all", "social", "ecommerce"] as Domain[]).map((d) => {
          const active = domainFilter === d;
          const count = domainCounts[d] ?? 0;
          return (
            <button
              key={d}
              onClick={() => { setDomainFilter(d); setCategoryFilter("all"); }}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${
                active
                  ? "border-[#7c5cbf] text-[#7c5cbf]"
                  : "border-transparent text-stone-400 hover:text-stone-600"
              }`}
            >
              <span>{DOMAIN_ICONS[d]}</span>
              <span>{DOMAIN_LABELS[d]}</span>
              {count > 0 && (
                <span className={`rounded-full px-1.5 py-0.5 text-xs font-semibold ${
                  active ? "bg-purple-100 text-purple-700" : "bg-stone-100 text-stone-500"
                }`}>
                  {count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Status filter */}
      <div className="flex flex-wrap gap-2">
        {([
          ["pending", "待審核"],
          ["approved", "已核准"],
          ["rejected", "已拒絕"],
          ["deferred", "已延後"],
          ["all", "全部"],
        ] as const).map(([key, label]) => (
          <button
            key={key}
            onClick={() => { setFilter(key); setCategoryFilter("all"); setDomainFilter("all"); }}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
              filter === key
                ? "bg-[#7c5cbf] text-white"
                : "border border-stone-200 bg-white text-stone-600 hover:border-[#7c5cbf]"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Category filter — only shown when there are items */}
      {items.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          <span className="self-center text-xs text-stone-400 mr-1">類別：</span>
          <button
            onClick={() => setCategoryFilter("all")}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              categoryFilter === "all"
                ? "bg-stone-700 text-white"
                : "border border-stone-200 bg-white text-stone-500 hover:border-stone-400"
            }`}
          >
            全部 ({items.length})
          </button>
          {(["content", "flow_lab", "external", "system"] as ActionCategory[])
            .filter((cat) => (categoryCounts[cat] ?? 0) > 0)
            .map((cat) => (
              <button
                key={cat}
                onClick={() => setCategoryFilter(cat)}
                className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                  categoryFilter === cat
                    ? CATEGORY_COLORS[cat]
                    : "border border-stone-200 bg-white text-stone-500 hover:border-stone-400"
                }`}
              >
                {CATEGORY_LABELS[cat]} ({categoryCounts[cat] ?? 0})
              </button>
            ))}
        </div>
      )}

      {loading ? (
        <div className="py-16 text-center text-stone-400">讀取中...</div>
      ) : visibleItems.length === 0 ? (
        <div className="py-16 text-center">
          <p className="text-stone-400">
            {items.length > 0 && categoryFilter !== "all"
              ? `沒有「${CATEGORY_LABELS[categoryFilter]}」類別的項目`
              : filter === "pending"
                ? "沒有待審核項目 — 系統目前沒有需要你決策的請求"
                : filter === "approved"
                  ? "沒有已核准的記錄 — 核准過的項目會保留在這裡"
                  : filter === "rejected"
                    ? "沒有已拒絕的記錄"
                    : filter === "deferred"
                      ? "沒有已延後的記錄 — 延後的項目仍保持 pending 狀態等待重新決策"
                      : "審核佇列是空的 — 一切運作正常"}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {visibleItems.map((item) => {
            const ctx = parseContext(item.context);
            const actionLabel = ctx.action ? (ACTION_LABELS[ctx.action] ?? ctx.action) : null;
            const cat: ActionCategory = ctx.action ? (ACTION_CATEGORY[ctx.action] ?? "system") : "system";
            const irreversible = ctx.action ? IRREVERSIBLE_ACTIONS.has(ctx.action) : false;
            return (
            <button
              key={item.id}
              type="button"
              onClick={async () => {
                setSelected(item);
                setNote(item.decision_note ?? "");
                setDrafts([]);
                setSelectedDraftId(null);
                setEditingContent("");
                setIsEditing(false);
                setRegenError(null);
                setPublishPlatforms({ x: true, threads: true });
                const ctx = parseContext(item.context);
                if (ctx.action === "publish_post") {
                  try {
                    const data = await fetchPublishableDrafts(20);
                    const list = data.drafts ?? [];
                    setDrafts(list);
                    if (list.length > 0) {
                      setSelectedDraftId(list[0].id);
                      setEditingContent(list[0].content);
                    }
                  } catch {
                    // non-fatal
                  }
                }
              }}
              className="w-full rounded-xl border border-stone-200 bg-white p-5 text-left transition-all hover:border-[#7c5cbf] hover:shadow-sm"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="mb-2 flex items-center gap-2 flex-wrap">
                    {/* Domain category badge */}
                    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${CATEGORY_COLORS[cat]}`}>
                      {CATEGORY_LABELS[cat]}
                    </span>
                    {actionLabel && (
                      <span className="rounded bg-stone-100 px-1.5 py-0.5 text-xs text-stone-500">
                        {actionLabel}
                      </span>
                    )}
                    {irreversible && item.status === "pending" && (
                      <span className="rounded bg-red-50 px-1.5 py-0.5 text-xs font-medium text-red-600">
                        不可逆
                      </span>
                    )}
                    {item.created_by && (
                      <span className="text-xs text-stone-300">by {item.created_by}</span>
                    )}
                  </div>
                  <p className="font-medium leading-snug text-stone-800">{item.question}</p>
                  {item.recommended && (
                    <p className="mt-1 text-xs text-[#7c5cbf]">建議：{item.recommended}</p>
                  )}
                </div>
                <div className="flex flex-shrink-0 flex-col items-end gap-2">
                  <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${STATUS_BADGES[item.status]}`}>
                    {STATUS_LABELS[item.status]}
                  </span>
                  <span className="text-xs text-stone-400">
                    {new Date(item.created_at).toLocaleDateString("zh-TW")}
                  </span>
                </div>
              </div>
            </button>
            );
          })}
        </div>
      )}

      {selected && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4"
          onClick={(event) => {
            if (event.target === event.currentTarget) setSelected(null);
          }}
        >
          <div className="max-h-[90vh] w-full max-w-xl overflow-y-auto rounded-2xl bg-white shadow-xl">
            <div className="p-6">
              <div className="mb-4 flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs font-medium uppercase tracking-wide text-stone-400">
                      {TYPE_LABELS[selected.item_type] ?? selected.item_type}
                    </span>
                    {(() => {
                      const ctx = parseContext(selected.context);
                      return ctx.action ? (
                        <span className="rounded bg-stone-100 px-1.5 py-0.5 text-xs text-stone-500">
                          {ACTION_LABELS[ctx.action] ?? ctx.action}
                        </span>
                      ) : null;
                    })()}
                  </div>
                  <h2 className="mt-1 text-lg font-bold text-stone-800">{selected.question}</h2>
                </div>
                <button
                  onClick={() => setSelected(null)}
                  className="ml-4 text-xl leading-none text-stone-400 hover:text-stone-600"
                >
                  ×
                </button>
              </div>

              {selected.context && (() => {
                const ctx = parseContext(selected.context);
                const cat: ActionCategory = ctx.action ? (ACTION_CATEGORY[ctx.action] ?? "system") : "system";
                const irreversible = ctx.action ? IRREVERSIBLE_ACTIONS.has(ctx.action) : false;
                return (
                  <>
                    {irreversible && selected.status === "pending" && (
                      <div className="mb-3 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-xs font-medium text-red-700">
                        ⚠ 不可逆操作 — 核准後無法撤銷，請確認後再決策
                      </div>
                    )}
                    <div className="mb-4 rounded-lg bg-stone-50 px-4 py-3 text-xs text-stone-500 space-y-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${CATEGORY_COLORS[cat]}`}>
                          {CATEGORY_LABELS[cat]}
                        </span>
                        {ctx.action && (
                          <span className="text-stone-400">{ACTION_LABELS[ctx.action] ?? ctx.action}</span>
                        )}
                      </div>
                      {ctx.run_id && <p><span className="font-medium">Run:</span> <span className="font-mono">{ctx.run_id.slice(0, 8)}…</span></p>}
                      {ctx.approval_id && <p><span className="font-medium">Approval:</span> <span className="font-mono">{ctx.approval_id.slice(0, 8)}…</span></p>}
                      {!ctx.run_id && !ctx.approval_id && (
                        <p className="text-stone-400 leading-relaxed">{selected.context}</p>
                      )}
                    </div>
                  </>
                );
              })()}

              {selected.options_json && parseOptions(selected.options_json).length > 0 && (
                <div className="mb-4">
                  <p className="mb-2 text-xs font-semibold uppercase text-stone-500">可選項目</p>
                  <div className="space-y-2">
                    {parseOptions(selected.options_json).map((option, index) => (
                      <div
                        key={`${option.label}-${index}`}
                        className={`rounded-lg border p-3 text-sm ${
                          selected.recommended === option.label
                            ? "border-[#7c5cbf] bg-purple-50"
                            : "border-stone-200"
                        }`}
                      >
                        <span className="font-medium text-stone-700">{option.label}</span>
                        {option.consequence && (
                          <span className="ml-2 text-stone-400">· {option.consequence}</span>
                        )}
                        {selected.recommended === option.label && (
                          <span className="ml-2 text-xs text-[#7c5cbf]">AI 建議</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Platform selection — only for publish_post */}
              {(() => {
                const ctx = parseContext(selected.context);
                if (ctx.action !== "publish_post") return null;
                return (
                  <div className="mb-4 rounded-lg border border-stone-200 bg-stone-50 px-4 py-3">
                    <p className="mb-2 text-xs font-semibold uppercase text-stone-500">發布平台</p>
                    <div className="flex gap-4">
                      <label className="flex items-center gap-2 cursor-pointer select-none">
                        <input
                          type="checkbox"
                          checked={publishPlatforms.x}
                          onChange={e => setPublishPlatforms(p => ({ ...p, x: e.target.checked }))}
                          className="accent-[#7c5cbf]"
                        />
                        <span className="text-sm font-medium text-stone-700">X (Twitter)</span>
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer select-none">
                        <input
                          type="checkbox"
                          checked={publishPlatforms.threads}
                          onChange={e => setPublishPlatforms(p => ({ ...p, threads: e.target.checked }))}
                          className="accent-[#7c5cbf]"
                        />
                        <span className="text-sm font-medium text-stone-700">Threads</span>
                      </label>
                    </div>
                    {!publishPlatforms.x && !publishPlatforms.threads && (
                      <p className="mt-2 text-xs text-amber-600">⚠ 未選任何平台，核准後不會發布</p>
                    )}
                  </div>
                );
              })()}

              {/* Draft selection + edit for publish_post approvals */}
              {drafts.length > 0 && (() => {
                const selected_draft = drafts.find(d => d.id === selectedDraftId);
                return (
                  <div className="mb-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <p className="text-xs font-semibold uppercase text-stone-500">
                        選擇草稿（{drafts.length} 篇）
                      </p>
                      {drafts.length > 1 && (
                        <span className="text-xs text-stone-400">點擊切換版本</span>
                      )}
                    </div>

                    {/* Draft selector tabs */}
                    <div className="flex gap-1.5 flex-wrap">
                      {drafts.map((draft, idx) => (
                        <button
                          key={draft.id}
                          type="button"
                          onClick={() => {
                            setSelectedDraftId(draft.id);
                            setEditingContent(draft.content);
                            setIsEditing(false);
                            setRegenError(null);
                          }}
                          className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                            draft.id === selectedDraftId
                              ? "bg-[#7c5cbf] text-white"
                              : "border border-stone-200 bg-white text-stone-600 hover:border-[#7c5cbf]"
                          }`}
                        >
                          {draft.style || `版本 ${idx + 1}`}
                        </button>
                      ))}
                    </div>

                    {/* Selected draft preview / editor */}
                    {selected_draft && (
                      <div className="rounded-lg border border-stone-200 bg-white">
                        {/* Toolbar */}
                        <div className="flex items-center justify-between border-b border-stone-100 px-3 py-2">
                          <span className="text-xs text-stone-400">
                            {isEditing ? "編輯中" : "預覽"} · 核准後發出
                          </span>
                          <div className="flex gap-1.5">
                            <button
                              type="button"
                              onClick={() => { setIsEditing(e => !e); setRegenError(null); }}
                              className="rounded px-2 py-1 text-xs font-medium text-stone-600 hover:bg-stone-100"
                            >
                              {isEditing ? "取消" : "✎ 編輯"}
                            </button>
                            {isEditing && (
                              <button
                                type="button"
                                onClick={async () => {
                                  setSaving(true);
                                  try {
                                    await updateDraft(selected_draft.id, editingContent);
                                    setDrafts(prev => prev.map(d =>
                                      d.id === selected_draft.id ? { ...d, content: editingContent } : d
                                    ));
                                    setIsEditing(false);
                                  } catch {
                                    // non-fatal
                                  } finally {
                                    setSaving(false);
                                  }
                                }}
                                disabled={saving}
                                className="rounded bg-[#7c5cbf] px-2 py-1 text-xs font-medium text-white hover:bg-purple-700 disabled:opacity-50"
                              >
                                {saving ? "儲存中…" : "儲存"}
                              </button>
                            )}
                          </div>
                        </div>

                        {/* Content area */}
                        <div className="px-3 py-3">
                          {isEditing ? (
                            <textarea
                              value={editingContent}
                              onChange={e => setEditingContent(e.target.value)}
                              rows={8}
                              className="w-full resize-y rounded border border-stone-200 px-2 py-2 text-sm focus:border-[#7c5cbf] focus:outline-none"
                            />
                          ) : (
                            <p className="whitespace-pre-wrap text-sm leading-relaxed text-stone-700 min-h-[6rem]">
                              {editingContent}
                            </p>
                          )}
                        </div>

                        {/* Regenerate row */}
                        <div className="border-t border-stone-100 px-3 py-2 space-y-1.5">
                          <div className="flex gap-2">
                            <input
                              type="text"
                              value={regenHint}
                              onChange={e => setRegenHint(e.target.value)}
                              placeholder="補充方向（選填）再重新生成"
                              className="flex-1 rounded border border-stone-200 bg-stone-50 px-2 py-1 text-xs focus:border-[#7c5cbf] focus:outline-none"
                              onKeyDown={async e => {
                                if (e.key !== "Enter" || regenerating) return;
                                e.preventDefault();
                                setRegenerating(true);
                                setRegenError(null);
                                try {
                                  const res = await regenerateDraft(selected_draft.id, regenHint);
                                  setEditingContent(res.content);
                                  setDrafts(prev => prev.map(d =>
                                    d.id === selected_draft.id ? { ...d, content: res.content } : d
                                  ));
                                } catch (err) {
                                  setRegenError(err instanceof Error ? err.message : "重新生成失敗，請稍後再試");
                                } finally {
                                  setRegenerating(false);
                                }
                              }}
                            />
                            <button
                              type="button"
                              onClick={async () => {
                                if (regenerating) return;
                                setRegenerating(true);
                                setRegenError(null);
                                try {
                                  const res = await regenerateDraft(selected_draft.id, regenHint);
                                  setEditingContent(res.content);
                                  setDrafts(prev => prev.map(d =>
                                    d.id === selected_draft.id ? { ...d, content: res.content } : d
                                  ));
                                } catch (err) {
                                  setRegenError(err instanceof Error ? err.message : "重新生成失敗，請稍後再試");
                                } finally {
                                  setRegenerating(false);
                                }
                              }}
                              disabled={regenerating || saving}
                              className="rounded bg-stone-100 px-2 py-1 text-xs font-medium text-stone-700 hover:bg-stone-200 disabled:opacity-50 whitespace-nowrap"
                            >
                              {regenerating ? "生成中…" : "↻ 重新生成"}
                            </button>
                          </div>
                          {regenError && (
                            <p className="text-xs text-red-600">{regenError}</p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })()}

              {selected.reason && (
                <div className="mb-4 text-sm text-stone-500">
                  <span className="font-semibold text-stone-700">AI 建議理由：</span>
                  {selected.reason}
                </div>
              )}

              {selected.related_agents && parseAgents(selected.related_agents).length > 0 && (
                <div className="mb-4 flex flex-wrap gap-2">
                  {parseAgents(selected.related_agents).map((agent) => (
                    <span
                      key={agent}
                      className="rounded-full bg-stone-100 px-2 py-1 text-xs text-stone-600"
                    >
                      {agent}
                    </span>
                  ))}
                </div>
              )}

              {selected.deadline && (
                <p className="mb-4 text-xs text-amber-600">
                  截止時間：{selected.deadline}
                  {selected.default_action && `，逾時預設：${selected.default_action}`}
                </p>
              )}

              {selected.status === "pending" ? (
                <div className="mt-2 border-t border-stone-100 pt-4">
                  <label className="text-xs font-semibold uppercase text-stone-500">
                    Decision note
                  </label>
                  <textarea
                    value={note}
                    onChange={(event) => setNote(event.target.value)}
                    placeholder="補充核准、拒絕或延後的原因..."
                    rows={2}
                    className="mt-1 mb-3 w-full resize-none rounded-lg border border-stone-200 px-3 py-2 text-sm focus:border-[#7c5cbf] focus:outline-none"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleDecide("approved")}
                      disabled={deciding}
                      className="flex-1 rounded-lg bg-green-500 py-2 text-sm font-medium text-white transition-colors hover:bg-green-600 disabled:opacity-50"
                    >
                      核准
                    </button>
                    <button
                      onClick={() => handleDecide("rejected")}
                      disabled={deciding}
                      className="flex-1 rounded-lg bg-red-500 py-2 text-sm font-medium text-white transition-colors hover:bg-red-600 disabled:opacity-50"
                    >
                      拒絕
                    </button>
                    <button
                      onClick={() => handleDecide("deferred")}
                      disabled={deciding}
                      className="flex-1 rounded-lg bg-stone-200 py-2 text-sm font-medium text-stone-700 transition-colors hover:bg-stone-300 disabled:opacity-50"
                    >
                      延後
                    </button>
                  </div>
                </div>
              ) : (
                <div className="mt-2 border-t border-stone-100 pt-4 text-sm text-stone-500">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${STATUS_BADGES[selected.status]}`}>
                    {STATUS_LABELS[selected.status]}
                  </span>
                  {selected.decision_by && <span className="ml-2">by {selected.decision_by}</span>}
                  {selected.decision_at && (
                    <span className="ml-2">
                      {new Date(selected.decision_at).toLocaleString("zh-TW")}
                    </span>
                  )}
                  {selected.decision_note && (
                    <p className="mt-2 rounded bg-stone-50 p-2">{selected.decision_note}</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
