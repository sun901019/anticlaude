"use client";
import { X } from "lucide-react";
import {
  Product, Setting,
  PRODUCT_STATUS_LABELS, PRODUCT_STATUS_COLOR, ROLE_COLOR,
  SH, shInputCls, fmt, pct,
  Field, ShToggleGroup,
} from "./ecommerce-shared";

export type DrawerTab = "decision" | "logistics" | "ops";

type Props = {
  product: Product;
  edits: Record<string, any>;
  setEdits: React.Dispatch<React.SetStateAction<Record<string, any>>>;
  drawerTab: DrawerTab;
  setDrawerTab: (t: DrawerTab) => void;
  prices: {
    traffic: number; core: number; profit: number;
    landed_cost?: number; fee_rate?: number; market_warning?: string;
    ceiling_traffic?: number; ceiling_core?: number; ceiling_profit?: number;
    max_rmb_traffic?: number; max_rmb_core?: number; max_rmb_profit?: number;
    breakdown?: {
      cost_twd: number; cross_border_freight: number; shipping_cost: number;
      packaging_cost: number; fss_cost: number; fss_plan: string;
      commission_cost: number; transaction_cost: number;
      ccb_cost: number; promo_cost: number; penalty_cost: number;
      risk_cost: number; coupon_cost: number;
    };
  } | null;
  settings: Setting[];
  onClose: () => void;
  onSave: () => void;
  onUpdateSales: () => void;
  onRestock: () => void;
  onPricingDecision: () => void;
  onDelete: () => void;
};

export function ProductDrawer({
  product, edits, setEdits, drawerTab, setDrawerTab,
  prices, settings, onClose, onSave, onUpdateSales, onRestock, onPricingDecision, onDelete,
}: Props) {
  const merged = { ...product, ...edits };
  const dp = prices ?? { traffic: 0, core: 0, profit: 0 };
  const de = edits as Record<string, any>;
  const dSet = (k: string, v: any) => setEdits(e => ({ ...e, [k]: v }));
  const iCls = `${shInputCls} text-[13px]`;
  const hasEdits = Object.keys(edits).length > 0;

  const stock = product.total_stock ?? 0;
  const margin = product.gross_margin_est;

  const aiSummary = stock === 0 ? "庫存已清零，請盡快補貨"
    : stock <= 5 ? `庫存僅剩 ${stock} 件，建議補貨`
    : margin != null && margin >= 0.40 ? "毛利健康，可考慮拉大廣告預算"
    : margin != null && margin < 0.25 ? "毛利偏低，建議重新評估定價"
    : "商品運作正常，持續觀察表現";

  const nextAction = stock === 0 ? { text: "補貨", color: "#dc2626", bg: "#fef2f2" }
    : stock <= 5 ? { text: "留意庫存", color: "#d97706", bg: "#fffbeb" }
    : margin == null ? { text: "設定售價", color: SH.primary, bg: SH.light }
    : margin >= 0.40 ? { text: "可放大", color: "#16a34a", bg: "#f0fdf4" }
    : margin >= 0.25 ? { text: "持續觀察", color: "#2563eb", bg: "#eff6ff" }
    : { text: "調整定價", color: "#dc2626", bg: "#fef2f2" };

  return (
    <>
      <div className="fixed inset-0 z-40 bg-black/30" onClick={onClose} />
      <div className="fixed right-0 top-0 h-full z-50 w-full max-w-[480px] shadow-2xl flex flex-col"
        style={{ background: "var(--surface)", borderLeft: `3px solid ${SH.primary}` }}>

        {/* ═ Layer A: Header Summary ═ */}
        <div className="px-5 pt-4 pb-3 shrink-0" style={{ background: SH.surface, borderBottom: `1px solid ${SH.border}` }}>
          <div className="flex items-start justify-between">
            <div className="min-w-0 flex-1">
              <div className="text-[11px] font-600 mb-0.5" style={{ color: SH.muted }}>{product.sku || "—"}</div>
              <div className="text-[18px] font-700 text-[var(--text-1)] leading-snug truncate">{product.name}</div>
              <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
                <span className={`text-[10px] px-2 py-0.5 rounded-full ${PRODUCT_STATUS_COLOR[product.status] || "bg-gray-100 text-gray-500"}`}>
                  {PRODUCT_STATUS_LABELS[product.status] || product.status}
                </span>
                <span className={`text-[10px] px-2 py-0.5 rounded-full ${ROLE_COLOR[merged.role] || "bg-gray-100 text-gray-500"}`}>
                  {merged.role || "未分類"}
                </span>
                {hasEdits && <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-50 text-amber-600">● 已修改</span>}
              </div>
            </div>
            <button onClick={onClose}
              className="p-1.5 rounded-[8px] hover:bg-white/60 text-[var(--text-3)] ml-2 shrink-0 transition-colors">
              <X size={17} />
            </button>
          </div>
          <div className="mt-2.5 flex items-center gap-2 px-3 py-2 rounded-[8px] text-[12px]"
            style={{ background: stock === 0 || (margin != null && margin < 0.25) ? "#fef2f2" : "white", border: "1px solid var(--border)" }}>
            <span style={{ color: stock === 0 || (margin != null && margin < 0.25) ? "#dc2626" : SH.muted }}>●</span>
            <span style={{ color: "var(--text-2)" }}>{aiSummary}</span>
          </div>
        </div>

        {/* ═ Layer B: Decision Cards ═ */}
        <div className="px-4 py-3 grid grid-cols-5 gap-2 shrink-0" style={{ background: "white", borderBottom: `1px solid ${SH.border}` }}>
          <div className="text-center">
            <div className="text-[9px] font-600 uppercase tracking-wide mb-1" style={{ color: SH.muted }}>目標售價</div>
            <div className="text-[14px] font-800" style={{ color: product.target_price ? SH.primary : "var(--text-3)" }}>
              {product.target_price ? `NT$${fmt(product.target_price)}` : "未設定"}
            </div>
          </div>
          <div className="text-center">
            <div className="text-[9px] font-600 uppercase tracking-wide mb-1" style={{ color: SH.muted }}>引流底價</div>
            <div className="text-[14px] font-800 text-[var(--text-1)]">NT${dp.traffic}</div>
          </div>
          <div className="text-center">
            <div className="text-[9px] font-600 uppercase tracking-wide mb-1" style={{ color: SH.muted }}>毛利率</div>
            <div className="text-[14px] font-800" style={{ color: margin == null ? "var(--text-3)" : margin >= 0.40 ? "#16a34a" : margin >= 0.25 ? "#d97706" : "#dc2626" }}>
              {margin != null ? pct(margin) : "—"}
            </div>
          </div>
          <div className="text-center">
            <div className="text-[9px] font-600 uppercase tracking-wide mb-1" style={{ color: SH.muted }}>庫存</div>
            <div className="text-[14px] font-800" style={{ color: stock === 0 ? "#dc2626" : stock <= 5 ? "#d97706" : "var(--text-1)" }}>
              {stock} 件
            </div>
          </div>
          <div className="text-center">
            <div className="text-[9px] font-600 uppercase tracking-wide mb-1" style={{ color: SH.muted }}>下一步</div>
            <div className="text-[11px] font-700 px-1.5 py-0.5 rounded-full inline-block" style={{ background: nextAction.bg, color: nextAction.color }}>
              {nextAction.text}
            </div>
          </div>
        </div>

        {/* ═ Tab Navigation ═ */}
        <div className="flex shrink-0" style={{ borderBottom: `1px solid ${SH.border}`, background: "var(--surface)" }}>
          {([
            { id: "decision"  as const, label: "定價決策" },
            { id: "logistics" as const, label: "成本物流" },
            { id: "ops"       as const, label: "操作"     },
          ]).map(t => (
            <button key={t.id} onClick={() => setDrawerTab(t.id)}
              className="flex-1 py-2.5 text-[12px] font-600 transition-all border-b-2"
              style={drawerTab === t.id
                ? { color: SH.primary, borderBottomColor: SH.primary, background: "white" }
                : { color: "var(--text-3)", borderBottomColor: "transparent" }}>
              {t.label}
            </button>
          ))}
        </div>

        {/* ═ Layer C: Tab Content ═ */}
        <div className="flex-1 p-4 space-y-4 overflow-y-auto">

          {/* ── Tab: 定價決策 ── */}
          {drawerTab === "decision" && (
            <>
              {/* ① 角色定位 + 建議售價（合一） */}
              <section>
                <ShToggleGroup
                  value={merged.role || ""}
                  onChange={v => dSet("role", v)}
                  options={[
                    { value: "引流款", label: "引流款", sub: "25%+" },
                    { value: "毛利款", label: "毛利款", sub: "40%+" },
                    { value: "主力款", label: "主力款", sub: "50%+" },
                  ]} />
                {dp.traffic > 0 && (
                  <div className="mt-2 rounded-[10px] overflow-hidden" style={{ border: `1px solid ${SH.border}` }}>
                    <div className="grid grid-cols-3 divide-x">
                      {(() => {
                        const cfg3 = Object.fromEntries(settings.map(s => [s.key, s.value]));
                        const tPct = Math.round(((cfg3["traffic_margin_target"] as number) ?? 0.25) * 100);
                        const cPct = Math.round(((cfg3["core_margin_target"]    as number) ?? 0.40) * 100);
                        const pPct = Math.round(((cfg3["profit_margin_target"]  as number) ?? 0.55) * 100);
                        return [
                          { label: "引流款", price: dp.traffic, desc: `${tPct}%`, color: "#92400e", bg: "#fffbeb", role: "引流款" },
                          { label: "毛利款", price: dp.core,    desc: `${cPct}%`, color: SH.primary, bg: SH.light, role: "毛利款" },
                          { label: "主力款", price: dp.profit,  desc: `${pPct}%`, color: "#15803d",  bg: "#f0fdf4", role: "主力款" },
                        ];
                      })().map(({ label, price, desc, color, bg, role }) => {
                        const isActive = (merged.role || "") === role;
                        return (
                          <div key={label} className="py-2.5 text-center cursor-pointer transition-all"
                            style={{ background: isActive ? bg : "var(--surface)", outline: isActive ? `2px solid ${color}` : "none" }}
                            onClick={() => dSet("role", role)}>
                            <div className="text-[9px] font-600" style={{ color }}>{label}</div>
                            <div className="text-[14px] font-800 mt-0.5" style={{ color }}>NT$ {price}</div>
                            <div className="text-[9px] mt-0.5" style={{ color, opacity: 0.65 }}>{desc} 毛利</div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </section>

              {/* ② 情境狀態 chips */}
              {(() => {
                const ccb = merged.ccb_plan || "none";
                const isPromo = !!merged.is_promo_day;
                const days = parseInt(String(merged.fulfillment_days || 1));
                const chips: { label: string; color: string; bg: string }[] = [];
                if (ccb === "ccb5")  chips.push({ label: "CCB5 +1.5%",     color: SH.primary, bg: SH.light });
                else if (ccb === "ccb10") chips.push({ label: "CCB10 +2.5%", color: SH.primary, bg: SH.light });
                if (isPromo && ccb === "ccb10") chips.push({ label: "促銷日 免費（CCB10）", color: "#15803d", bg: "#f0fdf4" });
                else if (isPromo) chips.push({ label: "促銷日 +2%", color: "#d97706", bg: "#fffbeb" });
                if (days > 2) chips.push({ label: `備貨 ${days}天 +3%`, color: "#dc2626", bg: "#fef2f2" });
                if (chips.length === 0) return null;
                return (
                  <div className="flex flex-wrap gap-1.5">
                    {chips.map(c => (
                      <span key={c.label} className="text-[10px] font-700 px-2 py-0.5 rounded-full" style={{ color: c.color, background: c.bg }}>
                        {c.label}
                      </span>
                    ))}
                  </div>
                );
              })()}

              {/* ③ 目標售價 + 角色評估 */}
              <section className="space-y-2">
                <Field label="目標售價（NT$）">
                  <input className={iCls} type="number" placeholder={String(product.target_price ?? "—")}
                    value={de.target_price ?? ""} onChange={e => dSet("target_price", e.target.value)} />
                </Field>

                {/* 角色評估 badge */}
                {(de.target_price || product.target_price) && (() => {
                  const tp = parseFloat(de.target_price ?? String(product.target_price ?? ""));
                  if (!tp) return null;
                  const rf = tp >= dp.profit ? { label: "主力款", col: "#15803d" }
                    : tp >= dp.core    ? { label: "毛利款", col: SH.primary }
                    : tp >= dp.traffic ? { label: "引流款", col: "#92400e" }
                    : { label: "低於成本", col: "#dc2626" };
                  return (
                    <div className="px-3 py-1.5 rounded-[8px] text-[11px] flex justify-between items-center" style={{ background: "var(--bg-2)" }}>
                      <span style={{ color: "var(--text-3)" }}>NT$ {tp} →</span>
                      <span className="font-700" style={{ color: rf.col }}>{rf.label}</span>
                    </div>
                  );
                })()}
              </section>

              {/* ④ 市場價格帶 */}
              <section className="space-y-2">
                <div className="text-[10px] font-700 uppercase tracking-wider" style={{ color: "var(--text-3)" }}>市場價格帶</div>
                <div className="grid grid-cols-2 gap-2">
                  <Field label="市場低價（NT$）" hint="競品最低">
                    <input className={iCls} type="number" placeholder={String(product.market_price_low ?? "—")}
                      value={de.market_price_low ?? ""} onChange={e => dSet("market_price_low", e.target.value)} />
                  </Field>
                  <Field label="市場高價（NT$）" hint="競品最高">
                    <input className={iCls} type="number" placeholder={String(product.market_price_high ?? "—")}
                      value={de.market_price_high ?? ""} onChange={e => dSet("market_price_high", e.target.value)} />
                  </Field>
                </div>

                {/* 市場警示 */}
                {prices?.market_warning && (
                  <div className="px-3 py-2 rounded-[8px] text-[11px] font-600" style={{ background: "#fef2f2", color: "#dc2626" }}>
                    ⚠ {prices.market_warning}
                  </div>
                )}

                {/* 天花板反推卡片 */}
                {prices?.ceiling_traffic != null && (
                  <div className="rounded-[10px] overflow-hidden" style={{ border: `1px solid ${SH.border}` }}>
                    <div className="px-3 py-1.5 text-[9px] font-700 flex items-center justify-between"
                      style={{ background: SH.light, color: SH.primary }}>
                      <span>1688 採購上限</span>
                      <span className="font-400" style={{ color: SH.muted }}>
                        市場高價 NT${de.market_price_high || product.market_price_high} 反推
                      </span>
                    </div>
                    <div className="grid grid-cols-3 divide-x text-center py-2">
                      {([
                        { label: "引流款", ceiling: prices.ceiling_traffic, rmb: prices.max_rmb_traffic, color: "#92400e", bg: "#fffbeb" },
                        { label: "毛利款", ceiling: prices.ceiling_core,    rmb: prices.max_rmb_core,    color: SH.primary,  bg: SH.light },
                        { label: "主力款", ceiling: prices.ceiling_profit,  rmb: prices.max_rmb_profit,  color: "#15803d",   bg: "#f0fdf4" },
                      ] as const).map(({ label, ceiling, rmb, color, bg }) => (
                        <div key={label} className="py-1" style={{ background: bg }}>
                          <div className="text-[9px] font-600" style={{ color }}>{label}</div>
                          <div className="text-[12px] font-800 mt-0.5" style={{ color }}>≤ ¥{rmb}</div>
                          <div className="text-[9px]" style={{ color, opacity: 0.65 }}>NT${ceiling}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </section>

              {/* ⑤ 情境設定折疊 */}
              <details className="group">
                <summary className="flex items-center gap-1.5 cursor-pointer text-[11px] font-600 select-none list-none py-1"
                  style={{ color: SH.muted }}>
                  <span className="transition-transform group-open:rotate-90">▶</span> 情境設定
                  <span className="text-[10px] font-400 ml-1" style={{ color: "var(--text-3)" }}>
                    {merged.ccb_plan && merged.ccb_plan !== "none" ? merged.ccb_plan.toUpperCase() + " · " : ""}
                    {merged.is_promo_day ? "促銷日 · " : ""}
                    廣告 · 備貨 {merged.fulfillment_days ?? 1}天
                  </span>
                </summary>
                <div className="mt-2 rounded-[10px] p-3 space-y-3" style={{ background: SH.surface, border: `1px solid ${SH.border}` }}>
                  <Field label="廣告預算（%）">
                    <input className={iCls} type="number" step="0.1" placeholder="例：10"
                      value={de.ad_budget ?? ""} onChange={e => dSet("ad_budget", e.target.value)} />
                  </Field>
                  <div>
                    <div className="text-[10px] font-600 mb-1.5" style={{ color: SH.muted }}>CCB 方案</div>
                    <div className="grid grid-cols-3 gap-1.5 text-[11px]">
                      {([
                        { v: "none",  label: "無 CCB",  sub: "" },
                        { v: "ccb5",  label: "CCB5",    sub: "-1.5% 毛利" },
                        { v: "ccb10", label: "CCB10",   sub: "-2.5% + 免促銷" },
                      ] as const).map(({ v, label, sub }) => (
                        <button key={v} type="button" onClick={() => dSet("ccb_plan", v)}
                          className="py-1.5 px-1 rounded-[7px] font-600 transition-all flex flex-col items-center gap-0.5"
                          style={merged.ccb_plan === v ? { background: SH.primary, color: "white" } : { background: "white", color: "#666", border: "1px solid #e5e7eb" }}>
                          <span>{label}</span>
                          {sub && <span className="text-[9px] font-400" style={{ opacity: merged.ccb_plan === v ? 0.8 : 0.6 }}>{sub}</span>}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] font-600 mb-1.5" style={{ color: SH.muted }}>活動日</div>
                    <div className="grid grid-cols-2 gap-1.5 text-[11px]">
                      {([
                        { v: "false", label: "平日",       sub: "" },
                        { v: "true",  label: "促銷日",     sub: merged.ccb_plan === "ccb10" ? "CCB10 已免促銷費" : "+2% 費用" },
                      ] as const).map(({ v, label, sub }) => (
                        <button key={v} type="button" onClick={() => dSet("is_promo_day", v === "true")}
                          className="py-1.5 rounded-[7px] font-600 transition-all flex flex-col items-center gap-0.5"
                          style={String(merged.is_promo_day) === v ? { background: SH.primary, color: "white" } : { background: "white", color: "#666", border: "1px solid #e5e7eb" }}>
                          <span>{label}</span>
                          {sub && <span className="text-[9px] font-400" style={{ opacity: String(merged.is_promo_day) === v ? 0.8 : 0.6 }}>{sub}</span>}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] font-600 mb-1.5" style={{ color: SH.muted }}>備貨天數</div>
                    <div className="grid grid-cols-4 gap-1.5 text-[11px]">
                      {(["1","2","3","4"] as const).map(v => (
                        <button key={v} type="button" onClick={() => dSet("fulfillment_days", parseInt(v))}
                          className="py-1.5 rounded-[7px] font-600 transition-all"
                          style={String(merged.fulfillment_days || 1) === v ? { background: SH.primary, color: "white" } : { background: "white", color: "#666", border: "1px solid #e5e7eb" }}>
                          {v}天
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </details>
            </>
          )}

          {/* ── Tab: 成本物流 ── */}
          {drawerTab === "logistics" && (
            <>
              <section>
                <div className="text-[10px] font-700 uppercase tracking-wider mb-2" style={{ color: "var(--text-3)" }}>費用結構估算</div>
                {prices?.breakdown ? (() => {
                  const bk = prices.breakdown;
                  const fixedRows = [
                    { label: "進貨成本", val: bk.cost_twd },
                    { label: "集運費", val: bk.cross_border_freight },
                    { label: "末端配送", val: bk.shipping_cost },
                    { label: "包材費", val: bk.packaging_cost },
                    { label: `FSS 免運費（${bk.fss_plan === "fixed" ? "固定制" : "百分比制"}）`, val: bk.fss_cost },
                  ].filter(r => r.val > 0);
                  const cfg = Object.fromEntries(settings.map(s => [s.key, s.value]));
                  const commPct = Math.round(((cfg["platform_fee"] as number) ?? 0.06) * 100 * 10) / 10;
                  const txPct   = Math.round(((cfg["payment_fee"]  as number) ?? 0.025) * 100 * 10) / 10;
                  const platformRows = [
                    { label: `成交手續費（${commPct}%）`, val: bk.commission_cost },
                    { label: `金流費（${txPct}%）`,       val: bk.transaction_cost },
                  ];
                  const ccbPlan = (merged.ccb_plan || product.ccb_plan || "none") as string;
                  const scenarioRows = [
                    bk.ccb_cost > 0     && { label: ccbPlan === "ccb10" ? "CCB10 回饋費（+2.5%）" : "CCB5 回饋費（+1.5%）", val: bk.ccb_cost, color: SH.primary },
                    bk.promo_cost > 0   && { label: "促銷日加成（+2%）", val: bk.promo_cost, color: "#d97706" },
                    bk.penalty_cost > 0 && { label: "備貨懲罰費（+3%）", val: bk.penalty_cost, color: "#dc2626" },
                  ].filter(Boolean) as { label: string; val: number; color: string }[];
                  const riskRows = [
                    { label: "退貨破損費", val: bk.risk_cost },
                    bk.coupon_cost > 0 && { label: "折扣券費", val: bk.coupon_cost },
                  ].filter(Boolean) as { label: string; val: number }[];
                  return (
                    <div className="rounded-[12px] overflow-hidden text-[12px]" style={{ border: "1px solid var(--border)" }}>
                      {/* Fixed cost block */}
                      <div className="px-3 pt-2.5 pb-1.5 space-y-1.5" style={{ background: "var(--bg-2)" }}>
                        <div className="text-[9px] font-700 uppercase tracking-wide mb-1 flex justify-between" style={{ color: "var(--text-4)" }}>
                          <span>落地成本</span>
                          <span className="font-400">商品 + 頭程 + 集運 + 包材</span>
                        </div>
                        {fixedRows.map(r => (
                          <div key={r.label} className="flex justify-between">
                            <span style={{ color: "var(--text-3)" }}>{r.label}</span>
                            <span className="font-600">NT$ {Math.round(r.val)}</span>
                          </div>
                        ))}
                        <div className="flex justify-between pt-1 font-700" style={{ borderTop: "1px solid var(--border)", color: SH.primary }}>
                          <span>落地成本</span>
                          <span>NT$ {prices.landed_cost != null ? Math.round(prices.landed_cost) : "—"}</span>
                        </div>
                      </div>
                      {/* Platform fees */}
                      <div className="px-3 py-1.5 space-y-1.5" style={{ borderTop: "1px solid var(--border)" }}>
                        <div className="text-[9px] font-700 uppercase tracking-wide mb-1 flex justify-between" style={{ color: "var(--text-4)" }}>
                          <span>平台基礎費率</span>
                          <span className="font-400">蝦皮固定收取</span>
                        </div>
                        {platformRows.map(r => (
                          <div key={r.label} className="flex justify-between">
                            <span style={{ color: "var(--text-3)" }}>{r.label}</span>
                            <span className="font-600">NT$ {Math.round(r.val)}</span>
                          </div>
                        ))}
                      </div>
                      {/* Scenario fees */}
                      {scenarioRows.length > 0 && (
                        <div className="px-3 py-1.5 space-y-1.5" style={{ borderTop: "1px solid var(--border)", background: "#fffbeb" }}>
                          <div className="text-[9px] font-700 uppercase tracking-wide mb-1 flex justify-between" style={{ color: "#92400e" }}>
                            <span>情境加成</span>
                            <span className="font-400">CCB / 活動日 / 備貨懲罰</span>
                          </div>
                          {scenarioRows.map(r => (
                            <div key={r.label} className="flex justify-between">
                              <span style={{ color: r.color }}>{r.label}</span>
                              <span className="font-700" style={{ color: r.color }}>NT$ {Math.round(r.val)}</span>
                            </div>
                          ))}
                        </div>
                      )}
                      {/* Risk */}
                      <div className="px-3 py-1.5 space-y-1.5" style={{ borderTop: "1px solid var(--border)" }}>
                        <div className="text-[9px] font-700 uppercase tracking-wide mb-1" style={{ color: "var(--text-4)" }}>風險假設</div>
                        {riskRows.map(r => (
                          <div key={r.label} className="flex justify-between">
                            <span style={{ color: "var(--text-3)" }}>{r.label}</span>
                            <span className="font-600">NT$ {Math.round(r.val)}</span>
                          </div>
                        ))}
                      </div>
                      {/* Summary */}
                      {dp.traffic > 0 && (
                        <div className="px-3 py-2 flex justify-between font-700" style={{ borderTop: `1px solid ${SH.border}`, background: SH.light }}>
                          <span style={{ color: SH.muted }}>最低建議售價</span>
                          <span style={{ color: SH.primary }}>NT$ {dp.traffic}</span>
                        </div>
                      )}
                    </div>
                  );
                })() : (
                  <div className="rounded-[12px] p-3 space-y-2 text-[12px]" style={{ background: "var(--bg-2)", border: "1px solid var(--border)" }}>
                    <div className="flex justify-between">
                      <span style={{ color: "var(--text-3)" }}>落地成本估算</span>
                      <span className="font-700 text-[var(--text-1)]">
                        {prices?.landed_cost != null ? `NT$ ${Math.round(prices.landed_cost)}` : "—"}
                      </span>
                    </div>
                    {dp.traffic > 0 && (
                      <div className="flex justify-between pt-1.5" style={{ borderTop: "1px solid var(--border)" }}>
                        <span className="font-600" style={{ color: SH.muted }}>最低建議售價</span>
                        <span className="font-700" style={{ color: SH.primary }}>NT$ {dp.traffic}</span>
                      </div>
                    )}
                  </div>
                )}
              </section>

              <section>
                <div className="text-[10px] font-700 uppercase tracking-wider mb-2" style={{ color: "var(--text-3)" }}>成本與物流</div>
                <div className="space-y-3">
                  <Field label="採購模式">
                    <ShToggleGroup
                      value={merged.procurement_mode || "standard_1688"}
                      onChange={v => dSet("procurement_mode", v)}
                      options={[
                        { value: "standard_1688", label: "1688 直購" },
                        { value: "qql_agent",     label: "QQL 代購" },
                      ]} />
                  </Field>
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="商品價（¥）">
                      <input className={iCls} type="number" placeholder={String(product.cost_rmb ?? "")}
                        value={de.cost_rmb ?? ""} onChange={e => dSet("cost_rmb", e.target.value)} />
                    </Field>
                    <Field label="境內運費（¥）">
                      <input className={iCls} type="number" placeholder={String(product.head_freight_rmb ?? "")}
                        value={de.head_freight_rmb ?? ""} onChange={e => dSet("head_freight_rmb", e.target.value)} />
                    </Field>
                    <Field label="重量（kg）">
                      <input className={iCls} type="number" step="0.1" placeholder={String(product.weight_kg ?? "0")}
                        value={de.weight_kg ?? ""} onChange={e => dSet("weight_kg", e.target.value)} />
                    </Field>
                    <Field label="包材費（NT$）">
                      <input className={iCls} type="number" placeholder={String(product.packaging_cost ?? "0")}
                        value={de.packaging_cost ?? ""} onChange={e => dSet("packaging_cost", e.target.value)} />
                    </Field>
                  </div>
                  {(merged.procurement_mode || product.procurement_mode) === "qql_agent" && (
                    <Field label="體積（選填）" hint="長 × 寬 × 高 cm">
                      <div className="grid grid-cols-3 gap-2">
                        {(["length_cm", "width_cm", "height_cm"] as const).map((dim, i) => (
                          <input key={dim} className={iCls} type="number" step="0.1"
                            placeholder={[String(product.length_cm ?? ""), String(product.width_cm ?? ""), String(product.height_cm ?? "")][i] || ["長","寬","高"][i]}
                            value={(de as any)[dim] ?? ""} onChange={e => dSet(dim, e.target.value)} />
                        ))}
                      </div>
                    </Field>
                  )}
                  {(merged.procurement_mode || product.procurement_mode || "standard_1688") === "standard_1688" && (
                    <>
                      <Field label="集運方式">
                        <ShToggleGroup
                          value={merged.freight_type || "sea_fast"}
                          onChange={v => dSet("freight_type", v)}
                          options={[
                            { value: "sea_fast",    label: "海快",  sub: "NT$45/kg" },
                            { value: "sea_regular", label: "海運",  sub: "NT$20/kg" },
                            { value: "air",         label: "空運",  sub: "NT$115/kg" },
                          ]} />
                      </Field>
                      <Field label="貨物類型">
                        <ShToggleGroup
                          value={merged.is_special_goods ? "true" : "false"}
                          onChange={v => dSet("is_special_goods", v === "true")}
                          options={[
                            { value: "false", label: "普貨" },
                            { value: "true",  label: "特貨", sub: "+NT$15/kg" },
                          ]} />
                      </Field>
                    </>
                  )}
                </div>
              </section>
            </>
          )}

          {/* ── Tab: 操作 ── */}
          {drawerTab === "ops" && (
            <>
              <section>
                <div className="text-[10px] font-700 uppercase tracking-wider mb-2" style={{ color: "var(--text-3)" }}>庫存 & 備註</div>
                <div className="space-y-3">
                  <div className="rounded-[10px] px-3 py-2.5" style={{ background: "var(--bg-2)" }}>
                    <div className="text-[10px] text-[var(--text-3)] mb-0.5">現有庫存</div>
                    <div className={`font-700 text-[16px] ${stock === 0 ? "text-red-500" : "text-[var(--text-1)]"}`}>
                      {stock} 件
                    </div>
                  </div>
                  <Field label="備註">
                    <input className={iCls} placeholder="供應商備注、產品特性等"
                      value={de.notes ?? (product.notes || "")}
                      onChange={e => dSet("notes", e.target.value)} />
                  </Field>
                </div>
              </section>

              <section>
                <div className="text-[10px] font-700 uppercase tracking-wider mb-2" style={{ color: "var(--text-3)" }}>系列分組</div>
                <div className="space-y-2">
                  <Field label="系列名稱" hint="同一商品概念下的共用名稱，例：躺贏招財貓">
                    <input className={iCls} placeholder="例：躺贏招財貓"
                      value={de.family_name ?? (product.family_name || "")}
                      onChange={e => dSet("family_name", e.target.value)} />
                  </Field>
                  <Field label="款式名稱" hint="同系列下的具體款式，例：閒樂款 / 招財款">
                    <input className={iCls} placeholder="例：閒樂款"
                      value={de.variant_name ?? (product.variant_name || "")}
                      onChange={e => dSet("variant_name", e.target.value)} />
                  </Field>
                  {(product.family_name || de.family_name) && (
                    <div className="px-3 py-2 rounded-[8px] text-[11px]" style={{ background: SH.light }}>
                      <span style={{ color: SH.muted }}>所屬系列：</span>
                      <span className="font-700" style={{ color: SH.primary }}>
                        {de.family_name || product.family_name}
                      </span>
                      {(de.variant_name || product.variant_name) && (
                        <span style={{ color: SH.muted }}> · {de.variant_name || product.variant_name}</span>
                      )}
                    </div>
                  )}
                </div>
              </section>

              <section>
                <div className="text-[10px] font-700 uppercase tracking-wider mb-2" style={{ color: "var(--text-3)" }}>商品狀態</div>
                <select className={iCls}
                  value={de.status ?? product.status ?? ""}
                  onChange={e => dSet("status", e.target.value)}>
                  {Object.entries(PRODUCT_STATUS_LABELS).map(([k, v]) => (
                    <option key={k} value={k}>{v}</option>
                  ))}
                </select>
              </section>
            </>
          )}

        </div>

        {/* ═ Layer D: Actions Footer ═ */}
        <div className="px-4 py-3 shrink-0" style={{ borderTop: `1px solid ${SH.border}`, background: "var(--surface)" }}>
          <div className="grid grid-cols-2 gap-2 mb-2">
            <button onClick={onSave}
              className="py-2.5 rounded-[12px] text-[13px] font-700 text-white transition-all"
              style={{ background: hasEdits ? SH.primary : "#ccc" }}
              disabled={!hasEdits}>
              {hasEdits ? "儲存修改" : "尚未修改"}
            </button>
            <button onClick={onUpdateSales}
              className="py-2.5 rounded-[12px] text-[13px] font-600 border transition-colors hover:bg-emerald-50 text-emerald-700 border-emerald-200">
              更新銷售
            </button>
          </div>
          <div className="grid grid-cols-2 gap-2 mb-2">
            <button onClick={onRestock}
              className="py-2 rounded-[10px] text-[12px] font-600 border transition-colors hover:bg-blue-50 text-blue-600 border-blue-200">
              補貨入庫
            </button>
            <button onClick={onPricingDecision}
              className="py-2 rounded-[10px] text-[12px] font-600 border transition-colors text-[var(--text-2)] border-[var(--border)] hover:bg-[var(--bg-2)]">
              定價決策
            </button>
          </div>
          <button onClick={onDelete}
            className="w-full py-1.5 text-[11px] font-500 text-red-400 hover:text-red-600 transition-colors">
            刪除此商品
          </button>
        </div>
      </div>
    </>
  );
}
