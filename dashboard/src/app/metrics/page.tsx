"use client";
import { useState, useEffect } from "react";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend, ReferenceLine, BarChart, Bar, Cell,
} from "recharts";
import { fetchMetrics, triggerTracker, getTrackerStatus, fetchInsights, triggerFeedback, getFeedbackStatus, fetchContentFeedback, BACKEND } from "@/lib/api";
import { BarChart2, Brain, Loader2, TrendingUp, TrendingDown, Minus, Package, ShoppingCart, ArrowRight, Zap } from "lucide-react";

const API = BACKEND;

type Post = {
  post_id: string; text: string; timestamp: string; media_type: string;
  views: number; likes: number; replies: number; reposts: number; quotes: number; engagement_rate: number;
};

type EcomProduct = {
  sku: string; name: string; role: string | null; status: string;
  revenue_7d: number; sales_7d: number; ad_spend_7d: number;
  gross_margin: number; safe_cpa: number; roas: number | null;
  stock: number; days_left: number | null; current_price: number;
};

type EcomData = {
  total_revenue_7d: number; total_profit_est: number; product_count: number;
  products: EcomProduct[];
};

type FunnelStage = { stage: string; label: string; count: number };

function StatCard({ label, value, sub, trend }: { label: string; value: string | number; sub?: string; trend?: "up" | "down" | "flat" }) {
  return (
    <div className="card-sm p-4">
      <p className="text-[11px] text-[var(--text-2)] mb-1 uppercase tracking-wider font-medium">{label}</p>
      <div className="flex items-end gap-2">
        <p className="text-2xl font-bold text-[var(--text-1)] leading-none">{value}</p>
        {trend && (
          <span className={`mb-0.5 ${trend === "up" ? "text-[var(--green)]" : trend === "down" ? "text-[var(--red)]" : "text-[var(--text-3)]"}`}>
            {trend === "up" ? <TrendingUp size={14} /> : trend === "down" ? <TrendingDown size={14} /> : <Minus size={14} />}
          </span>
        )}
      </div>
      {sub && <p className="text-[11px] text-[var(--text-3)] mt-0.5">{sub}</p>}
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="card-sm px-3 py-2.5 text-xs shadow-xl">
      <p className="text-[var(--text-2)] mb-1.5 font-medium">{label}</p>
      {payload.map((p: any) => (
        <p key={p.name} className="flex items-center gap-2" style={{ color: p.color }}>
          <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: p.color }} />
          {p.name}：{typeof p.value === "number" ? p.value.toFixed(2) : p.value}
        </p>
      ))}
    </div>
  );
};

const ROLE_COLORS: Record<string, string> = {
  "主力款": "#16a34a", "毛利款": "#7c5cbf", "引流款": "#f59e0b", "測試款": "#94a3b8",
};

const FUNNEL_COLORS = [
  "#e2dbd0","#d4c9bc","#c4b5a1","#b59285","#a07060",
  "#7c5cbf","#6d4fb3","#5c41a8","#4a34a0","#3a2898",
];

export default function MetricsPage() {
  const [tab, setTab] = useState<"content" | "ecom" | "funnel" | "feedback">("content");

  // Content tab state
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [days, setDays] = useState(30);
  const [sort, setSort] = useState<keyof Post>("timestamp");
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [insights, setInsights] = useState<any>(null);
  const [feedbackRunning, setFeedbackRunning] = useState(false);

  // Ecom tab state
  const [ecomData, setEcomData] = useState<EcomData | null>(null);
  const [ecomLoading, setEcomLoading] = useState(false);
  const [alerts, setAlerts] = useState<{sku: string; name: string; issues: string[]}[]>([]);
  const [alertChecked, setAlertChecked] = useState(false);
  const [perfHistory, setPerfHistory] = useState<{record_date: string; sku: string; name: string; revenue_7d: number; gross_margin: number}[]>([]);

  // Funnel tab state
  const [funnelData, setFunnelData] = useState<FunnelStage[]>([]);
  const [funnelLoading, setFunnelLoading] = useState(false);

  // Feedback tab state
  const [feedbackData, setFeedbackData] = useState<any>(null);
  const [feedbackLoading, setFeedbackLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetchMetrics(days).then(d => setPosts(d.data || [])).finally(() => setLoading(false));
  }, [days]);

  useEffect(() => {
    fetchInsights().then(d => setInsights(d.insights)).catch(() => {});
  }, []);

  useEffect(() => {
    if (tab === "ecom" && !ecomData) {
      setEcomLoading(true);
      Promise.all([
        fetch(`${API}/api/stats/monthly-ecommerce`).then(r => r.json()),
        fetch(`${API}/api/ecommerce/alerts`).then(r => r.json()),
        fetch(`${API}/api/ecommerce/performance-history`).then(r => r.json()),
      ])
        .then(([ecom, alertsRes, hist]) => {
          setEcomData(ecom);
          setAlerts(alertsRes.alerts || []);
          setAlertChecked(true);
          setPerfHistory(hist.history || []);
        })
        .catch(() => {})
        .finally(() => setEcomLoading(false));
    }
    if (tab === "funnel" && funnelData.length === 0) {
      setFunnelLoading(true);
      fetch(`${API}/api/ecommerce/funnel`)
        .then(r => r.json()).then(d => setFunnelData(d.funnel || [])).catch(() => {}).finally(() => setFunnelLoading(false));
    }
    if (tab === "feedback" && !feedbackData) {
      setFeedbackLoading(true);
      fetchContentFeedback(90).then(setFeedbackData).catch(() => {}).finally(() => setFeedbackLoading(false));
    }
  }, [tab]);

  const handleTracker = async () => {
    setRunning(true);
    await triggerTracker();
    let waited = 0;
    const poll = setInterval(async () => {
      waited += 2;
      try {
        const { running: r } = await getTrackerStatus();
        if (!r || waited >= 120) {
          clearInterval(poll);
          setRunning(false);
          const d = await fetchMetrics(days);
          setPosts(d.data || []);
        }
      } catch { clearInterval(poll); setRunning(false); }
    }, 2000);
  };

  const handleFeedback = async () => {
    setFeedbackRunning(true);
    await triggerFeedback(30);
    let waited = 0;
    const poll = setInterval(async () => {
      waited += 2;
      try {
        const { running: r } = await getFeedbackStatus();
        if (!r || waited >= 120) {
          clearInterval(poll);
          setFeedbackRunning(false);
          const d = await fetchInsights();
          setInsights(d.insights);
        }
      } catch { clearInterval(poll); setFeedbackRunning(false); }
    }, 2000);
  };

  const chartData = (() => {
    const byDate: Record<string, number[]> = {};
    posts.forEach(p => {
      const d = p.timestamp?.slice(0, 10) || "unknown";
      if (!byDate[d]) byDate[d] = [];
      byDate[d].push(p.engagement_rate);
    });
    return Object.entries(byDate).sort(([a], [b]) => a.localeCompare(b)).slice(-30).map(([date, rates]) => ({
      date: date.slice(5),
      avg_engagement: +(rates.reduce((a, b) => a + b, 0) / rates.length).toFixed(2),
      likes: posts.filter(p => p.timestamp?.startsWith(date)).reduce((a, p) => a + p.likes, 0),
    }));
  })();

  const totalViews = posts.reduce((a, p) => a + p.views, 0);
  const totalLikes = posts.reduce((a, p) => a + p.likes, 0);
  const avgEng = posts.length ? (posts.reduce((a, p) => a + p.engagement_rate, 0) / posts.length).toFixed(2) : "0";
  const avgLine = parseFloat(avgEng);

  const sorted = [...posts].sort((a, b) => {
    const av = a[sort] as any, bv = b[sort] as any;
    return typeof av === "number" ? bv - av : String(bv).localeCompare(String(av));
  });

  const marginChartData = ecomData?.products.map(p => ({
    name: p.name.length > 8 ? p.name.slice(0, 8) + "…" : p.name,
    毛利率: +(p.gross_margin * 100).toFixed(1),
    週營收: p.revenue_7d,
    role: p.role || "測試款",
  })) || [];

  const funnelTotal = funnelData.reduce((a, s) => a + s.count, 0) || 1;

  return (
    <div className="">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-1)]">績效中心</h1>
          <p className="text-[13px] text-[var(--text-2)] mt-0.5">內容 · 電商 · 選品數據</p>
        </div>
        {tab === "content" && (
          <div className="flex gap-2 items-center">
            <select value={days} onChange={e => setDays(+e.target.value)}
              className="text-[13px] border border-[var(--border)] rounded-lg px-3 py-2 bg-[var(--surface)] text-[var(--text-1)] outline-none">
              <option value={7}>近 7 天</option>
              <option value={30}>近 30 天</option>
              <option value={90}>近 90 天</option>
            </select>
            <button onClick={handleTracker} disabled={running}
              className="flex items-center gap-2 px-4 py-2 text-[13px] rounded-full bg-[var(--accent)] hover:opacity-90 text-white disabled:opacity-50 transition-all font-medium shadow-lg shadow-violet-500/20">
              {running ? <Loader2 size={13} className="animate-spin" /> : <BarChart2 size={13} />}
              {running ? "抓取中..." : "更新數據"}
            </button>
          </div>
        )}
        {tab === "ecom" && (
          <button onClick={() => { setEcomData(null); setEcomLoading(true); fetch(`${API}/api/stats/monthly-ecommerce`).then(r=>r.json()).then(setEcomData).catch(()=>{}).finally(()=>setEcomLoading(false)); }}
            className="flex items-center gap-2 px-4 py-2 text-[13px] rounded-full bg-[var(--accent)] hover:opacity-90 text-white transition-all font-medium shadow-lg shadow-violet-500/20">
            <ShoppingCart size={13} />重新整理
          </button>
        )}
        {tab === "funnel" && (
          <button onClick={() => { setFunnelData([]); setFunnelLoading(true); fetch(`${API}/api/ecommerce/funnel`).then(r=>r.json()).then(d=>setFunnelData(d.funnel||[])).catch(()=>{}).finally(()=>setFunnelLoading(false)); }}
            className="flex items-center gap-2 px-4 py-2 text-[13px] rounded-full bg-[var(--accent)] hover:opacity-90 text-white transition-all font-medium shadow-lg shadow-violet-500/20">
            <Package size={13} />重新整理
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-5 bg-[var(--bg-2)] rounded-xl p-1 w-fit">
        {(["content","ecom","funnel","feedback"] as const).map(t => (
          <button key={t} onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded-lg text-[12px] font-medium transition-all ${tab === t ? "bg-[var(--surface)] text-[var(--text-1)] shadow-sm" : "text-[var(--text-3)] hover:text-[var(--text-2)]"}`}>
            {t === "content" ? "內容績效" : t === "ecom" ? "電商績效" : t === "funnel" ? "選品漏斗" : "效果回饋"}
          </button>
        ))}
      </div>

      {/* ── Content Tab ── */}
      {tab === "content" && (
        loading ? (
          <div className="flex items-center justify-center h-64 text-[var(--text-3)]">
            <Loader2 size={20} className="animate-spin mr-2" />載入中...
          </div>
        ) : posts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 gap-4 text-[var(--text-3)]">
            <p>尚無數據</p>
            <button onClick={handleTracker} className="px-5 py-2 rounded-full bg-[var(--accent)] text-white text-[13px] font-medium">
              立即抓取
            </button>
          </div>
        ) : (
          <div className="space-y-5">
            <div className="grid grid-cols-3 gap-4">
              <StatCard label="總觀看數" value={totalViews.toLocaleString()} trend="up" />
              <StatCard label="總按讚數" value={totalLikes.toLocaleString()} />
              <StatCard label="平均互動率" value={`${avgEng}%`} sub={`${posts.length} 篇貼文`} />
            </div>

            <div className="card-sm p-5">
              <h2 className="text-[11px] font-semibold text-[var(--text-2)] mb-4 uppercase tracking-widest">互動率趨勢</h2>
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="engGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#7c5cbf" stopOpacity={0.25} />
                      <stop offset="95%" stopColor="#7c5cbf" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="likeGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#16a34a" stopOpacity={0.2} />
                      <stop offset="95%" stopColor="#16a34a" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ede8df" />
                  <XAxis dataKey="date" tick={{ fill: "#78716c", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#78716c", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ fontSize: 11, color: "#78716c" }} />
                  {avgLine > 0 && (
                    <ReferenceLine y={avgLine} stroke="#e2dbd0" strokeDasharray="4 3"
                      label={{ value: "均", fill: "#a8a29e", fontSize: 10, position: "insideLeft" }} />
                  )}
                  <Area type="monotone" dataKey="avg_engagement" name="互動率%" stroke="#7c5cbf" strokeWidth={2} fill="url(#engGrad)" dot={false} />
                  <Area type="monotone" dataKey="likes" name="按讚" stroke="#16a34a" strokeWidth={1.5} fill="url(#likeGrad)" dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="card-sm p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Brain size={14} className="text-[var(--accent)]" />
                  <h2 className="text-[11px] font-semibold text-[var(--text-2)] uppercase tracking-widest">受眾洞察</h2>
                </div>
                <button onClick={handleFeedback} disabled={feedbackRunning}
                  className="flex items-center gap-1.5 text-[11px] px-3 py-1.5 rounded-full border border-[var(--border)] text-[var(--text-2)] hover:text-[var(--text-1)] disabled:opacity-50 transition-all">
                  {feedbackRunning ? <Loader2 size={11} className="animate-spin" /> : <Brain size={11} />}
                  {feedbackRunning ? "分析中..." : "回饋分析"}
                </button>
              </div>
              {insights ? (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div className="text-center bg-[var(--bg-2)] rounded-xl p-3">
                    <p className="text-[10px] text-[var(--text-3)] mb-1 uppercase font-medium">最佳發文日</p>
                    <p className="text-[15px] font-bold text-[var(--text-1)]">{insights.best_posting_day || "—"}</p>
                  </div>
                  <div className="text-center bg-[var(--bg-2)] rounded-xl p-3">
                    <p className="text-[10px] text-[var(--text-3)] mb-1 uppercase font-medium">最佳時段</p>
                    <p className="text-[15px] font-bold text-[var(--text-1)]">{insights.best_posting_hour != null ? `${insights.best_posting_hour}:00` : "—"}</p>
                  </div>
                  <div className="text-center bg-[var(--bg-2)] rounded-xl p-3">
                    <p className="text-[10px] text-[var(--text-3)] mb-1 uppercase font-medium">互動趨勢</p>
                    <p className={`text-[15px] font-bold ${insights.engagement_trend === "up" ? "text-[var(--green)]" : insights.engagement_trend === "down" ? "text-[var(--red)]" : "text-[var(--text-3)]"}`}>
                      {insights.engagement_trend === "up" ? "↑ 上升" : insights.engagement_trend === "down" ? "↓ 下降" : "→ 持平"}
                    </p>
                  </div>
                  <div className="text-center bg-[var(--bg-2)] rounded-xl p-3">
                    <p className="text-[10px] text-[var(--text-3)] mb-1 uppercase font-medium">成長率</p>
                    <p className="text-[15px] font-bold text-[var(--text-1)]">{insights.growth_rate != null ? `${insights.growth_rate}%` : "—"}</p>
                  </div>
                  {insights.strategic_summary && (
                    <div className="col-span-2 sm:col-span-4 mt-1 bg-[var(--accent-soft)] rounded-xl px-4 py-3 border border-violet-200">
                      <p className="text-[10px] text-[var(--accent)] mb-1 uppercase tracking-wider font-semibold">策略建議</p>
                      <p className="text-[12px] text-[var(--text-1)] leading-relaxed">{insights.strategic_summary}</p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-5">
                  <p className="text-[var(--text-3)] text-[12px] mb-3">需要更多數據才能生成洞察</p>
                  <button onClick={handleFeedback} disabled={feedbackRunning}
                    className="px-4 py-2 rounded-full bg-[var(--accent)] text-white text-[12px] font-medium disabled:opacity-50">
                    {feedbackRunning ? "分析中..." : "生成受眾洞察"}
                  </button>
                </div>
              )}
            </div>

            <div className="card-sm overflow-hidden">
              <div className="px-4 py-3.5 border-b border-[var(--border)] flex items-center justify-between">
                <h2 className="text-[11px] font-semibold text-[var(--text-2)] uppercase tracking-widest">貼文列表</h2>
                <select value={sort} onChange={e => setSort(e.target.value as keyof Post)}
                  className="text-[11px] border border-[var(--border)] bg-[var(--bg-2)] rounded-lg px-2 py-1 text-[var(--text-2)] outline-none">
                  <option value="timestamp">依時間</option>
                  <option value="views">依觀看數</option>
                  <option value="engagement_rate">依互動率</option>
                  <option value="likes">依按讚數</option>
                </select>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-[12px]">
                  <thead>
                    <tr className="text-[10px] text-[var(--text-3)] border-b border-[var(--border)] uppercase tracking-wider bg-[var(--bg-2)]">
                      <th className="text-left px-4 py-3">內容</th>
                      <th className="text-right px-4 py-3">觀看</th>
                      <th className="text-right px-4 py-3">按讚</th>
                      <th className="text-right px-4 py-3">回覆</th>
                      <th className="text-right px-4 py-3">互動率</th>
                      <th className="text-right px-4 py-3">日期</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sorted.map(p => (
                      <tr key={p.post_id}
                        className="border-b border-[var(--border)] hover:bg-[var(--bg-2)] transition-colors cursor-pointer"
                        onClick={() => setExpandedRow(expandedRow === p.post_id ? null : p.post_id)}>
                        <td className="px-4 py-3 text-[var(--text-1)] max-w-xs">
                          <span className={expandedRow === p.post_id ? "whitespace-pre-wrap" : "truncate block"}>
                            {p.text || <span className="text-[var(--text-3)] italic">無文字</span>}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right text-[var(--text-2)]">{p.views.toLocaleString()}</td>
                        <td className="px-4 py-3 text-right text-[var(--text-2)]">{p.likes}</td>
                        <td className="px-4 py-3 text-right text-[var(--text-2)]">{p.replies}</td>
                        <td className="px-4 py-3 text-right">
                          <span className={`font-semibold ${p.engagement_rate >= 3 ? "text-[var(--green)]" : "text-[var(--text-2)]"}`}>
                            {p.engagement_rate}%
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right text-[var(--text-3)] text-[11px]">{p.timestamp?.slice(0, 10)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )
      )}

      {/* ── Ecom Tab ── */}
      {tab === "ecom" && (
        ecomLoading ? (
          <div className="flex items-center justify-center h-64 text-[var(--text-3)]">
            <Loader2 size={20} className="animate-spin mr-2" />載入中...
          </div>
        ) : !ecomData || ecomData.products.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-72 gap-4 text-center px-8">
            <div className="w-14 h-14 rounded-2xl bg-[var(--bg-2)] flex items-center justify-center mb-1">
              <ShoppingCart size={24} className="text-[var(--text-3)]" />
            </div>
            <div>
              <p className="text-[15px] font-semibold text-[var(--text-1)] mb-1">尚無電商績效數據</p>
              <p className="text-[12px] text-[var(--text-3)] leading-relaxed max-w-xs">
                請先在 Flow Lab 輸入商品週績效，數據會自動出現在此頁面
              </p>
            </div>
            <a href="/flowlab"
              className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-[var(--accent)] text-white text-[13px] font-medium hover:opacity-90 transition-all shadow-lg shadow-violet-500/20">
              前往 Flow Lab 輸入數據
              <ArrowRight size={13} />
            </a>
            <p className="text-[11px] text-[var(--text-3)]">Flow Lab → 週績效表 → 輸入各商品本週數據</p>
          </div>
        ) : (
          <div className="space-y-5">
            {/* Summary cards */}
            <div className="grid grid-cols-3 gap-4">
              <StatCard label="近 7 天營收" value={`$${ecomData.total_revenue_7d.toLocaleString()}`} trend="up" />
              <StatCard label="預估利潤" value={`$${ecomData.total_profit_est.toLocaleString()}`} />
              <StatCard label="在架商品數" value={ecomData.product_count} sub="非停售/封存" />
            </div>

            {/* Alerts */}
            {alertChecked && alerts.length > 0 && (
              <div className="rounded-2xl p-4 space-y-2" style={{ background: "rgba(220,38,38,0.05)", border: "1px solid rgba(220,38,38,0.18)" }}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[11px] font-semibold uppercase tracking-wider" style={{ color: "var(--red)" }}>⚠ 商品警示</span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full font-medium" style={{ background: "rgba(220,38,38,0.1)", color: "var(--red)" }}>{alerts.length} 項</span>
                </div>
                {alerts.map(a => (
                  <div key={a.sku} className="flex items-start gap-3 text-[12px]">
                    <span className="font-medium text-[var(--text-1)] shrink-0">{a.name}</span>
                    <span className="text-[var(--text-3)]">{a.issues.join("、")}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Margin bar chart */}
            {marginChartData.length > 0 && (
              <div className="card-sm p-5">
                <h2 className="text-[11px] font-semibold text-[var(--text-2)] mb-4 uppercase tracking-widest">各品項毛利率（%）</h2>
                <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={marginChartData} barSize={28}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ede8df" vertical={false} />
                    <XAxis dataKey="name" tick={{ fill: "#78716c", fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: "#78716c", fontSize: 10 }} axisLine={false} tickLine={false} unit="%" domain={[0, 'auto']} />
                    <Tooltip content={<CustomTooltip />} />
                    <Bar dataKey="毛利率" radius={[4,4,0,0]}>
                      {marginChartData.map((entry, i) => (
                        <Cell key={i} fill={ROLE_COLORS[entry.role] || "#94a3b8"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
                {/* Legend */}
                <div className="flex gap-4 mt-3 flex-wrap">
                  {Object.entries(ROLE_COLORS).map(([label, color]) => (
                    <span key={label} className="flex items-center gap-1.5 text-[11px] text-[var(--text-3)]">
                      <span className="w-2.5 h-2.5 rounded-sm" style={{ background: color }} />
                      {label}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Revenue history chart */}
            {perfHistory.length > 0 && (() => {
              // 按日期聚合總營收
              const byDate: Record<string, number> = {};
              perfHistory.forEach(r => {
                byDate[r.record_date] = (byDate[r.record_date] || 0) + r.revenue_7d;
              });
              const histChartData = Object.entries(byDate).sort(([a],[b]) => a.localeCompare(b)).map(([date, revenue]) => ({
                date: date.slice(5),
                週營收: revenue,
              }));
              return (
                <div className="card-sm p-5">
                  <h2 className="text-[11px] font-semibold text-[var(--text-2)] mb-4 uppercase tracking-widest">週營收歷史趨勢</h2>
                  <ResponsiveContainer width="100%" height={180}>
                    <BarChart data={histChartData} barSize={20}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#ede8df" vertical={false} />
                      <XAxis dataKey="date" tick={{ fill: "#78716c", fontSize: 10 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: "#78716c", fontSize: 10 }} axisLine={false} tickLine={false} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="週營收" fill="#7c5cbf" radius={[4,4,0,0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              );
            })()}

            {/* Product table */}
            <div className="card-sm overflow-hidden">
              <div className="px-4 py-3.5 border-b border-[var(--border)]">
                <h2 className="text-[11px] font-semibold text-[var(--text-2)] uppercase tracking-widest">商品詳細表現</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-[12px]">
                  <thead>
                    <tr className="text-[10px] text-[var(--text-3)] border-b border-[var(--border)] uppercase tracking-wider bg-[var(--bg-2)]">
                      <th className="text-left px-4 py-3">商品</th>
                      <th className="text-left px-4 py-3">角色</th>
                      <th className="text-right px-4 py-3">週營收</th>
                      <th className="text-right px-4 py-3">毛利率</th>
                      <th className="text-right px-4 py-3">安全 CPA</th>
                      <th className="text-right px-4 py-3">ROAS</th>
                      <th className="text-right px-4 py-3">庫存天數</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ecomData.products.map(p => {
                      const marginPct = (p.gross_margin * 100).toFixed(1);
                      const marginColor = p.gross_margin >= 0.3 ? "text-[var(--green)]" : p.gross_margin >= 0.15 ? "text-amber-600" : "text-[var(--red)]";
                      const daysLeft = p.days_left;
                      const daysColor = daysLeft != null && daysLeft < 7 ? "text-[var(--red)]" : daysLeft != null && daysLeft < 14 ? "text-amber-600" : "text-[var(--text-2)]";
                      return (
                        <tr key={p.sku} className="border-b border-[var(--border)] hover:bg-[var(--bg-2)] transition-colors">
                          <td className="px-4 py-3">
                            <p className="text-[var(--text-1)] font-medium">{p.name}</p>
                            <p className="text-[10px] text-[var(--text-3)]">{p.sku}</p>
                          </td>
                          <td className="px-4 py-3">
                            {p.role && (
                              <span className="text-[10px] px-2 py-0.5 rounded-full font-medium"
                                style={{ background: ROLE_COLORS[p.role] + "22", color: ROLE_COLORS[p.role] || "#78716c" }}>
                                {p.role}
                              </span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-right text-[var(--text-2)]">${p.revenue_7d.toLocaleString()}</td>
                          <td className={`px-4 py-3 text-right font-semibold ${marginColor}`}>{marginPct}%</td>
                          <td className="px-4 py-3 text-right text-[var(--text-2)]">${p.safe_cpa || "—"}</td>
                          <td className="px-4 py-3 text-right text-[var(--text-2)]">
                            {p.roas != null ? <span className={p.roas >= 3 ? "text-[var(--green)] font-semibold" : ""}>{p.roas}x</span> : "—"}
                          </td>
                          <td className={`px-4 py-3 text-right ${daysColor}`}>
                            {daysLeft != null ? `${daysLeft} 天` : "—"}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )
      )}

      {/* ── Funnel Tab ── */}
      {tab === "funnel" && (
        funnelLoading ? (
          <div className="flex items-center justify-center h-64 text-[var(--text-3)]">
            <Loader2 size={20} className="animate-spin mr-2" />載入中...
          </div>
        ) : funnelData.length === 0 ? (
          <div className="flex items-center justify-center h-64 text-[var(--text-3)]">尚無選品數據</div>
        ) : (
          <div className="space-y-5">
            {/* Summary */}
            <div className="grid grid-cols-3 gap-4">
              <StatCard label="總選品數" value={funnelTotal} />
              <StatCard label="進行中" value={funnelData.filter(s => !["stopped"].includes(s.stage)).reduce((a, s) => a + s.count, 0)} sub="非停售商品" />
              <StatCard label="已上架測試" value={funnelData.filter(s => ["listed","testing_ads","scaling"].includes(s.stage)).reduce((a,s)=>a+s.count,0)} />
            </div>

            {/* Funnel visualization */}
            <div className="card-sm p-5">
              <h2 className="text-[11px] font-semibold text-[var(--text-2)] mb-5 uppercase tracking-widest">選品生命週期漏斗</h2>
              <div className="space-y-2">
                {funnelData.map((stage, i) => {
                  const pct = funnelTotal > 0 ? (stage.count / funnelTotal) * 100 : 0;
                  const barWidth = stage.count > 0 ? Math.max(pct, 4) : 0;
                  return (
                    <div key={stage.stage} className="flex items-center gap-3">
                      <span className="text-[11px] text-[var(--text-3)] w-20 shrink-0 text-right">{stage.label}</span>
                      <div className="flex-1 bg-[var(--bg-2)] rounded-full h-5 overflow-hidden">
                        <div className="h-full rounded-full flex items-center transition-all duration-500"
                          style={{ width: `${barWidth}%`, background: FUNNEL_COLORS[i] || "#7c5cbf" }}>
                        </div>
                      </div>
                      <span className="text-[12px] font-semibold text-[var(--text-1)] w-8 text-right shrink-0">
                        {stage.count}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Funnel bar chart */}
            <div className="card-sm p-5">
              <h2 className="text-[11px] font-semibold text-[var(--text-2)] mb-4 uppercase tracking-widest">階段分佈</h2>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={funnelData} barSize={24}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ede8df" vertical={false} />
                  <XAxis dataKey="label" tick={{ fill: "#78716c", fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "#78716c", fontSize: 10 }} axisLine={false} tickLine={false} allowDecimals={false} />
                  <Tooltip formatter={(v: any) => [v, "商品數"]} labelStyle={{ color: "#78716c", fontSize: 11 }} contentStyle={{ borderRadius: 10, fontSize: 12, border: "1px solid var(--border)" }} />
                  <Bar dataKey="count" radius={[4,4,0,0]}>
                    {funnelData.map((_, i) => (
                      <Cell key={i} fill={FUNNEL_COLORS[i] || "#7c5cbf"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )
      )}

      {/* ── Feedback Tab（內容效果閉環）── */}
      {tab === "feedback" && (
        feedbackLoading ? (
          <div className="flex items-center justify-center h-64 text-[var(--text-3)]">
            <Loader2 size={20} className="animate-spin mr-2" />分析中...
          </div>
        ) : !feedbackData ? (
          <div className="flex flex-col items-center justify-center h-64 gap-3 text-[var(--text-3)]">
            <Zap size={28} />
            <p className="text-[14px]">需要更新 Threads 數據才能分析</p>
          </div>
        ) : (
          <div className="space-y-5">
            {/* 各類別平均互動率 */}
            <div className="card-sm p-5">
              <h2 className="text-[11px] font-semibold text-[var(--text-2)] mb-4 uppercase tracking-widest">各類別平均互動率（近 90 天）</h2>
              {feedbackData.by_category?.length === 0 ? (
                <p className="text-[13px] text-[var(--text-3)] text-center py-8">尚無分類數據，請確認 posts 表有 category 欄位</p>
              ) : (
                <div className="space-y-3">
                  {feedbackData.by_category?.map((cat: any, i: number) => {
                    const maxEng = Math.max(...feedbackData.by_category.map((c: any) => c.avg_engagement || 0));
                    const pct = maxEng > 0 ? (cat.avg_engagement / maxEng) * 100 : 0;
                    return (
                      <div key={cat.category} className="flex items-center gap-3">
                        <span className="text-[12px] text-[var(--text-2)] w-28 shrink-0 truncate">{cat.category}</span>
                        <div className="flex-1 bg-[var(--bg-2)] rounded-full h-5 overflow-hidden">
                          <div className="h-full rounded-full transition-all duration-500"
                            style={{ width: `${Math.max(pct, 4)}%`, background: i === 0 ? "var(--accent)" : "#b8a0e8" }} />
                        </div>
                        <div className="flex gap-3 shrink-0 text-[11px] text-[var(--text-3)]">
                          <span><span className="font-700 text-[var(--text-1)]">{(cat.avg_engagement * 100).toFixed(2)}%</span> 互動</span>
                          <span>{cat.post_count} 篇</span>
                          <span>均 {Math.round(cat.avg_views ?? 0)} 觸及</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* 互動趨勢 */}
            {feedbackData.daily_trend?.length > 0 && (
              <div className="card-sm p-5">
                <h2 className="text-[11px] font-semibold text-[var(--text-2)] mb-4 uppercase tracking-widest">每日互動率趨勢</h2>
                <ResponsiveContainer width="100%" height={180}>
                  <AreaChart data={feedbackData.daily_trend.map((d: any) => ({ ...d, eng_pct: +(d.avg_eng * 100).toFixed(3) }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ede8df" vertical={false} />
                    <XAxis dataKey="d" tick={{ fill: "#78716c", fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: "#78716c", fontSize: 10 }} axisLine={false} tickLine={false} unit="%" />
                    <Tooltip formatter={(v: any) => [`${v}%`, "互動率"]} contentStyle={{ borderRadius: 10, fontSize: 12, border: "1px solid var(--border)" }} />
                    <Area type="monotone" dataKey="eng_pct" stroke="#7c5cbf" fill="rgba(124,92,191,0.1)" strokeWidth={2} name="互動率" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Top 5 貼文 */}
            {feedbackData.top_posts?.length > 0 && (
              <div className="card-sm p-5">
                <h2 className="text-[11px] font-semibold text-[var(--text-2)] mb-4 uppercase tracking-widest">最高互動貼文 Top 5</h2>
                <div className="space-y-3">
                  {feedbackData.top_posts.map((p: any, i: number) => (
                    <div key={p.threads_id} className="flex items-start gap-3 py-3 border-b border-[var(--border)] last:border-0">
                      <span className="w-6 h-6 rounded-full bg-[var(--accent-soft)] text-[var(--accent)] text-[11px] font-800 flex items-center justify-center shrink-0">{i+1}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-[13px] text-[var(--text-1)] line-clamp-2">{p.text?.slice(0, 80)}...</p>
                        <div className="flex gap-3 mt-1 text-[11px] text-[var(--text-3)]">
                          {p.category && <span className="px-1.5 py-0.5 rounded bg-[var(--bg-2)]">{p.category}</span>}
                          <span>👁 {p.views?.toLocaleString()}</span>
                          <span>❤️ {p.likes}</span>
                          <span className="font-600 text-[var(--accent)]">{(p.engagement_rate * 100).toFixed(2)}% 互動</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="rounded-[12px] px-4 py-3 bg-violet-50 border border-violet-100 text-[12px] text-violet-600 flex items-start gap-2">
              <Zap size={13} className="shrink-0 mt-0.5" />
              <span>最高互動的類別會在下次 Pipeline 選題時獲得更高權重，讓系統越來越準。</span>
            </div>
          </div>
        )
      )}
    </div>
  );
}
