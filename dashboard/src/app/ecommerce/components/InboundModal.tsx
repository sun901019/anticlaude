"use client";
import { Product, Performance, Setting, emptyInv, SH, inputCls, Field, Modal, ModalActions, ShToggleGroup } from "./ecommerce-shared";

type InvForm = typeof emptyInv;

type Props = {
  invForm: InvForm;
  setInvForm: React.Dispatch<React.SetStateAction<InvForm>>;
  products: Product[];
  performances: (Performance & { name: string })[];
  settings: Setting[];
  onSubmit: () => void;
  onClose: () => void;
};

export function InboundModal({ invForm, setInvForm, products, performances, settings, onSubmit, onClose }: Props) {
  const selectedProd = products.find(p => p.sku === invForm.sku);
  const cfg2 = Object.fromEntries(settings.map(s => [s.key, s.value]));
  const exr = (cfg2["exchange_rate"] as number) ?? 4.5;
  const qql_exr = (cfg2["qql_exchange_rate"] as number) ?? 4.5;
  const qql_fee = (cfg2["qql_service_fee"] as number) ?? 0.03;
  const costRmb = parseFloat(invForm.cost_rmb) || 0;
  const headFreight = selectedProd?.head_freight_rmb || 0;
  const qty = parseInt(invForm.quantity) || 0;
  const isQql = invForm.procurement_mode === "qql_agent";

  const landedUnit = isQql
    ? (costRmb + headFreight) * qql_exr * (1 + qql_fee)
    : (costRmb + headFreight) * exr;
  const totalTwd = landedUnit * qty;
  const currentStock = selectedProd?.total_stock ?? 0;
  const projectedStock = currentStock + qty;

  const perfRow = performances.find(p => p.sku === invForm.sku);
  const dailySales = ((perfRow?.sales_7d ?? 0) / 7) || 0;
  const daysCoverage = dailySales > 0 ? Math.round(projectedStock / dailySales) : null;

  const invRec = daysCoverage === null
    ? { text: "尚無銷售數據，請先更新週銷售再評估", color: SH.muted }
    : daysCoverage < 14
    ? { text: `⚠ 補貨量偏少，進貨後約可撐 ${daysCoverage} 天，建議增加數量`, color: "#dc2626" }
    : daysCoverage <= 45
    ? { text: `✓ 補貨量正常，進貨後庫存可支撐約 ${daysCoverage} 天`, color: "#15803d" }
    : { text: `進貨後可撐 ${daysCoverage} 天，屬積極備貨，請確認需求穩定再決定`, color: SH.muted };

  const leadDays = parseInt(invForm.lead_days) || 0;
  const eta = leadDays > 0 ? (() => { const d = new Date(); d.setDate(d.getDate() + leadDays); return d.toLocaleDateString("zh-TW"); })() : null;
  const hasPreview = !!invForm.sku && !!invForm.cost_rmb && !!invForm.quantity;

  return (
    <Modal title="補貨入庫" subtitle="採購成本、進貨後庫存、補貨決策評估" onClose={onClose}>

      <Field label="選擇商品" required>
        <select className={inputCls} value={invForm.sku} onChange={e => setInvForm(f => ({ ...f, sku: e.target.value }))}>
          <option value="">— 請選擇 —</option>
          {products.map(p => (
            <option key={p.sku} value={p.sku}>{p.sku}｜{p.name}（庫存 {p.total_stock ?? 0} 件）</option>
          ))}
        </select>
      </Field>

      <Field label="採購模式">
        <ShToggleGroup
          options={[
            { value: "standard_1688", label: "1688 直採" },
            { value: "qql_agent",     label: "QQL 代購" },
          ]}
          value={invForm.procurement_mode}
          onChange={v => setInvForm(f => ({ ...f, procurement_mode: v }))} />
      </Field>

      {selectedProd && (
        <div className="text-[11px] rounded-[8px] px-3 py-2 flex gap-4" style={{ background: SH.light, color: SH.primary }}>
          <span>上次成本 ¥{selectedProd.cost_rmb ?? "—"}</span>
          <span>境內運 ¥{selectedProd.head_freight_rmb || 0}</span>
          <span>目標售價 NT${selectedProd.target_price ?? "—"}</span>
          {(perfRow?.sales_7d ?? 0) > 0 && <span>週銷 {perfRow!.sales_7d} 件</span>}
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        <Field label="進貨價（¥/件）" required>
          <input className={inputCls} type="number" placeholder="例：25" value={invForm.cost_rmb}
            onChange={e => setInvForm(f => ({ ...f, cost_rmb: e.target.value }))} />
        </Field>
        <Field label="進貨數量（件）" required>
          <input className={inputCls} type="number" placeholder="例：50" value={invForm.quantity}
            onChange={e => setInvForm(f => ({ ...f, quantity: e.target.value }))} />
        </Field>
      </div>

      {hasPreview && (
        <div className="rounded-[12px] overflow-hidden" style={{ border: `1.5px solid ${SH.border}` }}>
          <div className="px-4 py-2 text-[11px] font-700 uppercase tracking-wider" style={{ background: SH.light, color: SH.primary }}>
            這批採購分析
          </div>
          <div className="grid grid-cols-2 divide-x text-center py-3" style={{ borderBottom: `1px solid ${SH.border}` }}>
            <div>
              <div className="text-[10px] text-[var(--text-3)] mb-1">單件落地成本</div>
              <div className="text-[18px] font-800" style={{ color: SH.primary }}>NT$ {Math.round(landedUnit)}</div>
              <div className="text-[10px] text-[var(--text-3)] mt-0.5">
                {isQql ? `QQL 匯率 ${qql_exr} × (1+${(qql_fee*100).toFixed(0)}%)` : `¥${costRmb} + ¥${headFreight} × ${exr}`}
              </div>
            </div>
            <div>
              <div className="text-[10px] text-[var(--text-3)] mb-1">批次總金額</div>
              <div className="text-[18px] font-800 text-[var(--text-1)]">NT$ {Math.round(totalTwd).toLocaleString()}</div>
              <div className="text-[10px] text-[var(--text-3)] mt-0.5">{qty} 件</div>
            </div>
          </div>
          <div className="grid grid-cols-3 divide-x text-center py-2.5" style={{ borderBottom: `1px solid ${SH.border}` }}>
            <div>
              <div className="text-[10px] text-[var(--text-3)] mb-0.5">進貨後庫存</div>
              <div className="text-[15px] font-700 text-[var(--text-1)]">{projectedStock} 件</div>
              <div className="text-[10px] text-[var(--text-3)]">+{qty}</div>
            </div>
            <div>
              <div className="text-[10px] text-[var(--text-3)] mb-0.5">可撐天數</div>
              {daysCoverage !== null
                ? <div className="text-[15px] font-700" style={{ color: daysCoverage < 14 ? "#dc2626" : daysCoverage > 45 ? SH.muted : "#15803d" }}>{daysCoverage} 天</div>
                : <div className="text-[13px] text-[var(--text-3)]">無銷售數據</div>}
            </div>
            <div>
              <div className="text-[10px] text-[var(--text-3)] mb-0.5">成本佔售價</div>
              {selectedProd?.target_price ? (
                <div className="text-[15px] font-700" style={{ color: landedUnit / selectedProd.target_price > 0.6 ? "#dc2626" : "#15803d" }}>
                  {((landedUnit / selectedProd.target_price) * 100).toFixed(0)}%
                </div>
              ) : <div className="text-[13px] text-[var(--text-3)]">未設售價</div>}
            </div>
          </div>
          {selectedProd?.cost_rmb != null && (
            (() => {
              const prevLanded = ((selectedProd.cost_rmb || 0) + (selectedProd.head_freight_rmb || 0)) * exr;
              const diff = landedUnit - prevLanded;
              const diffPct = prevLanded > 0 ? (diff / prevLanded * 100) : 0;
              const isHigher = diff > 1;
              const isLower = diff < -1;
              return (
                <div className="px-4 py-2 text-[11px] flex items-center justify-between" style={{ borderBottom: `1px solid ${SH.border}` }}>
                  <span style={{ color: "var(--text-3)" }}>vs 商品記錄成本</span>
                  <span className="font-600" style={{ color: isHigher ? "#dc2626" : isLower ? "#15803d" : "var(--text-2)" }}>
                    {isHigher ? "▲" : isLower ? "▼" : "="} NT${Math.abs(Math.round(diff))}/件
                    {Math.abs(diffPct) > 1 && ` (${diffPct > 0 ? "+" : ""}${diffPct.toFixed(0)}%)`}
                  </span>
                </div>
              );
            })()
          )}
          {eta && (
            <div className="px-4 py-2 text-[11px] flex items-center justify-between" style={{ borderBottom: `1px solid ${SH.border}` }}>
              <span style={{ color: "var(--text-3)" }}>預計到貨</span>
              <span className="font-600 text-[var(--text-1)]">{eta}</span>
            </div>
          )}
          <div className="px-4 py-2.5 text-[12px] font-500" style={{ color: invRec.color }}>
            {invRec.text}
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        <Field label="預計到貨（天）" hint={eta ? `預計 ${eta}` : "填入後顯示到貨日"}>
          <input className={inputCls} type="number" min={1} placeholder="例：10" value={invForm.lead_days}
            onChange={e => setInvForm(f => ({ ...f, lead_days: e.target.value }))} />
        </Field>
        <Field label="供應商（選填）">
          <input className={inputCls} placeholder="1688 店家名稱" value={invForm.supplier}
            onChange={e => setInvForm(f => ({ ...f, supplier: e.target.value }))} />
        </Field>
        <Field label="採購日期（選填）">
          <input className={inputCls} type="date" value={invForm.purchase_date}
            onChange={e => setInvForm(f => ({ ...f, purchase_date: e.target.value }))} />
        </Field>
        <Field label="折扣券比例（%）" hint="若有券活動">
          <input className={inputCls} type="number" step="0.1" placeholder="例：10"
            value={invForm.coupon_rate ?? ""}
            onChange={e => setInvForm(f => ({ ...f, coupon_rate: e.target.value }))} />
        </Field>
      </div>

      <ModalActions
        onCancel={onClose}
        onConfirm={onSubmit}
        disabled={!invForm.sku || !invForm.cost_rmb || !invForm.quantity}
        label="確認進貨" />
    </Modal>
  );
}
