"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { fetchAgentEvents, fetchAgentStatus, fetchTodayStats, triggerDemoHandoff, triggerPipeline, getPipelineStatus, fetchArtifacts, fetchWorkflowRuns, fetchPendingApprovals, fetchApprovalPackage, fetchSkillRouting, callDeliberate, type DeliberationResult, BACKEND } from "@/lib/api";
import { AlertCircle, Brain, CheckCircle2, X, ShieldAlert, XCircle } from "lucide-react";
import ApprovalCard, { type ApprovalPackage } from "@/components/ApprovalCard";

type TaskMeta = {
  id: string;
  title: string;
  task_type: string;
  status: string;
  priority: string;
  started_at: string;
  updated_at: string;
  source_agent_id: string;
  target_agent_id: string;
  artifact_refs: string[];
  action_type: string;
  ref_id: string;
};

type AgentStat = {
  label: string;
  signal_count?: number;
  top3?: string[];
  drafts_count?: number;
  last_at?: string;
  latest_hook?: string;
  last_insights_date?: string;
  trend?: string;
  growth_rate?: number;
  pending_candidates?: number;
};

type TodayStats = {
  today: string;
  pipeline: {
    ran_today: boolean;
    ran_at: string | null;
    status: string | null;
    topics_found: number;
    top3: string[];
    drafts_count: number;
    models: Record<string, string>;
  };
  agents: Record<string, AgentStat>;
  threads: { last_sync: string | null; trend: string | null; growth_rate: number | null };
  flowlab: { pending_candidates: number };
  next_pipeline: { label: string; hours_until: number; mins_until: number };
};

type AgentInfo = {
  nickname: string;
  role: string;
  emoji: string;
  desc: string;
  status: "idle" | "working" | "blocked" | "handoff_pending" | "done" | "awaiting_human";
  task: string;
  updated_at: string;
  task_meta?: TaskMeta;
  last_task?: string;
  last_active_at?: string;
};

type AgentMap = Record<string, AgentInfo>;

type ActivityEvent = {
  id: string;
  time: string;
  agentId: string;
  agentName: string;
  agentEmoji: string;
  title: string;
  taskType: string;
  nextOwner: string;
};

const AGENT_ORDER = ["ori", "lala", "craft", "lumi", "sage", "pixel"];

const TASK_TYPE_LABELS: Record<string, string> = {
  research: "研究",
  strategy: "策略",
  content: "內容",
  engineering: "工程",
  analysis: "分析",
  design: "設計",
};

function formatElapsed(iso: string) {
  if (!iso) return "剛剛";
  const diffMs = Date.now() - new Date(iso).getTime();
  const diffMin = Math.max(0, Math.floor(diffMs / 60000));
  if (diffMin < 1) return "剛剛";
  if (diffMin < 60) return `${diffMin}m`;
  const hours = Math.floor(diffMin / 60);
  const minutes = diffMin % 60;
  return minutes > 0 ? `${hours}h ${minutes}m` : `${hours}h`;
}

function formatClock(iso: string) {
  if (!iso) return "--";
  return new Date(iso).toLocaleTimeString("zh-TW", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function taskLabel(agent: AgentInfo) {
  const taskType = agent.task_meta?.task_type || "";
  return TASK_TYPE_LABELS[taskType] || taskType || "一般";
}

function priorityTone(priority: string) {
  switch (priority) {
    case "high":
      return { bg: "rgba(220,38,38,0.06)", border: "rgba(220,38,38,0.18)", text: "#dc2626" };
    case "low":
      return { bg: "rgba(120,113,108,0.06)", border: "rgba(120,113,108,0.14)", text: "var(--text-3)" };
    default:
      return { bg: "rgba(124,92,191,0.08)", border: "rgba(124,92,191,0.18)", text: "var(--accent)" };
  }
}

function statusStyle(status: string) {
  switch (status) {
    case "working":
      return { bg: "rgba(124,92,191,0.06)", border: "rgba(124,92,191,0.28)", glow: "0 0 0 1px rgba(124,92,191,0.08)", badge: "rgba(124,92,191,0.1)", badgeText: "#7c5cbf", label: "工作中" };
    case "blocked":
      return { bg: "rgba(217,119,6,0.06)", border: "rgba(217,119,6,0.28)", glow: "none", badge: "rgba(217,119,6,0.1)", badgeText: "#b45309", label: "阻塞中" };
    case "handoff_pending":
      return { bg: "rgba(124,92,191,0.05)", border: "rgba(124,92,191,0.38)", glow: "none", badge: "rgba(124,92,191,0.12)", badgeText: "#7c5cbf", label: "待交接" };
    case "done":
      return { bg: "rgba(22,163,74,0.04)", border: "rgba(22,163,74,0.22)", glow: "none", badge: "rgba(22,163,74,0.1)", badgeText: "#16a34a", label: "完成" };
    case "awaiting_human":
      return { bg: "rgba(217,119,6,0.06)", border: "rgba(217,119,6,0.32)", glow: "none", badge: "rgba(217,119,6,0.12)", badgeText: "#b45309", label: "等待你決策" };
    default:
      return { bg: "var(--surface)", border: "var(--border)", glow: "none", badge: "rgba(22,163,74,0.08)", badgeText: "#16a34a", label: "待命中" };
  }
}

function artifactLink(ref: string) {
  if (ref.includes("daily_reports") || ref.includes("drafts")) return "/reports";
  if (ref.includes("weekly")) return "/reports";
  return null;
}

function AgentCard({
  id,
  agent,
  agentMap,
  stat,
}: {
  id: string;
  agent: AgentInfo;
  agentMap: AgentMap;
  stat?: AgentStat;
}) {
  const style = statusStyle(agent.status);
  const isActive = ["working", "blocked", "handoff_pending", "awaiting_human"].includes(agent.status);
  const currentTask = agent.task_meta;
  const nextOwner = currentTask?.target_agent_id
    ? agentMap[currentTask.target_agent_id]?.nickname || currentTask.target_agent_id
    : "";
  const sourceOwner = currentTask?.source_agent_id
    ? agentMap[currentTask.source_agent_id]?.nickname || currentTask.source_agent_id
    : "";
  const tone = priorityTone(currentTask?.priority || "normal");
  const [imageFailed, setImageFailed] = useState(false);
  const artifacts = currentTask?.artifact_refs || [];

  return (
    <div
      className="relative rounded-3xl p-4 overflow-hidden transition-all duration-300"
      style={{ background: style.bg, border: `1px solid ${style.border}`, boxShadow: style.glow }}
    >
      {/* scanline — accent purple for light bg */}
      {agent.status === "working" && (
        <div className="absolute inset-0 pointer-events-none" style={{
          background: "linear-gradient(115deg, transparent 32%, rgba(124,92,191,0.05) 50%, transparent 68%)",
          animation: "scanline 2.8s linear infinite",
        }} />
      )}
      {agent.status === "handoff_pending" && (
        <div className="absolute inset-0 pointer-events-none" style={{
          background: "linear-gradient(115deg, transparent 32%, rgba(124,92,191,0.04) 50%, transparent 68%)",
          animation: "scanline 1.6s linear infinite",
        }} />
      )}
      {agent.status === "awaiting_human" && (
        <div className="absolute inset-0 pointer-events-none" style={{
          background: "linear-gradient(115deg, transparent 32%, rgba(217,119,6,0.04) 50%, transparent 68%)",
          animation: "scanline 2.2s linear infinite",
        }} />
      )}

      <div className="relative">
        {/* ── 頭像 + 名字 + 狀態 Badge（一排）── */}
        <div className="flex items-center gap-3">
          <div
            className="h-12 w-12 rounded-2xl flex items-center justify-center text-sm font-bold tracking-wider shrink-0 overflow-hidden"
            style={{ background: isActive ? style.badge : "var(--bg-2)", color: isActive ? style.badgeText : "var(--text-2)" }}
          >
            {!imageFailed ? (
              <img src={`/agents/${id}.png`} alt={agent.nickname} className="h-full w-full object-cover" onError={() => setImageFailed(true)} />
            ) : <span>{agent.emoji}</span>}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-[15px] font-semibold text-[var(--text-1)]">{agent.nickname}</div>
            <div className="text-[11px] text-[var(--text-3)]">{agent.role}</div>
          </div>
          <div
            className="rounded-full px-2.5 py-0.5 text-[10px] uppercase tracking-[0.16em] shrink-0"
            style={{ background: style.badge, color: style.badgeText }}
          >
            {style.label}
          </div>
        </div>

        {/* ── 描述 —— 全寬 ── */}
        <p className="mt-2 text-[11px] leading-relaxed text-[var(--text-2)]">
          {agent.desc}
        </p>

        {/* ── 目前任務 / 上次任務 —— 全寬 ── */}
        <div className="mt-3 rounded-2xl p-3" style={{ background: "var(--bg-2)", border: "1px solid var(--border)" }}>
          {agent.status === "idle" ? (
            <>
              <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--text-3)] mb-2">上次任務</div>
              {agent.last_task ? (
                <>
                  <div className="text-[13px] font-semibold text-[var(--text-1)]">{agent.last_task}</div>
                  <div className="mt-1.5 text-[11px] text-[var(--text-3)]">
                    完成於 {formatElapsed(agent.last_active_at || agent.updated_at)} 前
                  </div>
                </>
              ) : (
                <div className="text-[12px] text-[var(--text-3)]">今日尚未執行任務</div>
              )}
            </>
          ) : (
            <>
              <div className="flex items-center justify-between gap-3 mb-2">
                <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--text-3)]">目前任務</div>
                <div
                  className="rounded-full px-2 py-0.5 text-[10px] uppercase tracking-[0.12em]"
                  style={{ background: tone.bg, border: `1px solid ${tone.border}`, color: tone.text }}
                >
                  {taskLabel(agent)}
                </div>
              </div>

              <div className="text-[13px] font-semibold text-[var(--text-1)]">
                {currentTask?.title || agent.task || "處理中"}
              </div>

              <div className="mt-2 grid grid-cols-3 gap-1 text-[11px]">
                {[
                  { label: "來源", value: sourceOwner || "直接指派" },
                  { label: "下一棒", value: nextOwner || "尚未指定" },
                  { label: "已進行", value: formatElapsed(currentTask?.started_at || agent.updated_at) },
                ].map(({ label, value }) => (
                  <div key={label} className="rounded-xl px-2.5 py-1.5" style={{ background: "var(--surface)" }}>
                    <div className="text-[var(--text-3)]">{label}</div>
                    <div className="mt-0.5 text-[var(--text-1)] font-medium truncate">{value}</div>
                  </div>
                ))}
              </div>
            </>
          )}

          {artifacts.length > 0 && (
            <div className="mt-1 rounded-xl px-2.5 py-1.5" style={{ background: "var(--surface)" }}>
              <div className="text-[10px] text-[var(--text-3)] mb-1">產出</div>
              <div className="flex flex-wrap gap-x-3 gap-y-0.5 text-[11px]">
                {artifacts.map((ref, i) => {
                  const href = artifactLink(ref);
                  const name = (ref.split("/").pop() || ref).replace(/\.[^.]+$/, "");
                  return href ? (
                    <a key={i} href={href} className="truncate max-w-full font-medium" style={{ color: "var(--accent)" }} title={ref}>{name}</a>
                  ) : (
                    <span key={i} className="truncate max-w-full text-[var(--text-1)]" title={ref}>{name}</span>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* ── awaiting_human 操作按鈕 ── */}
        {agent.status === "awaiting_human" && currentTask && (
          <AwaitingHumanActions
            actionType={currentTask.action_type || ""}
            refId={currentTask.ref_id || ""}
          />
        )}

        {/* ── 今日數據 ── */}
        {stat && (
          <div className="mt-2 rounded-2xl p-3" style={{ background: "var(--bg-2)", border: "1px solid var(--border)" }}>
            <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--text-3)] mb-2">今日</div>
            <div className="space-y-1">
              {stat.signal_count !== undefined && (
                <div className="flex justify-between text-[11px]">
                  <span className="text-[var(--text-2)]">信號數</span>
                  <span className="text-[var(--text-1)] font-semibold">{stat.signal_count}</span>
                </div>
              )}
              {stat.top3 && stat.top3.length > 0 && (
                <div className="text-[11px]">
                  <span className="text-[var(--text-2)]">主題 Top 3</span>
                  <div className="mt-1 space-y-0.5">
                    {stat.top3.slice(0, 3).map((t, i) => (
                      <div key={i} className="truncate text-[var(--text-1)]" title={t}>{i + 1}. {t}</div>
                    ))}
                  </div>
                </div>
              )}
              {stat.drafts_count !== undefined && (
                <div className="flex justify-between text-[11px]">
                  <span className="text-[var(--text-2)]">草稿數</span>
                  <span className="text-[var(--text-1)] font-semibold">{stat.drafts_count}</span>
                </div>
              )}
              {stat.latest_hook && (
                <div className="text-[11px]">
                  <span className="text-[var(--text-2)]">最新 Hook</span>
                  <div className="mt-0.5 text-[var(--text-1)] line-clamp-2">{stat.latest_hook}</div>
                </div>
              )}
              {stat.trend && (
                <div className="flex justify-between text-[11px]">
                  <span className="text-[var(--text-2)]">趨勢</span>
                  <span className="text-[var(--text-1)] font-semibold">
                    {stat.trend}{stat.growth_rate !== undefined ? ` ${stat.growth_rate > 0 ? "+" : ""}${stat.growth_rate}%` : ""}
                  </span>
                </div>
              )}
              {stat.pending_candidates !== undefined && (
                <div className="flex justify-between text-[11px]">
                  <span className="text-[var(--text-2)]">待審選品</span>
                  <span className="text-[var(--text-1)] font-semibold">{stat.pending_candidates}</span>
                </div>
              )}
              {stat.label && (
                <div className="text-[10px] text-[var(--text-3)] mt-1">{stat.label}</div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function AwaitingHumanActions({ actionType, refId }: { actionType: string; refId: string }) {
  const patchCandidate = async (status: "approved" | "rejected") => {
    if (!refId) return;
    await fetch(`${BACKEND}/api/ecommerce/selection/candidates/${refId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
  };

  if (actionType === "approve_purchase") {
    return (
      <div className="mt-3 flex gap-2">
        <button
          onClick={() => patchCandidate("approved")}
          className="flex-1 rounded-xl py-2 text-[11px] font-semibold tracking-[0.1em] transition-all"
          style={{ background: "rgba(22,163,74,0.1)", border: "1px solid rgba(22,163,74,0.24)", color: "#16a34a" }}
        >
          核准進貨
        </button>
        <button
          onClick={() => patchCandidate("rejected")}
          className="flex-1 rounded-xl py-2 text-[11px] font-semibold tracking-[0.1em] transition-all"
          style={{ background: "rgba(220,38,38,0.08)", border: "1px solid rgba(220,38,38,0.18)", color: "#dc2626" }}
        >
          不進貨
        </button>
      </div>
    );
  }

  if (actionType === "select_draft") {
    return (
      <div className="mt-3">
        <a
          href="/"
          className="block w-full rounded-xl py-2 text-center text-[11px] font-semibold tracking-[0.1em]"
          style={{ background: "rgba(124,92,191,0.1)", border: "1px solid rgba(124,92,191,0.22)", color: "var(--accent)" }}
        >
          查看草稿 →
        </a>
      </div>
    );
  }

  if (actionType === "confirm_analysis") {
    return (
      <div className="mt-3">
        <a
          href="/reports"
          className="block w-full rounded-xl py-2 text-center text-[11px] font-semibold tracking-[0.1em]"
          style={{ background: "rgba(124,92,191,0.1)", border: "1px solid rgba(124,92,191,0.22)", color: "var(--accent)" }}
        >
          查看分析
        </a>
      </div>
    );
  }

  return null;
}

function SystemHealthPanel({ stats }: { stats: TodayStats | null }) {
  const pipeline = stats?.pipeline;
  const threads = stats?.threads;
  const flowlab = stats?.flowlab;
  const next = stats?.next_pipeline;

  const pipelineOk = pipeline?.ran_today && pipeline.status === "success";
  const pipelineFail = pipeline?.ran_today && pipeline.status !== "success";

  const rows = [
    {
      label: "每日 Pipeline",
      value: pipeline
        ? pipeline.ran_today
          ? `${pipelineOk ? "完成" : "失敗"} ${pipeline.ran_at ?? ""}`
          : "今日未執行"
        : "—",
      color: pipelineOk ? "var(--green)" : pipelineFail ? "var(--red)" : "var(--text-3)",
    },
    {
      label: "草稿",
      value: pipeline ? `${pipeline.drafts_count} 份` : "—",
      color: "var(--text-1)",
    },
    {
      label: "下次執行",
      value: next ? next.label : "—",
      color: "var(--accent)",
    },
    {
      label: "Threads",
      value: threads?.last_sync ? threads.last_sync : "尚未同步",
      color: threads?.last_sync ? "var(--green)" : "var(--text-3)",
    },
    {
      label: "Flow Lab",
      value: flowlab ? `${flowlab.pending_candidates} 待審` : "—",
      color: flowlab && flowlab.pending_candidates > 0 ? "var(--amber)" : "var(--text-3)",
    },
  ];

  return (
    <div className="card p-5">
      <div className="text-[11px] uppercase tracking-[0.2em] text-[var(--text-3)] mb-4">系統健康</div>
      <div className="space-y-1.5">
        {rows.map(({ label, value, color }) => (
          <div key={label} className="flex items-center justify-between rounded-xl px-3 py-2"
            style={{ background: "var(--bg-2)" }}>
            <span className="text-[11px] text-[var(--text-2)]">{label}</span>
            <span className="text-[11px] font-semibold" style={{ color }}>{value}</span>
          </div>
        ))}
      </div>
      {pipeline?.top3 && pipeline.top3.length > 0 && (
        <div className="mt-3">
          <div className="text-[10px] uppercase tracking-[0.16em] text-[var(--text-3)] mb-1.5">今日主題</div>
          <div className="space-y-1">
            {pipeline.top3.map((t, i) => (
              <div key={i} className="text-[11px] truncate text-[var(--text-1)]" title={t}>{i + 1}. {t}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function OfficePage() {
  const [agents, setAgents] = useState<AgentMap>({});
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState<ActivityEvent[]>([]);
  const [filterAgent, setFilterAgent] = useState<string | null>(null);
  const filterAgentRef = useRef<string | null>(null);
  const [filterTaskType, setFilterTaskType] = useState<string | null>(null);
  const [demoRunning, setDemoRunning] = useState(false);
  const [demoError, setDemoError] = useState("");
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [pipelineError, setPipelineError] = useState<{ msg: string; at: string } | null>(null);
  const [errorDismissed, setErrorDismissed] = useState(false);
  const [todayStats, setTodayStats] = useState<TodayStats | null>(null);
  const [systemLogs, setSystemLogs] = useState<string[]>([]);
  const [artifacts, setArtifacts] = useState<any[]>([]);
  const [workflowRuns, setWorkflowRuns] = useState<any[]>([]);
  const [approvalPackages, setApprovalPackages] = useState<ApprovalPackage[]>([]);
  const [skillRoutes, setSkillRoutes] = useState<any[]>([]);
  const listRef = useRef<HTMLDivElement>(null);
  const [deliberateQ, setDeliberateQ] = useState("");
  const [deliberating, setDeliberating] = useState(false);
  const [deliberationResult, setDeliberationResult] = useState<DeliberationResult | null>(null);

  useEffect(() => {
    filterAgentRef.current = filterAgent;
  }, [filterAgent]);

  useEffect(() => {
    fetchAgentStatus().then(setAgents).catch(() => {});
    fetchTodayStats().then(setTodayStats).catch(() => {});
    fetchArtifacts(8).then(d => setArtifacts(d.artifacts || [])).catch(() => {});
    fetchWorkflowRuns(8).then(d => setWorkflowRuns(d.runs || [])).catch(() => {});
    fetchSkillRouting().then(d => setSkillRoutes(d?.routes || [])).catch(() => {});

    // Load CEO approval packages
    const loadApprovals = async () => {
      try {
        const pending = await fetchPendingApprovals();
        const pkgs = await Promise.all(
          (pending as any[]).slice(0, 5).map((a: any) =>
            fetchApprovalPackage(a.id).catch(() => null)
          )
        );
        setApprovalPackages(pkgs.filter(Boolean) as ApprovalPackage[]);
      } catch { /* silent */ }
    };
    loadApprovals();
    fetch(`${BACKEND}/api/system/logs?lines=30`)
      .then(r => r.json()).then(d => setSystemLogs(d.logs || [])).catch(() => {});
    // 檢查 pipeline 是否有未處理的失敗
    getPipelineStatus().then(s => {
      if (s.last_error) setPipelineError({ msg: s.last_error, at: s.last_error_at });
    }).catch(() => {});
    const t = setInterval(() => {
      fetchTodayStats().then(setTodayStats).catch(() => {});
      getPipelineStatus().then(s => {
        if (s.last_error) setPipelineError({ msg: s.last_error, at: s.last_error_at });
        else setPipelineError(null);
      }).catch(() => {});
    }, 60_000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    const loadEvents = async () => {
      try {
        const response = await fetchAgentEvents(40, filterAgent ?? undefined);
        const STATUS_LABELS: Record<string, string> = {
          working: "開始工作", idle: "回到待命", blocked: "進入阻塞",
          done: "任務完成", handoff_pending: "等待交接", awaiting_human: "等待決策",
        };
        const items: ActivityEvent[] = (response.events || []).map((event: any, index: number) => ({
          id: `${event.agent_id}-${event.task_meta?.id || index}-${event.recorded_at}`,
          time: formatClock(event.recorded_at),
          agentId: event.agent_id,
          agentName: event.agent_id.charAt(0).toUpperCase() + event.agent_id.slice(1),
          agentEmoji: event.agent_id.slice(0, 2).toUpperCase(),
          title: event.task_meta?.title || event.task || STATUS_LABELS[event.status] || "狀態更新",
          taskType: TASK_TYPE_LABELS[event.task_meta?.task_type || ""] || event.task_meta?.task_type || "一般",
          nextOwner: event.task_meta?.target_agent_id || "",
        }));
        setEvents(items);
      } catch {
        // silent
      }
    };
    loadEvents();
  }, [filterAgent]);

  useEffect(() => {
    const es = new EventSource(`${BACKEND}/api/agents/stream`);
    es.onopen = () => setConnected(true);
    es.onerror = () => setConnected(false);
    es.onmessage = (event) => {
      try {
        const payload: AgentMap = JSON.parse(event.data);
        setAgents((prev) => {
          const next = { ...prev, ...payload };
          const newEvents: ActivityEvent[] = [];

          for (const [agentId, info] of Object.entries(payload)) {
            const previous = prev[agentId];
            const nextTitle = info.task_meta?.title || info.task || "";
            const previousTitle = previous?.task_meta?.title || previous?.task || "";
            const becameActive = info.status === "working" && previous?.status !== "working";
            const taskChanged = Boolean(nextTitle) && nextTitle !== previousTitle;

            if (becameActive || taskChanged) {
              newEvents.push({
                id: `${agentId}-${info.task_meta?.id || info.updated_at}`,
                time: formatClock(info.updated_at),
                agentId,
                agentName: info.nickname,
                agentEmoji: info.emoji,
                title: nextTitle || "開始工作",
                taskType: taskLabel(info),
                nextOwner: info.task_meta?.target_agent_id
                  ? next[info.task_meta.target_agent_id]?.nickname || info.task_meta.target_agent_id
                  : "",
              });
            }
          }

          const activeFilter = filterAgentRef.current;
          const filtered = activeFilter ? newEvents.filter((e) => e.agentId === activeFilter) : newEvents;
          if (filtered.length > 0) {
            setEvents((current) => [...filtered, ...current].slice(0, 80));
            setTimeout(() => listRef.current?.scrollTo({ top: 0, behavior: "smooth" }), 60);
          }

          return next;
        });
      } catch {
        setConnected(false);
      }
    };

    return () => es.close();
  }, []);

  const handleDeliberate = async () => {
    const q = deliberateQ.trim();
    if (!q || deliberating) return;
    setDeliberating(true);
    setDeliberationResult(null);
    try {
      const result = await callDeliberate(q);
      setDeliberationResult(result);
    } catch (e: unknown) {
      setDeliberationResult({ error: e instanceof Error ? e.message : String(e) });
    } finally {
      setDeliberating(false);
    }
  };

  const orderedAgents = useMemo(
    () => AGENT_ORDER.map((id) => [id, agents[id]] as const).filter(([, value]) => Boolean(value)),
    [agents],
  );

  const activeAgents = orderedAgents.filter(([, agent]) => ["working", "awaiting_human"].includes(agent.status));

  return (
    <>
      <style>{`
        @keyframes scanline {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(220%); }
        }
      `}</style>

      <div className="min-h-screen px-8 py-8" style={{ background: "var(--bg)" }}>
        <div className="mx-auto max-w-[1320px]">

          {/* ── Pipeline 失敗警告橫幅 ── */}
          {pipelineError && !errorDismissed && (
            <div className="mb-6 flex items-start gap-3 rounded-[14px] border border-red-200 bg-red-50 px-5 py-4">
              <AlertCircle size={18} className="shrink-0 text-red-500 mt-0.5" />
              <div className="flex-1 min-w-0">
                <div className="text-[13px] font-700 text-red-700">Pipeline 執行失敗</div>
                <div className="text-[12px] text-red-500 mt-0.5 break-all">{pipelineError.msg}</div>
                {pipelineError.at && (
                  <div className="text-[11px] text-red-400 mt-1">
                    失敗時間：{new Date(pipelineError.at).toLocaleString("zh-TW")}
                  </div>
                )}
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={async () => {
                    if (!confirm("確定要重新執行 Pipeline？")) return;
                    setPipelineRunning(true);
                    setErrorDismissed(true);
                    try {
                      await triggerPipeline();
                      let waited = 0;
                      const poll = setInterval(async () => {
                        waited += 3;
                        try {
                          const { running: r } = await getPipelineStatus();
                          if (!r || waited >= 180) {
                            clearInterval(poll);
                            setPipelineRunning(false);
                            fetchTodayStats().then(setTodayStats).catch(() => {});
                          }
                        } catch { clearInterval(poll); setPipelineRunning(false); }
                      }, 3000);
                    } catch { setPipelineRunning(false); }
                  }}
                  disabled={pipelineRunning}
                  className="px-3 py-1.5 rounded-[8px] text-[12px] font-600 bg-red-500 text-white hover:bg-red-600 disabled:opacity-50"
                >
                  {pipelineRunning ? "重試中..." : "一鍵重試"}
                </button>
                <button onClick={() => setErrorDismissed(true)} className="p-1 text-red-400 hover:text-red-600">
                  <X size={15} />
                </button>
              </div>
            </div>
          )}

          {/* ── Header ── */}
          <div className="mb-8 flex items-start justify-between gap-6">
            <div>
              <div className="text-[11px] uppercase tracking-[0.32em] font-medium" style={{ color: "var(--accent)" }}>
                AntiClaude AI Office
              </div>
              <h1 className="mt-2 text-[32px] font-black tracking-tight text-[var(--text-1)]">任務總控</h1>
              <p className="mt-2 max-w-[680px] text-[14px] leading-relaxed text-[var(--text-2)]">
                這裡是 AI 團隊的即時辦公室。你應該能一眼看出現在誰在處理工作、
                任務內容是什麼，以及下一棒會交給誰。
              </p>
            </div>

            <div className="flex items-center gap-2 mt-1">
              <button
                onClick={async () => {
                  if (!confirm("確定要立即觸發今日 Pipeline？")) return;
                  setPipelineRunning(true);
                  try {
                    await triggerPipeline();
                    let waited = 0;
                    const poll = setInterval(async () => {
                      waited += 3;
                      try {
                        const { running: r } = await getPipelineStatus();
                        if (!r || waited >= 180) {
                          clearInterval(poll);
                          setPipelineRunning(false);
                          fetchTodayStats().then(setTodayStats).catch(() => {});
                        }
                      } catch { clearInterval(poll); setPipelineRunning(false); }
                    }, 3000);
                  } catch {
                    setPipelineRunning(false);
                  }
                }}
                disabled={pipelineRunning}
                className="rounded-full px-4 py-2 text-[12px] font-semibold tracking-[0.1em] transition-all disabled:opacity-50"
                style={{
                  background: pipelineRunning ? "rgba(124,92,191,0.1)" : "var(--surface)",
                  border: `1px solid ${pipelineRunning ? "rgba(124,92,191,0.3)" : "var(--border-2)"}`,
                  color: pipelineRunning ? "var(--accent)" : "var(--text-1)",
                }}
              >
                {pipelineRunning ? "Pipeline 執行中..." : "觸發 Pipeline"}
              </button>
              <button
                onClick={async () => {
                  if (!confirm("啟動深度分析模式：評分後暫停，等你確認主題再繼續。")) return;
                  setPipelineRunning(true);
                  try {
                    await fetch(`${BACKEND}/api/pipeline/graph-run?approval_gate=true&deliberation=true`, { method: "POST" });
                    setTimeout(() => fetchWorkflowRuns(8).then(d => setWorkflowRuns(d.runs || [])).catch(() => {}), 2000);
                  } finally {
                    setPipelineRunning(false);
                  }
                }}
                disabled={pipelineRunning}
                className="rounded-full px-4 py-2 text-[12px] font-semibold tracking-[0.1em] transition-all disabled:opacity-50"
                style={{
                  background: "rgba(124,92,191,0.08)",
                  border: "1px solid rgba(124,92,191,0.22)",
                  color: "var(--accent)",
                }}
              >
                深度分析
              </button>
              <button
                onClick={async () => {
                  try {
                    setDemoError("");
                    setDemoRunning(true);
                    await triggerDemoHandoff();
                  } catch {
                    setDemoError("示範交接失敗，請確認 API 與前端服務都已啟動。");
                  } finally {
                    setDemoRunning(false);
                  }
                }}
                className="rounded-full px-4 py-2 text-[12px] font-semibold tracking-[0.1em] transition-all"
                style={{
                  background: "var(--surface)",
                  border: "1px solid var(--border-2)",
                  color: "var(--text-1)",
                }}
              >
                {demoRunning ? "交接中" : "示範交接"}
              </button>
              <div
                className="rounded-full px-4 py-2 text-[12px] font-semibold tracking-[0.14em]"
                style={{
                  background: "rgba(124,92,191,0.08)",
                  border: "1px solid rgba(124,92,191,0.2)",
                  color: "var(--accent)",
                }}
              >
                啟動中 {activeAgents.length} 位
              </div>
              <div
                className="rounded-full px-4 py-2 text-[12px] font-semibold tracking-[0.14em]"
                style={{
                  background: connected ? "rgba(22,163,74,0.08)" : "var(--bg-2)",
                  border: `1px solid ${connected ? "rgba(22,163,74,0.22)" : "var(--border)"}`,
                  color: connected ? "var(--green)" : "var(--text-3)",
                }}
              >
                {connected ? "已連線" : "未連線"}
              </div>
            </div>
          </div>

          {demoError && (
            <div
              className="mb-5 rounded-2xl px-4 py-3 text-[13px]"
              style={{ background: "rgba(220,38,38,0.06)", border: "1px solid rgba(220,38,38,0.16)", color: "var(--red)" }}
            >
              {demoError}
            </div>
          )}

          {/* ── CEO 審核中心 ── */}
          {approvalPackages.length > 0 && (
            <div className="mb-8 animate-slide-up">
              <div className="flex items-center gap-2.5 mb-3">
                <ShieldAlert size={15} className="text-amber-500" />
                <span className="text-[11px] uppercase tracking-[0.2em] font-semibold text-amber-600">
                  需要你的決策 · {approvalPackages.length} 個待審核
                </span>
              </div>
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
                {approvalPackages.map((pkg) => (
                  <ApprovalCard
                    key={pkg.approval_id}
                    pkg={pkg}
                    onDecided={(id) =>
                      setApprovalPackages((prev) => prev.filter((p) => p.approval_id !== id))
                    }
                  />
                ))}
              </div>
            </div>
          )}

          {/* ── CEO 深度分析面板 ── */}
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-3">
              <Brain size={15} className="text-[var(--accent)]" />
              <span className="text-[11px] uppercase tracking-[0.2em] font-semibold text-[var(--accent)]">
                CEO 深度分析 · Ori + Lala + Sage 協作
              </span>
            </div>
            <div className="card p-5">
              <div className="flex gap-2 mb-4">
                <input
                  value={deliberateQ}
                  onChange={(e) => setDeliberateQ(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter" && !deliberating) void handleDeliberate(); }}
                  placeholder="輸入要深度分析的問題，例如：這週應該發什麼主題？"
                  disabled={deliberating}
                  className="flex-1 rounded-xl border border-[var(--border)] bg-[var(--bg-2)] px-4 py-2 text-[13px] text-[var(--text-1)] placeholder:text-[var(--text-3)] focus:border-[var(--accent)] focus:outline-none disabled:opacity-60"
                />
                <button
                  onClick={() => void handleDeliberate()}
                  disabled={deliberating || !deliberateQ.trim()}
                  className="rounded-xl px-5 py-2 text-[13px] font-semibold text-white disabled:opacity-40 transition-all"
                  style={{ background: deliberating ? "rgba(124,92,191,0.6)" : "var(--accent)" }}
                >
                  {deliberating ? "分析中..." : "分析"}
                </button>
                {deliberationResult && (
                  <button
                    onClick={() => setDeliberationResult(null)}
                    className="p-2 rounded-xl text-[var(--text-3)] hover:text-[var(--text-1)] hover:bg-[var(--bg-2)] transition-colors"
                  >
                    <X size={14} />
                  </button>
                )}
              </div>

              {deliberationResult && !deliberationResult.error && (
                <div className="space-y-4">
                  {/* Per-agent inputs */}
                  {deliberationResult.agent_inputs && deliberationResult.agent_inputs.length > 0 && (
                    <div>
                      <div className="text-[10px] uppercase tracking-[0.18em] text-[var(--text-3)] mb-2">各顧問輸入</div>
                      <div className="grid grid-cols-3 gap-2">
                        {deliberationResult.agent_inputs.map((inp) => (
                          <div key={inp.agent} className="rounded-xl px-3 py-2.5"
                            style={{ background: inp.success ? "rgba(124,92,191,0.06)" : "rgba(220,38,38,0.05)",
                                     border: `1px solid ${inp.success ? "rgba(124,92,191,0.18)" : "rgba(220,38,38,0.14)"}` }}>
                            <div className="flex items-center gap-1.5 mb-1">
                              {inp.success
                                ? <CheckCircle2 size={10} className="shrink-0 text-green-500" />
                                : <XCircle size={10} className="shrink-0 text-red-400" />}
                              <span className="text-[11px] font-semibold text-[var(--text-1)] uppercase">{inp.agent}</span>
                              <span className="ml-auto text-[9px] text-[var(--text-3)]">{inp.task_type.replace(/_/g," ")}</span>
                            </div>
                            <p className="text-[10px] text-[var(--text-2)] line-clamp-3 leading-relaxed">{inp.summary || "—"}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Synthesis */}
                  <div className="rounded-2xl p-4"
                    style={{ background: "rgba(124,92,191,0.05)", border: "1px solid rgba(124,92,191,0.16)" }}>
                    {deliberationResult.consensus && (
                      <div className="mb-3">
                        <div className="text-[10px] uppercase tracking-[0.16em] text-[var(--accent)] mb-1">共識</div>
                        <p className="text-[13px] text-[var(--text-1)] leading-relaxed">{deliberationResult.consensus}</p>
                      </div>
                    )}
                    {deliberationResult.key_insights && deliberationResult.key_insights.length > 0 && (
                      <div className="mb-3">
                        <div className="text-[10px] uppercase tracking-[0.16em] text-[var(--accent)] mb-1">關鍵洞察</div>
                        <ul className="space-y-1">
                          {deliberationResult.key_insights.map((ins, i) => (
                            <li key={i} className="text-[12px] text-[var(--text-1)] flex gap-2">
                              <span className="text-[var(--accent)] shrink-0">•</span>{ins}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {deliberationResult.recommendation && (
                      <div className="mb-3">
                        <div className="text-[10px] uppercase tracking-[0.16em] text-[var(--accent)] mb-1">建議行動</div>
                        <p className="text-[13px] font-semibold text-[var(--text-1)] leading-relaxed">{deliberationResult.recommendation}</p>
                      </div>
                    )}
                    {deliberationResult.next_steps && deliberationResult.next_steps.length > 0 && (
                      <div className="mb-3">
                        <div className="text-[10px] uppercase tracking-[0.16em] text-[var(--accent)] mb-1">後續步驟</div>
                        <ol className="space-y-1">
                          {deliberationResult.next_steps.map((s, i) => (
                            <li key={i} className="text-[12px] text-[var(--text-1)] flex gap-2">
                              <span className="text-[var(--text-3)] shrink-0">{i+1}.</span>{s}
                            </li>
                          ))}
                        </ol>
                      </div>
                    )}
                    {deliberationResult.confidence && (
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-[10px] text-[var(--text-3)]">信心度</span>
                        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                          deliberationResult.confidence === "high" ? "bg-green-100 text-green-700" :
                          deliberationResult.confidence === "low" ? "bg-red-100 text-red-600" :
                          "bg-amber-100 text-amber-700"
                        }`}>
                          {deliberationResult.confidence === "high" ? "高" :
                           deliberationResult.confidence === "low" ? "低" : "中"}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {deliberationResult?.error && (
                <div className="rounded-xl px-4 py-3 text-[13px]"
                  style={{ background: "rgba(220,38,38,0.06)", color: "var(--red)" }}>
                  深度分析失敗：{deliberationResult.error}
                </div>
              )}
            </div>
          </div>

          {/* ── Main Grid ── */}
          <div className="grid grid-cols-[minmax(0,1fr)_340px] gap-6 items-start">

            {/* Agent Cards */}
            <div className="grid grid-cols-2 gap-4 xl:grid-cols-3 items-start">
              {orderedAgents.length === 0
                ? AGENT_ORDER.map((id) => (
                    <div
                      key={id}
                      className="h-[240px] rounded-3xl animate-pulse"
                      style={{ background: "var(--bg-2)", border: "1px solid var(--border)" }}
                    />
                  ))
                : orderedAgents.map(([id, agent]) => (
                    <AgentCard key={id} id={id} agent={agent} agentMap={agents} stat={todayStats?.agents[id]} />
                  ))}
            </div>

            {/* Sidebar */}
            <div className="flex flex-col gap-4">

              {/* 系統健康 */}
              <SystemHealthPanel stats={todayStats} />

              {/* 系統日誌 */}
              {systemLogs.length > 0 && (
                <div className="card p-5">
                  <div className="text-[11px] uppercase tracking-[0.2em] text-[var(--text-3)] mb-3">今日警告 / 錯誤</div>
                  <div className="space-y-1 max-h-40 overflow-y-auto">
                    {systemLogs.map((line, i) => {
                      const isError = line.includes("| ERROR");
                      return (
                        <div key={i} className="text-[10px] font-mono leading-relaxed px-2 py-1 rounded-lg"
                          style={{ background: isError ? "rgba(220,38,38,0.06)" : "rgba(217,119,6,0.05)",
                                   color: isError ? "var(--red)" : "#b45309" }}>
                          {line.split("|").slice(2).join("|").trim()}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* 進行中 */}
              <div className="card p-5">
                <div className="text-[11px] uppercase tracking-[0.2em] text-[var(--text-3)] mb-4">進行中</div>
                <div className="space-y-3">
                  {activeAgents.length === 0 ? (
                    <div className="rounded-2xl px-4 py-6 text-center text-[12px] text-[var(--text-3)]"
                      style={{ background: "var(--bg-2)" }}>
                      目前沒有 agent 正在執行任務。
                    </div>
                  ) : (
                    activeAgents.map(([id, agent]) => {
                      const nextOwner = agent.task_meta?.target_agent_id
                        ? agents[agent.task_meta.target_agent_id]?.nickname || agent.task_meta.target_agent_id
                        : "";
                      return (
                        <div key={id} className="rounded-2xl px-4 py-3" style={{ background: "var(--bg-2)" }}>
                          <div className="flex items-center justify-between gap-3">
                            <div>
                              <div className="text-[13px] font-semibold text-[var(--text-1)]">{agent.nickname}</div>
                              <div className="mt-0.5 text-[11px] text-[var(--text-2)]">{taskLabel(agent)}</div>
                            </div>
                            <div className="text-[11px] text-[var(--text-3)]">
                              {formatElapsed(agent.task_meta?.started_at || agent.updated_at)}
                            </div>
                          </div>
                          <div className="mt-2 text-[12px] font-medium text-[var(--text-1)]">
                            {agent.task_meta?.title || agent.task || "進行中的任務"}
                          </div>
                          <div className="mt-2 text-[11px] text-[var(--text-2)]">
                            下一棒: {nextOwner || "尚未指定"}
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>

              {/* 活動流 */}
              <div className="card flex flex-col overflow-hidden" style={{ height: "520px" }}>
                <div className="px-5 py-4" style={{ borderBottom: "1px solid var(--border)" }}>
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-[11px] uppercase tracking-[0.2em] text-[var(--text-3)]">活動流</div>
                    <div className="text-[11px] text-[var(--text-3)]">
                      {filterAgent || filterTaskType
                        ? `${events.filter(e => (!filterTaskType || e.taskType === filterTaskType)).length} / ${events.length}`
                        : `${events.length}`} events
                    </div>
                  </div>
                  {/* Agent filter */}
                  <div className="flex flex-wrap gap-1.5 mb-2">
                    {[null, ...AGENT_ORDER].map((id) => {
                      const label = id ? (agents[id]?.nickname || id) : "全部";
                      const active = filterAgent === id;
                      return (
                        <button
                          key={id ?? "all"}
                          onClick={() => setFilterAgent(id)}
                          className="rounded-full px-2.5 py-0.5 text-[10px] tracking-[0.12em] transition-all"
                          style={{
                            background: active ? "rgba(124,92,191,0.12)" : "var(--bg-2)",
                            border: `1px solid ${active ? "rgba(124,92,191,0.3)" : "var(--border)"}`,
                            color: active ? "var(--accent)" : "var(--text-2)",
                          }}
                        >
                          {label}
                        </button>
                      );
                    })}
                  </div>
                  {/* Task type filter */}
                  <div className="flex flex-wrap gap-1.5">
                    {[null, ...Object.values(TASK_TYPE_LABELS)].map((type) => {
                      const active = filterTaskType === type;
                      return (
                        <button
                          key={type ?? "all-type"}
                          onClick={() => setFilterTaskType(type)}
                          className="rounded-full px-2.5 py-0.5 text-[10px] tracking-[0.12em] transition-all"
                          style={{
                            background: active ? "rgba(22,163,74,0.1)" : "var(--bg-2)",
                            border: `1px solid ${active ? "rgba(22,163,74,0.28)" : "var(--border)"}`,
                            color: active ? "#16a34a" : "var(--text-3)",
                          }}
                        >
                          {type ?? "所有類型"}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div ref={listRef} className="flex-1 overflow-y-auto px-4 py-3">
                  {(() => {
                    const displayEvents = filterTaskType
                      ? events.filter(e => e.taskType === filterTaskType)
                      : events;
                    if (displayEvents.length === 0) return (
                      <div className="rounded-2xl px-4 py-8 text-center text-[12px] text-[var(--text-3)]"
                        style={{ background: "var(--bg-2)" }}>
                        {events.length === 0
                          ? "等待 agent 活動。一旦任務開始流動，這裡就會出現團隊時間線。"
                          : "此類型暫無活動記錄。"}
                      </div>
                    );
                    return (
                      <div className="space-y-2">
                        {displayEvents.map((item) => (
                          <div key={item.id} className="rounded-2xl px-4 py-3" style={{ background: "var(--bg-2)" }}>
                            <div className="flex items-center gap-2 text-[11px] text-[var(--text-3)]">
                              <span>{item.time}</span>
                              <span>{item.agentEmoji}</span>
                              <span className="font-semibold text-[var(--text-1)]">{item.agentName}</span>
                              <span className="ml-auto rounded-full px-1.5 py-0.5 text-[9px] tracking-wider"
                                style={{ background: "rgba(22,163,74,0.08)", color: "#16a34a" }}>
                                {item.taskType}
                              </span>
                            </div>
                            <div className="mt-1.5 text-[12px] font-medium text-[var(--text-1)]">{item.title}</div>
                            {item.nextOwner && (
                              <div className="mt-1 text-[11px] text-[var(--text-2)]">→ {item.nextOwner}</div>
                            )}
                          </div>
                        ))}
                      </div>
                    );
                  })()}
                </div>
              </div>

              {/* Workflow Runs Timeline */}
              {workflowRuns.length > 0 && (
                <div className="card p-5">
                  <div className="text-[11px] uppercase tracking-[0.2em] text-[var(--text-3)] mb-3">工作流執行記錄</div>
                  <div className="space-y-2">
                    {workflowRuns.map((run: any) => {
                      const statusMap: Record<string, { color: string; label: string }> = {
                        completed: { color: "#16a34a", label: "完成" },
                        running:   { color: "var(--accent)", label: "執行中" },
                        paused:    { color: "#b45309", label: "等待審核" },
                        failed:    { color: "var(--red)", label: "失敗" },
                        pending:   { color: "var(--text-3)", label: "等待中" },
                      };
                      const { color, label } = statusMap[run.status] || { color: "var(--text-3)", label: run.status };
                      const isPaused = run.status === "paused";
                      return (
                        <div key={run.id} className="rounded-xl px-3 py-2.5"
                          style={{ background: "var(--bg-2)", border: isPaused ? "1px solid rgba(217,119,6,0.28)" : "1px solid transparent" }}>
                          <div className="flex items-center justify-between gap-2">
                            <div className="text-[11px] font-medium text-[var(--text-1)] truncate">
                              {run.name?.replace(/_/g, " ") || "workflow"}
                            </div>
                            <span className="shrink-0 text-[10px] font-semibold rounded-full px-2 py-0.5"
                              style={{ background: `${color}18`, color }}>
                              {label}
                            </span>
                          </div>
                          <div className="mt-1 text-[10px] text-[var(--text-3)]">
                            {run.started_at ? new Date(run.started_at).toLocaleString("zh-TW", { month: "numeric", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "—"}
                            {run.domain && ` · ${run.domain}`}
                          </div>
                          {run.error && (
                            <div className="mt-1 text-[10px] text-[var(--red)] truncate">{run.error}</div>
                          )}
                          {isPaused && (
                            <button
                              onClick={async () => {
                                await fetch(`${BACKEND}/api/pipeline/resume/${run.id}`, { method: "POST" });
                                setTimeout(() => fetchWorkflowRuns(8).then(d => setWorkflowRuns(d.runs || [])).catch(() => {}), 1500);
                              }}
                              className="mt-2 w-full rounded-lg py-1.5 text-[10px] font-semibold tracking-[0.1em]"
                              style={{ background: "rgba(217,119,6,0.1)", border: "1px solid rgba(217,119,6,0.24)", color: "#b45309" }}
                            >
                              繼續執行 →
                            </button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Skill Routing Panel */}
              {skillRoutes.length > 0 && (
                <div className="card p-5">
                  <div className="text-[11px] uppercase tracking-[0.2em] text-[var(--text-3)] mb-3">Skill 路由矩陣</div>
                  <div className="space-y-1.5">
                    {skillRoutes.map((r: any) => (
                      <div key={r.task_type} className="rounded-lg px-3 py-2" style={{ background: "var(--bg-2)" }}>
                        <div className="flex items-center justify-between gap-1 mb-0.5">
                          <span className="text-[11px] font-semibold text-[var(--text-1)] truncate">{r.task_type}</span>
                          <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-medium shrink-0 ${
                            r.risk_level === "high" ? "bg-red-100 text-red-600" :
                            r.risk_level === "medium" ? "bg-amber-100 text-amber-600" :
                            "bg-green-100 text-green-600"
                          }`}>{r.risk_level}</span>
                        </div>
                        <div className="text-[10px] text-[var(--text-3)] truncate">
                          {r.primary_pattern} · {r.required_skills.join(", ")}
                          {r.requires_review && <span className="ml-1 text-amber-500">· 需審核</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Artifact Panel */}
              {artifacts.length > 0 && (
                <div className="card p-5">
                  <div className="text-[11px] uppercase tracking-[0.2em] text-[var(--text-3)] mb-3">最近產出物</div>
                  <div className="space-y-2">
                    {artifacts.map((art: any) => {
                      const typeMap: Record<string, { emoji: string; label: string }> = {
                        draft:                  { emoji: "✍️", label: "草稿" },
                        weekly_report:          { emoji: "📊", label: "週報" },
                        selection_report:       { emoji: "🛍️", label: "選品報告" },
                        screenshot_extraction:  { emoji: "📸", label: "截圖分析" },
                      };
                      const { emoji, label } = typeMap[art.artifact_type] || { emoji: "📄", label: art.artifact_type };
                      return (
                        <div key={art.id} className="flex items-center justify-between gap-2 rounded-xl px-3 py-2.5"
                          style={{ background: "var(--bg-2)" }}>
                          <div className="flex items-center gap-2 min-w-0">
                            <span className="text-base">{emoji}</span>
                            <div className="min-w-0">
                              <div className="text-[12px] font-medium text-[var(--text-1)] truncate">{label}</div>
                              <div className="text-[10px] text-[var(--text-3)]">{art.producer} · {art.created_at?.slice(11, 16)}</div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

            </div>
          </div>
        </div>
      </div>
    </>
  );
}
