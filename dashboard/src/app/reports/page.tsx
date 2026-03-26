"use client";
import { useState, useEffect } from "react";
import {
  fetchLatestWeekly, fetchWeeklyList, fetchWeekly,
  triggerWeekly, getWeeklyStatus, fetchPostStats,
} from "@/lib/api";
import ReactMarkdown from "react-markdown";
import { FileText, RefreshCw, BarChart2 } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

type CategoryRow = {
  category: string;
  post_type: string | null;
  count: number;
  avg_views: number;
  avg_engagement: number;
};

type StatsData = {
  rows: CategoryRow[];
};

const ACCENT = "#7c5cbf";
const BAR_COLORS = [ACCENT, "#9b6bdf", "#b48ae8", "#caa8f0", "#dcc5f5"];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="card-sm px-3 py-2 text-xs shadow-xl">
      <p className="text-[var(--text-2)] mb-1 font-medium">{label || "未分類"}</p>
      <p className="text-[var(--text-1)]">平均互動率：{payload[0]?.value?.toFixed(2)}%</p>
      <p className="text-[var(--text-3)]">貼文數：{payload[0]?.payload?.count}</p>
    </div>
  );
};

export default function ReportsPage() {
  const [content, setContent] = useState<string | null>(null);
  const [currentWeek, setCurrentWeek] = useState<string>("");
  const [weekList, setWeekList] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [lastGeneratedAt, setLastGeneratedAt] = useState<string | null>(null);
  const [stats, setStats] = useState<StatsData | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const [latest, list, postStats] = await Promise.all([
          fetchLatestWeekly(),
          fetchWeeklyList(),
          fetchPostStats(7),
        ]);
        if (latest.content) {
          setContent(latest.content);
          setCurrentWeek(latest.week || "");
          setLastGeneratedAt(latest.last_generated_at || null);
        }
        setWeekList(list.reports || []);
        if (postStats?.stats?.rows) setStats(postStats.stats);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  useEffect(() => {
    if (!generating) return;
    const interval = setInterval(async () => {
      const s = await getWeeklyStatus();
      if (!s.running) {
        setGenerating(false);
        const [latest, list] = await Promise.all([fetchLatestWeekly(), fetchWeeklyList()]);
        if (latest.content) {
          setContent(latest.content);
          setCurrentWeek(latest.week || "");
          setLastGeneratedAt(latest.last_generated_at || null);
        }
        setWeekList(list.reports || []);
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [generating]);

  const handleGenerate = async () => {
    setGenerating(true);
    await triggerWeekly();
  };

  const handleSelect = async (week: string) => {
    const d = await fetchWeekly(week);
    setContent(d.content || null);
    setCurrentWeek(week);
  };

  // Prepare chart data — top 5 categories by engagement, label empty category
  const chartData = (stats?.rows ?? [])
    .filter((r) => r.avg_engagement > 0)
    .slice(0, 6)
    .map((r) => ({
      name: r.category || "未分類",
      avg_engagement: r.avg_engagement,
      count: r.count,
    }));

  const totalPosts = stats?.rows.reduce((s, r) => s + r.count, 0) ?? 0;
  const topCategory = stats?.rows[0]?.category || "—";
  const avgEng = stats?.rows.length
    ? (stats.rows.reduce((s, r) => s + r.avg_engagement * r.count, 0) / Math.max(totalPosts, 1)).toFixed(2)
    : null;

  const statPills = [
    { label: "貼文數", value: totalPosts },
    { label: "加權平均互動率", value: avgEng != null ? `${avgEng}%` : "—" },
    { label: "最佳主題", value: topCategory, accent: true },
  ];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-1)]">週報</h1>
          <p className="text-[13px] text-[var(--text-2)] mt-0.5">
            內容策略分析與建議
            {lastGeneratedAt && (
              <span className="ml-2 text-[var(--text-3)]">· 上次生成：{lastGeneratedAt}</span>
            )}
          </p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="flex items-center gap-2 px-4 py-2 text-[13px] rounded-full bg-[var(--accent)] hover:opacity-90 text-white disabled:opacity-50 font-medium shadow-lg shadow-violet-500/20"
        >
          <RefreshCw size={13} className={generating ? "animate-spin" : ""} />
          {generating ? "生成中..." : "生成週報"}
        </button>
      </div>

      {/* ── 近 7 天績效摘要 ── */}
      {(chartData.length > 0 || totalPosts > 0) && (
        <div className="card-sm p-5 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <BarChart2 size={14} className="text-[var(--accent)]" />
            <span className="text-[12px] font-semibold text-[var(--text-2)] uppercase tracking-wider">近 7 天績效摘要</span>
          </div>

          {/* Stat pills */}
          <div className="flex gap-3 mb-5 flex-wrap">
            {statPills.map(({ label, value, accent }) => (
              <div key={label} className="flex flex-col px-4 py-2.5 rounded-xl bg-[var(--bg-2)] border border-[var(--border)]">
                <span className="text-[10px] text-[var(--text-3)] uppercase tracking-wider">{label}</span>
                <span className={`font-bold leading-none mt-0.5 max-w-[140px] truncate ${accent ? "text-lg text-[var(--accent)]" : "text-xl text-[var(--text-1)]"}`}>
                  {value}
                </span>
              </div>
            ))}
          </div>

          {/* Bar chart — category engagement */}
          {chartData.length > 0 && (
            <div>
              <p className="text-[11px] text-[var(--text-3)] mb-2">各主題平均互動率（%）</p>
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={chartData} layout="vertical" margin={{ left: 8, right: 24, top: 0, bottom: 0 }}>
                  <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={(v) => `${v}%`} />
                  <YAxis
                    type="category"
                    dataKey="name"
                    width={80}
                    tick={{ fontSize: 11, fill: "var(--text-2)" }}
                  />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: "rgba(124,92,191,0.06)" }} />
                  <Bar dataKey="avg_engagement" radius={[0, 4, 4, 0]}>
                    {chartData.map((_, i) => (
                      <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      <div className="flex gap-5">
        {/* Week list */}
        {weekList.length > 0 && (
          <div className="w-44 shrink-0">
            <p className="text-[11px] text-[var(--text-3)] mb-2 uppercase tracking-wider font-medium">歷史週報</p>
            <div className="space-y-1">
              {weekList.map((w) => (
                <button
                  key={w}
                  onClick={() => handleSelect(w)}
                  className={`w-full text-left px-3 py-2 text-[12px] rounded-lg transition-colors font-medium ${
                    currentWeek === w
                      ? "bg-[var(--accent)] text-white"
                      : "bg-[var(--bg-2)] text-[var(--text-2)] hover:text-[var(--text-1)] border border-[var(--border)]"
                  }`}
                >
                  {w}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          {loading ? (
            <div className="flex items-center justify-center h-64 text-[var(--text-3)]">載入中...</div>
          ) : !content ? (
            <div className="flex flex-col items-center justify-center h-64 gap-4">
              <div className="w-16 h-16 rounded-2xl bg-[var(--bg-2)] flex items-center justify-center">
                <FileText size={28} className="text-[var(--text-3)]" />
              </div>
              <p className="text-[var(--text-3)] text-sm">尚無週報</p>
              <button
                onClick={handleGenerate}
                disabled={generating}
                className="px-5 py-2.5 rounded-full bg-[var(--accent)] text-white text-[13px] font-medium disabled:opacity-50"
              >
                {generating ? "生成中..." : "立即生成"}
              </button>
            </div>
          ) : (
            <div className="card-sm p-6">
              {currentWeek && (
                <p className="text-[11px] text-[var(--text-3)] mb-4 uppercase tracking-wider font-medium">{currentWeek}</p>
              )}
              <div className="prose prose-sm max-w-none text-[var(--text-1)]
                [&_h1]:text-[var(--text-1)] [&_h2]:text-[var(--text-1)] [&_h3]:text-[var(--text-1)]
                [&_p]:text-[var(--text-2)] [&_li]:text-[var(--text-2)]
                [&_strong]:text-[var(--text-1)] [&_a]:text-[var(--accent)]">
                <ReactMarkdown>{content}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
