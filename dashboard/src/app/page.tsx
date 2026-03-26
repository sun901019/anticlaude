"use client";
import { useState, useEffect, useCallback } from "react";
import { Copy, Check, Zap, BarChart2, ChevronDown, ChevronUp, Loader2, Send, CheckCircle2, AlertCircle, Clock, TrendingUp, ShieldAlert } from "lucide-react";
import Link from "next/link";
import { fetchToday, triggerPipeline, getPipelineStatus, triggerTracker, getTrackerStatus, publishToThreads, fetchMorningBriefing, fetchPendingApprovals } from "@/lib/api";
import ReactMarkdown from "react-markdown";

// ─── Types ────────────────────────────────────────────────────────────────────
type Dimensions = { timeliness: number; heat: number; controversy: number; audience_fit: number };
type Draft = { cluster_label: string; hook?: string; version_a?: { style: string; content: string }; version_b?: { style: string; content: string } };
type Topic = {
  cluster_label: string; rank: number; score: number; post_type: string;
  reason?: string; strategy_reason?: string; merged_summary?: string;
  dimensions?: Dimensions; draft?: Draft;
};

// ─── Design tokens ────────────────────────────────────────────────────────────
const TYPE_BAR: Record<string, string> = {
  "AI工具實測":  "from-violet-500 to-purple-500",
  "職涯觀點":    "from-blue-500 to-cyan-500",
  "個人成長":    "from-green-500 to-emerald-500",
  "趨勢解讀":    "from-fuchsia-500 to-pink-500",
  "互動貼文":    "from-orange-500 to-amber-500",
};

const TYPE_TAG: Record<string, string> = {
  "AI工具實測":  "bg-violet-50 text-violet-700 border-violet-200",
  "職涯觀點":    "bg-blue-50 text-blue-700 border-blue-200",
  "個人成長":    "bg-emerald-50 text-emerald-700 border-emerald-200",
  "趨勢解讀":    "bg-fuchsia-50 text-fuchsia-700 border-fuchsia-200",
  "互動貼文":    "bg-orange-50 text-orange-700 border-orange-200",
};

// Dimension bar colors (light theme)
const DIM_COLOR: Record<string, { bar: string; bg: string }> = {
  timeliness:   { bar: "bg-violet-500", bg: "bg-violet-100" },
  heat:         { bar: "bg-orange-500", bg: "bg-orange-100" },
  controversy:  { bar: "bg-red-500",    bg: "bg-red-100" },
  audience_fit: { bar: "bg-blue-500",   bg: "bg-blue-100" },
};

// ─── Helpers ──────────────────────────────────────────────────────────────────
function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      onClick={async () => { await navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 1500); }}
      className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg transition-all border ${
        copied
          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
          : "bg-[var(--bg-2)] hover:bg-[var(--border)] text-[var(--text-2)] hover:text-[var(--text-1)] border-[var(--border)]"
      }`}
    >
      {copied ? <Check size={11} /> : <Copy size={11} />}
      {copied ? "已複製" : "複製"}
    </button>
  );
}

function PublishButton({ text }: { text: string }) {
  const [state, setState] = useState<"idle" | "loading" | "ok" | "err">("idle");
  const handlePublish = async () => {
    if (!confirm("確定要發布到 Threads？")) return;
    setState("loading");
    try {
      const res = await publishToThreads(text);
      setState(res.ok ? "ok" : "err");
      setTimeout(() => setState("idle"), 3000);
    } catch {
      setState("err");
      setTimeout(() => setState("idle"), 3000);
    }
  };
  return (
    <button
      onClick={handlePublish}
      disabled={state === "loading"}
      className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg transition-all border ${
        state === "ok"
          ? "bg-violet-50 text-violet-700 border-violet-200"
          : state === "err"
          ? "bg-red-50 text-red-600 border-red-200"
          : "bg-[var(--bg-2)] hover:bg-[var(--border)] text-[var(--text-2)] hover:text-[var(--text-1)] border-[var(--border)] disabled:opacity-50"
      }`}
    >
      {state === "loading" ? <Loader2 size={11} className="animate-spin" /> : <Send size={11} />}
      {state === "ok" ? "已發布！" : state === "err" ? "發布失敗" : state === "loading" ? "發布中..." : "發布"}
    </button>
  );
}

function ScoreRing({ score }: { score: number }) {
  const r = 16;
  const circ = 2 * Math.PI * r;
  const pct = Math.min((score / 10) * circ, circ);
  const color = score >= 9 ? "#16a34a" : score >= 7 ? "#7c5cbf" : "#78716c";
  return (
    <svg width="44" height="44" viewBox="0 0 44 44" className="shrink-0">
      <circle cx="22" cy="22" r={r} fill="none" stroke="#ede8df" strokeWidth="2.5" />
      <circle cx="22" cy="22" r={r} fill="none" stroke={color} strokeWidth="2.5"
        strokeDasharray={`${pct} ${circ}`} strokeLinecap="round"
        transform="rotate(-90 22 22)" style={{ transition: "stroke-dasharray 0.6s ease" }} />
      <text x="22" y="22" textAnchor="middle" dominantBaseline="central"
        fill={color} fontSize="11" fontWeight="700">{score}</text>
    </svg>
  );
}

function MiniBar({ label, value, dimKey }: { label: string; value: number; dimKey?: string }) {
  const colors = dimKey ? DIM_COLOR[dimKey] : { bar: "bg-violet-500", bg: "bg-violet-100" };
  return (
    <div className="flex items-center gap-2 min-w-0">
      <span className="text-[11px] text-[var(--text-2)] font-medium w-12 shrink-0">{label}</span>
      <div className={`flex-1 h-[5px] ${colors.bg} rounded-full overflow-hidden`}>
        <div className={`h-full ${colors.bar} rounded-full transition-all duration-500`} style={{ width: `${value * 10}%` }} />
      </div>
      <span className="text-[11px] font-semibold text-[var(--text-1)] w-4 text-right">{value}</span>
    </div>
  );
}

function EmptyState({ onAction, loading }: { onAction: () => void; loading: boolean }) {
  return (
    <div className="flex flex-col items-center justify-center h-72 gap-5 animate-fade-in">
      <div className="w-16 h-16 rounded-2xl bg-[var(--accent-soft)] flex items-center justify-center">
        <Zap size={28} className="text-[var(--accent)]" />
      </div>
      <div className="text-center">
        <p className="text-[var(--text-1)] text-sm font-semibold">今天還沒有分析資料</p>
        <p className="text-[var(--text-3)] text-xs mt-1">點下方按鈕啟動完整 AI 分析流程</p>
      </div>
      <button
        onClick={onAction} disabled={loading}
        className="flex items-center gap-2 px-6 py-2.5 rounded-full bg-[var(--accent)] hover:opacity-90 text-white text-sm font-medium disabled:opacity-50 transition-all shadow-lg shadow-violet-500/20"
      >
        {loading ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
        {loading ? "分析中..." : "立即抓取分析"}
      </button>
    </div>
  );
}

// ─── TopicCard ────────────────────────────────────────────────────────────────
function TopicCard({ topic, rank }: { topic: Topic; rank: number }) {
  const [tab, setTab] = useState<"a" | "b">("a");
  const [expanded, setExpanded] = useState(rank === 1);
  const draft = topic.draft;
  const dims = topic.dimensions;
  const score = topic.score ?? 0;
  const tagCls = TYPE_TAG[topic.post_type] || "bg-gray-50 text-gray-600 border-gray-200";
  const barGrad = TYPE_BAR[topic.post_type] || "from-gray-400 to-gray-500";
  const activeContent = tab === "a" ? draft?.version_a?.content : draft?.version_b?.content;

  return (
    <div className="card-sm overflow-hidden hover:-translate-y-0.5 transition-all duration-200 animate-slide-up"
      style={{ animationDelay: `${(rank - 1) * 80}ms` }}>
      {/* Colored top bar */}
      <div className={`h-[3px] w-full bg-gradient-to-r ${barGrad}`} />

      {/* Header button */}
      <button onClick={() => setExpanded(!expanded)} className="w-full flex items-center gap-4 px-5 py-4 text-left">
        <ScoreRing score={score} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className={`text-[11px] px-2 py-0.5 rounded-full border font-medium ${tagCls}`}>{topic.post_type}</span>
            <span className="text-[11px] text-[var(--text-3)] font-medium">#{rank}</span>
          </div>
          <h3 className="text-[14px] font-semibold text-[var(--text-1)] leading-snug">{topic.cluster_label}</h3>
          {topic.strategy_reason && (
            <p className="text-[12px] text-[var(--text-2)] mt-0.5 leading-relaxed line-clamp-1">{topic.strategy_reason}</p>
          )}
        </div>
        {/* Mini dims preview when collapsed */}
        {!expanded && dims && (
          <div className="hidden sm:flex flex-col gap-1.5 w-36 shrink-0">
            {(["timeliness","heat","controversy","audience_fit"] as const).map(k => (
              <MiniBar key={k}
                label={k === "timeliness" ? "時效" : k === "heat" ? "熱度" : k === "controversy" ? "爭議" : "受眾"}
                value={dims[k]}
                dimKey={k}
              />
            ))}
          </div>
        )}
        <div className="shrink-0 text-[var(--text-3)] ml-2">
          {expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
        </div>
      </button>

      {/* Body */}
      {expanded && (
        <div className="px-5 pb-5 space-y-4 border-t border-[var(--border)] pt-4">
          {/* Dimensions row */}
          {dims && (
            <div className="bg-[var(--bg-2)] rounded-xl p-4 space-y-2.5">
              <p className="text-[10px] font-semibold text-[var(--text-3)] uppercase tracking-widest mb-3">評分維度</p>
              <MiniBar label="時效性" value={dims.timeliness} dimKey="timeliness" />
              <MiniBar label="話題熱度" value={dims.heat} dimKey="heat" />
              <MiniBar label="爭議性" value={dims.controversy} dimKey="controversy" />
              <MiniBar label="受眾匹配" value={dims.audience_fit} dimKey="audience_fit" />
            </div>
          )}

          {/* Summary */}
          {topic.merged_summary && (
            <p className="text-[13px] text-[var(--text-2)] leading-relaxed bg-[var(--bg-2)] rounded-xl p-4 border border-[var(--border)]">
              {topic.merged_summary}
            </p>
          )}

          {/* Hook */}
          {draft?.hook && (
            <div className="flex items-start gap-2.5 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
              <span className="text-amber-600 text-[11px] font-bold shrink-0 mt-0.5">🔥 HOOK</span>
              <p className="text-[13px] text-amber-800 leading-relaxed font-medium">{draft.hook}</p>
            </div>
          )}

          {/* Version tabs */}
          {draft && (draft.version_a || draft.version_b) && (
            <div>
              <div className="flex gap-1 mb-3 bg-[var(--bg-2)] rounded-xl p-1 w-fit border border-[var(--border)]">
                {(["a","b"] as const).map(v => (
                  <button key={v} onClick={() => setTab(v)}
                    className={`px-3 py-1.5 text-[12px] rounded-lg transition-colors font-medium ${
                      tab === v
                        ? "bg-[var(--accent)] text-white shadow-sm"
                        : "text-[var(--text-2)] hover:text-[var(--text-1)]"
                    }`}>
                    版本 {v.toUpperCase()} · {v === "a" ? draft.version_a?.style || "資訊型" : draft.version_b?.style || "故事型"}
                  </button>
                ))}
              </div>
              {activeContent && (
                <div className="bg-[var(--surface-2)] border border-[var(--border)] border-l-4 border-l-[var(--accent)] rounded-r-xl rounded-l-none pl-4 pr-4 py-4">
                  <div className="flex justify-end gap-2 mb-3">
                    <PublishButton text={activeContent} />
                    <CopyButton text={activeContent} />
                  </div>
                  <p className="text-[13px] text-[var(--text-1)] whitespace-pre-wrap leading-relaxed">{activeContent}</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Legacy markdown parser ───────────────────────────────────────────────────
function parseDraftsFromMd(md: string) {
  if (!md) return [];
  const sections = md.split(/---\s*\n/).filter(Boolean);
  const results: { label: string; va: string; vb: string }[] = [];
  for (const section of sections) {
    const labelMatch = section.match(/##\s*主題\s*\d+：(.+)/);
    const vaMatch = section.match(/###\s*版本\s*A[^）)]*[）)]\s*\n([\s\S]*?)(?=###|$)/);
    const vbMatch = section.match(/###\s*版本\s*B[^）)]*[）)]\s*\n([\s\S]*?)(?=###|$)/);
    if (labelMatch) {
      results.push({ label: labelMatch[1].trim(), va: vaMatch?.[1].trim() ?? "", vb: vbMatch?.[1].trim() ?? "" });
    }
  }
  return results;
}

// ─── Morning Briefing Card ────────────────────────────────────────────────────
function MorningBriefing() {
  const [b, setB] = useState<any>(null);
  useEffect(() => { fetchMorningBriefing().then(setB).catch(() => {}); }, []);
  if (!b) return null;

  const items = [
    b.pipeline_ran_today
      ? { icon: CheckCircle2, color: "#22c55e", label: `Pipeline 完成`, sub: b.pipeline_ran_at ? `${b.pipeline_ran_at} 執行` : "" }
      : { icon: Clock, color: "#a8a29e", label: "Pipeline 未執行", sub: `${b.next_pipeline_label}後自動執行` },
    b.drafts_today > 0
      ? { icon: CheckCircle2, color: "#22c55e", label: `${b.drafts_today} 篇草稿已生成`, sub: `${b.topics_today} 個主題` }
      : { icon: Clock, color: "#a8a29e", label: "今日草稿未生成", sub: "" },
    b.posts_today > 0
      ? { icon: CheckCircle2, color: "#7c5cbf", label: `今日發布 ${b.posts_today} 篇`, sub: "" }
      : { icon: Clock, color: "#a8a29e", label: "今日尚未發布", sub: "" },
    b.yesterday_avg_engagement != null
      ? { icon: TrendingUp, color: "#7c5cbf", label: `昨日互動率 ${b.yesterday_avg_engagement}%`, sub: b.yesterday_best ? b.yesterday_best.text : "" }
      : { icon: TrendingUp, color: "#a8a29e", label: "昨日無數據", sub: "" },
  ];

  return (
    <div className={`rounded-[14px] border px-5 py-3.5 mb-6 flex items-center gap-6 flex-wrap animate-fade-in
      ${b.has_error ? "border-red-200 bg-red-50" : "border-[var(--border)] bg-[var(--bg-2)]"}`}>
      {b.has_error && (
        <div className="flex items-center gap-2 text-red-600 text-[12px] font-600 w-full pb-2 border-b border-red-200">
          <AlertCircle size={13} />
          Pipeline 有錯誤：{b.error_summary}
        </div>
      )}
      {items.map((it, i) => {
        const Icon = it.icon;
        return (
          <div key={i} className="flex items-center gap-2 min-w-[160px]">
            <Icon size={13} style={{ color: it.color }} className="shrink-0" />
            <div>
              <div className="text-[12px] font-600 text-[var(--text-1)]">{it.label}</div>
              {it.sub && <div className="text-[11px] text-[var(--text-3)] truncate max-w-[160px]">{it.sub}</div>}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function TodayPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [trackerRunning, setTrackerRunning] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);

  const load = useCallback(async () => {
    try { const d = await fetchToday(); setData(d); }
    catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    fetchPendingApprovals().then((d: any[]) => setPendingCount(d.length)).catch(() => {});
  }, []);

  useEffect(() => {
    if (!pipelineRunning) return;
    const iv = setInterval(async () => {
      const s = await getPipelineStatus();
      if (!s.running) { setPipelineRunning(false); await load(); clearInterval(iv); }
    }, 3000);
    return () => clearInterval(iv);
  }, [pipelineRunning, load]);

  useEffect(() => {
    if (!trackerRunning) return;
    const iv = setInterval(async () => {
      const s = await getTrackerStatus();
      if (!s.running) { setTrackerRunning(false); clearInterval(iv); }
    }, 2000);
    return () => clearInterval(iv);
  }, [trackerRunning]);

  const today = new Date().toLocaleDateString("zh-TW", { year: "numeric", month: "long", day: "numeric" });
  const structured = data?.structured;
  const legacyDrafts = parseDraftsFromMd(data?.drafts || "");

  return (
    <div className="">
      <MorningBriefing />

      {/* ── System status chips ── */}
      {pendingCount > 0 && (
        <Link
          href="/office"
          className="inline-flex items-center gap-2 mb-5 px-4 py-2 rounded-full text-[12px] font-semibold transition-all hover:opacity-90 animate-fade-in"
          style={{ background: "rgba(217,119,6,0.1)", border: "1px solid rgba(217,119,6,0.28)", color: "#b45309" }}
        >
          <ShieldAlert size={13} />
          {pendingCount} 個待你審核 — 前往 AI Office →
        </Link>
      )}

      {/* Hero Header */}
      <div className="flex items-start justify-between mb-7">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-1)] tracking-tight">今日焦點</h1>
          <p className="text-[13px] text-[var(--text-2)] mt-0.5">{today}</p>
        </div>
        <div className="flex gap-2 flex-wrap justify-end">
          <button
            onClick={async () => { setTrackerRunning(true); await triggerTracker(); }}
            disabled={trackerRunning}
            className="flex items-center gap-2 px-4 py-2 text-[13px] rounded-full border border-[var(--border)] bg-[var(--surface)] text-[var(--text-2)] hover:text-[var(--text-1)] hover:border-[var(--border-2)] disabled:opacity-50 transition-all font-medium"
          >
            {trackerRunning ? <Loader2 size={13} className="animate-spin" /> : <BarChart2 size={13} />}
            {trackerRunning ? "抓取中..." : "抓 Threads 數據"}
          </button>
          <button
            onClick={async () => { setPipelineRunning(true); await triggerPipeline(); }}
            disabled={pipelineRunning}
            className="flex items-center gap-2 px-5 py-2 text-[13px] rounded-full bg-[var(--accent)] hover:opacity-90 text-white disabled:opacity-50 transition-all font-medium shadow-lg shadow-violet-500/20"
          >
            {pipelineRunning ? <Loader2 size={13} className="animate-spin" /> : <Zap size={13} />}
            {pipelineRunning ? "執行中..." : "一鍵全部跑"}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64 text-[var(--text-3)]">
          <Loader2 size={20} className="animate-spin mr-2" />載入中...
        </div>

      ) : !data?.has_data ? (
        <EmptyState
          onAction={async () => { setPipelineRunning(true); await triggerPipeline(); }}
          loading={pipelineRunning}
        />

      ) : structured ? (
        <div className="space-y-4">
          {structured.weekly_insight && (
            <div className="card-sm px-5 py-4 animate-fade-in">
              <p className="text-[11px] font-semibold text-[var(--text-3)] mb-1.5 uppercase tracking-widest">週度洞察</p>
              <p className="text-[13px] text-[var(--text-1)] leading-relaxed">{structured.weekly_insight}</p>
            </div>
          )}

          {structured.debate_summary && (
            <div className="card-sm px-5 py-4 animate-fade-in border-l-4 border-l-violet-300">
              <p className="text-[11px] font-semibold text-[var(--text-3)] mb-1.5 uppercase tracking-widest">辯論分歧點</p>
              <div className="flex items-start gap-2">
                <span className="text-violet-500 shrink-0 mt-0.5 text-[13px]">⚖️</span>
                <p className="text-[13px] text-[var(--text-1)] leading-relaxed">{structured.debate_summary}</p>
              </div>
            </div>
          )}

          <div>
            <div className="flex items-center gap-2 mb-3">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)]" />
              <p className="text-[12px] font-semibold text-[var(--text-2)] uppercase tracking-wider">
                Top {structured.top3?.length ?? 0} 主題 · {(structured.top3?.length ?? 0) * 2} 篇草稿
              </p>
            </div>
            <div className="space-y-3">
              {(structured.top3 ?? []).map((topic: Topic, i: number) => (
                <TopicCard key={i} topic={topic} rank={i + 1} />
              ))}
            </div>
          </div>

          {structured.all_topics?.length > 0 && (
            <div className="card-sm p-5 animate-fade-in">
              <p className="text-[11px] font-semibold text-[var(--text-3)] mb-4 uppercase tracking-widest">
                所有主題評分（{structured.all_topics.length} 則）
              </p>
              <div className="space-y-2.5">
                {structured.all_topics.map((t: any, i: number) => (
                  <div key={i} className="flex items-start gap-3">
                    <span className={`text-[12px] font-bold shrink-0 w-9 ${t.score >= 9 ? "text-[var(--green)]" : t.score >= 7 ? "text-[var(--accent)]" : "text-[var(--text-3)]"}`}>
                      {t.score}分
                    </span>
                    <div className="min-w-0">
                      <span className="text-[13px] text-[var(--text-1)] font-medium">{t.cluster_label}</span>
                      {t.reason && <span className="text-[12px] text-[var(--text-3)] ml-2">— {t.reason}</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

      ) : (
        <div className="space-y-6 animate-fade-in">
          {data.report && (
            <div className="card-sm p-5">
              <h2 className="text-[12px] font-semibold text-[var(--text-2)] mb-4 flex items-center gap-2 uppercase tracking-widest">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)]" />今日分析報告
              </h2>
              <div className="prose prose-sm max-w-none text-[var(--text-1)]">
                <ReactMarkdown>{data.report}</ReactMarkdown>
              </div>
            </div>
          )}
          {legacyDrafts.length > 0 && (
            <div>
              <h2 className="text-[12px] font-semibold text-[var(--text-2)] mb-3 flex items-center gap-2 uppercase tracking-widest">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--green)]" />貼文草稿（共 {legacyDrafts.length * 2} 篇）
              </h2>
              <div className="space-y-6">
                {legacyDrafts.map((draft, i) => (
                  <div key={i}>
                    <p className="text-[14px] font-semibold text-[var(--text-1)] mb-3">{i + 1}. {draft.label}</p>
                    <div className="grid grid-cols-1 gap-3">
                      {[{ v: "版本 A", s: "資訊型", c: draft.va }, { v: "版本 B", s: "故事型", c: draft.vb }].map(({ v, s, c }) => (
                        <div key={v} className="card-sm p-4 border-l-4 border-l-[var(--accent)]">
                          <div className="flex items-center justify-between mb-3">
                            <div>
                              <span className="text-[12px] font-bold text-[var(--accent)]">{v}</span>
                              <span className="text-[12px] text-[var(--text-3)] ml-2">{s}</span>
                            </div>
                            <div className="flex gap-2">
                              <PublishButton text={c} />
                              <CopyButton text={c} />
                            </div>
                          </div>
                          <p className="text-[13px] text-[var(--text-1)] whitespace-pre-wrap leading-relaxed">{c}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
