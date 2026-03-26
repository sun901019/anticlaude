"use client";
import { useState, useEffect, useCallback } from "react";
import { ChevronLeft, ChevronRight, Circle, CheckCircle2, FileText, CalendarDays } from "lucide-react";
import { fetchContentCalendar } from "@/lib/api";

type DayStatus = "published" | "draft" | "empty";
type CalendarData = { year: number; month: number; days: Record<string, DayStatus> };

const WEEKDAYS = ["日", "一", "二", "三", "四", "五", "六"];
const MONTH_NAMES = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"];

function getDaysInMonth(year: number, month: number) {
  return new Date(year, month, 0).getDate();
}
function getFirstWeekday(year: number, month: number) {
  return new Date(year, month - 1, 1).getDay();
}

const STATUS_CONFIG: Record<DayStatus, { dot: string; bg: string; label: string }> = {
  published: { dot: "bg-emerald-400", bg: "bg-emerald-50 border-emerald-200", label: "已發布" },
  draft:     { dot: "bg-amber-400",   bg: "bg-amber-50 border-amber-200",     label: "草稿待發" },
  empty:     { dot: "bg-gray-200",    bg: "",                                  label: "無內容" },
};

export default function CalendarPage() {
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [data, setData] = useState<CalendarData | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async (y: number, m: number) => {
    setLoading(true);
    try {
      const d = await fetchContentCalendar(y, m);
      setData(d);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(year, month); }, [load, year, month]);

  const prev = () => {
    if (month === 1) { setYear(y => y - 1); setMonth(12); }
    else setMonth(m => m - 1);
  };
  const next = () => {
    if (month === 12) { setYear(y => y + 1); setMonth(1); }
    else setMonth(m => m + 1);
  };

  const days = data?.days || {};
  const daysInMonth = getDaysInMonth(year, month);
  const firstWeekday = getFirstWeekday(year, month);

  // Stats
  const publishedCount = Object.values(days).filter(s => s === "published").length;
  const draftCount = Object.values(days).filter(s => s === "draft").length;
  const emptyCount = Object.values(days).filter(s => s === "empty").length;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-1)]">內容日曆</h1>
          <p className="text-[13px] text-[var(--text-2)] mt-0.5">每日發布狀況一覽</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="rounded-[14px] p-4 bg-emerald-50 border border-emerald-100">
          <div className="flex items-center gap-2 mb-1">
            <CheckCircle2 size={15} className="text-emerald-500" />
            <span className="text-[12px] font-600 text-emerald-600 uppercase tracking-wider">已發布</span>
          </div>
          <div className="text-[28px] font-800 text-emerald-700">{publishedCount}</div>
          <div className="text-[12px] text-emerald-400 mt-0.5">本月天數</div>
        </div>
        <div className="rounded-[14px] p-4 bg-amber-50 border border-amber-100">
          <div className="flex items-center gap-2 mb-1">
            <FileText size={15} className="text-amber-500" />
            <span className="text-[12px] font-600 text-amber-600 uppercase tracking-wider">草稿待發</span>
          </div>
          <div className="text-[28px] font-800 text-amber-700">{draftCount}</div>
          <div className="text-[12px] text-amber-400 mt-0.5">有草稿未發布</div>
        </div>
        <div className="rounded-[14px] p-4 bg-[var(--bg-2)] border border-[var(--border)]">
          <div className="flex items-center gap-2 mb-1">
            <CalendarDays size={15} className="text-[var(--text-3)]" />
            <span className="text-[12px] font-600 text-[var(--text-3)] uppercase tracking-wider">發布率</span>
          </div>
          <div className="text-[28px] font-800 text-[var(--text-1)]">
            {daysInMonth > 0 ? `${Math.round((publishedCount / daysInMonth) * 100)}%` : "—"}
          </div>
          <div className="text-[12px] text-[var(--text-3)] mt-0.5">本月發布天數比</div>
        </div>
      </div>

      {/* Calendar */}
      <div className="rounded-[16px] border border-[var(--border)] bg-white overflow-hidden">
        {/* Month nav */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)]">
          <button onClick={prev} className="p-2 rounded-[8px] hover:bg-[var(--bg-2)] transition-colors">
            <ChevronLeft size={16} className="text-[var(--text-2)]" />
          </button>
          <span className="text-[16px] font-700 text-[var(--text-1)]">
            {year} 年 {MONTH_NAMES[month - 1]}
          </span>
          <button onClick={next} className="p-2 rounded-[8px] hover:bg-[var(--bg-2)] transition-colors">
            <ChevronRight size={16} className="text-[var(--text-2)]" />
          </button>
        </div>

        {/* Weekday headers */}
        <div className="grid grid-cols-7 border-b border-[var(--border)]">
          {WEEKDAYS.map((d, i) => (
            <div key={d} className={`py-3 text-center text-[12px] font-600 ${i === 0 || i === 6 ? "text-red-400" : "text-[var(--text-3)]"}`}>
              {d}
            </div>
          ))}
        </div>

        {/* Day grid */}
        {loading ? (
          <div className="h-64 flex items-center justify-center text-[var(--text-3)] text-[13px]">載入中...</div>
        ) : (
          <div className="grid grid-cols-7">
            {/* Empty cells before first day */}
            {Array.from({ length: firstWeekday }).map((_, i) => (
              <div key={`empty-${i}`} className="h-20 border-b border-r border-[var(--border)] bg-[var(--bg-2)]" />
            ))}
            {/* Day cells */}
            {Array.from({ length: daysInMonth }).map((_, i) => {
              const d = i + 1;
              const dateStr = `${year}-${String(month).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
              const status: DayStatus = days[dateStr] || "empty";
              const cfg = STATUS_CONFIG[status];
              const isToday = dateStr === now.toISOString().slice(0, 10);
              const weekday = (firstWeekday + i) % 7;
              const isWeekend = weekday === 0 || weekday === 6;

              return (
                <div
                  key={dateStr}
                  className={`h-20 border-b border-r border-[var(--border)] p-2 relative transition-colors
                    ${status !== "empty" ? cfg.bg + " border " : ""}
                    ${isWeekend && status === "empty" ? "bg-gray-50/50" : ""}
                  `}
                >
                  <div className={`text-[13px] font-600 mb-1 inline-flex items-center justify-center w-6 h-6 rounded-full
                    ${isToday ? "bg-[var(--accent)] text-white" : isWeekend ? "text-red-400" : "text-[var(--text-2)]"}
                  `}>
                    {d}
                  </div>
                  {status !== "empty" && (
                    <div className="flex items-center gap-1">
                      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
                      <span className={`text-[10px] font-600 ${status === "published" ? "text-emerald-600" : "text-amber-600"}`}>
                        {cfg.label}
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Legend */}
        <div className="flex items-center gap-6 px-6 py-3 border-t border-[var(--border)] bg-[var(--bg-2)]">
          {Object.entries(STATUS_CONFIG).filter(([k]) => k !== "empty").map(([key, cfg]) => (
            <div key={key} className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${cfg.dot}`} />
              <span className="text-[12px] text-[var(--text-3)]">{cfg.label}</span>
            </div>
          ))}
          <div className="flex items-center gap-1.5 ml-auto">
            <span className="w-2 h-2 rounded-full bg-gray-200" />
            <span className="text-[12px] text-[var(--text-3)]">無內容</span>
          </div>
        </div>
      </div>
    </div>
  );
}
