"use client";
import { useEffect, useRef, useState } from "react";
import {
  ShoppingBag, TrendingUp, Plus, Package, BarChart3,
  Trash2, X, Check, RefreshCw, Save, Zap, ClipboardCheck,
  Settings, BookOpen, Layers,
} from "lucide-react";
import { fetchReviewQueue, decideReviewItem } from "@/lib/api";
import {
  Product, Performance, DashboardData, Pricing, Setting,
  BundleSuggestion, Portfolio, ProductFamily,
  PRODUCT_STATUS_LABELS, PRODUCT_STATUS_COLOR, ROLE_COLOR, ACTION_COLOR,
  fmt, pct, emptyInv, emptyProduct,
  SH, inputCls,
} from "./components/ecommerce-shared";
import { ManualTab } from "./components/ManualTab";
import { BundlesTab } from "./components/SelectionTabs";
import { ProductDrawer, DrawerTab } from "./components/ProductDrawer";
import { SalesModal } from "./components/SalesModal";
import { InboundModal } from "./components/InboundModal";
import { QuickAddModal } from "./components/QuickAddModal";
import { DashboardTab } from "./components/DashboardTab";
import { PerformanceTab } from "./components/PerformanceTab";

// ─── Page ────────────────────────────────────────────────────────────────────

export default function EcommercePage() {
  const [tab, setTab] = useState<"dashboard" | "products" | "performance" | "settings" | "manual" | "bundles">("dashboard");
  const [dash, setDash] = useState<DashboardData | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [performances, setPerformances] = useState<(Performance & { name: string })[]>([]);
  const [loading, setLoading] = useState(true);
  const DEFAULT_SETTINGS: Setting[] = [
    { key: "exchange_rate",       value: 4.5,   label: "人民幣匯率",   unit: "RMB→TWD" },
    { key: "platform_fee",        value: 0.05,  label: "平台手續費",   unit: "%" },
    { key: "payment_fee",         value: 0.12,  label: "金流手續費",   unit: "%" },
    { key: "shipping_per_kg",     value: 40,    label: "末端配送費（蝦皮物流補貼）", unit: "NT$/kg" },
    { key: "campaign_fee",        value: 0,     label: "蝦皮活動費",   unit: "%" },
    { key: "default_return_rate", value: 0.02,  label: "預設退貨率",   unit: "%" },
    { key: "default_damage_rate", value: 0.01,  label: "預設破損率",   unit: "%" },
    { key: "low_stock_days",      value: 7,     label: "低庫存警示天數", unit: "天" },
    { key: "last_mile_fee",       value: 0,     label: "末端配送費（平台包運填0）", unit: "NT$/件" },
  ];
  const [settings, setSettings] = useState<Setting[]>(DEFAULT_SETTINGS);
  const [settingsEdit, setSettingsEdit] = useState<Record<string, string>>({
    exchange_rate: "4.5", platform_fee: "0.05", payment_fee: "0.12",
    shipping_per_kg: "40", campaign_fee: "0",
    default_return_rate: "0.02", default_damage_rate: "0.01",
    low_stock_days: "7",
  });
  const [settingsSaved, setSettingsSaved] = useState(false);
  const [settingsTab, setSettingsTab] = useState<"platform" | "sourcing" | "ops">("platform");

  const [bundleSuggestions, setBundleSuggestions] = useState<BundleSuggestion[]>([]);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);

  // Drawer
  const [drawerProduct, setDrawerProduct] = useState<Product | null>(null);
  const [drawerEdits, setDrawerEdits] = useState<Record<string, any>>({});
  const [drawerTab, setDrawerTab] = useState<DrawerTab>("decision");
  const [drawerPrices, setDrawerPrices] = useState<{
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
  } | null>(null);
  const calcDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Modals
  const [showAddInv, setShowAddInv] = useState(false);
  const [showAddProduct, setShowAddProduct] = useState(false);
  const [salesProduct, setSalesProduct] = useState<Product | null>(null);
  const [salesForm, setSalesForm] = useState({ current_price: "", sales_7d: "", ad_spend_7d: "", current_stock: "" });
  const [salesResult, setSalesResult] = useState<{ revenue_7d: number; gross_profit: number; gross_margin: string; next_action: string } | null>(null);
  const [invForm, setInvForm] = useState({ ...emptyInv });
  const [productForm, setProductForm] = useState({ ...emptyProduct });
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [statusCounts, setStatusCounts] = useState<{ code: string; label: string; count: number }[]>([]);
  const [groupByFamily, setGroupByFamily] = useState(false);
  const [families, setFamilies] = useState<ProductFamily[]>([]);
  const [expandedFamilies, setExpandedFamilies] = useState<Set<string>>(new Set());

  // ── 即時成本計算（前端 JS，2026 蝦皮費率）──
  type CostPreview = {
    cost_twd: number; freight: number; shipping: number; packaging: number; fss: number;
    commission: number; transaction: number; ccb: number; promo: number; penalty: number; risk: number;
    total_cost: number; profit: number; gross_margin: number;
    // 三段建議售價
    price_traffic: number; price_core: number; price_profit: number;
    safe_cpa: number;
    // 角色判斷（4 段）
    viability: "not_suitable" | "traffic" | "core" | "profit";
    suggested_role: string;
    // 市場天花板警示（有填市場高價時）
    market_warning: string;
    // 天花板反推（有填市場高價時）
    ceiling_traffic?: number; ceiling_core?: number; ceiling_profit?: number;
    max_rmb_traffic?: number; max_rmb_core?: number; max_rmb_profit?: number;
  } | null;
  const [costPreview, setCostPreview] = useState<CostPreview>(null);
  const [showCostDetail, setShowCostDetail] = useState(false);
  const [showShopeeOptions, setShowShopeeOptions] = useState(false);

  function calcPreview(overrides: Partial<typeof productForm> = {}) {
    const form = { ...productForm, ...overrides };
    const cr = parseFloat(form.cost_rmb);
    const sp = parseFloat(form.target_price) || 0;
    if (!cr) { setCostPreview(null); return; }

    if (calcDebounceRef.current) clearTimeout(calcDebounceRef.current);
    calcDebounceRef.current = setTimeout(async () => {
      try {
        const body: Record<string, unknown> = {
          cost_rmb:         cr,
          selling_price:    sp || cr * 3,  // 若無售價用 3 倍成本估算
          weight_kg:        parseFloat(form.weight_kg) || 0,
          packaging_cost:   parseFloat(form.packaging_cost) || 0,
          head_freight_rmb: parseFloat(form.head_freight_rmb) || 0,
          ccb_plan:         form.ccb_plan || "none",
          is_promo_day:     form.is_promo_day,
          fulfillment_days: parseInt(form.fulfillment_days) || 1,
          procurement_mode: form.procurement_mode || "standard_1688",
          freight_type:     form.freight_type || "sea_fast",
          is_special_goods: form.is_special_goods,
        };
        if (form.procurement_mode === "qql_agent") {
          body.length_cm = parseFloat((form as any).length_cm) || null;
          body.width_cm  = parseFloat((form as any).width_cm)  || null;
          body.height_cm = parseFloat((form as any).height_cm) || null;
        }
        if (form.return_rate !== "")  body.return_rate  = parseFloat(form.return_rate)  / 100;
        if (form.damage_rate !== "")  body.damage_rate  = parseFloat(form.damage_rate)  / 100;
        if (form.coupon_rate !== "")  body.coupon_rate  = parseFloat(form.coupon_rate)  / 100;
        const mh = parseFloat(form.market_price_high) || 0;
        if (mh > 0) body.market_price_high = mh;

        const res = await fetch("/api/ecommerce/calc-cost", {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        if (!res.ok) return;
        const d = await res.json();

        const bd = d.breakdown || {};
        setCostPreview({
          cost_twd:      bd.cost_twd           ?? 0,
          freight:       bd.cross_border_freight ?? 0,
          shipping:      bd.shipping_cost       ?? 0,
          packaging:     bd.packaging_cost      ?? 0,
          fss:           bd.fss_cost            ?? 0,
          commission:    bd.commission_cost     ?? 0,
          transaction:   bd.transaction_cost    ?? 0,
          ccb:           bd.ccb_cost            ?? 0,
          promo:         bd.promo_cost          ?? 0,
          penalty:       bd.penalty_cost        ?? 0,
          risk:          bd.risk_cost           ?? 0,
          total_cost:    d.total_cost           ?? 0,
          profit:        sp ? d.profit          ?? 0 : 0,
          gross_margin:  sp ? d.gross_margin    ?? 0 : 0,
          price_traffic: d.price_traffic,
          price_core:    d.price_core,
          price_profit:  d.price_profit,
          safe_cpa:      d.safe_cpa             ?? 0,
          viability:     sp ? d.viability        : "not_suitable",
          suggested_role: sp ? d.suggested_role  : "不建議",
          market_warning: d.market_warning ?? "",
          ceiling_traffic: d.ceiling_traffic,
          ceiling_core:    d.ceiling_core,
          ceiling_profit:  d.ceiling_profit,
          max_rmb_traffic: d.max_rmb_traffic,
          max_rmb_core:    d.max_rmb_core,
          max_rmb_profit:  d.max_rmb_profit,
        });
      } catch { /* network error → keep showing last preview */ }
    }, 300);
  }

  async function fetchDrawerPrices(p: Product, edits: Record<string, any> = {}) {
    const merged = { ...p, ...edits };
    if (!merged.cost_rmb) { setDrawerPrices(null); return; }
    try {
      const body: Record<string, unknown> = {
        cost_rmb:         merged.cost_rmb || 0,
        selling_price:    merged.target_price || (merged.cost_rmb || 0) * 3,
        weight_kg:        merged.weight_kg || 0,
        packaging_cost:   merged.packaging_cost || 0,
        head_freight_rmb: merged.head_freight_rmb || 0,
        ccb_plan:         merged.ccb_plan || "none",
        is_promo_day:     merged.is_promo_day || false,
        fulfillment_days: merged.fulfillment_days || 1,
        procurement_mode: merged.procurement_mode || "standard_1688",
        freight_type:     merged.freight_type || "sea_fast",
        is_special_goods: merged.is_special_goods || false,
        length_cm:        merged.length_cm ?? null,
        width_cm:         merged.width_cm  ?? null,
        height_cm:        merged.height_cm ?? null,
        return_rate:      merged.return_rate ?? null,
        damage_rate:      merged.damage_rate ?? null,
        coupon_rate:      merged.coupon_rate ?? 0,
        market_price_high: merged.market_price_high ?? null,
      };
      const res = await fetch("/api/ecommerce/calc-cost", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) return;
      const d = await res.json();
      setDrawerPrices({
        traffic: d.price_traffic,
        core: d.price_core,
        profit: d.price_profit,
        landed_cost: d.landed_cost,
        fee_rate: d.platform_fee_rate,
        market_warning: d.market_warning ?? "",
        ceiling_traffic: d.ceiling_traffic,
        ceiling_core: d.ceiling_core,
        ceiling_profit: d.ceiling_profit,
        max_rmb_traffic: d.max_rmb_traffic,
        max_rmb_core: d.max_rmb_core,
        max_rmb_profit: d.max_rmb_profit,
        breakdown: d.breakdown,
      });
    } catch { /* keep existing prices */ }
  }

  function openDrawer(p: Product) {
    setDrawerProduct(p);
    setDrawerEdits({});
    setDrawerTab("decision");
    setDrawerPrices(null);
    fetchDrawerPrices(p);
  }

  async function saveDrawerEdits() {
    if (!drawerProduct) return;
    const body: Record<string, any> = {};
    for (const [k, v] of Object.entries(drawerEdits)) {
      if (v === "" || v === null || v === undefined) continue;
      if (["cost_rmb", "head_freight_rmb", "target_price", "market_price_low", "market_price_high", "weight_kg", "packaging_cost", "length_cm", "width_cm", "height_cm"].includes(k)) {
        body[k] = parseFloat(v);
      } else if (k === "is_special_goods" || k === "is_promo_day") {
        body[k] = Boolean(v);
      } else if (k === "fulfillment_days") {
        body[k] = parseInt(v);
      } else {
        body[k] = v;
      }
    }
    if (Object.keys(body).length === 0) { setDrawerProduct(null); return; }
    await fetch(`/api/ecommerce/products/${drawerProduct.sku}`, {
      method: "PUT", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    setDrawerProduct(null); setDrawerEdits({}); reload();
  }

  const reload = () => {
    fetch("/api/ecommerce/dashboard").then(r => r.json()).then(setDash).catch(() => {});
    fetch("/api/ecommerce/products").then(r => r.json())
      .then(d => { setProducts(Array.isArray(d) ? d : []); setLoading(false); })
      .catch(() => { setLoading(false); });
    fetch("/api/ecommerce/products/statuses").then(r => r.json())
      .then(d => setStatusCounts(d.statuses || [])).catch(() => {});
  };

  const loadFamilies = () => {
    fetch("/api/ecommerce/products/families").then(r => r.json()).then(setFamilies).catch(() => {});
  };

  const loadPerformance = () => {
    Promise.all([
      fetch("/api/ecommerce/products").then(r => r.json()),
      fetch("/api/ecommerce/performance/latest").then(r => r.json()),
    ]).then(([prods, perfs]) => {
      const nameMap: Record<string, string> = {};
      const prodsArr = Array.isArray(prods) ? prods : [];
      const perfsArr = Array.isArray(perfs) ? perfs : [];
      prodsArr.forEach((p: Product) => { nameMap[p.sku] = p.name; });
      setPerformances(perfsArr.map((p: Performance) => ({ ...p, name: nameMap[p.sku] || p.sku })));
    }).catch(() => {});
  };

  const loadSettings = () => {
    fetch("/api/ecommerce/settings").then(r => r.json()).then((data) => {
      if (!Array.isArray(data)) return;
      setSettings(data);
      const init: Record<string, string> = {};
      (data as Setting[]).forEach(s => { init[s.key] = String(s.value); });
      setSettingsEdit(init);
    }).catch(() => {});
  };

  const loadBundles = () => {
    fetch("/api/ecommerce/selection/bundles/suggest", { method: "POST" }).then(r => r.json())
      .then(d => setBundleSuggestions(Array.isArray(d?.suggestions) ? d.suggestions : [])).catch(() => {});
    fetch("/api/ecommerce/selection/portfolio").then(r => r.json()).then(setPortfolio).catch(() => {});
  };
  // ── Mini ecommerce review panel ──
  type MiniReviewItem = { id: number; question: string; context?: string; status: string; created_at: string };
  const [pendingReviews, setPendingReviews] = useState<MiniReviewItem[]>([]);
  const [reviewDeciding, setReviewDeciding] = useState<number | null>(null);

  const ECOMMERCE_ACTIONS = new Set(["promote_product", "approve_purchase"]);

  async function loadPendingReviews() {
    try {
      const data = await fetchReviewQueue("pending");
      const items: MiniReviewItem[] = (data.items ?? []).filter((item: MiniReviewItem & { context?: string }) => {
        try { const ctx = JSON.parse(item.context ?? "{}"); return ECOMMERCE_ACTIONS.has(ctx.action); }
        catch { return false; }
      });
      setPendingReviews(items);
    } catch { /* silent */ }
  }

  async function handleMiniDecide(id: number, action: "approved" | "rejected") {
    setReviewDeciding(id);
    try { await decideReviewItem(id, action); await loadPendingReviews(); }
    catch { /* silent */ }
    finally { setReviewDeciding(null); }
  }

  useEffect(() => { reload(); loadSettings(); loadPendingReviews(); }, []);

  // Re-fetch drawer prices when edits change pricing-relevant fields
  useEffect(() => {
    if (!drawerProduct) return;
    const pricingKeys = ["cost_rmb","head_freight_rmb","weight_kg","packaging_cost",
      "freight_type","is_special_goods","procurement_mode","length_cm","width_cm","height_cm",
      "ccb_plan","is_promo_day","fulfillment_days","target_price","return_rate","damage_rate","market_price_high"];
    const hasPricingEdit = Object.keys(drawerEdits).some(k => pricingKeys.includes(k));
    if (hasPricingEdit) fetchDrawerPrices(drawerProduct, drawerEdits);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [drawerEdits]);

  async function submitInventory() {
    if (!invForm.sku || !invForm.cost_rmb || !invForm.quantity) return;
    await fetch("/api/ecommerce/inventory", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sku: invForm.sku, cost_rmb: parseFloat(invForm.cost_rmb), quantity: parseInt(invForm.quantity), purchase_date: invForm.purchase_date || null, supplier: invForm.supplier || null, lead_days: invForm.lead_days ? parseInt(invForm.lead_days) : null, exchange_rate: (settings.find(s => s.key === "exchange_rate")?.value as number) ?? 4.5 }),
    });
    setShowAddInv(false); setInvForm({ ...emptyInv }); reload();
  }

  async function submitProduct() {
    if (!productForm.name || !productForm.cost_rmb) return;
    const sku = productForm.sku || `SKU-${Date.now()}`;
    await fetch("/api/ecommerce/products", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sku, name: productForm.name, role: productForm.role,
        product_type: productForm.product_type || null, scene: productForm.scene || null,
        keyword: productForm.keyword || null,
        market_price_low: productForm.market_price_low ? parseFloat(productForm.market_price_low) : null,
        market_price_high: productForm.market_price_high ? parseFloat(productForm.market_price_high) : null,
        supplier: productForm.supplier || null,
        cost_rmb: productForm.cost_rmb ? parseFloat(productForm.cost_rmb) : null,
        head_freight_rmb: productForm.head_freight_rmb ? parseFloat(productForm.head_freight_rmb) : 0,
        target_price: productForm.target_price ? parseFloat(productForm.target_price) : null,
        notes: productForm.notes || null,
        weight_kg: productForm.weight_kg ? parseFloat(productForm.weight_kg) : 0,
        packaging_cost: productForm.packaging_cost ? parseFloat(productForm.packaging_cost) : 0,
        return_rate: productForm.return_rate ? parseFloat(productForm.return_rate) / 100 : null,
        damage_rate: productForm.damage_rate ? parseFloat(productForm.damage_rate) / 100 : null,
        coupon_rate: productForm.coupon_rate ? parseFloat(productForm.coupon_rate) / 100 : 0,
        freight_type: productForm.freight_type || "sea_fast",
        is_special_goods: productForm.is_special_goods || false,
        procurement_mode: productForm.procurement_mode || "standard_1688",
        length_cm: productForm.length_cm ? parseFloat(productForm.length_cm) : null,
        width_cm:  productForm.width_cm  ? parseFloat(productForm.width_cm)  : null,
        height_cm: productForm.height_cm ? parseFloat(productForm.height_cm) : null,
        ccb_plan: productForm.ccb_plan || "none",
        is_promo_day: productForm.is_promo_day || false,
        fulfillment_days: productForm.fulfillment_days ? parseInt(productForm.fulfillment_days) : 1,
        family_name: (productForm as any).family_name || null,
        variant_name: (productForm as any).variant_name || null,
      }),
    });
    // 有填初始庫存則立即設定
    if (productForm.init_stock && parseInt(productForm.init_stock) > 0) {
      await fetch(`/api/ecommerce/products/${sku}/stock`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quantity: parseInt(productForm.init_stock) }),
      });
    }
    setShowAddProduct(false); setProductForm({ ...emptyProduct }); reload();
  }

  async function deleteProduct(sku: string) {
    if (!confirm(`確定要刪除 ${sku}？此操作不可復原。`)) return;
    await fetch(`/api/ecommerce/products/${sku}`, { method: "DELETE" });
    reload();
  }

  async function submitSales() {
    if (!salesProduct || !salesForm.current_price || !salesForm.sales_7d) return;
    const res = await fetch("/api/ecommerce/performance", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sku: salesProduct.sku,
        current_price: parseFloat(salesForm.current_price),
        sales_7d: parseInt(salesForm.sales_7d),
        ad_spend_7d: salesForm.ad_spend_7d ? parseFloat(salesForm.ad_spend_7d) : 0,
        current_stock: salesForm.current_stock ? parseInt(salesForm.current_stock) : 0,
      }),
    });
    const data = await res.json();
    setSalesResult(data);
    reload();
  }

  async function saveSettings() {
    const values: Record<string, number> = {};
    Object.entries(settingsEdit).forEach(([k, v]) => { values[k] = parseFloat(v); });
    await fetch("/api/ecommerce/settings", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ values }),
    });
    setSettingsSaved(true);
    setTimeout(() => setSettingsSaved(false), 2000);
    loadSettings();
  }

  // ── Tabs config ──
  // group: "primary" = daily work | "secondary" = low-freq tools | "archive" = selection research tools
  const tabs = [
    { id: "dashboard",   label: "營運總覽",    icon: BarChart3,    group: "primary" },
    { id: "products",    label: "在售商品",    icon: Package,      group: "primary" },
    { id: "performance", label: "週績效表",    icon: TrendingUp,   group: "primary" },
    { id: "bundles",     label: "組合設計",    icon: Layers,       group: "primary" },
    { id: "settings",    label: "系統設定",    icon: Settings,     group: "secondary" },
    { id: "manual",      label: "說明書",      icon: BookOpen,     group: "secondary" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-700 tracking-tight flex items-center gap-2" style={{ color: "var(--text-1)" }}>
            <ShoppingBag size={22} style={{ color: SH.primary }} />
            Flow Lab 電商
          </h1>
          <p className="text-[13px] text-[var(--text-3)] mt-1">蝦皮選品管理 · 採購 · 定價決策</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowAddProduct(true)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-[10px] text-[13px] font-600 border transition-all hover:opacity-90"
            style={{ background: "var(--surface)", borderColor: SH.border, color: SH.primary }}>
            <Plus size={14} /> 新增商品
          </button>
          <button onClick={() => setShowAddInv(true)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-[10px] text-[13px] font-600 text-white transition-all hover:opacity-90"
            style={{ background: SH.primary }}>
            <Package size={14} /> 補貨入庫
          </button>
        </div>
      </div>

      {/* 電商待審核 mini panel */}
      {pendingReviews.length > 0 && (
        <div className="rounded-[14px] border border-amber-200 bg-amber-50 p-4 space-y-3">
          <div className="flex items-center gap-2 text-[13px] font-600 text-amber-800">
            <ClipboardCheck size={15} />
            待電商審核 <span className="ml-auto text-[12px] font-500 text-amber-600">{pendingReviews.length} 件</span>
          </div>
          <div className="space-y-2">
            {pendingReviews.map(item => {
              let actionLabel = "操作";
              try { const ctx = JSON.parse(item.context ?? "{}"); actionLabel = ctx.action === "promote_product" ? "推廣商品" : "採購決策"; } catch {}
              return (
                <div key={item.id} className="flex items-start gap-3 bg-white rounded-[10px] border border-amber-100 px-3 py-2.5">
                  <div className="flex-1 min-w-0">
                    <div className="text-[12px] text-amber-700 font-500 mb-0.5">{actionLabel}</div>
                    <div className="text-[13px] text-[var(--text-1)] leading-snug line-clamp-2">{item.question}</div>
                  </div>
                  <div className="flex gap-1.5 shrink-0">
                    <button
                      disabled={reviewDeciding === item.id}
                      onClick={() => void handleMiniDecide(item.id, "approved")}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-[8px] text-[12px] font-500 bg-emerald-100 text-emerald-700 hover:bg-emerald-200 disabled:opacity-50">
                      <Check size={12} /> 核准
                    </button>
                    <button
                      disabled={reviewDeciding === item.id}
                      onClick={() => void handleMiniDecide(item.id, "rejected")}
                      className="flex items-center gap-1 px-2.5 py-1.5 rounded-[8px] text-[12px] font-500 bg-red-100 text-red-600 hover:bg-red-200 disabled:opacity-50">
                      <X size={12} /> 拒絕
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tabs — 三層：主要工作 / 低頻工具 / 選品引擎 */}
      <div className="space-y-1.5">
        {/* Primary: daily work tabs */}
        <div className="flex gap-1 p-1 rounded-[12px] w-fit" style={{ background: "var(--bg-2)" }}>
          {tabs.filter(t => t.group === "primary").map(({ id, label, icon: Icon }) => {
            const active = tab === id;
            return (
              <button key={id} onClick={() => {
                setTab(id as typeof tab);
                if (id === "performance") loadPerformance();
                if (id === "bundles") loadBundles();
              }}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-[10px] text-[13px] font-medium transition-all"
                style={active ? { background: "white", boxShadow: "0 1px 3px rgba(0,0,0,0.08)", color: SH.primary } : { color: "var(--text-3)" }}>
                <Icon size={13} /> {label}
              </button>
            );
          })}
          {/* Secondary: low-frequency tools — visually separated, smaller */}
          <div className="w-px mx-1 self-stretch" style={{ background: "var(--border)" }} />
          {tabs.filter(t => t.group === "secondary").map(({ id, label, icon: Icon }) => {
            const active = tab === id;
            return (
              <button key={id} onClick={() => {
                setTab(id as typeof tab);
                if (id === "settings") loadSettings();
              }}
                className="flex items-center gap-1 px-2.5 py-1.5 rounded-[8px] text-[12px] transition-all"
                style={active ? { background: "white", boxShadow: "0 1px 2px rgba(0,0,0,0.06)", color: SH.primary } : { color: "var(--text-4)" }}>
                <Icon size={12} /> {label}
              </button>
            );
          })}
        </div>
      </div>

      {/* ── Dashboard ── */}
      {tab === "dashboard" && dash && <DashboardTab dash={dash} />}

      {/* ── Products ── */}
      {tab === "products" && (
        <div className="space-y-3">
          {/* 工具列 */}
          <div className="flex justify-end gap-2 px-1">
            <button onClick={() => { setGroupByFamily(g => !g); if (!groupByFamily) loadFamilies(); }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-[10px] text-[12px] font-medium border"
              style={{ background: groupByFamily ? SH.primary : "var(--surface)", borderColor: groupByFamily ? SH.primary : "var(--border)", color: groupByFamily ? "white" : "var(--text-2)" }}>
              <Layers size={12} /> {groupByFamily ? "家族分組" : "平鋪顯示"}
            </button>
            <button onClick={async () => {
              if (!confirm("自動檢查所有商品，標記低毛利 / 零銷售商品？")) return;
              const r = await fetch("/api/ecommerce/auto-flag", { method: "POST" });
              const d = await r.json();
              alert(d.count > 0 ? `已標記 ${d.count} 項商品：\n${d.flagged.map((f: any) => `• ${f.name}：${f.action}`).join("\n")}` : "目前所有商品狀況正常");
              reload();
            }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-[10px] text-[12px] font-medium border"
              style={{ background: "var(--surface)", borderColor: "var(--border)", color: "var(--text-2)" }}>
              <Zap size={12} /> 自動標記滯銷
            </button>
          </div>
          {/* 狀態篩選器 */}
          <div className="flex flex-wrap gap-2 px-1">
            {[{ code: "all", label: `全部`, count: products.length }, ...statusCounts.filter(s => s.count > 0)].map(s => {
              const active = statusFilter === s.code;
              return (
                <button key={s.code} onClick={() => setStatusFilter(s.code)}
                  className="px-3 py-1 rounded-full text-[12px] font-600 transition-all"
                  style={{ background: active ? SH.primary : "var(--bg-2)", color: active ? "white" : "var(--text-2)", border: `1px solid ${active ? SH.primary : "var(--border)"}` }}>
                  {s.label} ({s.count})
                </button>
              );
            })}
          </div>
          {/* Zone B: 決策摘要 */}
          {!loading && (() => {
            const lowStock = products.filter(p => (p.total_stock ?? 0) <= 5).length;
            const weakMargin = products.filter(p => p.gross_margin_est != null && p.gross_margin_est < 0.25).length;
            const noTargetPrice = products.filter(p => !p.target_price).length;
            const readyToScale = products.filter(p => p.gross_margin_est != null && p.gross_margin_est >= 0.40).length;
            const summaryCards = [
              { label: "需要訂價", value: noTargetPrice, icon: "💰", color: SH.primary, bg: SH.light, tip: "尚未設定目標售價" },
              { label: "庫存偏低", value: lowStock, icon: "📦", color: "#d97706", bg: "#fffbeb", tip: "庫存 ≤ 5 件" },
              { label: "毛利偏弱", value: weakMargin, icon: "⚠️", color: "#dc2626", bg: "#fef2f2", tip: "毛利率 < 25%" },
              { label: "可放大", value: readyToScale, icon: "🚀", color: "#16a34a", bg: "#f0fdf4", tip: "毛利率 ≥ 40%" },
            ];
            return (
              <div className="grid grid-cols-4 gap-3 px-1">
                {summaryCards.map(c => (
                  <div key={c.label} className="rounded-[12px] px-4 py-3 flex items-center gap-3" style={{ background: c.bg, border: `1px solid ${c.color}22` }}>
                    <span className="text-[20px]">{c.icon}</span>
                    <div>
                      <div className="text-[22px] font-700 leading-none" style={{ color: c.color }}>{c.value}</div>
                      <div className="text-[11px] font-500 mt-0.5" style={{ color: c.color }}>{c.label}</div>
                      <div className="text-[10px] text-[var(--text-3)] mt-0.5">{c.tip}</div>
                    </div>
                  </div>
                ))}
              </div>
            );
          })()}
        {groupByFamily ? (
          <div className="rounded-[14px] overflow-hidden" style={{ background: "var(--surface)" }}>
            {families.length === 0 ? (
              <div className="p-8 text-center text-[var(--text-3)]">尚無家族分組資料，請在商品詳細頁設定家族名稱</div>
            ) : families.map(fam => {
              const isExpanded = expandedFamilies.has(fam.family_id ?? "__ungrouped__");
              const toggle = () => setExpandedFamilies(prev => {
                const next = new Set(prev);
                const key = fam.family_id ?? "__ungrouped__";
                if (next.has(key)) next.delete(key); else next.add(key);
                return next;
              });
              const marginColor = fam.best_margin == null ? "var(--text-3)" : fam.best_margin >= 0.40 ? "#16a34a" : fam.best_margin >= 0.25 ? "#d97706" : "#dc2626";
              return (
                <div key={fam.family_id ?? "__ungrouped__"} className="border-b border-[var(--border)] last:border-b-0">
                  {/* Family header row */}
                  <div onClick={fam.family_id ? toggle : undefined}
                    className={`flex items-center gap-3 px-4 py-3 ${fam.family_id ? "cursor-pointer hover:bg-[var(--bg-2)]" : ""} transition-colors`}
                    style={{ background: "var(--bg-2)" }}>
                    {fam.family_id && (
                      <span className="text-[11px] transition-transform" style={{ display: "inline-block", transform: isExpanded ? "rotate(90deg)" : "rotate(0deg)" }}>▶</span>
                    )}
                    <span className="font-700 text-[13px] text-[var(--text-1)] flex-1">{fam.family_name}</span>
                    <span className="text-[11px] px-2 py-0.5 rounded-full bg-[var(--surface)] text-[var(--text-3)] border border-[var(--border)]">{fam.variant_count} 款</span>
                    <span className="text-[11px] px-2 py-0.5 rounded-full bg-[var(--surface)] text-[var(--text-3)] border border-[var(--border)]">{fam.total_stock} 件庫存</span>
                    {fam.best_margin != null && (
                      <span className="text-[11px] px-2 py-0.5 rounded-full font-700" style={{ color: marginColor, background: marginColor + "18" }}>
                        最高 {(fam.best_margin * 100).toFixed(0)}% 毛利
                      </span>
                    )}
                  </div>
                  {/* Variant rows */}
                  {(isExpanded || !fam.family_id) && fam.products.map(p => (
                    <div key={p.sku} onClick={() => openDrawer(p)}
                      className="flex items-center gap-3 px-4 py-2.5 border-t border-[var(--border)] hover:bg-[var(--surface)] cursor-pointer transition-colors"
                      style={{ paddingLeft: fam.family_id ? "2.5rem" : "1rem" }}>
                      <span className="font-mono text-[11px] text-[var(--text-3)] w-20 shrink-0">{p.sku}</span>
                      <span className="text-[12px] text-[var(--text-1)] flex-1">{p.variant_name || p.name}</span>
                      <span className={`text-[11px] px-2 py-0.5 rounded-full ${PRODUCT_STATUS_COLOR[p.status] || "bg-gray-50 text-gray-500"}`}>
                        {PRODUCT_STATUS_LABELS[p.status] || p.status}
                      </span>
                      {p.role && (
                        <span className={`text-[11px] px-2 py-0.5 rounded-full ${ROLE_COLOR[p.role] || "bg-gray-50 text-gray-500"}`}>{p.role}</span>
                      )}
                      {p.target_price && (
                        <span className="text-[12px] font-600 text-[var(--text-2)]">NT$ {p.target_price}</span>
                      )}
                      {p.gross_margin_est != null && (() => {
                        const m = p.gross_margin_est;
                        const mc = m >= 0.40 ? "#16a34a" : m >= 0.25 ? "#d97706" : "#dc2626";
                        return <span className="text-[12px] font-700" style={{ color: mc }}>{(m * 100).toFixed(0)}%</span>;
                      })()}
                      <span className={`text-[12px] font-700 ${(p.total_stock ?? 0) === 0 ? "text-red-500" : (p.total_stock ?? 0) <= 5 ? "text-amber-500" : "text-[var(--text-1)]"}`}>
                        {p.total_stock ?? 0} 件
                      </span>
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        ) : (
        <div className="rounded-[14px] overflow-hidden" style={{ background: "var(--surface)" }}>
          {loading ? <div className="p-8 text-center text-[var(--text-3)]">載入中...</div> : (
            <table className="w-full text-[13px]">
              <thead>
                <tr className="border-b border-[var(--border)]">
                  {["商品", "狀態", "角色", "落地成本 → 目標售價", "毛利", "庫存", "下一步", ""].map(h => (
                    <th key={h} className="text-left px-4 py-3 text-[11px] font-600 text-[var(--text-3)] uppercase tracking-wide">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {products.filter(p => statusFilter === "all" || p.status === statusFilter || (statusFilter === "listed" && p.status === "active")).map(p => {
                  const margin = p.gross_margin_est;
                  const marginColor = margin == null ? "var(--text-3)" : margin >= 0.40 ? "#16a34a" : margin >= 0.25 ? "#d97706" : "#dc2626";
                  const marginBg   = margin == null ? "transparent" : margin >= 0.40 ? "#f0fdf4" : margin >= 0.25 ? "#fffbeb" : "#fef2f2";
                  const stock = p.total_stock ?? 0;
                  const exr = (settings.find(s => s.key === "exchange_rate")?.value as number) ?? 4.5;
                  const landedTwd = p.cost_rmb != null ? Math.round((p.cost_rmb + (p.head_freight_rmb || 0)) * exr) : null;
                  return (
                  <tr key={p.sku} onClick={() => openDrawer(p)} className="border-b border-[var(--border)] hover:bg-[var(--bg-2)] transition-colors group cursor-pointer">
                    {/* 商品（name + SKU） */}
                    <td className="px-4 py-3">
                      <div className="font-600 text-[13px] text-[var(--text-1)] leading-tight">{p.name}</div>
                      <div className="font-mono text-[11px] text-[var(--text-3)] mt-0.5">{p.sku}</div>
                    </td>
                    {/* 狀態 */}
                    <td className="px-4 py-3">
                      <span className={`text-[11px] px-2 py-0.5 rounded-full ${PRODUCT_STATUS_COLOR[p.status] || "bg-gray-50 text-gray-500"}`}>
                        {PRODUCT_STATUS_LABELS[p.status] || p.status}
                      </span>
                    </td>
                    {/* 角色 */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1">
                        <span className={`text-[11px] px-2 py-0.5 rounded-full ${ROLE_COLOR[p.role] || "bg-gray-50 text-gray-500"}`}>
                          {p.role || "未分類"}
                        </span>
                        {p.role && !p.role_confirmed && (
                          <button
                            onClick={e => { e.stopPropagation(); fetch(`/api/ecommerce/products/${p.sku}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ role_confirmed: true }) }).then(() => reload()); }}
                            className="text-[10px] px-1.5 py-0.5 rounded-full bg-amber-50 text-amber-600 border border-amber-200 hover:bg-amber-100 transition-colors"
                            title="AI 建議，點擊確認">✓</button>
                        )}
                      </div>
                    </td>
                    {/* 落地成本 → 目標售價 */}
                    <td className="px-4 py-3 text-[12px]">
                      {landedTwd != null ? (
                        <div>
                          <span className="text-[var(--text-3)]">NT$ {landedTwd}</span>
                          {p.target_price && (
                            <span className="text-[var(--text-2)] font-600"> → {p.target_price}</span>
                          )}
                        </div>
                      ) : <span className="text-[var(--text-3)]">—</span>}
                    </td>
                    {/* 毛利（彩色 badge） */}
                    <td className="px-4 py-3">
                      {margin != null ? (
                        <span className="text-[12px] font-700 px-2 py-0.5 rounded-full" style={{ color: marginColor, background: marginBg }}>
                          {(margin * 100).toFixed(0)}%
                        </span>
                      ) : <span className="text-[11px] text-[var(--text-3)]">—</span>}
                    </td>
                    {/* 庫存 */}
                    <td className="px-4 py-3">
                      <span className={`text-[13px] font-700 ${stock === 0 ? "text-red-500" : stock <= 5 ? "text-amber-500" : "text-[var(--text-1)]"}`}>
                        {stock}
                        {stock === 0 && <span className="ml-1 text-[10px] font-500">缺貨</span>}
                        {stock > 0 && stock <= 5 && <span className="ml-1 text-[10px] font-500">低庫</span>}
                      </span>
                    </td>
                    {/* 下一步建議 */}
                    <td className="px-4 py-3">
                      {(() => {
                        if (stock === 0) return <span className="text-[11px] px-2 py-0.5 rounded-full font-600 bg-red-50 text-red-500">補貨</span>;
                        if (stock <= 5)  return <span className="text-[11px] px-2 py-0.5 rounded-full font-600 bg-amber-50 text-amber-600">留意庫存</span>;
                        if (margin == null) return <span className="text-[11px] text-[var(--text-3)]">—</span>;
                        if (margin >= 0.40) return <span className="text-[11px] px-2 py-0.5 rounded-full font-600 bg-emerald-50 text-emerald-600">可放大</span>;
                        if (margin >= 0.25) return <span className="text-[11px] px-2 py-0.5 rounded-full font-600 bg-blue-50 text-blue-600">持續觀察</span>;
                        if (!p.target_price)return <span className="text-[11px] px-2 py-0.5 rounded-full font-600" style={{ background: SH.light, color: SH.primary }}>設定售價</span>;
                        return <span className="text-[11px] px-2 py-0.5 rounded-full font-600 bg-red-50 text-red-500">調整定價</span>;
                      })()}
                    </td>
                    <td className="px-4 py-3" onClick={e => e.stopPropagation()}>
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onClick={() => { setSalesProduct(p); setSalesForm({ current_price: "", sales_7d: "", ad_spend_7d: "", current_stock: "" }); setSalesResult(null); }}
                          className="p-1.5 rounded-[6px] hover:bg-emerald-50 text-[var(--text-3)] hover:text-emerald-600" title="更新週銷售">
                          <RefreshCw size={13} />
                        </button>
                        <button onClick={() => deleteProduct(p.sku)}
                          className="p-1.5 rounded-[6px] hover:bg-red-50 text-[var(--text-3)] hover:text-red-500">
                          <Trash2 size={13} />
                        </button>
                      </div>
                    </td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
        )}
        </div>
      )}

      {/* ── Performance Table ── */}
      {tab === "performance" && <PerformanceTab performances={performances} loadPerformance={loadPerformance} />}

      {/* ── Settings ── */}
      {tab === "settings" && (
        <div className="max-w-[640px] space-y-4">

          {/* Tab 切換 */}
          <div className="flex gap-1 p-1 rounded-[12px]" style={{ background: SH.surface, border: `1px solid ${SH.border}` }}>
            {([
              { id: "platform", label: "平台費率",   desc: "蝦皮手續費、FSS、促銷罰則" },
              { id: "sourcing", label: "採購與物流", desc: "集運費率、匯率、QQL 設定" },
              { id: "ops",      label: "運營與風險", desc: "角色門檻、退損率、庫存警示" },
            ] as const).map(t => (
              <button key={t.id} onClick={() => setSettingsTab(t.id)}
                className="flex-1 py-2.5 px-3 rounded-[9px] text-center transition-all"
                style={settingsTab === t.id
                  ? { background: "white", boxShadow: "0 1px 4px rgba(0,0,0,0.08)" }
                  : { background: "transparent" }}>
                <div className="text-[13px] font-700" style={{ color: settingsTab === t.id ? SH.primary : "var(--text-2)" }}>{t.label}</div>
                <div className="text-[10px] mt-0.5" style={{ color: settingsTab === t.id ? SH.muted : "var(--text-3)" }}>{t.desc}</div>
              </button>
            ))}
          </div>

          {/* 群組渲染輔助 */}
          {(() => {
            const allGroups: Record<string, { title: string; keys: string[]; note: string }[]> = {
              platform: [
                {
                  title: "蝦皮費率 2026",
                  keys: ["commission_fee", "transaction_fee", "fss_pct", "fss_fixed", "fss_threshold", "promo_surcharge", "fulfillment_penalty"],
                  note: "FSS 售價 > NT$1000 自動切換固定制（NT$60），低於門檻用百分比制（6%）",
                },
              ],
              sourcing: [
                {
                  title: "匯率與末端物流",
                  keys: ["exchange_rate", "shipping_per_kg"],
                  note: "末端物流：蝦皮官方物流費，通常有補貼，實際可能接近 NT$0",
                },
                {
                  title: "集運費率（NT$/kg）",
                  keys: ["air_freight_per_kg", "sea_fast_per_kg", "sea_regular_per_kg", "special_goods_surcharge"],
                  note: "特貨（帶電/液體/磁性）在對應費率上再加 special_goods_surcharge",
                },
                {
                  title: "QQL 採購代理",
                  keys: ["qql_exchange_rate", "qql_service_fee", "sea_express_rate", "volumetric_divisor"],
                  note: "採購模式選「QQL 代購」時使用。服務費：代購手續費；海快費率：NT$/kg；體積除數：cm³/kg（標準 6000）",
                },
              ],
              ops: [
                {
                  title: "角色毛利門檻",
                  keys: ["traffic_margin_target", "core_margin_target", "profit_margin_target"],
                  note: "調整後影響 Quick Add 建議售價、Drawer 即時計算、以及角色分類判斷",
                },
                {
                  title: "風險預設值",
                  keys: ["default_return_rate", "default_damage_rate", "low_stock_days"],
                  note: "新增商品時未填退貨率/破損率，系統使用這裡的預設值估算",
                },
              ],
            };
            const groups = allGroups[settingsTab] ?? [];
            const settingMap = Object.fromEntries(settings.map(s => [s.key, s]));
            return (
              <div className="space-y-4">
                {groups.map(g => (
                  <div key={g.title} className="rounded-[14px] p-5 space-y-4" style={{ background: "var(--surface)" }}>
                    <div>
                      <div className="text-[14px] font-700 text-[var(--text-1)]">{g.title}</div>
                      <div className="text-[11px] text-[var(--text-3)] mt-0.5">{g.note}</div>
                    </div>
                    <div className="space-y-3">
                      {g.keys.map(key => {
                        const s = settingMap[key];
                        if (!s) return null;
                        return (
                          <div key={key} className="flex items-center gap-3">
                            <label className="text-[13px] font-500 text-[var(--text-1)] w-[180px] shrink-0">{s.label}</label>
                            <div className="flex items-center gap-2 flex-1">
                              <input
                                type="number"
                                step={s.unit === "%" ? "0.001" : s.unit === "天" ? "1" : "0.5"}
                                className={inputCls + " flex-1 py-2"}
                                value={settingsEdit[key] ?? ""}
                                onChange={e => setSettingsEdit(prev => ({ ...prev, [key]: e.target.value }))}
                              />
                              <span className="text-[12px] text-[var(--text-3)] w-[70px] shrink-0">
                                {s.unit === "%" ? `${((parseFloat(settingsEdit[key] || "0")) * 100).toFixed(1)}%` : s.unit}
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            );
          })()}

          <button onClick={saveSettings}
            className="flex items-center gap-2 px-6 py-3 rounded-[12px] text-[14px] font-700 text-white transition-all w-full justify-center"
            style={{ background: settingsSaved ? "#22c55e" : SH.primary }}>
            {settingsSaved ? <Check size={15} /> : <Save size={15} />}
            {settingsSaved ? "已儲存" : "儲存所有設定"}
          </button>
        </div>
      )}

      {/* ── Manual ── */}
      {tab === "manual" && <ManualTab />}

      {/* ── Modal: 更新週銷售 ── */}
      {salesProduct && (
        <SalesModal
          product={salesProduct}
          result={salesResult}
          form={salesForm}
          setForm={setSalesForm}
          onSubmit={submitSales}
          onClose={() => { setSalesProduct(null); setSalesResult(null); }}
        />
      )}

      {/* ── Modal: 補貨入庫 ── */}
      {showAddInv && (
        <InboundModal
          invForm={invForm}
          setInvForm={setInvForm}
          products={products}
          performances={performances}
          settings={settings}
          onSubmit={submitInventory}
          onClose={() => { setShowAddInv(false); setInvForm({ ...emptyInv }); }}
        />
      )}

      {/* ── Modal: 新增商品（Quick Add）── */}
      {showAddProduct && (
        <QuickAddModal
          productForm={productForm}
          setProductForm={setProductForm}
          costPreview={costPreview}
          settings={settings}
          onSubmit={submitProduct}
          onClose={() => { setShowAddProduct(false); setProductForm({ ...emptyProduct }); setCostPreview(null); }}
          onCalcPreview={calcPreview}
        />
      )}

      {/* ── 組合設計 ── */}
      {tab === "bundles" && (
        <BundlesTab bundleSuggestions={bundleSuggestions} portfolio={portfolio} loadBundles={loadBundles} products={products} />
      )}

      {/* ── Product Detail Drawer ── */}
      {drawerProduct && (
        <ProductDrawer
          product={drawerProduct}
          edits={drawerEdits}
          setEdits={setDrawerEdits}
          drawerTab={drawerTab}
          setDrawerTab={setDrawerTab}
          prices={drawerPrices}
          settings={settings}
          onClose={() => { setDrawerProduct(null); setDrawerEdits({}); }}
          onSave={saveDrawerEdits}
          onUpdateSales={() => {
            setSalesProduct(drawerProduct);
            setSalesForm({ current_price: "", sales_7d: "", ad_spend_7d: "", current_stock: "" });
            setSalesResult(null);
            setDrawerProduct(null);
            setDrawerEdits({});
          }}
          onRestock={() => {
            setShowAddInv(true);
            setInvForm({ ...emptyInv, sku: drawerProduct.sku });
            setDrawerProduct(null);
            setDrawerEdits({});
          }}
          onPricingDecision={() => {
            setDrawerProduct(null);
            setDrawerEdits({});
          }}
          onDelete={() => {
            deleteProduct(drawerProduct.sku);
            setDrawerProduct(null);
            setDrawerEdits({});
          }}
        />
      )}

    </div>
  );
}

