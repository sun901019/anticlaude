"use client";
import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { fetchInsights, triggerFeedback, getFeedbackStatus } from "@/lib/api";
import { Brain, Loader2, RefreshCw } from "lucide-react";

const DAYS = ["一", "二", "三", "四", "五", "六", "日"];
const PERIODS = [
  { label: "早晨", hours: [6, 7, 8, 9] },
  { label: "上午", hours: [10, 11, 12] },
  { label: "下午", hours: [13, 14, 15, 16, 17] },
  { label: "晚上", hours: [18, 19, 20, 21, 22, 23] },
];

const DAY_MAP: Record<string, number> = {
  "週一": 0, "週二": 1, "週三": 2, "週四": 3, "週五": 4, "週六": 5, "週日": 6,
  "一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6,
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="card-sm px-3 py-2.5 text-xs shadow-xl">
      <p className="text-[var(--text-2)] mb-1 font-medium">{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} style={{ color: p.color }}>{p.name}：{p.value}</p>
      ))}
    </div>
  );
};

export default function InsightsPage() {
  const [insights, setInsights] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const d = await fetchInsights();
      setInsights(d.insights);
    } catch {}
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const handleRun = async () => {
    setRunning(true);
    await triggerFeedback(30);
    let waited = 0;
    const poll = setInterval(async () => {
      waited += 2;
      try {
        const { running: r } = await getFeedbackStatus();
        if (!r || waited >= 120) {
          clearInterval(poll);
          setRunning(false);
          await load();
        }
      } catch { clearInterval(poll); setRunning(false); }
    }, 2000);
  };

  const catData = (() => {
    if (!insights?.category_performance) return [];
    return Object.entries(insights.category_performance as Record<string, any>)
      .map(([name, v]: [string, any]) => ({
        name: name.length > 6 ? name.slice(0, 6) + "…" : name,
        fullName: name,
        avg_views: v.avg_views ?? 0,
        avg_engagement: v.avg_engagement ?? 0,
        count: v.count ?? 0,
      }))
      .sort((a, b) => b.avg_views - a.avg_views);
  })();

  const topHooks: string[] = (() => {
    if (!insights?.effective_hashtags) return [];
    const h = insights.effective_hashtags;
    return Array.isArray(h) ? h : (typeof h === "string" ? JSON.parse(h) : []);
  })();

  const bestDayIdx = insights?.best_posting_day ? (DAY_MAP[insights.best_posting_day] ?? -1) : -1;
  const bestHour = insights?.best_posting_hour ?? -1;
  const bestPeriodIdx = bestHour < 0 ? -1 : PERIODS.findIndex(p => p.hours.includes(bestHour));

  const trendColor = insights?.engagement_trend === "up"
    ? "text-[var(--green)]"
    : insights?.engagement_trend === "down"
    ? "text-[var(--red)]"
    : "text-[var(--text-3)]";

  return (
    <div className="">
      {/* Header */}
      <div className="flex items-start justify-between mb-7">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-1)] flex items-center gap-2">
            <Brain size={20} className="text-[var(--accent)]" />
            閉環洞察
          </h1>
          <p className="text-[13px] text-[var(--text-2)] mt-0.5">
            {insights?.analysis_date
              ? `上次分析：${insights.analysis_date}`
              : "AI 受眾偏好分析報告"}
          </p>
        </div>
        <button onClick={handleRun} disabled={running}
          className="flex items-center gap-2 px-5 py-2 text-[13px] rounded-full bg-[var(--accent)] hover:opacity-90 text-white disabled:opacity-50 transition-all font-medium shadow-lg shadow-violet-500/20">
          {running ? <Loader2 size={13} className="animate-spin" /> : <RefreshCw size={13} />}
          {running ? "分析中..." : "重新分析"}
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64 text-[var(--text-3)]">
          <Loader2 size={20} className="animate-spin mr-2" />載入中...
        </div>
      ) : !insights ? (
        <div className="flex flex-col items-center justify-center h-72 gap-5 animate-fade-in">
          <div className="w-16 h-16 rounded-2xl bg-[var(--accent-soft)] flex items-center justify-center">
            <Brain size={28} className="text-[var(--accent)]" />
          </div>
          <div className="text-center">
            <p className="text-[var(--text-1)] text-sm font-semibold">還沒有受眾洞察數據</p>
            <p className="text-[var(--text-3)] text-xs mt-1">需要先累積貼文數據，再執行回饋分析</p>
          </div>
          <button onClick={handleRun} disabled={running}
            className="flex items-center gap-2 px-6 py-2.5 rounded-full bg-[var(--accent)] hover:opacity-90 text-white text-[13px] font-medium disabled:opacity-50 shadow-lg shadow-violet-500/20">
            {running ? <Loader2 size={14} className="animate-spin" /> : <Brain size={14} />}
            {running ? "分析中..." : "開始分析"}
          </button>
        </div>
      ) : (
        <div className="space-y-5 animate-slide-up">
          {/* Summary stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: "最佳發文日", value: insights.best_posting_day || "—", color: "" },
              { label: "最佳時段", value: insights.best_posting_hour != null ? `${insights.best_posting_hour}:00` : "—", color: "" },
              { label: "互動趨勢", value: insights.engagement_trend === "up" ? "↑ 上升" : insights.engagement_trend === "down" ? "↓ 下降" : "→ 持平", color: trendColor },
              { label: "成長率", value: insights.growth_rate != null ? `${insights.growth_rate}%` : "—", color: "" },
            ].map(item => (
              <div key={item.label} className="card-sm p-4 text-center">
                <p className="text-[10px] text-[var(--text-3)] mb-1.5 uppercase tracking-wider font-medium">{item.label}</p>
                <p className={`text-xl font-bold ${item.color || "text-[var(--text-1)]"}`}>{item.value}</p>
              </div>
            ))}
          </div>

          {/* Category performance bar chart */}
          {catData.length > 0 && (
            <div className="card-sm p-5">
              <h2 className="text-[11px] font-semibold text-[var(--text-2)] mb-4 uppercase tracking-widest">類別表現排名</h2>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={catData} layout="vertical" margin={{ left: 8, right: 16 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ede8df" horizontal={false} />
                  <XAxis type="number" tick={{ fill: "#78716c", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis type="category" dataKey="name" tick={{ fill: "#57534e", fontSize: 11 }} axisLine={false} tickLine={false} width={52} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="avg_views" name="平均觀看" radius={[0, 4, 4, 0]}>
                    {catData.map((_, i) => (
                      <Cell key={i} fill={i === 0 ? "#7c5cbf" : i === 1 ? "#9b6bdf" : "#c4b5fd"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Posting heatmap */}
          <div className="card-sm p-5">
            <h2 className="text-[11px] font-semibold text-[var(--text-2)] mb-4 uppercase tracking-widest">最佳發文時段</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-center">
                <thead>
                  <tr>
                    <th className="text-[10px] text-[var(--text-3)] pb-2 pr-3 font-normal text-left">時段</th>
                    {DAYS.map((d, di) => (
                      <th key={d} className={`text-[11px] pb-2 font-semibold px-1 ${di === bestDayIdx ? "text-[var(--accent)]" : "text-[var(--text-3)]"}`}>
                        週{d}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {PERIODS.map((period, pi) => (
                    <tr key={period.label}>
                      <td className={`text-[11px] pr-3 py-2 text-left font-medium ${pi === bestPeriodIdx ? "text-[var(--accent)]" : "text-[var(--text-3)]"}`}>
                        {period.label}
                      </td>
                      {DAYS.map((_, di) => {
                        const isHighlight = di === bestDayIdx && pi === bestPeriodIdx;
                        const isDayMatch = di === bestDayIdx;
                        const isPeriodMatch = pi === bestPeriodIdx;
                        return (
                          <td key={di} className="px-1 py-2">
                            <div className={`w-8 h-8 mx-auto rounded-lg flex items-center justify-center text-[10px] font-bold transition-all ${
                              isHighlight
                                ? "bg-[var(--accent)] text-white shadow-md shadow-violet-300 animate-pulse-glow"
                                : isDayMatch && isPeriodMatch
                                ? "bg-violet-100 text-violet-700"
                                : isDayMatch || isPeriodMatch
                                ? "bg-[var(--bg-2)] text-[var(--text-2)]"
                                : "bg-[var(--bg-2)] text-[var(--text-3)]"
                            }`}>
                              {isHighlight ? "★" : "·"}
                            </div>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-[10px] text-[var(--text-3)] mt-3">★ 最佳發文時段（{insights.best_posting_day} {insights.best_posting_hour}:00）</p>
          </div>

          {/* Effective hashtags */}
          {topHooks.length > 0 && (
            <div className="card-sm p-5">
              <h2 className="text-[11px] font-semibold text-[var(--text-2)] mb-4 uppercase tracking-widest">有效 Hashtag</h2>
              <div className="flex flex-wrap gap-2">
                {topHooks.map((tag, i) => (
                  <span key={i}
                    className="text-[12px] px-3 py-1.5 rounded-full border border-violet-200 text-violet-700 bg-violet-50 font-medium animate-slide-up"
                    style={{ animationDelay: `${i * 50}ms` }}>
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Strategic summary */}
          {insights.strategic_summary && (
            <div className="card-sm p-5 border-l-4 border-l-[var(--accent)]">
              <h2 className="text-[11px] font-semibold text-[var(--text-2)] mb-3 uppercase tracking-widest">策略建議</h2>
              <p className="text-[13px] text-[var(--text-1)] leading-relaxed">{insights.strategic_summary}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
