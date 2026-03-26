"use client";
import { useState, useEffect } from "react";
import { fetchPicks, fetchPicksDates } from "@/lib/api";
import { ListChecks, Star, Copy, Check, ChevronDown, ChevronUp, Newspaper, ExternalLink } from "lucide-react";

type Topic = {
  cluster_label: string;
  merged_summary: string;
  score: number;
  post_type: string;
  score_reason: string;
  articles?: string[];
};

type Article = {
  title: string;
  url: string;
  source: string;
  summary: string;
  language: string;
  published_at: string;
  scraped_at: string;
};

const POST_TYPE_COLOR: Record<string, string> = {
  "趨勢解讀":   "bg-violet-50 text-violet-600 border-violet-200",
  "AI工具實測": "bg-blue-50 text-blue-600 border-blue-200",
  "個人成長":   "bg-emerald-50 text-emerald-600 border-emerald-200",
  "觀點評論":   "bg-orange-50 text-orange-600 border-orange-200",
  "商業洞察":   "bg-teal-50 text-teal-600 border-teal-200",
  "時事分析":   "bg-rose-50 text-rose-600 border-rose-200",
  "職涯觀點":   "bg-amber-50 text-amber-600 border-amber-200",
};

const SOURCE_LABEL: Record<string, string> = {
  serper_en: "Google EN",
  serper_zh: "Google 中文",
  serper_biz: "商業",
  serper_work: "職場",
  serper_tw: "台灣",
  hackernews: "HN",
  perplexity: "Perplexity",
  rss: "RSS",
};

const SCORE_COLOR = (s: number) =>
  s >= 9 ? "text-emerald-600" : s >= 7 ? "text-violet-600" : s >= 5 ? "text-amber-600" : "text-[var(--text-3)]";

function ScoreDot({ score }: { score: number }) {
  const filled = Math.round(score / 2);
  return (
    <div className="flex gap-0.5">
      {Array.from({ length: 5 }).map((_, i) => (
        <span key={i} className={`w-1.5 h-1.5 rounded-full ${i < filled ? "bg-violet-500" : "bg-[var(--border-2)]"}`} />
      ))}
    </div>
  );
}

function TopicCard({ topic, isTop3, index }: { topic: Topic; isTop3: boolean; index: number }) {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(
      `【${topic.cluster_label}】\n\n${topic.merged_summary}\n\n類型：${topic.post_type}\n評分：${topic.score}/10`
    );
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const typeColor = POST_TYPE_COLOR[topic.post_type] || "bg-gray-900/40 text-gray-400 border-gray-700/30";

  return (
    <div
      className={`card-sm p-5 transition-all duration-200 animate-slide-up ${
        isTop3 ? "ring-1 ring-violet-300" : ""
      }`}
      style={{ animationDelay: `${index * 40}ms` }}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2 flex-wrap">
          {isTop3 && (
            <span className="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-violet-100 text-violet-700 border border-violet-200 font-medium">
              <Star size={9} fill="currentColor" /> TOP3
            </span>
          )}
          <span className={`text-[10px] px-2 py-0.5 rounded-full border ${typeColor}`}>
            {topic.post_type}
          </span>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <span className={`text-lg font-bold tabular-nums ${SCORE_COLOR(topic.score)}`}>
            {topic.score}
          </span>
          <span className="text-[10px] text-[var(--text-3)]">/10</span>
        </div>
      </div>
      <h3 className="text-[14px] font-semibold text-[var(--text-1)] mb-1.5 leading-snug">{topic.cluster_label}</h3>
      <ScoreDot score={topic.score} />
      <p className={`text-[12px] text-[var(--text-2)] leading-relaxed mt-2 ${expanded ? "" : "line-clamp-2"}`}>
        {topic.merged_summary}
      </p>
      {topic.score_reason && (
        <p className={`text-[11px] text-[var(--text-3)] mt-1.5 italic ${expanded ? "" : "hidden"}`}>
          評分理由：{topic.score_reason}
        </p>
      )}
      <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-[var(--border)]">
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-1 text-[11px] text-[var(--text-3)] hover:text-[var(--text-1)] transition-colors"
        >
          {expanded ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
          {expanded ? "收起" : "展開詳情"}
        </button>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 text-[11px] px-3 py-1 rounded-lg bg-violet-50 hover:bg-violet-100 text-violet-700 border border-violet-200 transition-all"
        >
          {copied ? <Check size={11} /> : <Copy size={11} />}
          {copied ? "已複製" : "複製"}
        </button>
      </div>
    </div>
  );
}

function ArticleCard({ article, index }: { article: Article; index: number }) {
  const srcLabel = SOURCE_LABEL[article.source] || article.source;
  const isZh = article.language === "zh-TW";

  return (
    <div
      className="card-sm p-4 animate-slide-up hover:-translate-y-0.5 transition-all duration-150"
      style={{ animationDelay: `${index * 30}ms` }}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className={`text-[10px] px-2 py-0.5 rounded-full border shrink-0 font-medium ${
          isZh ? "bg-teal-50 text-teal-700 border-teal-200" : "bg-blue-50 text-blue-700 border-blue-200"
        }`}>
          {srcLabel}
        </span>
        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="shrink-0 text-[var(--text-3)] hover:text-violet-400 transition-colors"
        >
          <ExternalLink size={12} />
        </a>
      </div>
      <h3 className="text-[13px] font-semibold text-[var(--text-1)] leading-snug mb-2 line-clamp-2">
        {article.title}
      </h3>
      {article.summary && (
        <p className="text-[11px] text-[var(--text-2)] leading-relaxed line-clamp-3">{article.summary}</p>
      )}
      {article.published_at && (
        <p className="text-[10px] text-[var(--text-3)] mt-2">{article.published_at.slice(0, 10)}</p>
      )}
    </div>
  );
}

export default function PicksPage() {
  const [tab, setTab] = useState<"topics" | "articles">("topics");

  const [picks, setPicks] = useState<Topic[]>([]);
  const [top3Labels, setTop3Labels] = useState<string[]>([]);
  const [topicsLoading, setTopicsLoading] = useState(true);
  const [dates, setDates] = useState<string[]>([]);
  const [selectedDate, setSelectedDate] = useState("");
  const [filter, setFilter] = useState<"all" | "top3" | "high">("all");

  const [articles, setArticles] = useState<Article[]>([]);
  const [articlesLoading, setArticlesLoading] = useState(false);
  const [articleDays, setArticleDays] = useState(1);
  const [articleCount, setArticleCount] = useState(0);

  useEffect(() => {
    fetchPicksDates().then(d => {
      const list: string[] = d.dates || [];
      setDates(list);
      if (list.length > 0) setSelectedDate(list[0]);
    });
  }, []);

  useEffect(() => {
    if (!selectedDate) { setTopicsLoading(false); return; }
    setTopicsLoading(true);
    fetchPicks(selectedDate)
      .then(d => { setPicks(d.picks || []); setTop3Labels(d.top3_labels || []); })
      .finally(() => setTopicsLoading(false));
  }, [selectedDate]);

  const loadArticles = (days: number) => {
    setArticlesLoading(true);
    fetch(`/api/articles/recent?days=${days}&limit=60`)
      .then(r => r.json())
      .then(d => { setArticles(d.articles || []); setArticleCount(d.count || 0); })
      .finally(() => setArticlesLoading(false));
  };

  useEffect(() => {
    if (tab === "articles") loadArticles(articleDays);
  }, [tab]);

  const filtered = picks.filter(p => {
    if (filter === "top3") return top3Labels.includes(p.cluster_label);
    if (filter === "high") return p.score >= 7;
    return true;
  });

  return (
    <div className="">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-1)] flex items-center gap-2">
            <ListChecks size={20} className="text-violet-400" />
            精選清單
          </h1>
          <p className="text-[13px] text-[var(--text-2)] mt-0.5">評分主題 + 原始素材，選你想發的內容</p>
        </div>
        {tab === "topics" && dates.length > 0 && (
          <select
            value={selectedDate}
            onChange={e => setSelectedDate(e.target.value)}
            className="text-[13px] border border-[var(--border)] rounded-lg px-3 py-2 bg-[var(--surface)] text-[var(--text-1)] outline-none"
          >
            {dates.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        )}
      </div>

      <div className="flex gap-1 bg-[var(--bg-2)] border border-[var(--border)] rounded-xl p-1 mb-5 w-fit">
        <button
          onClick={() => setTab("topics")}
          className={`flex items-center gap-1.5 px-4 py-1.5 text-[12px] rounded-md transition-colors font-medium ${
            tab === "topics" ? "bg-[var(--accent)] text-white shadow-sm" : "text-[var(--text-2)] hover:text-[var(--text-1)] hover:bg-[var(--bg-2)]"
          }`}
        >
          <Star size={11} /> 評分主題
        </button>
        <button
          onClick={() => setTab("articles")}
          className={`flex items-center gap-1.5 px-4 py-1.5 text-[12px] rounded-md transition-colors font-medium ${
            tab === "articles" ? "bg-[var(--accent)] text-white shadow-sm" : "text-[var(--text-2)] hover:text-[var(--text-1)] hover:bg-[var(--bg-2)]"
          }`}
        >
          <Newspaper size={11} /> 原始素材
        </button>
      </div>

      {tab === "topics" && (
        <>
          <div className="flex gap-1 bg-[var(--bg-2)] border border-[var(--border)] rounded-xl p-1 mb-5 w-fit">
            {(["all", "top3", "high"] as const).map(f => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-1.5 text-[12px] rounded-md transition-colors font-medium ${
                  filter === f ? "bg-[var(--bg-2)] text-[var(--text-1)] shadow-sm" : "text-[var(--text-2)] hover:text-[var(--text-1)]"
                }`}
              >
                {f === "all" ? `全部 (${picks.length})` : f === "top3" ? "★ TOP3" : "7分以上"}
              </button>
            ))}
          </div>
          {topicsLoading ? (
            <div className="flex items-center justify-center h-64 text-[var(--text-3)]">載入中...</div>
          ) : filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64">
              <p className="text-[var(--text-3)] text-sm">
                {picks.length === 0 ? "此日期尚未執行 Pipeline" : "沒有符合條件的主題"}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {filtered.map((topic, i) => (
                <TopicCard key={topic.cluster_label} topic={topic} isTop3={top3Labels.includes(topic.cluster_label)} index={i} />
              ))}
            </div>
          )}
        </>
      )}

      {tab === "articles" && (
        <>
          <div className="flex items-center gap-3 mb-5">
            <div className="flex gap-1 bg-[var(--bg-2)] border border-[var(--border)] rounded-xl p-1">
              {[1, 3, 7].map(d => (
                <button
                  key={d}
                  onClick={() => { setArticleDays(d); loadArticles(d); }}
                  className={`px-3 py-1.5 text-[12px] rounded-md transition-colors font-medium ${
                    articleDays === d ? "bg-[var(--accent)] text-white shadow-sm" : "text-[var(--text-2)] hover:text-[var(--text-1)] hover:bg-[var(--bg-2)]"
                  }`}
                >
                  近 {d} 天
                </button>
              ))}
            </div>
            <span className="text-[12px] text-[var(--text-3)]">共 {articleCount} 篇原始素材</span>
          </div>
          {articlesLoading ? (
            <div className="flex items-center justify-center h-64 text-[var(--text-3)]">載入中...</div>
          ) : articles.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64">
              <p className="text-[var(--text-3)] text-sm">尚無素材，請先執行 Pipeline</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {articles.map((article, i) => (
                <ArticleCard key={article.url} article={article} index={i} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
