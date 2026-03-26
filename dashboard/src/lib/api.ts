const BASE = "/api";

/** Direct backend base URL — used for POST/PATCH/DELETE that can't go through Next.js rewrite proxy. */
export const BACKEND = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function fetchToday(date?: string) {
  const params = date ? `?date=${date}` : "";
  const res = await fetch(`${BASE}/today${params}`);
  if (!res.ok) throw new Error("Failed to fetch today");
  return res.json();
}

export async function triggerPipeline(dryRun = false) {
  if (dryRun) {
    // dry_run still uses the legacy linear pipeline (for quick test only)
    const res = await fetch(`${BASE}/pipeline/run?dry_run=true`, { method: "POST" });
    return res.json();
  }
  // Real run: graph pipeline with approval gate → surfaces in /review when drafts ready
  const res = await fetch(`${BASE}/pipeline/graph-run?approval_gate=true`, { method: "POST" });
  return res.json();
}

export async function getPipelineStatus() {
  const res = await fetch(`${BASE}/pipeline/status`);
  return res.json();
}

export async function triggerTracker() {
  const res = await fetch(`${BASE}/tracker/run`, { method: "POST" });
  return res.json();
}

export async function getTrackerStatus() {
  const res = await fetch(`${BASE}/tracker/status`);
  return res.json();
}

export async function fetchMetrics(days = 30) {
  const res = await fetch(`${BASE}/metrics?days=${days}`);
  if (!res.ok) throw new Error("Failed to fetch metrics");
  return res.json();
}

export async function fetchLibrary(date?: string) {
  const params = date ? `?date=${date}` : "";
  const res = await fetch(`${BASE}/library${params}`);
  if (!res.ok) throw new Error("Failed to fetch library");
  return res.json();
}

export async function fetchLibraryDates() {
  const res = await fetch(`${BASE}/library/dates`);
  return res.json();
}

export async function triggerWeekly() {
  const res = await fetch(`${BASE}/weekly/run`, { method: "POST" });
  return res.json();
}

export async function getWeeklyStatus() {
  const res = await fetch(`${BASE}/weekly/status`);
  return res.json();
}

export async function fetchLatestWeekly() {
  const res = await fetch(`${BASE}/weekly/latest`);
  if (!res.ok) throw new Error("Failed to fetch weekly");
  return res.json();
}

export async function fetchWeeklyList() {
  const res = await fetch(`${BASE}/weekly/list`);
  return res.json();
}

export async function fetchWeekly(weekId: string) {
  const res = await fetch(`${BASE}/weekly/${weekId}`);
  return res.json();
}

// ── 精選清單 ──────────────────────────────────────────────────────────────────

export async function fetchPicks(date?: string) {
  const params = date ? `?date=${date}` : "";
  const res = await fetch(`${BASE}/picks${params}`);
  if (!res.ok) throw new Error("Failed to fetch picks");
  return res.json();
}

export async function fetchPicksDates() {
  const res = await fetch(`${BASE}/picks/dates`);
  return res.json();
}

// ── Feedback / Insights ──────────────────────────────────────────────────────

export async function fetchInsights() {
  const res = await fetch(`${BASE}/feedback/insights`);
  return res.json();
}

export async function triggerFeedback(days = 30) {
  const res = await fetch(`${BASE}/feedback/run?days=${days}`, { method: "POST" });
  return res.json();
}

export async function getFeedbackStatus() {
  const res = await fetch(`${BASE}/feedback/status`);
  return res.json();
}

export async function fetchPostStats(days = 30) {
  const res = await fetch(`${BASE}/stats/posts?days=${days}`);
  return res.json();
}

export async function fetchAgentEvents(limit = 50, agentId?: string) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (agentId) params.set("agent_id", agentId);
  const res = await fetch(`${BASE}/agents/events?${params}`);
  if (!res.ok) throw new Error("Failed to fetch agent events");
  return res.json();
}

export async function triggerDemoHandoff() {
  const res = await fetch(`${BASE}/agents/demo-handoff`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to trigger demo handoff");
  return res.json();
}

export async function fetchAgentStatus() {
  const res = await fetch(`${BASE}/agents/status`);
  if (!res.ok) throw new Error("Failed to fetch agent status");
  return res.json();
}

export async function fetchTodayStats() {
  const res = await fetch(`${BASE}/agents/today-stats`);
  if (!res.ok) throw new Error("Failed to fetch today stats");
  return res.json();
}

export async function fetchContentCalendar(year?: number, month?: number) {
  const params = new URLSearchParams();
  if (year) params.set("year", String(year));
  if (month) params.set("month", String(month));
  const res = await fetch(`${BASE}/content/calendar?${params}`);
  return res.json();
}

export async function fetchMorningBriefing() {
  const res = await fetch(`${BASE}/morning/briefing`, { cache: "no-store" });
  return res.json();
}

export async function fetchContentFeedback(days = 90) {
  const res = await fetch(`${BASE}/content/feedback?days=${days}`);
  return res.json();
}

export async function publishToThreads(text: string, draftId?: number) {
  // Next.js rewrite proxy 會丟失 POST body，直接打後端
  const body: Record<string, unknown> = { text };
  if (draftId != null) body.draft_id = draftId;
  const res = await fetch(`${BACKEND}/api/threads/publish`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

export async function sendCeoMessage(
  message: string,
  context?: { role: string; content: string }[],
  image_base64?: string
) {
  const res = await fetch(`${BACKEND}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, context, image_base64 }),
  });
  if (!res.ok) throw new Error("CEO chat failed");
  return res.json();
}

export async function fetchMorningReport() {
  const res = await fetch(`${BASE}/morning-report`);
  if (!res.ok) throw new Error("Failed to fetch morning report");
  return res.json();
}

export async function fetchReviewQueue(status?: string) {
  const params = status ? `?status=${status}` : "";
  const res = await fetch(`${BASE}/review-queue${params}`);
  if (!res.ok) throw new Error("Failed to fetch review queue");
  return res.json();
}

export async function fetchNightShiftStatus() {
  const res = await fetch(`${BASE}/night-shift/status`);
  if (!res.ok) throw new Error("Failed to fetch night shift status");
  return res.json();
}

export async function triggerNightShift() {
  const res = await fetch(`${BACKEND}/api/night-shift/trigger`, { method: "POST" });
  return res.json();
}

// ── Review Queue Stats ────────────────────────────────────────────────────────

export async function fetchReviewStats() {
  const res = await fetch(`${BASE}/review-queue/stats`);
  if (!res.ok) return { pending: 0, approved: 0, rejected: 0, deferred: 0, total: 0 };
  return res.json();
}

// ── Artifacts / Workflows ─────────────────────────────────────────────────────

export async function fetchArtifacts(limit = 20, artifactType?: string) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (artifactType) params.set("artifact_type", artifactType);
  const res = await fetch(`${BASE}/artifacts?${params}`);
  return res.json();
}

export async function fetchWorkflowRuns(limit = 20) {
  const res = await fetch(`${BASE}/workflows/runs?limit=${limit}`);
  return res.json();
}

export async function fetchPendingApprovals() {
  const res = await fetch(`${BASE}/approvals/pending`);
  return res.json();
}

export async function decideApproval(id: string, decision: "approved" | "rejected", note = "") {
  const res = await fetch(`${BACKEND}/api/approvals/${id}/decide`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision, note }),
  });
  return res.json();
}

export async function fetchApprovalPackage(approvalId: string) {
  const res = await fetch(`${BASE}/approvals/${approvalId}/package`);
  if (!res.ok) throw new Error("Approval package not found");
  return res.json();
}

export async function decideReviewItem(
  id: number,
  status: "approved" | "rejected" | "deferred",
  decision_note?: string,
  platforms?: string[],
  draft_id?: number
) {
  const res = await fetch(`${BACKEND}/api/review-queue/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status, decision_by: "human", decision_note, platforms, draft_id }),
  });
  if (!res.ok) throw new Error("Failed to update review item");
  return res.json();
}

export async function cleanupReviewQueue(status: "pending" | "approved" | "rejected" | "deferred" | "decided" | "all") {
  const res = await fetch(`${BACKEND}/api/review-queue?status=${status}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to cleanup review queue");
  return res.json();
}

// ── Video Analysis (Flow Lab M1) ───────────────────────────────────────────────

export async function uploadVideo(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BACKEND}/api/flowlab/video-upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Upload failed: ${res.status}`);
  }
  return res.json();
}

export async function fetchVideoAnalyses(status?: string) {
  const params = status ? `?status=${status}` : "";
  const res = await fetch(`${BACKEND}/api/flowlab/video-analyses${params}`);
  if (!res.ok) throw new Error("Failed to fetch video analyses");
  return res.json();
}

export async function fetchVideoAnalysis(videoId: string) {
  const res = await fetch(`${BACKEND}/api/flowlab/video-analyses/${videoId}`);
  if (!res.ok) throw new Error("Video analysis not found");
  return res.json();
}

export async function fetchPublishableDrafts(limit = 20) {
  const res = await fetch(`${BASE}/threads/drafts?limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch drafts");
  return res.json();
}

export async function updateDraft(id: number, content: string) {
  const res = await fetch(`${BACKEND}/api/drafts/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  if (!res.ok) throw new Error("Failed to update draft");
  return res.json();
}

export async function regenerateDraft(id: number, hint = "") {
  const res = await fetch(`${BACKEND}/api/drafts/${id}/regenerate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ hint }),
  });
  if (!res.ok) throw new Error("Failed to regenerate draft");
  return res.json();
}

export async function fetchSkillRouting() {
  const res = await fetch(`${BASE}/skills/routing`, { cache: "no-store" });
  if (!res.ok) return null;
  return res.json();
}

export async function decideVideoAnalysis(
  videoId: string,
  decision: "approved" | "rejected",
  note = ""
) {
  const res = await fetch(`${BACKEND}/api/flowlab/video-analyses/${videoId}/decide`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision, note }),
  });
  if (!res.ok) throw new Error("Failed to decide video analysis");
  return res.json();
}

// ── CEO Deliberation ──────────────────────────────────────────────────────────

export interface DeliberationResult {
  consensus?: string;
  key_insights?: string[];
  divergences?: string | null;
  recommendation?: string;
  confidence?: string;
  next_steps?: string[];
  agent_inputs?: { agent: string; task_type: string; success: boolean; summary: string }[];
  error?: string;
}

/** POST /api/chat/deliberate — multi-agent consultation (Ori + Lala + Sage → CEO synthesis). */
export async function callDeliberate(question: string): Promise<DeliberationResult> {
  const res = await fetch(`${BACKEND}/api/chat/deliberate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.json();
}

// ── Runtime Health ─────────────────────────────────────────────────────────────

/** Lightweight backend ping — returns true if backend is reachable. */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${BACKEND}/api/health`, { cache: "no-store" });
    return res.ok;
  } catch {
    return false;
  }
}
