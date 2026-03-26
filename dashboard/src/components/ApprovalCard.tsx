"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, ShieldAlert, ShieldCheck, ShieldOff, Loader2, CheckCircle2, XCircle } from "lucide-react";
import { decideApproval } from "@/lib/api";

export type ApprovalPackage = {
  approval_id: string;
  run_id: string | null;
  action: string;
  risk_level: "low" | "medium" | "high";
  status: "pending" | "approved" | "rejected";
  summary: string;
  evidence: Record<string, unknown>;
  artifact_links: string[];
  approve_label: string;
  reject_label: string;
};

const RISK_CONFIG = {
  high:   { cls: "card-risk-high",   badge: "bg-red-100 text-red-700",    icon: ShieldAlert,  label: "高風險" },
  medium: { cls: "card-risk-medium", badge: "bg-amber-100 text-amber-700", icon: ShieldAlert,  label: "中風險" },
  low:    { cls: "card-risk-low",    badge: "bg-violet-100 text-violet-700", icon: ShieldCheck, label: "低風險" },
};

export default function ApprovalCard({
  pkg,
  onDecided,
}: {
  pkg: ApprovalPackage;
  onDecided?: (id: string, decision: "approved" | "rejected") => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [state, setState] = useState<"idle" | "approving" | "rejecting" | "done_ok" | "done_rej" | "err">("idle");
  const cfg = RISK_CONFIG[pkg.risk_level] ?? RISK_CONFIG.medium;
  const Icon = cfg.icon;
  const busy = state === "approving" || state === "rejecting";

  const decide = async (decision: "approved" | "rejected") => {
    setState(decision === "approved" ? "approving" : "rejecting");
    try {
      await decideApproval(pkg.approval_id, decision);
      setState(decision === "approved" ? "done_ok" : "done_rej");
      onDecided?.(pkg.approval_id, decision);
    } catch {
      setState("err");
      setTimeout(() => setState("idle"), 3000);
    }
  };

  if (state === "done_ok" || state === "done_rej") {
    return (
      <div className={`${cfg.cls} p-4 flex items-center gap-3 animate-fade-in`}>
        {state === "done_ok"
          ? <CheckCircle2 size={16} className="text-green-600 shrink-0" />
          : <XCircle size={16} className="text-red-600 shrink-0" />
        }
        <span className="text-[13px] font-medium text-[var(--text-1)]">
          {state === "done_ok" ? "已核准" : "已拒絕"} — {pkg.action}
        </span>
      </div>
    );
  }

  // Flatten evidence for display
  const evidenceEntries = Object.entries(pkg.evidence || {})
    .filter(([, v]) => typeof v === "string" || typeof v === "number")
    .slice(0, 6);

  const outputsSummary = pkg.evidence?.outputs_summary as Record<string, string> | undefined;

  return (
    <div className={`${cfg.cls} overflow-hidden transition-all duration-200`}>
      {/* Header row */}
      <button
        className="w-full flex items-start gap-3 p-4 text-left hover:bg-black/[0.02] transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <Icon size={16} className="shrink-0 mt-0.5" style={{ color: pkg.risk_level === "high" ? "#dc2626" : pkg.risk_level === "medium" ? "#d97706" : "#7c5cbf" }} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${cfg.badge}`}>
              {cfg.label}
            </span>
            <span className="text-[11px] text-[var(--text-3)] font-mono">{pkg.action}</span>
          </div>
          <p className="text-[13px] font-semibold text-[var(--text-1)] leading-snug">{pkg.summary}</p>
          {pkg.artifact_links.length > 0 && (
            <p className="text-[11px] text-[var(--text-3)] mt-0.5">{pkg.artifact_links.length} 個相關產出</p>
          )}
        </div>
        <div className="shrink-0 text-[var(--text-3)] mt-0.5">
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </div>
      </button>

      {/* Expanded evidence */}
      {expanded && (
        <div className="px-4 pb-3 space-y-3 border-t border-black/[0.06] pt-3 animate-slide-down">
          {/* Outputs summary */}
          {outputsSummary && Object.keys(outputsSummary).length > 0 && (
            <div>
              <p className="text-[10px] uppercase tracking-widest text-[var(--text-3)] mb-2 font-semibold">工作流產出摘要</p>
              <div className="space-y-1.5">
                {Object.entries(outputsSummary).slice(0, 5).map(([k, v]) => (
                  <div key={k} className="flex gap-2 text-[11px]">
                    <span className="text-[var(--text-3)] shrink-0 w-20 truncate">{k}</span>
                    <span className="text-[var(--text-1)] line-clamp-2 flex-1">{v}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          {/* Other evidence fields */}
          {evidenceEntries.length > 0 && (
            <div className="grid grid-cols-2 gap-1.5">
              {evidenceEntries.map(([k, v]) => (
                <div key={k} className="rounded-lg px-2.5 py-1.5 bg-black/[0.03]">
                  <div className="text-[9px] uppercase tracking-widest text-[var(--text-3)]">{k}</div>
                  <div className="text-[11px] font-medium text-[var(--text-1)] truncate">{String(v)}</div>
                </div>
              ))}
            </div>
          )}
          {/* run_id */}
          {pkg.run_id && (
            <p className="text-[10px] text-[var(--text-3)] font-mono">run: {pkg.run_id}</p>
          )}
        </div>
      )}

      {/* Action buttons — always visible */}
      <div className="px-4 pb-4 flex gap-2">
        <button
          disabled={busy}
          onClick={() => decide("approved")}
          className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-xl text-[12px] font-semibold transition-all disabled:opacity-60"
          style={{ background: "rgba(22,163,74,0.12)", border: "1px solid rgba(22,163,74,0.28)", color: "#16a34a" }}
        >
          {state === "approving" ? <Loader2 size={12} className="animate-spin" /> : <CheckCircle2 size={12} />}
          {pkg.approve_label}
        </button>
        <button
          disabled={busy}
          onClick={() => decide("rejected")}
          className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-xl text-[12px] font-semibold transition-all disabled:opacity-60"
          style={{ background: "rgba(220,38,38,0.08)", border: "1px solid rgba(220,38,38,0.22)", color: "#dc2626" }}
        >
          {state === "rejecting" ? <Loader2 size={12} className="animate-spin" /> : <XCircle size={12} />}
          {pkg.reject_label}
        </button>
        {state === "err" && (
          <span className="text-[11px] text-red-600 self-center ml-1">操作失敗</span>
        )}
      </div>
    </div>
  );
}
