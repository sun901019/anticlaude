"use client";
import { X, Check } from "lucide-react";

// ─── Types ───────────────────────────────────────────────────────────────────

export type Product = {
  sku: string; name: string; role: string; role_confirmed: number; product_type: string;
  cost_rmb: number; head_freight_rmb: number; cost_twd: number; target_price: number;
  market_price_low: number; market_price_high: number;
  total_stock: number; status: string; notes: string;
  weight_kg: number; packaging_cost: number;
  return_rate: number; damage_rate: number; coupon_rate: number;
  freight_type: string; is_special_goods: boolean;
  procurement_mode: string;
  length_cm: number | null; width_cm: number | null; height_cm: number | null;
  ccb_plan: string; is_promo_day: boolean; fulfillment_days: number;
  gross_margin_est: number | null;
  family_id?: string | null; family_name?: string | null; variant_name?: string | null;
  _newStock?: number;
};
export type ProductFamily = {
  family_id: string | null;
  family_name: string;
  variant_count: number;
  total_stock: number;
  best_margin: number | null;
  products: Product[];
};
export type Performance = {
  sku: string; record_date: string; current_price: number;
  sales_7d: number; revenue_7d: number; ad_spend_7d: number;
  current_stock: number; roas: number; gross_profit: number;
  gross_margin: number; next_action: string;
};
export type DashboardData = {
  summary: { monthly_revenue_est: number; monthly_profit_est: number; active_skus: number; avg_margin: number };
  top3: { sku: string; name: string; role: string; revenue_7d: number; gross_margin: number; next_action: string }[];
  low_stock_alert: { sku: string; name: string; current_stock: number; sales_7d: number }[];
};
export type CostBreakdown = {
  cost_twd: number; head_freight_cost: number; shipping_cost: number; packaging_cost: number;
  platform_cost: number; payment_cost: number; campaign_cost: number;
  discount_cost: number; risk_cost: number;
};
export type Pricing = {
  breakdown: CostBreakdown;
  fixed_cost: number; variable_cost: number; total_cost: number;
  profit: number; gross_margin: number; safe_cpa: number;
  recommended_price: number; conservative_price: number; suggested_role: string;
  cost_twd: number; min_price: number; suggested_price: number; target_margin: number; est_gross_margin: number;
};
export type Decision = {
  sku: string; name: string; role: string;
  pricing: Pricing | null;
  restock_qty: number; current_stock: number; gross_margin: number; next_action: string;
};
export type Setting = { key: string; value: number; label: string; unit: string };

// ─── Selection Types ──────────────────────────────────────────────────────────
export type Candidate = {
  candidate_id: string; product_name: string; market_type: string;
  source_platform: string; category: string; status: string;
  selection_status: string; risk_score: number | null;
  score_total?: number; created_at: string;
};
export type Analysis = {
  id: number; candidate_id: string; analysis_date: string;
  demand_score: number; competition_score: number; profit_score: number;
  pain_point_score: number; brand_fit_score: number;
  score_total: number; viability_band: string;
  recommended_role: string; role_confidence: number;
  decision_status: string; reasoning: string;
  negative_reviews_json: string; financials_json: string;
  score_breakdown_json: string;
  next_steps_json: string;
};
export type Report = {
  id: number; candidate_id: string; report_title: string;
  created_by_agent: string; created_at: string;
};
export type Lesson = {
  id: number; theme: string; lesson_type: string;
  lesson_text: string; confidence: number; created_at: string;
};
export type BundleSuggestion = {
  bundle_name: string; scene: string; role_composition: string;
  bundle_type?: "traffic" | "profit" | "scene" | "cleanup";
  source?: "relation" | "family" | "role" | "candidate";
  products: { candidate_id?: string; sku?: string; name: string; role: string; price: number; gross_margin?: number; stock?: number }[];
  base_price_sum: number; bundle_price: number;
  discount_pct: number; estimated_margin: number; viability_score?: number;
  suggestion_reason: string; bundle_action?: string;
};
export type Portfolio = {
  approved_count: number;
  role_distribution: Record<string, number>;
  portfolio_target: Record<string, string>;
  gaps: string[];
};

// ─── Constants ───────────────────────────────────────────────────────────────

export const ROLES = ["引流款", "毛利款", "主力款"];
export const PRODUCT_STATUS_LABELS: Record<string, string> = {
  idea: "靈感發現", investigating: "調查中", sample_pending: "可進樣",
  sample_received: "已進樣", evaluating: "待評估", ready: "可上架",
  listed: "已上架", testing_ads: "廣告測試中", scaling: "放大中", stopped: "停止/淘汰",
  active: "已上架", archived: "停止/淘汰",
};
export const PRODUCT_STATUS_COLOR: Record<string, string> = {
  idea: "bg-gray-50 text-gray-500", investigating: "bg-blue-50 text-blue-600",
  sample_pending: "bg-sky-50 text-sky-600", sample_received: "bg-cyan-50 text-cyan-700",
  evaluating: "bg-amber-50 text-amber-600", ready: "bg-lime-50 text-lime-700",
  listed: "bg-emerald-50 text-emerald-700", testing_ads: "bg-violet-50 text-violet-600",
  scaling: "bg-purple-50 text-purple-700", stopped: "bg-red-50 text-red-500",
  active: "bg-emerald-50 text-emerald-700", archived: "bg-red-50 text-red-500",
};
export const ROLE_COLOR: Record<string, string> = {
  "引流款": "bg-blue-50 text-blue-600",
  "毛利款": "bg-emerald-50 text-emerald-600",
  "主力款": "bg-violet-50 text-violet-600",
};
export const ACTION_COLOR: Record<string, string> = {
  "放大 (補貨/加預算)": "text-emerald-600",
  "觀察 (優化圖文)": "text-amber-500",
  "停售 (出清庫存)": "text-red-500",
};

export function fmt(n: number) { return n?.toLocaleString("zh-TW", { maximumFractionDigits: 0 }) ?? "—"; }
export function pct(n: number) { return n != null ? `${(n * 100).toFixed(1)}%` : "—"; }

export const emptyInv = { sku: "", cost_rmb: "", quantity: "", purchase_date: "", supplier: "", lead_days: "", procurement_mode: "standard_1688", coupon_rate: "" };
export const emptyProduct = {
  sku: "", name: "", cost_rmb: "", head_freight_rmb: "",
  freight_type: "sea_fast", weight_kg: "", is_special_goods: false,
  target_price: "", market_price_low: "", market_price_high: "",
  init_stock: "", keyword: "", notes: "", packaging_cost: "",
  return_rate: "", damage_rate: "", coupon_rate: "", supplier: "",
  ad_budget: "",
  ccb_plan: "none", is_promo_day: false, fulfillment_days: "1",
  procurement_mode: "standard_1688",
  length_cm: "", width_cm: "", height_cm: "",
  role: "", role_confirmed: false,
  product_type: "", scene: "",
  family_id: "", family_name: "", variant_name: "",
};

// ── 蝦皮品牌色（電商模組專用）────────────────────────────────────────────────
export const SH = {
  primary:  "#EE4D2D",
  strong:   "#D93C1A",
  light:    "#FFF1ED",
  surface:  "#FFF8F4",
  border:   "#F3D8CF",
  text:     "#2E221D",
  muted:    "#7A685F",
  get hover() { return this.strong; },
};

export const inputCls = "w-full px-4 py-3 rounded-[10px] text-[14px] border border-[var(--border)] bg-white text-[var(--text-1)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)] focus:ring-opacity-30 focus:border-[var(--accent)] transition-all placeholder:text-[var(--text-3)]";
export const shInputCls = "w-full px-4 py-3 rounded-[10px] text-[14px] border bg-white text-[var(--text-1)] focus:outline-none transition-all placeholder:text-[var(--text-3)]";

// ─── UI Primitives ────────────────────────────────────────────────────────────

export function Field({ label, required, hint, children }: { label: string; required?: boolean; hint?: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <label className="block text-[13px] font-600 text-[var(--text-1)]">
        {label}
        {required && <span className="text-[var(--accent)] ml-1">*</span>}
        {hint && <span className="text-[12px] font-400 text-[var(--text-3)] ml-2">{hint}</span>}
      </label>
      {children}
    </div>
  );
}

export function ToggleGroup({ value, onChange, options, fullWidth }: {
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string; sub?: string }[];
  fullWidth?: boolean;
}) {
  return (
    <div className={`flex gap-2 flex-wrap ${fullWidth ? "w-full" : ""}`}>
      {options.map(o => (
        <button
          key={o.value}
          type="button"
          onClick={() => onChange(o.value)}
          className={`flex-1 min-w-0 px-3 py-2.5 rounded-[10px] text-[13px] font-600 border transition-all text-center ${
            value === String(o.value)
              ? "text-white border-transparent"
              : "bg-white text-[var(--text-2)] border-[var(--border)] hover:border-[var(--accent)] hover:text-[var(--accent)]"
          }`}
          style={value === String(o.value) ? { background: "var(--accent)" } : {}}>
          {o.label}
          {o.sub && <span className={`block text-[10px] font-400 mt-0.5 ${value === String(o.value) ? "opacity-80" : "text-[var(--text-3)]"}`}>{o.sub}</span>}
        </button>
      ))}
    </div>
  );
}

export function ShToggleGroup({ value, onChange, options }: {
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string; sub?: string }[];
}) {
  return (
    <div className="flex gap-2">
      {options.map(o => {
        const active = value === String(o.value);
        return (
          <button
            key={o.value}
            type="button"
            onClick={() => onChange(o.value)}
            className="flex-1 min-w-0 px-3 py-2.5 rounded-[10px] text-[13px] font-600 border transition-all text-center"
            style={active
              ? { background: SH.primary, color: "white", borderColor: SH.primary }
              : { background: "white", color: "#666", borderColor: "#e5e7eb" }
            }>
            {o.label}
            {o.sub && <span className={`block text-[10px] font-400 mt-0.5 ${active ? "opacity-80" : "text-[#999]"}`}>{o.sub}</span>}
          </button>
        );
      })}
    </div>
  );
}

export function Modal({ title, subtitle, onClose, children }: { title: string; subtitle?: string; onClose: () => void; children: React.ReactNode }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: "rgba(0,0,0,0.45)", backdropFilter: "blur(4px)" }}>
      <div className="rounded-[20px] w-full max-w-[500px] max-h-[90vh] overflow-y-auto shadow-2xl"
        style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
        <div className="flex items-start justify-between px-6 pt-6 pb-5" style={{ borderBottom: "1px solid var(--border)" }}>
          <div>
            <h3 className="text-[17px] font-700 text-[var(--text-1)] tracking-tight">{title}</h3>
            {subtitle && <p className="text-[13px] text-[var(--text-3)] mt-0.5">{subtitle}</p>}
          </div>
          <button onClick={onClose}
            className="ml-4 p-2 rounded-[8px] hover:bg-[var(--bg-2)] text-[var(--text-3)] hover:text-[var(--text-1)] transition-colors">
            <X size={16} />
          </button>
        </div>
        <div className="px-6 py-5 space-y-5">{children}</div>
      </div>
    </div>
  );
}

export function ModalActions({ onCancel, onConfirm, disabled, label }: { onCancel: () => void; onConfirm: () => void; disabled?: boolean; label: string }) {
  return (
    <div className="flex gap-3 pt-2">
      <button onClick={onCancel}
        className="flex-1 py-3 rounded-[12px] text-[14px] font-500 text-[var(--text-2)] transition-colors"
        style={{ background: "var(--bg-2)", border: "1px solid var(--border)" }}>
        取消
      </button>
      <button onClick={onConfirm} disabled={disabled}
        className="flex-2 px-6 py-3 rounded-[12px] text-[14px] font-600 text-white disabled:opacity-40 flex items-center justify-center gap-2 transition-all"
        style={{ background: disabled ? "var(--text-3)" : "#EE4D2D", flex: 2 }}>
        <Check size={15} /> {label}
      </button>
    </div>
  );
}
