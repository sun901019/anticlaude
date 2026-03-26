"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle, Clock, TrendingUp, FileText, Send, Zap, BarChart2, Moon } from "lucide-react";

type MorningData = {
  date: string;
  pipeline_ran_today: boolean;
  pipeline_ran_at?: string;
  topics_today: number;
  drafts_today: number;
  posts_today: number;
  yesterday_best?: { text: string; views: number; engagement_rate: number };
  yesterday_avg_engagement?: number;
  next_pipeline_label: string;
  has_error: boolean;
  error_summary?: string;
};

type NightShiftData = {
  running: boolean;
  last_result?: {
    ran?: boolean;
    date?: string;
    tasks_success?: number;
    tasks_failed?: number;
    tasks_run?: number;
    sprint_counts?: { done: number; todo: number; in_progress: number; blocked: number };
    summary_preview?: string;
    message?: string;
    error?: string;
  };
};

function StatusCard({
  icon: Icon,
  label,
  value,
  sub,
  ok,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  sub?: string;
  ok?: boolean;
}) {
  return (
    <div className="bg-white border border-stone-200 rounded-xl p-5">
      <div className="flex items-center gap-2 mb-3">
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ background: ok === false ? "#fee2e2" : ok === true ? "#dcfce7" : "#f5f2ec" }}
        >
          <Icon
            size={16}
            className={ok === false ? "text-red-500" : ok === true ? "text-green-600" : "text-stone-500"}
          />
        </div>
        <span className="text-xs font-medium text-stone-500 uppercase tracking-wide">{label}</span>
      </div>
      <div className="text-2xl font-bold text-stone-800">{value}</div>
      {sub && <div className="text-xs text-stone-400 mt-1">{sub}</div>}
    </div>
  );
}

export default function MorningPage() {
  const [data, setData] = useState<MorningData | null>(null);
  const [nightShift, setNightShift] = useState<NightShiftData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [now, setNow] = useState(new Date());

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch("/api/morning-report");
        if (!res.ok) throw new Error();
        const json = await res.json();
        setData(json);
      } catch {
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    const loadNightShift = async () => {
      try {
        const res = await fetch("/api/night-shift/status");
        if (res.ok) setNightShift(await res.json());
      } catch {
        // 靜默失敗
      }
    };
    load();
    loadNightShift();
    const tick = setInterval(() => setNow(new Date()), 60000);
    return () => clearInterval(tick);
  }, []);

  const hour = now.getHours();
  const greeting =
    hour < 6 ? "深夜好" : hour < 12 ? "早安" : hour < 18 ? "午安" : "晚安";

  const dateLabel = now.toLocaleDateString("zh-TW", {
    year: "numeric",
    month: "long",
    day: "numeric",
    weekday: "long",
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-[#faf9f7] flex items-center justify-center">
        <div className="text-stone-400 text-sm">載入晨報中...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#faf9f7]">
      <div className="max-w-3xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="mb-10">
          <div className="text-sm text-stone-400 mb-1">{dateLabel}</div>
          <h1 className="text-3xl font-bold text-stone-800">{greeting}，Sun ☀️</h1>
          <p className="text-stone-500 mt-2">以下是今日系統狀態概覽</p>
        </div>

        {/* Error Banner */}
        {(error || data?.has_error) && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4 flex gap-3">
            <AlertTriangle size={18} className="text-red-500 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-red-700">系統警告</p>
              <p className="text-sm text-red-600 mt-0.5">
                {error ? "無法連接後端 API" : data?.error_summary || "Pipeline 執行失敗"}
              </p>
            </div>
          </div>
        )}

        {data && (
          <>
            {/* Status Grid */}
            <div className="grid grid-cols-2 gap-4 mb-8">
              <StatusCard
                icon={Zap}
                label="Pipeline"
                value={data.pipeline_ran_today ? "已完成" : "未執行"}
                sub={
                  data.pipeline_ran_today && data.pipeline_ran_at
                    ? `執行於 ${new Date(data.pipeline_ran_at).toLocaleTimeString("zh-TW", { hour: "2-digit", minute: "2-digit" })}`
                    : `下次執行：${data.next_pipeline_label}`
                }
                ok={data.pipeline_ran_today}
              />
              <StatusCard
                icon={FileText}
                label="今日草稿"
                value={data.drafts_today}
                sub={data.topics_today > 0 ? `${data.topics_today} 個主題已分析` : "等待 pipeline"}
                ok={data.drafts_today > 0}
              />
              <StatusCard
                icon={Send}
                label="今日發布"
                value={data.posts_today}
                sub="已發布貼文數"
                ok={data.posts_today > 0}
              />
              <StatusCard
                icon={BarChart2}
                label="昨日互動率"
                value={
                  data.yesterday_avg_engagement != null
                    ? `${(data.yesterday_avg_engagement * 100).toFixed(1)}%`
                    : "—"
                }
                sub="昨日平均互動率"
                ok={data.yesterday_avg_engagement != null && data.yesterday_avg_engagement > 0}
              />
            </div>

            {/* Yesterday Best */}
            {data.yesterday_best && (
              <div className="bg-white border border-stone-200 rounded-xl p-5 mb-8">
                <div className="flex items-center gap-2 mb-3">
                  <TrendingUp size={16} className="text-[#7c5cbf]" />
                  <span className="text-sm font-semibold text-stone-700">昨日最佳表現</span>
                </div>
                <p className="text-stone-700 text-sm leading-relaxed mb-3">
                  &ldquo;{data.yesterday_best.text}&rdquo;
                </p>
                <div className="flex gap-4 text-xs text-stone-400">
                  <span>👁 {data.yesterday_best.views.toLocaleString()} 次觀看</span>
                  <span>
                    💬 互動率 {(data.yesterday_best.engagement_rate * 100).toFixed(2)}%
                  </span>
                </div>
              </div>
            )}

            {/* Night Shift Summary */}
            {nightShift && (
              <div className="bg-white border border-stone-200 rounded-xl p-5 mb-6">
                <div className="flex items-center gap-2 mb-3">
                  <Moon size={16} className="text-indigo-500" />
                  <span className="text-sm font-semibold text-stone-700">昨晚夜班摘要</span>
                  {nightShift.running && (
                    <span className="text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full">執行中</span>
                  )}
                </div>
                {nightShift.last_result?.ran === false ? (
                  <p className="text-sm text-stone-400">
                    {nightShift.last_result.message || "尚無夜班記錄"}
                  </p>
                ) : nightShift.last_result?.date ? (
                  <div className="space-y-2">
                    <div className="flex gap-4 text-sm text-stone-600">
                      <span>📅 {nightShift.last_result.date}</span>
                      <span>✅ {nightShift.last_result.tasks_success ?? 0} 項完成</span>
                      {(nightShift.last_result.tasks_failed ?? 0) > 0 && (
                        <span className="text-red-500">❌ {nightShift.last_result.tasks_failed} 項失敗</span>
                      )}
                    </div>
                    {nightShift.last_result.sprint_counts && (
                      <div className="flex gap-3 text-xs text-stone-400">
                        <span>Sprint：{nightShift.last_result.sprint_counts.done} 完成</span>
                        <span>/ {nightShift.last_result.sprint_counts.todo} 待辦</span>
                        {nightShift.last_result.sprint_counts.blocked > 0 && (
                          <span className="text-red-400">/ {nightShift.last_result.sprint_counts.blocked} 阻塞</span>
                        )}
                      </div>
                    )}
                  </div>
                ) : null}
              </div>
            )}

            {/* Today Plan */}
            <div className="bg-white border border-stone-200 rounded-xl p-5 mb-8">
              <h2 className="text-sm font-semibold text-stone-700 mb-4">今日建議行動</h2>
              <div className="space-y-3">
                {!data.pipeline_ran_today && (
                  <ActionItem
                    icon="🚀"
                    text="Pipeline 尚未執行，前往 CEO Console 觸發或等待 08:00 自動排程"
                    href="/chat"
                    linkText="前往 CEO Console"
                  />
                )}
                {data.drafts_today > 0 && (
                  <ActionItem
                    icon="✍️"
                    text={`已有 ${data.drafts_today} 篇草稿等待審核，前往今日總覽選擇版本發布`}
                    href="/"
                    linkText="前往今日總覽"
                  />
                )}
                {data.posts_today === 0 && data.drafts_today === 0 && (
                  <ActionItem
                    icon="💡"
                    text="今日尚無內容，建議先觸發 Pipeline 生成今日草稿"
                    href="/chat"
                    linkText="前往 CEO Console"
                  />
                )}
                <ActionItem
                  icon="📋"
                  text="查看 AI 團隊提交的待審決策"
                  href="/review"
                  linkText="前往 Review Queue"
                />
              </div>
            </div>

            {/* Next Pipeline */}
            <div className="flex items-center gap-2 text-xs text-stone-400">
              <Clock size={12} />
              <span>下次 Pipeline 排程：{data.next_pipeline_label}</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function ActionItem({
  icon,
  text,
  href,
  linkText,
}: {
  icon: string;
  text: string;
  href: string;
  linkText: string;
}) {
  return (
    <div className="flex items-start gap-3">
      <span className="text-base shrink-0 mt-0.5">{icon}</span>
      <div className="flex-1 text-sm text-stone-600">
        {text}{" "}
        <a href={href} className="text-[#7c5cbf] font-medium hover:underline">
          {linkText} →
        </a>
      </div>
    </div>
  );
}
