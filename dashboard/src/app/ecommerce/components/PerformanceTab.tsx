"use client";
import { RefreshCw, Trash2 } from "lucide-react";
import { Performance, fmt, pct, SH, ACTION_COLOR } from "./ecommerce-shared";

type Props = {
  performances: (Performance & { name: string })[];
  loadPerformance: () => void;
};

function actionLabel(row: Performance & { name: string }): { text: string; color: string } {
  const m = row.gross_margin ?? 0;
  const s7 = row.sales_7d ?? 0;
  const stock = row.current_stock ?? 0;
  if (s7 === 0) return { text: "測試中", color: "#9ca3af" };
  if (m >= 0.40 && s7 > 0) return { text: "可放大", color: "#16a34a" };
  if (m < 0.25 && s7 > 0) return { text: "調整定價", color: "#dc2626" };
  if (m >= 0.25 && stock < 10) return { text: "補貨", color: "#d97706" };
  return { text: "持續觀察", color: "#2563eb" };
}

export function PerformanceTab({ performances, loadPerformance }: Props) {
  return (
    <div className="space-y-4">
      {performances.length > 0 && (() => {
        const totalRevenue = performances.reduce((s, p) => s + (p.revenue_7d || 0), 0);
        const totalProfit  = performances.reduce((s, p) => s + (p.gross_profit || 0), 0);
        const avgMargin    = performances.filter(p => p.gross_margin != null).reduce((s, p, _, a) => s + p.gross_margin / a.length, 0);
        const atRisk       = performances.filter(p => p.gross_margin != null && p.gross_margin < 0.25).length;
        const kpis = [
          { label: "7天總營收", value: `NT$ ${fmt(totalRevenue)}`, color: "var(--text-1)" },
          { label: "7天總毛利", value: `NT$ ${fmt(totalProfit)}`, color: totalProfit >= 0 ? "#16a34a" : "#dc2626" },
          { label: "平均毛利率", value: pct(avgMargin), color: avgMargin >= 0.3 ? "#16a34a" : avgMargin >= 0.15 ? "#d97706" : "#dc2626" },
          { label: "需關注商品", value: `${atRisk} 件`, color: atRisk > 0 ? SH.primary : "#16a34a" },
        ];
        return (
          <div className="grid grid-cols-4 gap-3">
            {kpis.map(k => (
              <div key={k.label} className="rounded-[12px] px-4 py-3" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
                <div className="text-[11px] text-[var(--text-3)] mb-1">{k.label}</div>
                <div className="text-[20px] font-700" style={{ color: k.color }}>{k.value}</div>
              </div>
            ))}
          </div>
        );
      })()}
      <div className="flex items-center justify-between">
        <p className="text-[13px] text-[var(--text-3)]">最新一筆週績效數據（每 SKU 取最近一次更新）</p>
        <button onClick={loadPerformance} className="flex items-center gap-1.5 text-[12px] text-[var(--text-3)] hover:text-[var(--text-1)]">
          <RefreshCw size={12} /> 重新整理
        </button>
      </div>
      <div className="rounded-[14px] overflow-x-auto" style={{ background: "var(--surface)" }}>
        <table className="w-full text-[13px] min-w-[900px]">
          <thead>
            <tr className="border-b border-[var(--border)]">
              {["SKU", "商品名稱", "目前售價", "7天銷量", "7天營收", "廣告花費", "毛利", "毛利率", "ROAS", "庫存", "策略", "廣告建議", "建議行動", ""].map(h => (
                <th key={h} className="text-left px-4 py-3 text-[12px] font-600 text-[var(--text-3)] whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {performances.length === 0 ? (
              <tr><td colSpan={12} className="px-4 py-8 text-center text-[var(--text-3)]">尚無績效數據，請在選品庫點擊 ↺ 更新週銷售</td></tr>
            ) : performances.map(p => (
              <tr key={p.sku} className="border-b border-[var(--border)] hover:bg-[var(--bg-2)] transition-colors group">
                <td className="px-4 py-3 font-mono text-[12px] text-[var(--text-3)]">{p.sku}</td>
                <td className="px-4 py-3 font-600 text-[var(--text-1)] max-w-[140px] truncate">{p.name}</td>
                <td className="px-4 py-3">{p.current_price ? `NT$ ${p.current_price}` : "—"}</td>
                <td className="px-4 py-3 text-center">{p.sales_7d ?? "—"}</td>
                <td className="px-4 py-3 font-600">{p.revenue_7d ? `NT$ ${fmt(p.revenue_7d)}` : "—"}</td>
                <td className="px-4 py-3 text-[var(--text-3)]">{p.ad_spend_7d ? `NT$ ${fmt(p.ad_spend_7d)}` : "0"}</td>
                <td className={`px-4 py-3 font-600 ${p.gross_profit > 0 ? "text-emerald-600" : "text-red-500"}`}>
                  {p.gross_profit != null ? `NT$ ${fmt(p.gross_profit)}` : "—"}
                </td>
                <td className={`px-4 py-3 font-700 ${p.gross_margin >= 0.3 ? "text-emerald-600" : p.gross_margin > 0 ? "text-amber-500" : "text-red-500"}`}>
                  {pct(p.gross_margin)}
                </td>
                <td className="px-4 py-3 text-[var(--text-2)]">{p.roas ? p.roas.toFixed(2) : "—"}</td>
                <td className="px-4 py-3 text-center">{p.current_stock ?? "—"}</td>
                <td className={`px-4 py-3 text-[12px] font-600 ${ACTION_COLOR[p.next_action] || "text-[var(--text-3)]"}`}>
                  {p.next_action || "—"}
                </td>
                <td className="px-4 py-3">
                  {(() => {
                    const gm = p.gross_margin;
                    const roas = p.roas;
                    if (gm <= 0) return <span className="px-2 py-0.5 rounded-full text-[11px] font-600 bg-red-50 text-red-500">停止投放</span>;
                    if (roas >= 2 && gm >= 0.3) return <span className="px-2 py-0.5 rounded-full text-[11px] font-600 bg-emerald-50 text-emerald-600">放大預算</span>;
                    if (roas >= 1 && gm >= 0.15) return <span className="px-2 py-0.5 rounded-full text-[11px] font-600 bg-blue-50 text-blue-600">維持/優化</span>;
                    if (!roas && gm >= 0.15) return <span className="px-2 py-0.5 rounded-full text-[11px] font-600 bg-violet-50 text-violet-600">建議測試</span>;
                    return <span className="px-2 py-0.5 rounded-full text-[11px] font-600 bg-amber-50 text-amber-600">優化效益</span>;
                  })()}
                </td>
                <td className="px-4 py-3">
                  {(() => {
                    const al = actionLabel(p);
                    return <span className="px-2 py-0.5 rounded-full text-[11px] font-600 whitespace-nowrap" style={{ background: al.color + "1a", color: al.color }}>{al.text}</span>;
                  })()}
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={async () => {
                      if (!confirm(`確定清除 ${p.sku} 的週績效紀錄？`)) return;
                      await fetch(`/api/ecommerce/performance/${p.sku}`, { method: "DELETE" });
                      loadPerformance();
                    }}
                    className="p-1.5 rounded-[6px] hover:bg-red-50 text-[var(--text-3)] hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                    title="清除週績效紀錄">
                    <Trash2 size={13} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
