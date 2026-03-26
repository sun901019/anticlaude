"use client";
import { Product, fmt, ACTION_COLOR, SH, inputCls, Field, Modal, ModalActions } from "./ecommerce-shared";

type SalesForm = { current_price: string; sales_7d: string; ad_spend_7d: string; current_stock: string };
type SalesResult = { revenue_7d: number; gross_profit: number; gross_margin: string; next_action: string };

type Props = {
  product: Product;
  result: SalesResult | null;
  form: SalesForm;
  setForm: React.Dispatch<React.SetStateAction<SalesForm>>;
  onSubmit: () => void;
  onClose: () => void;
};

export function SalesModal({ product, result, form, setForm, onSubmit, onClose }: Props) {
  return (
    <Modal title="更新週銷售" subtitle={`${product.sku} · ${product.name}`} onClose={onClose}>
      {!result ? (
        <>
          <div className="grid grid-cols-2 gap-3">
            <Field label="目前售價（NT$）" required>
              <input className={inputCls} type="number" placeholder="例：299" value={form.current_price}
                onChange={e => setForm(f => ({ ...f, current_price: e.target.value }))} />
            </Field>
            <Field label="7天銷量（件）" required>
              <input className={inputCls} type="number" placeholder="例：12" value={form.sales_7d}
                onChange={e => setForm(f => ({ ...f, sales_7d: e.target.value }))} />
            </Field>
            <Field label="廣告花費（NT$）" hint="沒跑廣告填 0">
              <input className={inputCls} type="number" placeholder="0" value={form.ad_spend_7d}
                onChange={e => setForm(f => ({ ...f, ad_spend_7d: e.target.value }))} />
            </Field>
            <Field label="目前庫存（件）">
              <input className={inputCls} type="number" placeholder="例：38" value={form.current_stock}
                onChange={e => setForm(f => ({ ...f, current_stock: e.target.value }))} />
            </Field>
          </div>
          <ModalActions
            onCancel={onClose}
            onConfirm={onSubmit}
            disabled={!form.current_price || !form.sales_7d}
            label="計算並儲存" />
        </>
      ) : (
        <>
          <div className="rounded-[12px] p-5 space-y-3" style={{ background: "var(--bg-2)" }}>
            <div className="text-[12px] font-600 text-[var(--text-3)] mb-2">本週計算結果</div>
            {[
              { label: "7天營收", value: `NT$ ${fmt(result.revenue_7d)}` },
              { label: "毛利", value: `NT$ ${fmt(result.gross_profit)}`, highlight: result.gross_profit > 0 },
              { label: "毛利率", value: result.gross_margin },
            ].map(({ label, value, highlight }) => (
              <div key={label} className="flex justify-between items-center py-1.5 border-b border-[var(--border)] last:border-0">
                <span className="text-[13px] text-[var(--text-3)]">{label}</span>
                <span className={`text-[14px] font-700 ${highlight ? "text-emerald-600" : result.gross_profit < 0 ? "text-red-500" : "text-[var(--text-1)]"}`}>{value}</span>
              </div>
            ))}
            <div className="pt-2">
              <div className="text-[12px] text-[var(--text-3)] mb-1">建議策略</div>
              <div className={`text-[15px] font-700 ${ACTION_COLOR[result.next_action] || "text-[var(--text-1)]"}`}>
                {result.next_action}
              </div>
            </div>
          </div>
          <button onClick={onClose}
            className="w-full py-3 rounded-[12px] text-[14px] font-600 text-white"
            style={{ background: SH.primary }}>
            完成
          </button>
        </>
      )}
    </Modal>
  );
}
