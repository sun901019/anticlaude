"use client";
import { useState, useEffect, useCallback } from "react";
import { AlertTriangle, AlertCircle, Info, RefreshCw, Activity } from "lucide-react";

type LogLevel = "ERROR" | "WARNING" | "ALL";

function parseLine(line: string): { level: "ERROR" | "WARNING" | "INFO" | "DEBUG"; time: string; msg: string } {
  const errorMatch = line.includes("| ERROR");
  const warnMatch = line.includes("| WARNING");
  const infoMatch = line.includes("| INFO");
  const level = errorMatch ? "ERROR" : warnMatch ? "WARNING" : infoMatch ? "INFO" : "DEBUG";
  // Try parse time from format "2026-03-17 08:00:01 | ..."
  const timeMatch = line.match(/^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/);
  const time = timeMatch ? timeMatch[1].split(" ")[1] : "";
  const msg = line;
  return { level, time, msg };
}

export default function SystemPage() {
  const [logs, setLogs] = useState<string[]>([]);
  const [date, setDate] = useState("");
  const [level, setLevel] = useState<LogLevel>("ERROR");
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchLogs = useCallback(async () => {
    try {
      const res = await fetch(`/api/system/logs?lines=200&level=${level}`, { cache: "no-store" });
      const data = await res.json();
      setLogs(data.logs || []);
      setDate(data.date || "");
      setLastRefresh(new Date());
    } catch {
      setLogs(["[連線錯誤] 無法取得日誌，請確認後端是否啟動"]);
    } finally {
      setLoading(false);
    }
  }, [level]);

  useEffect(() => {
    setLoading(true);
    fetchLogs();
  }, [fetchLogs]);

  useEffect(() => {
    if (!autoRefresh) return;
    const iv = setInterval(fetchLogs, 30000);
    return () => clearInterval(iv);
  }, [autoRefresh, fetchLogs]);

  const errorCount = logs.filter(l => l.includes("| ERROR")).length;
  const warnCount = logs.filter(l => l.includes("| WARNING")).length;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-1)]">系統日誌</h1>
          <p className="text-[13px] text-[var(--text-2)] mt-0.5">
            {date ? `${date} 日誌` : "今日日誌"} · 自動每 30 秒刷新
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/* Level filter */}
          <select
            value={level}
            onChange={e => setLevel(e.target.value as LogLevel)}
            className="px-3 py-1.5 text-[13px] rounded-[10px] border border-[var(--border)] bg-white text-[var(--text-1)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)] focus:ring-opacity-30"
          >
            <option value="ERROR">僅 ERROR</option>
            <option value="WARNING">ERROR + WARNING</option>
            <option value="ALL">全部</option>
          </select>

          {/* Auto refresh toggle */}
          <button
            onClick={() => setAutoRefresh(v => !v)}
            className={`flex items-center gap-1.5 px-3 py-1.5 text-[13px] rounded-[10px] border transition-colors ${
              autoRefresh
                ? "border-[var(--accent)] bg-[var(--accent-soft)] text-[var(--accent)]"
                : "border-[var(--border)] text-[var(--text-2)]"
            }`}
          >
            <Activity size={13} />
            {autoRefresh ? "自動刷新" : "手動"}
          </button>

          {/* Manual refresh */}
          <button
            onClick={() => { setLoading(true); fetchLogs(); }}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-[13px] rounded-[10px] bg-[var(--accent)] text-white hover:opacity-90 disabled:opacity-50"
          >
            <RefreshCw size={13} className={loading ? "animate-spin" : ""} />
            刷新
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="rounded-[14px] p-4 bg-red-50 border border-red-100">
          <div className="flex items-center gap-2 mb-1">
            <AlertCircle size={15} className="text-red-500" />
            <span className="text-[12px] font-600 text-red-500 uppercase tracking-wider">錯誤</span>
          </div>
          <div className="text-[28px] font-800 text-red-600">{errorCount}</div>
          <div className="text-[12px] text-red-400 mt-0.5">今日 ERROR 條數</div>
        </div>
        <div className="rounded-[14px] p-4 bg-amber-50 border border-amber-100">
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle size={15} className="text-amber-500" />
            <span className="text-[12px] font-600 text-amber-500 uppercase tracking-wider">警告</span>
          </div>
          <div className="text-[28px] font-800 text-amber-600">{warnCount}</div>
          <div className="text-[12px] text-amber-400 mt-0.5">今日 WARNING 條數</div>
        </div>
        <div className="rounded-[14px] p-4 bg-[var(--bg-2)] border border-[var(--border)]">
          <div className="flex items-center gap-2 mb-1">
            <Info size={15} className="text-[var(--text-3)]" />
            <span className="text-[12px] font-600 text-[var(--text-3)] uppercase tracking-wider">總計</span>
          </div>
          <div className="text-[28px] font-800 text-[var(--text-1)]">{logs.length}</div>
          <div className="text-[12px] text-[var(--text-3)] mt-0.5">顯示條數（最新 200）</div>
        </div>
      </div>

      {/* Log list */}
      <div className="rounded-[16px] border border-[var(--border)] bg-[#1a1a2e] overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3 border-b border-white/10">
          <span className="text-[12px] font-600 text-white/50 uppercase tracking-wider font-mono">
            {date}.log
          </span>
          {lastRefresh && (
            <span className="text-[11px] text-white/30 font-mono">
              更新：{lastRefresh.toLocaleTimeString("zh-TW")}
            </span>
          )}
        </div>

        <div className="overflow-auto max-h-[600px] p-4 space-y-0.5 font-mono text-[12px]">
          {loading ? (
            <div className="text-white/40 py-8 text-center">載入中...</div>
          ) : logs.length === 0 ? (
            <div className="text-white/40 py-8 text-center">
              {level === "ERROR" ? "今日暫無 ERROR 記錄" : "今日暫無日誌記錄"}
            </div>
          ) : (
            [...logs].reverse().map((line, i) => {
              const { level: lv } = parseLine(line);
              return (
                <div
                  key={i}
                  className={`px-3 py-1.5 rounded-[6px] leading-relaxed break-all ${
                    lv === "ERROR"
                      ? "bg-red-500/15 text-red-300"
                      : lv === "WARNING"
                      ? "bg-amber-500/15 text-amber-300"
                      : lv === "INFO"
                      ? "text-white/60"
                      : "text-white/30"
                  }`}
                >
                  {line}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
