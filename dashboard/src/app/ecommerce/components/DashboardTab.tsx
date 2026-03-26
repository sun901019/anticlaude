"use client";
import { TrendingUp, AlertTriangle } from "lucide-react";
import { DashboardData, fmt, pct, SH, ROLE_COLOR, ACTION_COLOR } from "./ecommerce-shared";

type Props = {
  dash: DashboardData;
};

export function DashboardTab({ dash }: Props) {
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "月營收預估", value: `NT$ ${fmt(dash.summary.monthly_revenue_est)}`, sub: "7天×4" },
          { label: "月毛利預估", value: `NT$ ${fmt(dash.summary.monthly_profit_est)}`, sub: "扣廣告後" },
          { label: "平均毛利率", value: pct(dash.summary.avg_margin), sub: "全店" },
          { label: "在售 SKU", value: `${dash.summary.active_skus} 個`, sub: "Flow Lab" },
        ].map(({ label, value, sub }) => (
          <div key={label} className="rounded-[14px] p-5" style={{ background: "var(--surface)" }}>
            <div className="text-[12px] text-[var(--text-3)] mb-1">{label}</div>
            <div className="text-2xl font-700 text-[var(--text-1)]">{value}</div>
            <div className="text-[11px] text-[var(--text-4)] mt-1">{sub}</div>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-5">
        <div className="rounded-[14px] p-5 space-y-3" style={{ background: "var(--surface)" }}>
          <div className="flex items-center gap-2 text-[13px] font-600 text-[var(--text-1)]">
            <TrendingUp size={14} style={{ color: SH.primary }} /> 熱銷 Top 3
          </div>
          {dash.top3.length === 0 ? (
            <p className="text-[12px] text-[var(--text-3)]">尚無銷售數據，請先更新週銷售</p>
          ) : dash.top3.map((p, i) => (
            <div key={p.sku} className="flex items-center justify-between py-2 border-b border-[var(--border)] last:border-0">
              <div className="flex items-center gap-3">
                <span className="text-[13px] font-700 text-[var(--text-3)] w-4">{i + 1}</span>
                <div>
                  <div className="text-[13px] font-600 text-[var(--text-1)]">{p.name}</div>
                  <span className={`text-[11px] px-1.5 py-0.5 rounded-full ${ROLE_COLOR[p.role] || "bg-gray-50 text-gray-500"}`}>{p.role}</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-[13px] font-600">NT$ {fmt(p.revenue_7d)}</div>
                <div className={`text-[11px] ${ACTION_COLOR[p.next_action] || "text-[var(--text-3)]"}`}>{p.next_action}</div>
              </div>
            </div>
          ))}
        </div>
        <div className="rounded-[14px] p-5 space-y-3" style={{ background: "var(--surface)" }}>
          <div className="flex items-center gap-2 text-[13px] font-600 text-[var(--text-1)]">
            <AlertTriangle size={14} className="text-amber-500" /> 補貨警示
            <span className="ml-auto text-[11px] text-[var(--text-3)]">{dash.low_stock_alert.length} 個</span>
          </div>
          {dash.low_stock_alert.length === 0 ? (
            <p className="text-[12px] text-[var(--text-3)]">庫存充足</p>
          ) : (
            <div className="space-y-1 max-h-[200px] overflow-y-auto">
              {dash.low_stock_alert.map(p => (
                <div key={p.sku} className="flex items-center justify-between text-[12px] py-1.5 border-b border-[var(--border)] last:border-0">
                  <div>
                    <span className="font-600 text-[var(--text-1)]">{p.name}</span>
                    <span className="text-[var(--text-3)] ml-1.5 font-mono">{p.sku}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`font-600 ${p.current_stock === 0 ? "text-red-500" : "text-amber-500"}`}>庫存 {p.current_stock}</span>
                    <span className="text-[var(--text-3)]">週銷 {p.sales_7d}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
