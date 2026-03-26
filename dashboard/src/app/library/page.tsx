"use client";
import { useState, useEffect } from "react";
import { fetchLibrary, fetchLibraryDates } from "@/lib/api";
import { ExternalLink, Search } from "lucide-react";

type Article = {
  title: string; url: string; source: string;
  summary: string; published_at: string; language: string;
};

const FAVICON_DOMAINS: Record<string, string> = {
  techcrunch:  "techcrunch.com",
  venturebeat: "venturebeat.com",
  theverge:    "theverge.com",
  ainews:      "buttondown.com",
  serper_en:   "google.com",
  serper_zh:   "google.com",
  serper_biz:  "google.com",
  serper_work: "google.com",
  serper_tw:   "google.com",
  perplexity:  "perplexity.ai",
  hackernews:  "news.ycombinator.com",
};

const SOURCE_COLOR: Record<string, string> = {
  techcrunch:  "text-green-600",
  venturebeat: "text-blue-600",
  theverge:    "text-purple-600",
  ainews:      "text-amber-600",
  serper_en:   "text-orange-600",
  serper_zh:   "text-red-600",
  serper_biz:  "text-teal-600",
  serper_work: "text-cyan-700",
  serper_tw:   "text-rose-600",
  perplexity:  "text-pink-600",
  hackernews:  "text-amber-700",
};

function SourceBadge({ source }: { source: string }) {
  const domain = FAVICON_DOMAINS[source] || "google.com";
  const color = SOURCE_COLOR[source] || "text-[var(--text-2)]";
  return (
    <span className={`flex items-center gap-1 text-[11px] font-medium ${color}`}>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={`https://www.google.com/s2/favicons?domain=${domain}&sz=16`} alt="" width={12} height={12} className="opacity-70 rounded-sm" />
      {source}
    </span>
  );
}

export default function LibraryPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [dates, setDates] = useState<string[]>([]);
  const [selectedDate, setSelectedDate] = useState("");
  const [search, setSearch] = useState("");
  const [langFilter, setLangFilter] = useState<"all" | "en" | "zh-TW">("all");

  useEffect(() => {
    fetchLibraryDates().then(d => {
      const list: string[] = d.dates || [];
      setDates(list);
      if (list.length > 0) setSelectedDate(list[0]);
    });
  }, []);

  useEffect(() => {
    if (!selectedDate) { setLoading(false); return; }
    setLoading(true);
    fetchLibrary(selectedDate).then(d => setArticles(d.articles || [])).finally(() => setLoading(false));
  }, [selectedDate]);

  const filtered = articles.filter(a => {
    const matchLang = langFilter === "all" || a.language === langFilter;
    const matchSearch = !search || a.title.toLowerCase().includes(search.toLowerCase()) || a.summary.toLowerCase().includes(search.toLowerCase());
    return matchLang && matchSearch;
  });

  return (
    <div className="">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-1)]">素材庫</h1>
          <p className="text-[13px] text-[var(--text-2)] mt-0.5">所有抓取到的原始素材</p>
        </div>
        <select value={selectedDate} onChange={e => setSelectedDate(e.target.value)}
          className="text-[13px] border border-[var(--border)] rounded-lg px-3 py-2 bg-[var(--surface)] text-[var(--text-1)] outline-none">
          {dates.map(d => <option key={d} value={d}>{d}</option>)}
        </select>
      </div>

      <div className="flex gap-3 mb-5">
        <div className="relative flex-1">
          <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-3)]" />
          <input type="text" placeholder="搜尋標題或摘要..." value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-[13px] bg-[var(--surface)] rounded-xl text-[var(--text-1)] placeholder-[var(--text-3)] outline-none border border-[var(--border)] focus:border-[var(--accent)]" />
        </div>
        <div className="flex gap-1 bg-[var(--bg-2)] border border-[var(--border)] rounded-xl p-1">
          {(["all", "en", "zh-TW"] as const).map(l => (
            <button key={l} onClick={() => setLangFilter(l)}
              className={`px-3 py-1 text-[11px] rounded-lg transition-colors font-medium ${
                langFilter === l
                  ? "bg-[var(--accent)] text-white shadow-sm"
                  : "text-[var(--text-2)] hover:text-[var(--text-1)]"
              }`}>
              {l === "all" ? "全部" : l}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64 text-[var(--text-3)]">載入中...</div>
      ) : filtered.length === 0 ? (
        <div className="flex items-center justify-center h-64 text-[var(--text-3)]">
          {articles.length === 0 ? "此日期沒有素材" : "沒有符合的結果"}
        </div>
      ) : (
        <div className="card-sm overflow-hidden">
          <div className="px-4 py-3 border-b border-[var(--border)] bg-[var(--bg-2)]">
            <p className="text-[11px] text-[var(--text-3)] uppercase tracking-wider font-medium">{filtered.length} 則素材</p>
          </div>
          <div className="divide-y divide-[var(--border)]">
            {filtered.map((a, i) => (
              <div key={i}
                className="flex items-start gap-3 px-4 py-3 hover:bg-[var(--bg-2)] transition-colors group animate-slide-up"
                style={{ animationDelay: `${Math.min(i * 30, 300)}ms` }}>
                <span className="text-[11px] text-[var(--text-3)] w-6 shrink-0 pt-0.5 text-right select-none">{i + 1}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <SourceBadge source={a.source} />
                    <span className="text-[10px] text-[var(--text-3)]">{a.published_at?.slice(0, 10)}</span>
                  </div>
                  <a href={a.url} target="_blank" rel="noopener noreferrer"
                    className="text-[13px] font-semibold text-[var(--text-1)] hover:text-[var(--accent)] transition-colors leading-snug line-clamp-1 group-hover:line-clamp-none">
                    {a.title}
                  </a>
                  <p className="text-[12px] text-[var(--text-2)] mt-0.5 leading-relaxed line-clamp-1 group-hover:line-clamp-2 transition-all">
                    {a.summary}
                  </p>
                </div>
                <a href={a.url} target="_blank" rel="noopener noreferrer"
                  className="shrink-0 p-1.5 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-[var(--bg-2)] text-[var(--text-3)] hover:text-[var(--accent)] transition-all">
                  <ExternalLink size={12} />
                </a>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
