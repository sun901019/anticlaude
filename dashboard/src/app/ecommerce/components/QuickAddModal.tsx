"use client";
import { Setting, SH, shInputCls, emptyProduct, Field, Modal, ShToggleGroup } from "./ecommerce-shared";

type ProductForm = typeof emptyProduct;
type CostPreview = {
  cost_twd: number; freight: number; shipping: number;
  price_traffic: number; price_core: number; price_profit: number;
  ceiling_traffic?: number; ceiling_core?: number; ceiling_profit?: number;
  max_rmb_traffic?: number; max_rmb_core?: number; max_rmb_profit?: number;
} | null;

type Props = {
  productForm: ProductForm;
  setProductForm: React.Dispatch<React.SetStateAction<ProductForm>>;
  costPreview: CostPreview;
  settings: Setting[];
  onSubmit: () => void;
  onClose: () => void;
  onCalcPreview: (overrides?: Partial<ProductForm>) => void;
};

export function QuickAddModal({
  productForm, setProductForm, costPreview, settings, onSubmit, onClose, onCalcPreview,
}: Props) {
  const hasCost = !!productForm.cost_rmb && !!productForm.head_freight_rmb;

  return (
    <Modal title="新增商品" subtitle="填入基本資訊即可，細節之後在商品頁調整" onClose={onClose}>

      <Field label="商品名稱" required>
        <input className={shInputCls} placeholder="例：桌上型加濕器" value={productForm.name}
          style={{ borderColor: productForm.name ? SH.primary : "#e5e7eb" }}
          onChange={e => setProductForm(f => ({ ...f, name: e.target.value }))} />
      </Field>

      <Field label="SKU" hint="選填，留空系統自動生成">
        <input className={shInputCls} placeholder="例：FL-016" value={productForm.sku}
          style={{ borderColor: "#e5e7eb" }}
          onChange={e => setProductForm(f => ({ ...f, sku: e.target.value }))} />
      </Field>

      <Field label="採購模式">
        <ShToggleGroup
          value={productForm.procurement_mode}
          onChange={v => { setProductForm(f => ({ ...f, procurement_mode: v })); onCalcPreview({ procurement_mode: v }); }}
          options={[
            { value: "standard_1688", label: "1688 直購", sub: "自行集運報關" },
            { value: "qql_agent",     label: "QQL 代購",  sub: "代理採購+海快" },
          ]} />
      </Field>

      <div className="grid grid-cols-2 gap-3">
        <Field label={productForm.procurement_mode === "qql_agent" ? "商品單價（¥）" : "1688 商品價（¥）"} required>
          <input className={shInputCls} type="number" placeholder="¥" value={productForm.cost_rmb}
            style={{ borderColor: productForm.cost_rmb ? SH.primary : "#e5e7eb" }}
            onChange={e => { const v = e.target.value; setProductForm(f => ({ ...f, cost_rmb: v })); onCalcPreview({ cost_rmb: v }); }} />
        </Field>
        <Field label={productForm.procurement_mode === "qql_agent" ? "境內運費分攤（¥）" : "境內運費（¥）"} required hint="1688→集運倉">
          <input className={shInputCls} type="number" placeholder="¥ 例：5" value={productForm.head_freight_rmb}
            style={{ borderColor: productForm.head_freight_rmb ? SH.primary : "#e5e7eb" }}
            onChange={e => { const v = e.target.value; setProductForm(f => ({ ...f, head_freight_rmb: v })); onCalcPreview({ head_freight_rmb: v }); }} />
        </Field>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <Field label="重量（kg）" hint={productForm.procurement_mode === "qql_agent" ? "影響海快費率" : "影響集運費"}>
          <input className={shInputCls} type="number" step="0.1" placeholder="0.4" value={productForm.weight_kg}
            style={{ borderColor: "#e5e7eb" }}
            onChange={e => { const v = e.target.value; setProductForm(f => ({ ...f, weight_kg: v })); onCalcPreview({ weight_kg: v }); }} />
        </Field>
        {productForm.procurement_mode === "standard_1688" && (
          <Field label="貨物類型" hint="特貨+NT$15/kg">
            <ShToggleGroup
              value={productForm.is_special_goods ? "true" : "false"}
              onChange={v => { const b = v === "true"; setProductForm(f => ({ ...f, is_special_goods: b })); onCalcPreview({ is_special_goods: b }); }}
              options={[{ value: "false", label: "普貨" }, { value: "true", label: "特貨" }]} />
          </Field>
        )}
      </div>

      {productForm.procurement_mode === "qql_agent" && (() => {
        const lc = parseFloat((productForm as any).length_cm) || 0;
        const wc = parseFloat((productForm as any).width_cm)  || 0;
        const hc = parseFloat((productForm as any).height_cm) || 0;
        const wkg = parseFloat(productForm.weight_kg) || 0;
        const cfg2 = Object.fromEntries(settings.map(s => [s.key, s.value]));
        const vol_div = (cfg2["volumetric_divisor"] as number) ?? 6000;
        const vol_w = (lc && wc && hc) ? lc * wc * hc / vol_div : 0;
        const billable = vol_w > 0 ? Math.max(wkg, vol_w) : wkg;
        const volOverride = vol_w > wkg && vol_w > 0;
        return (
          <>
            <Field label="體積（選填）" hint="長 × 寬 × 高 cm，未填則以實重計費">
              <div className="grid grid-cols-3 gap-2">
                {(["length_cm", "width_cm", "height_cm"] as const).map((dim, i) => (
                  <input key={dim} className={shInputCls} type="number" step="0.1" placeholder={["長", "寬", "高"][i] + " cm"}
                    value={(productForm as any)[dim]}
                    style={{ borderColor: volOverride ? "#d97706" : "#e5e7eb" }}
                    onChange={e => { const v = e.target.value; setProductForm(f => ({ ...f, [dim]: v })); onCalcPreview({ [dim]: v }); }} />
                ))}
              </div>
            </Field>
            {vol_w > 0 && (
              <div className="rounded-[10px] px-3 py-2.5 text-[12px]"
                style={{ background: volOverride ? "#fffbeb" : SH.surface, border: `1px solid ${volOverride ? "#d97706" : SH.border}` }}>
                <div className="flex justify-between">
                  <span style={{ color: "var(--text-3)" }}>體積重</span>
                  <span className="font-600" style={{ color: volOverride ? "#d97706" : "var(--text-2)" }}>{vol_w.toFixed(2)} kg</span>
                </div>
                <div className="flex justify-between mt-0.5">
                  <span style={{ color: "var(--text-3)" }}>實際重</span>
                  <span className="font-600" style={{ color: "var(--text-2)" }}>{wkg || "—"} kg</span>
                </div>
                <div className="flex justify-between mt-0.5 pt-0.5" style={{ borderTop: `1px solid ${volOverride ? "#d9770640" : SH.border}` }}>
                  <span className="font-700" style={{ color: volOverride ? "#d97706" : SH.primary }}>計費重</span>
                  <span className="font-700" style={{ color: volOverride ? "#d97706" : SH.primary }}>{billable.toFixed(2)} kg</span>
                </div>
                {volOverride && (
                  <div className="mt-1.5 text-[11px] font-600" style={{ color: "#d97706" }}>
                    ⚠ 體積重 &gt; 實重，將以體積重計費，注意集運成本偏高
                  </div>
                )}
              </div>
            )}
          </>
        );
      })()}

      {productForm.procurement_mode === "standard_1688" && (
        <Field label="集運方式">
          <ShToggleGroup
            value={productForm.freight_type}
            onChange={v => { setProductForm(f => ({ ...f, freight_type: v })); onCalcPreview({ freight_type: v }); }}
            options={[
              { value: "sea_fast",    label: "海快",  sub: "5-8天 · NT$45/kg" },
              { value: "sea_regular", label: "海運",  sub: "12-15天 · NT$20/kg" },
              { value: "air",         label: "空運",  sub: "3-5天 · NT$115/kg" },
            ]} />
        </Field>
      )}

      {costPreview && (
        <div className="rounded-[14px] overflow-hidden" style={{ border: `1.5px solid ${SH.border}` }}>
          <div className="px-4 py-2.5 flex items-center justify-between" style={{ background: SH.light }}>
            <span className="text-[12px] font-700" style={{ color: SH.primary }}>
              進場成本 NT$ {Math.round(costPreview.cost_twd + costPreview.freight + costPreview.shipping)}
            </span>
            <span className="text-[10px]" style={{ color: SH.muted }}>含進貨 + 集運 + 末端配送</span>
          </div>
          <div className="grid grid-cols-3 divide-x" style={{ borderTop: `1px solid ${SH.border}` }}>
            {(() => {
              const cfg2 = Object.fromEntries(settings.map(s => [s.key, s.value]));
              const tPct = Math.round(((cfg2["traffic_margin_target"] as number) ?? 0.25) * 100);
              const cPct = Math.round(((cfg2["core_margin_target"]    as number) ?? 0.40) * 100);
              const pPct = Math.round(((cfg2["profit_margin_target"]  as number) ?? 0.55) * 100);
              return ([
                { label: "引流款", price: costPreview.price_traffic, desc: `${tPct}% 毛利`, color: "#92400e", bg: "#fffbeb" },
                { label: "毛利款", price: costPreview.price_core,    desc: `${cPct}% 毛利`, color: SH.hover,   bg: SH.light },
                { label: "主力款", price: costPreview.price_profit,  desc: `${pPct}% 毛利`, color: "#15803d",  bg: "#f0fdf4" },
              ] as const);
            })().map(({ label, price, desc, color, bg }) => (
              <div key={label} className="py-3 text-center" style={{ background: bg }}>
                <div className="text-[10px] font-600 mb-0.5" style={{ color }}>{label}</div>
                <div className="text-[16px] font-800" style={{ color }}>NT$ {price}</div>
                <div className="text-[10px] mt-0.5" style={{ color, opacity: 0.65 }}>{desc}</div>
              </div>
            ))}
          </div>
          <div className="px-4 py-2 text-[10px]" style={{ borderTop: `1px solid ${SH.border}`, color: SH.muted }}>
            建立後可在商品詳細頁調整目標售價、市場參考、CCB 等進階設定
          </div>
        </div>
      )}

      <Field label="市場高價（NT$）" hint="填入後顯示進場成本上限（天花板反推）">
        <input className={shInputCls} type="number" placeholder="市場最高售價，例：299"
          value={productForm.market_price_high}
          style={{ borderColor: "#e5e7eb" }}
          onChange={e => { const v = e.target.value; setProductForm(f => ({ ...f, market_price_high: v })); onCalcPreview({ market_price_high: v }); }} />
      </Field>

      {costPreview?.ceiling_traffic != null && (
        <div className="rounded-[12px] overflow-hidden" style={{ border: `1px solid ${SH.border}` }}>
          <div className="px-3 py-2 text-[10px] font-700 uppercase tracking-wider"
            style={{ background: SH.light, color: SH.primary }}>
            進場成本天花板 — 你的 1688 報價不能超過
          </div>
          <div className="grid grid-cols-3 divide-x text-center py-2.5">
            {([
              { label: "引流款", ceiling: costPreview.ceiling_traffic, rmb: costPreview.max_rmb_traffic, color: "#92400e", bg: "#fffbeb" },
              { label: "毛利款", ceiling: costPreview.ceiling_core,    rmb: costPreview.max_rmb_core,    color: SH.hover,  bg: SH.light },
              { label: "主力款", ceiling: costPreview.ceiling_profit,  rmb: costPreview.max_rmb_profit,  color: "#15803d", bg: "#f0fdf4" },
            ] as const).map(({ label, ceiling, rmb, color, bg }) => (
              <div key={label} className="py-1.5" style={{ background: bg }}>
                <div className="text-[9px] font-600 mb-0.5" style={{ color }}>{label}</div>
                <div className="text-[13px] font-800" style={{ color }}>NT$ {ceiling}</div>
                <div className="text-[9px] mt-0.5" style={{ color, opacity: 0.7 }}>≤ ¥{rmb}</div>
              </div>
            ))}
          </div>
          <div className="px-3 py-1.5 text-[9px]" style={{ borderTop: `1px solid ${SH.border}`, color: SH.muted }}>
            落地成本上限（進貨+集運+末端配送）· ¥ 為粗估 1688 最高報價
          </div>
        </div>
      )}

      <Field label="初始庫存（件）" hint="建立後可在商品頁調整備註、供應商等細節">
        <input className={shInputCls} type="number" min={0} placeholder="0" value={productForm.init_stock}
          style={{ borderColor: "#e5e7eb" }}
          onChange={e => setProductForm(f => ({ ...f, init_stock: e.target.value }))} />
      </Field>

      <details className="group">
        <summary className="flex items-center gap-1.5 cursor-pointer select-none list-none py-1 text-[12px] font-600"
          style={{ color: SH.muted }}>
          <span className="transition-transform group-open:rotate-90 text-[10px]">▶</span>
          系列分組（選填）
          <span className="text-[10px] font-400 ml-1" style={{ color: "var(--text-3)" }}>同系列商品填一樣的系列名稱</span>
        </summary>
        <div className="mt-2 space-y-2">
          <Field label="系列名稱" hint="同一商品概念下的共用名稱，例：躺贏招財貓">
            <input className={shInputCls} placeholder="例：躺贏招財貓"
              value={(productForm as any).family_name ?? ""}
              style={{ borderColor: "#e5e7eb" }}
              onChange={e => setProductForm(f => ({ ...f, family_name: e.target.value }))} />
          </Field>
          <Field label="款式名稱" hint="同系列下的具體款式，例：閒樂款 / 招財款">
            <input className={shInputCls} placeholder="例：閒樂款"
              value={(productForm as any).variant_name ?? ""}
              style={{ borderColor: "#e5e7eb" }}
              onChange={e => setProductForm(f => ({ ...f, variant_name: e.target.value }))} />
          </Field>
        </div>
      </details>

      <button
        onClick={onSubmit}
        disabled={!productForm.name || !productForm.cost_rmb || !productForm.head_freight_rmb}
        className="w-full py-3.5 rounded-[12px] text-[15px] font-700 text-white mt-2 transition-all disabled:opacity-40 disabled:cursor-not-allowed"
        style={{ background: hasCost ? SH.primary : "#ccc" }}>
        {hasCost ? "新增商品" : "請先填入成本資訊"}
      </button>
      <button onClick={onClose} className="w-full py-2 text-[13px] text-[#999] font-500 mt-1">取消</button>
    </Modal>
  );
}
