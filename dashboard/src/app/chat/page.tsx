"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  AlertCircle,
  BarChart2,
  Bot,
  Brain,
  Calendar,
  CheckCircle2,
  Clock,
  FileText,
  Paperclip,
  RefreshCw,
  Search,
  Send,
  X,
  Zap,
} from "lucide-react";

import {
  fetchAgentStatus,
  fetchMorningBriefing,
  fetchTodayStats,
  getPipelineStatus,
  sendCeoMessage,
  triggerPipeline,
  triggerTracker,
  triggerWeekly,
  BACKEND,
} from "@/lib/api";

type AgentState = "idle" | "running" | "done" | "error" | "awaiting_human";

interface Agent {
  id: string;
  name: string;
  role: string;
  status: AgentState;
  last_task?: string;
  last_active_at?: string;
}

interface Message {
  id: number;
  role: "user" | "system";
  text: string;
  ts: Date;
  loading?: boolean;
  agent?: string;
  pendingTask?: string;  // high-risk task awaiting user confirmation
}

interface ImageAttachment {
  base64: string;
  preview: string;
  name: string;
}

const QUICK_COMMANDS = [
  { label: "執行 Pipeline", icon: Zap, desc: "立即觸發內容生成 Pipeline。", cmd: "run pipeline" },
  { label: "更新追蹤數據", icon: RefreshCw, desc: "刷新 Threads 指標與發布狀態。", cmd: "run tracker" },
  { label: "週報生成", icon: FileText, desc: "產生本週內容績效摘要。", cmd: "run weekly" },
  { label: "Pipeline 狀態", icon: BarChart2, desc: "查看上次 Pipeline 執行詳情。", cmd: "pipeline status" },
  { label: "今日數據", icon: Calendar, desc: "查看今日發文與互動統計。", cmd: "today stats" },
  { label: "Agent 狀態", icon: Bot, desc: "列出所有 Agent 目前運作狀態。", cmd: "agent status" },
];

const AGENT_CONFIG: Record<string, { emoji: string; color: string }> = {
  ori: { emoji: "OR", color: "#3b82f6" },
  lala: { emoji: "LA", color: "#8b5cf6" },
  craft: { emoji: "CR", color: "#ec4899" },
  sage: { emoji: "SA", color: "#10b981" },
  lumi: { emoji: "LU", color: "#f59e0b" },
  pixel: { emoji: "PX", color: "#06b6d4" },
  ceo: { emoji: "CEO", color: "#7c5cbf" },
};

const taskType_labels: Record<string, string> = {
  content_research: "內容研究",
  market_analysis: "市場分析",
  topic_strategy: "選題策略",
  draft_generation: "草稿生成",
  copywriting: "文案寫作",
  data_analysis: "數據分析",
  seo_analysis: "SEO 分析",
  product_evaluation: "選品評估",
};

const STATUS_ICON: Record<AgentState, { icon: typeof CheckCircle2; color: string; label: string }> = {
  idle: { icon: Clock, color: "#a8a29e", label: "待機" },
  running: { icon: RefreshCw, color: "#f59e0b", label: "執行中" },
  done: { icon: CheckCircle2, color: "#22c55e", label: "完成" },
  error: { icon: AlertCircle, color: "#ef4444", label: "錯誤" },
  awaiting_human: { icon: AlertCircle, color: "#8b5cf6", label: "等待確認" },
};

const msgVariants = {
  hidden: { opacity: 0, y: 10, scale: 0.98 },
  visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.18, ease: "easeOut" as const } },
  exit: { opacity: 0, scale: 0.96, transition: { duration: 0.1 } },
};

const panelVariants = {
  hidden: { opacity: 0, y: -8, scale: 0.98 },
  visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.15, ease: "easeOut" as const } },
  exit: { opacity: 0, y: -4, scale: 0.97, transition: { duration: 0.1 } },
};

const cardVariants = {
  hidden: { opacity: 0, x: 8 },
  visible: (i: number) => ({
    opacity: 1,
    x: 0,
    transition: { duration: 0.2, delay: i * 0.05, ease: "easeOut" as const },
  }),
};

function summarizeTodayStats(stats: Record<string, unknown> | null | undefined) {
  if (!stats || stats.error) return "今日數據尚未取得。";

  const lines = ["今日數據"];
  if (typeof stats.posts_today === "number") lines.push(`發文：${stats.posts_today} 篇`);
  if (typeof stats.total_views === "number") lines.push(`總觀看：${stats.total_views.toLocaleString()}`);
  if (typeof stats.avg_engagement === "number") lines.push(`平均互動率：${stats.avg_engagement}%`);
  return lines.join("\n");
}

async function routeCommand(
  input: string,
  history: { role: string; content: string }[],
  imageBase64?: string
): Promise<{ text: string; agent?: string; pendingTask?: string }> {
  const q = input.toLowerCase().trim();

  if (q === "run pipeline" || q === "/pipeline") {
    const r = await triggerPipeline();
    return {
      text:
        r.status === "started"
          ? `Pipeline 已啟動。\n${r.message || "任務已由後端接受，正在執行中。"}`
          : `Pipeline 啟動失敗：${r.detail || r.message || "未知錯誤"}`,
    };
  }

  if (q === "run tracker" || q === "/tracker") {
    const r = await triggerTracker();
    return {
      text:
        r.status === "started"
          ? `追蹤器已啟動。\n${r.message || "指標刷新進行中。"}`
          : `追蹤器啟動失敗：${r.detail || r.message || "未知錯誤"}`,
    };
  }

  if (q === "run weekly" || q === "/weekly") {
    const r = await triggerWeekly();
    return {
      text:
        r.status === "started"
          ? `週報生成已啟動。\n${r.message || "週報任務執行中。"}`
          : `週報啟動失敗：${r.detail || r.message || "未知錯誤"}`,
    };
  }

  if (q === "pipeline status" || q === "/status") {
    const r = await getPipelineStatus();
    const lines = ["Pipeline 狀態"];
    if (r.last_run_at) lines.push(`上次執行：${r.last_run_at}`);
    if (r.last_success_at) lines.push(`上次成功：${r.last_success_at}`);
    if (r.last_error) lines.push(`上次錯誤：${r.last_error}`);
    lines.push(r.is_running ? "目前狀態：執行中" : "目前狀態：待機");
    return { text: lines.join("\n") };
  }

  if (q === "today stats" || q === "/today") {
    const r = await fetchTodayStats();
    return { text: summarizeTodayStats(r) };
  }

  if (q === "agent status" || q === "/agents") {
    const r = await fetchAgentStatus();
    if (!r?.agents?.length) return { text: "Agent 狀態尚未取得。" };

    const lines = ["Agent 狀態"];
    for (const agent of r.agents as Agent[]) {
      const status = STATUS_ICON[agent.status] || STATUS_ICON.idle;
      lines.push(
        `${agent.name} (${agent.id}) — ${status.label}${agent.last_task ? `｜${agent.last_task}` : ""}`
      );
    }
    return { text: lines.join("\n") };
  }

  try {
    const result = await sendCeoMessage(
      input,
      history as { role: "user" | "assistant"; content: string }[],
      imageBase64
    );
    const agentId = result.agent && result.agent !== "none" ? result.agent : undefined;
    let text = result.response || "No response returned.";
    if (agentId) {
      const cfg = AGENT_CONFIG[agentId];
      text = `${cfg?.emoji ?? "AI"} ${agentId.toUpperCase()}\n\n${text}`;
    }

    // Show auto-execution result
    if (result.execution?.triggered) {
      text += result.execution.ok
        ? `\n\n✅ 已自動執行：${result.execution.summary}`
        : `\n\n⚠️ 執行失敗：${result.execution.summary}`;
    }

    if (result.actions?.length) {
      text += `\n\n建議下一步\n${result.actions.map((action: string) => `- ${action}`).join("\n")}`;
    }

    // High-risk task: CEO identified but didn't auto-execute → surface task_type for UI button
    const pendingTask =
      !result.execution?.triggered && result.task_type && agentId
        ? (result.task_type as string)
        : undefined;

    return { text, agent: agentId, pendingTask };
  } catch {
    return { text: "CEO Agent 請求失敗，請再試一次。" };
  }
}

function formatDeliberationResult(d: Record<string, unknown>): string {
  const lines: string[] = ["深度分析結果（Ori + Lala + Sage）", ""];
  if (d.consensus) lines.push(`共識\n${d.consensus}`, "");
  if (Array.isArray(d.key_insights) && d.key_insights.length) {
    lines.push("關鍵洞察");
    for (const ins of d.key_insights as string[]) lines.push(`• ${ins}`);
    lines.push("");
  }
  if (d.divergences) lines.push(`分歧點\n${d.divergences}`, "");
  if (d.recommendation) lines.push(`建議行動\n${d.recommendation}`, "");
  if (Array.isArray(d.next_steps) && d.next_steps.length) {
    lines.push("後續步驟");
    (d.next_steps as string[]).forEach((s, i) => lines.push(`${i + 1}. ${s}`));
    lines.push("");
  }
  const conf = (d.confidence as string) ?? "?";
  const confLabel = conf === "high" ? "高" : conf === "medium" ? "中" : conf === "low" ? "低" : conf;
  lines.push(`信心度：${confLabel}`);
  if (Array.isArray(d.agent_inputs)) {
    const successCount = (d.agent_inputs as { success: boolean }[]).filter((a) => a.success).length;
    lines.push(`（${successCount}/${d.agent_inputs.length} 位顧問提供資料）`);
  }
  return lines.join("\n");
}

const AGENT_LABEL: Record<string, string> = { ori: "OR 研究", lala: "LA 策略", sage: "SA 分析" };

const CHAT_STORAGE_KEY = "anticlaude_chat_messages";
const HISTORY_STORAGE_KEY = "anticlaude_chat_history";

function loadSavedMessages(): Message[] | null {
  try {
    const raw = sessionStorage.getItem(CHAT_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as (Omit<Message, "ts"> & { ts: string })[];
    if (!parsed.length) return null;
    return parsed.map((m) => ({ ...m, ts: new Date(m.ts) }));
  } catch {
    return null;
  }
}

function saveMessages(msgs: Message[]) {
  try {
    // Don't save loading states
    const toSave = msgs.filter((m) => !m.loading);
    sessionStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(toSave));
  } catch {}
}

function loadSavedHistory(): { role: string; content: string }[] {
  try {
    const raw = sessionStorage.getItem(HISTORY_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>(() => {
    const saved = loadSavedMessages();
    return saved ?? [{ id: 0, role: "system", text: "載入今日晨報中...", ts: new Date(), loading: true }];
  });
  const [input, setInput] = useState("");
  const [agents, setAgents] = useState<Agent[]>([]);
  const [showCommands, setShowCmds] = useState(false);
  const [sending, setSending] = useState(false);
  const [deliberating, setDeliberating] = useState(false);
  const [attachment, setAttachment] = useState<ImageAttachment | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const nextId = useRef(1);
  const historyRef = useRef<{ role: string; content: string }[]>([]);

  // Restore historyRef and nextId from sessionStorage on mount
  useEffect(() => {
    historyRef.current = loadSavedHistory();
    const saved = loadSavedMessages();
    if (saved) {
      nextId.current = Math.max(...saved.map((m) => m.id)) + 1;
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Persist messages to sessionStorage whenever they change
  useEffect(() => {
    saveMessages(messages);
  }, [messages]);

  useEffect(() => {
    // Skip morning briefing if we restored a saved session
    if (loadSavedMessages()) return;
    fetchMorningBriefing()
      .then((briefing) => {
        const lines: string[] = ["早安！今日晨報"];
        if (briefing?.pipeline_ran_today) {
          lines.push(`Pipeline 已於 ${briefing.pipeline_ran_at || "今日"} 執行。`);
        } else {
          lines.push(`Pipeline 尚未執行，下次預計：${briefing?.next_pipeline_label || "未知"}。`);
        }
        if (typeof briefing?.drafts_today === "number" && briefing.drafts_today > 0) {
          lines.push(`今日草稿：${briefing.drafts_today} 篇，選題：${briefing.topics_today || 0} 個。`);
        }
        if (typeof briefing?.posts_today === "number" && briefing.posts_today > 0) {
          lines.push(`今日已發布：${briefing.posts_today} 篇。`);
        }
        if (briefing?.yesterday_avg_engagement != null) {
          lines.push(`昨日平均互動率：${briefing.yesterday_avg_engagement}%。`);
        }
        if (briefing?.has_error) {
          lines.push(`⚠️ 系統警告：${briefing.error_summary || "後端回報錯誤"}。`);
        }
        lines.push("有什麼需要幫忙的嗎？可以直接問我，或使用下方快速指令。");
        setMessages([{ id: 0, role: "system", text: lines.join("\n"), ts: new Date() }]);
      })
      .catch(() => {
        setMessages([
          {
            id: 0,
            role: "system",
            text: "晨報載入失敗，後端可能尚未就緒。\n\n有什麼需要幫忙的嗎？可以直接問我，或使用下方快速指令。",
            ts: new Date(),
          },
        ]);
      });
  }, []);

  const loadAgents = useCallback(async () => {
    try {
      const r = await fetchAgentStatus();
      if (r?.agents) setAgents(r.agents);
    } catch {}
  }, []);

  useEffect(() => {
    loadAgents();
    const timer = setInterval(loadAgents, 15000);
    return () => clearInterval(timer);
  }, [loadAgents]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const addMessage = (role: Message["role"], text: string, loading = false, agent?: string) => {
    const id = nextId.current++;
    setMessages((prev) => [...prev, { id, role, text, ts: new Date(), loading, agent }]);
    return id;
  };

  const updateMessage = (id: number, text: string, agent?: string) => {
    setMessages((prev) => prev.map((message) => (message.id === id ? { ...message, text, loading: false, agent } : message)));
  };

  const attachFile = useCallback((file: File | null) => {
    if (!file) return;
    if (!file.type.startsWith("image/")) return;

    const reader = new FileReader();
    reader.onload = () => {
      const result = typeof reader.result === "string" ? reader.result : "";
      if (!result) return;
      setAttachment({
        base64: result,
        preview: result,
        name: file.name || "clipboard-image",
      });
    };
    reader.readAsDataURL(file);
  }, []);

  const removeAttachment = useCallback(() => {
    setAttachment(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }, []);

  const send = async (rawText: string) => {
    const text = rawText.trim();
    const attachmentToSend = attachment;
    if ((!text && !attachmentToSend) || sending) return;

    setSending(true);
    setInput("");
    setShowCmds(false);
    setAttachment(null);
    if (fileInputRef.current) fileInputRef.current.value = "";

    const userMessage = text || "[Image]";
    addMessage("user", userMessage);
    historyRef.current = [...historyRef.current, { role: "user", content: userMessage }];
    try { sessionStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(historyRef.current)); } catch {};

    const sysId = addMessage("system", "", true);
    try {
      const { text: reply, agent, pendingTask } = await routeCommand(text, historyRef.current, attachmentToSend?.base64);
      // Attach pendingTask to the message for the Execute button
      setMessages((prev) => prev.map((m) => m.id === sysId
        ? { ...m, text: reply, loading: false, agent, pendingTask }
        : m
      ));
      historyRef.current = [...historyRef.current, { role: "assistant", content: reply }];
      if (historyRef.current.length > 12) {
        historyRef.current = historyRef.current.slice(-12);
      }
      try { sessionStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(historyRef.current)); } catch {}
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : "未知錯誤";
      updateMessage(sysId, `請求失敗：${msg}`);
    } finally {
      setSending(false);
      inputRef.current?.focus();
    }
  };

  const sendDeliberate = async () => {
    const question = input.trim();
    if (!question || sending || deliberating) return;
    setDeliberating(true);
    setInput("");
    setShowCmds(false);
    addMessage("user", question);
    historyRef.current = [...historyRef.current, { role: "user", content: question }];
    const sysId = addMessage("system", "深度分析中，正在諮詢顧問團隊...", true);

    try {
      const url = `${BACKEND}/api/chat/deliberate/stream?question=${encodeURIComponent(question)}`;
      const es = new EventSource(url);
      const agentLines: string[] = [];
      let synthText = "";

      await new Promise<void>((resolve, reject) => {
        es.onmessage = (e) => {
          if (e.data === "[DONE]") { es.close(); resolve(); return; }
          try {
            const data: Record<string, unknown> = JSON.parse(e.data);
            if (data.type === "agent") {
              const label = AGENT_LABEL[data.agent as string] ?? String(data.agent).toUpperCase();
              const ok = data.success ? "✓" : "✗";
              agentLines.push(`${ok} ${label}：${String(data.summary || "").slice(0, 80)}`);
              const preview = agentLines.join("\n");
              setMessages((prev) => prev.map((m) => m.id === sysId
                ? { ...m, text: `顧問回覆中...\n\n${preview}`, loading: true } : m));
            } else if (data.type === "synthesis") {
              synthText = formatDeliberationResult(data);
            } else if (data.type === "error") {
              reject(new Error(String(data.message ?? "SSE error")));
            }
          } catch { /* ignore parse errors */ }
        };
        es.onerror = () => { es.close(); reject(new Error("SSE 連線中斷")); };
      });

      const finalText = synthText || agentLines.join("\n");
      updateMessage(sysId, finalText, "ceo");
      historyRef.current = [...historyRef.current, { role: "assistant", content: finalText }];
      if (historyRef.current.length > 12) historyRef.current = historyRef.current.slice(-12);
      try { sessionStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(historyRef.current)); } catch {}
    } catch (e: unknown) {
      updateMessage(sysId, `深度分析失敗：${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setDeliberating(false);
      inputRef.current?.focus();
    }
  };

  const handleKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void send(input);
    }
    if (e.key === "Escape") setShowCmds(false);
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    const file = Array.from(e.clipboardData.items)
      .find((item) => item.type.startsWith("image/"))
      ?.getAsFile();
    if (!file) return;

    e.preventDefault();
    attachFile(file);
  };

  return (
    <div className="flex gap-6 h-[calc(100vh-120px)]">
      <div className="flex-1 flex flex-col min-w-0">
        <div className="mb-4">
          <h1 className="text-2xl font-bold text-[var(--text-1)]">CEO Console</h1>
          <p className="text-[13px] text-[var(--text-2)] mt-0.5">
            指揮中心：對話、快速指令，支援圖片輸入
          </p>
        </div>

        <div className="flex-1 overflow-y-auto rounded-[16px] border border-[var(--border)] bg-white p-4 mb-4">
          <AnimatePresence initial={false}>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                variants={msgVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                layout
                className={`flex mb-4 ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {message.role === "system" && (
                  <div
                    className="w-7 h-7 rounded-full flex items-center justify-center mr-2 mt-0.5 shrink-0"
                    style={{ background: message.agent ? (AGENT_CONFIG[message.agent]?.color ?? "#7c5cbf") : "#7c5cbf" }}
                  >
                    {message.agent ? (
                      <span className="text-[10px] leading-none text-white">
                        {AGENT_CONFIG[message.agent]?.emoji ?? "AI"}
                      </span>
                    ) : (
                      <Bot size={14} className="text-white" />
                    )}
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-[14px] px-4 py-3 text-[13px] leading-relaxed whitespace-pre-wrap
                    ${
                      message.role === "user"
                        ? "bg-[var(--accent)] text-white"
                        : "bg-[var(--bg-2)] text-[var(--text-1)] border border-[var(--border)]"
                    }`}
                >
                  {message.loading ? (
                    <span className="flex items-center gap-2 text-[var(--text-3)]">
                      <motion.span
                        animate={{ rotate: 360 }}
                        transition={{ repeat: Infinity, duration: 0.8, ease: "linear" }}
                        className="inline-block"
                      >
                        <RefreshCw size={12} />
                      </motion.span>
                      {message.text || (deliberating ? "多 Agent 深度分析中..." : "CEO Agent 思考中...")}
                    </span>
                  ) : (
                    <>
                      {message.text}
                      {message.pendingTask && (
                        <div className="mt-3 pt-3 border-t border-[var(--border)]">
                          <p className="text-[11px] text-[var(--text-3)] mb-2">
                            此任務需要你確認後執行
                          </p>
                          <button
                            onClick={async () => {
                              const taskType = message.pendingTask!;
                              // Remove pendingTask to prevent double-click
                              setMessages((prev) => prev.map((m) =>
                                m.id === message.id ? { ...m, pendingTask: undefined } : m
                              ));
                              const execId = nextId.current++;
                              setMessages((prev) => [...prev, {
                                id: execId, role: "system",
                                text: "", loading: true, ts: new Date(),
                              }]);
                              try {
                                const r = await fetch(`${BACKEND}/api/pipeline/dynamic`, {
                                  method: "POST",
                                  headers: { "Content-Type": "application/json" },
                                  body: JSON.stringify({ task_type: taskType }),
                                });
                                const data = await r.json();
                                const ok = data.ok ?? data.success ?? r.ok;
                                setMessages((prev) => prev.map((m) => m.id === execId ? {
                                  ...m, loading: false,
                                  text: ok
                                    ? `✅ ${taskType} 執行完成`
                                    : `⚠️ 執行失敗：${data.error || data.detail || "未知錯誤"}`,
                                } : m));
                              } catch (e) {
                                setMessages((prev) => prev.map((m) => m.id === execId ? {
                                  ...m, loading: false, text: `⚠️ 執行失敗：${String(e)}`,
                                } : m));
                              }
                            }}
                            className="px-3 py-1.5 bg-[var(--accent)] text-white text-[12px] font-medium rounded-lg hover:opacity-90 transition-opacity"
                          >
                            ▶ 立即執行 {taskType_labels[message.pendingTask] ?? message.pendingTask}
                          </button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={bottomRef} />
        </div>

        <AnimatePresence>
          {showCommands && (
            <motion.div
              key="commands"
              variants={panelVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              className="rounded-[14px] border border-[var(--border)] bg-white shadow-lg mb-2 overflow-hidden"
            >
              <div className="px-4 py-2 border-b border-[var(--border)]">
                <span className="text-[11px] font-600 text-[var(--text-3)] uppercase tracking-wider">快速指令</span>
              </div>
              {QUICK_COMMANDS.map((command, index) => (
                <motion.button
                  key={command.cmd}
                  initial={{ opacity: 0, x: -6 }}
                  animate={{ opacity: 1, x: 0, transition: { delay: index * 0.04, duration: 0.14 } }}
                  onClick={() => void send(command.cmd)}
                  className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-[var(--bg-2)] transition-colors text-left"
                >
                  <command.icon size={14} className="text-[var(--accent)] shrink-0" />
                  <div>
                    <div className="text-[13px] font-600 text-[var(--text-1)]">{command.label}</div>
                    <div className="text-[11px] text-[var(--text-3)]">{command.desc}</div>
                  </div>
                </motion.button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {attachment && (
          <div className="mb-2 rounded-[14px] border border-[var(--border)] bg-white px-3 py-2 flex items-center gap-3">
            <img
              src={attachment.preview}
              alt={attachment.name}
              className="w-14 h-14 rounded-[10px] object-cover border border-[var(--border)]"
            />
            <div className="flex-1 min-w-0">
              <div className="text-[12px] font-600 text-[var(--text-1)] truncate">{attachment.name}</div>
              <div className="text-[11px] text-[var(--text-3)]">圖片將隨下一則訊息傳送給 CEO Agent。</div>
            </div>
            <button
              type="button"
              onClick={removeAttachment}
              className="p-1.5 rounded-[8px] text-[var(--text-3)] hover:text-[var(--accent)] hover:bg-[var(--accent-soft)] transition-colors"
              aria-label="Remove image"
            >
              <X size={14} />
            </button>
          </div>
        )}

        <motion.div
          animate={(sending || deliberating) ? { opacity: 0.7, scale: 0.995 } : { opacity: 1, scale: 1 }}
          transition={{ duration: 0.1 }}
          className="rounded-[14px] border border-[var(--border)] bg-white flex items-center gap-2 px-4 py-3
                     focus-within:border-[var(--accent)] focus-within:shadow-[0_0_0_3px_var(--accent-glow)] transition-all"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => attachFile(e.target.files?.[0] || null)}
          />
          <button
            type="button"
            onClick={() => setShowCmds((value) => !value)}
            className={`p-1.5 rounded-[8px] transition-colors shrink-0
              ${
                showCommands
                  ? "bg-[var(--accent)] text-white"
                  : "text-[var(--text-3)] hover:text-[var(--accent)] hover:bg-[var(--accent-soft)]"
              }`}
            title="Quick commands"
          >
            <Zap size={14} />
          </button>
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className={`p-1.5 rounded-[8px] transition-colors shrink-0
              ${
                attachment
                  ? "bg-[var(--accent-soft)] text-[var(--accent)]"
                  : "text-[var(--text-3)] hover:text-[var(--accent)] hover:bg-[var(--accent-soft)]"
              }`}
            title="Attach image"
          >
            <Paperclip size={14} />
          </button>
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            onPaste={handlePaste}
            placeholder="問 CEO Agent 任何問題，或使用快速指令..."
            className="flex-1 bg-transparent text-[13px] text-[var(--text-1)] placeholder:text-[var(--text-3)] outline-none"
            disabled={sending}
          />
          <motion.button
            whileTap={{ scale: 0.88 }}
            onClick={() => void sendDeliberate()}
            disabled={!input.trim() || sending || deliberating}
            title="深度分析（多 Agent 協作）"
            className="p-1.5 rounded-[8px] text-[var(--text-3)] disabled:opacity-40 hover:text-[var(--accent)] hover:bg-[var(--accent-soft)] transition-colors shrink-0"
          >
            <Brain size={14} />
          </motion.button>
          <motion.button
            whileTap={{ scale: 0.88 }}
            onClick={() => void send(input)}
            disabled={(!input.trim() && !attachment) || sending || deliberating}
            className="p-1.5 rounded-[8px] bg-[var(--accent)] text-white disabled:opacity-40 hover:bg-[var(--accent-hover)] transition-colors shrink-0"
          >
            <Send size={14} />
          </motion.button>
        </motion.div>
      </div>

      <div className="w-64 shrink-0 flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <span className="text-[13px] font-600 text-[var(--text-2)]">Agent 狀態</span>
          <motion.button
            whileTap={{ rotate: 180 }}
            transition={{ duration: 0.3 }}
            onClick={() => void loadAgents()}
            className="p-1 rounded-[6px] hover:bg-[var(--bg-2)] transition-colors"
          >
            <RefreshCw size={12} className="text-[var(--text-3)]" />
          </motion.button>
        </div>

        {agents.length === 0 ? (
          <div className="rounded-[14px] border border-[var(--border)] bg-white p-4 text-center">
            <Search size={20} className="text-[var(--text-3)] mx-auto mb-2" />
            <p className="text-[12px] text-[var(--text-3)]">載入 Agent 中...</p>
          </div>
        ) : (
          <AnimatePresence>
            {agents.map((agent, index) => {
              const cfg = AGENT_CONFIG[agent.id] || { emoji: "AI", color: "#6b7280" };
              const status = STATUS_ICON[agent.status as AgentState] || STATUS_ICON.idle;
              const Icon = status.icon;
              const isRunning = agent.status === "running";
              return (
                <motion.div
                  key={agent.id}
                  custom={index}
                  variants={cardVariants}
                  initial="hidden"
                  animate="visible"
                  layout
                  className="rounded-[14px] border border-[var(--border)] bg-white p-3 transition-all"
                  style={isRunning ? { borderColor: cfg.color, boxShadow: `0 0 0 2px ${cfg.color}22` } : {}}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <motion.span
                      className="text-[11px] leading-none font-700"
                      animate={isRunning ? { scale: [1, 1.15, 1] } : { scale: 1 }}
                      transition={isRunning ? { repeat: Infinity, duration: 1.5 } : {}}
                      style={{ color: cfg.color }}
                    >
                      {cfg.emoji}
                    </motion.span>
                    <div className="flex-1 min-w-0">
                      <div className="text-[13px] font-600 text-[var(--text-1)]">{agent.name}</div>
                      <div className="text-[11px] text-[var(--text-3)] truncate">{agent.role || ""}</div>
                    </div>
                    <Icon size={13} style={{ color: status.color }} className={isRunning ? "animate-spin" : ""} />
                  </div>
                  <div className="flex items-center justify-between mt-1.5">
                    <span
                      className="text-[11px] font-600 px-1.5 py-0.5 rounded-full"
                      style={{ backgroundColor: `${status.color}18`, color: status.color }}
                    >
                      {status.label}
                    </span>
                  </div>
                  {agent.last_task && (
                    <p className="text-[11px] text-[var(--text-3)] mt-1.5 leading-relaxed line-clamp-2">
                      {agent.last_task}
                    </p>
                  )}
                </motion.div>
              );
            })}
          </AnimatePresence>
        )}

        <motion.div
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="rounded-[12px] bg-[var(--accent-soft)] border border-[var(--border)] p-3 mt-auto"
        >
          <p className="text-[11px] text-[var(--accent)] leading-relaxed">
            <strong>CEO Agent</strong>
            <br />
            傳送文字、截圖或貼上圖片，提供 CEO 路由器更多上下文。
            <br />
            快速指令讓日常操作一鍵完成。
          </p>
        </motion.div>
      </div>
    </div>
  );
}
