"use client";
import { useState } from "react";
import { Product, Modal, ModalActions, Field, SH, ShToggleGroup } from "./ecommerce-shared";

type Props = {
  products: Product[];
  onClose: () => void;
  onSaved: () => void;
};

const BUNDLE_TYPE_OPTIONS = [
  { value: "traffic", label: "流量組合", sub: "引流款帶主力款" },
  { value: "profit",  label: "利潤組合", sub: "毛利款互補" },
  { value: "scene",   label: "場景組合", sub: "同場景搭配" },
  { value: "cleanup", label: "清庫存",   sub: "高庫存去化" },
];

export default function BundleBuilderModal({ products, onClose, onSaved }: Props) {
  const [skuA, setSkuA] = useState("");
  const [skuB, setSkuB] = useState("");
  const [bundleType, setBundleType] = useState("traffic");
  const [scene, setScene] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);

  const liveProducts = products.filter(p =>
    ["active", "listed", "scaling", "testing_ads", "pending"].includes(p.status)
  );

  const prodA = liveProducts.find(p => p.sku === skuA);
  const prodB = liveProducts.find(p => p.sku === skuB);

  const basePriceSum = (prodA?.target_price || 0) + (prodB?.target_price || 0);
  const avgMargin = ((prodA?.gross_margin_est || 0) + (prodB?.gross_margin_est || 0)) / 2;
  const discount = avgMargin >= 0.50 ? 0.85 : avgMargin >= 0.40 ? 0.88 : avgMargin >= 0.30 ? 0.92 : 0.95;
  const bundlePrice = basePriceSum > 0 ? Math.round(basePriceSum * discount / 10) * 10 : 0;
  const discountPct = Math.round((1 - discount) * 100);

  const marginColor = (m: number) =>
    m >= 0.40 ? "#15803d" : m >= 0.25 ? "#d97706" : "#dc2626";

  const canSave = !!skuA && !!skuB && skuA !== skuB;

  const handleSave = async () => {
    if (!canSave || saving) return;
    setSaving(true);
    try {
      await fetch(`/api/ecommerce/products/${skuA}/relations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          related_sku: skuB,
          related_name: prodB?.name || "",
          relation_type: "bundle",
          scene: scene || null,
          is_bundle_candidate: true,
          notes: notes || null,
        }),
      });
      onSaved();
      onClose();
    } catch {
      // ignore; user can retry
    } finally {
      setSaving(false);
    }
  };

  const selectCls = "w-full px-3 py-2.5 rounded-[10px] text-[13px] border border-[var(--border)] bg-white text-[var(--text-1)] focus:outline-none focus:ring-2 focus:ring-opacity-30 transition-all";

  return (
    <Modal title="自建組合" subtitle="手動選擇商品，系統計算組合毛利與建議售價" onClose={onClose}>
      <div className="space-y-4">

        {/* Product A */}
        <Field label="商品 A" required>
          <select value={skuA} onChange={e => setSkuA(e.target.value)} className={selectCls}>
            <option value="">— 選擇商品 A —</option>
            {liveProducts.filter(p => p.sku !== skuB).map(p => (
              <option key={p.sku} value={p.sku}>
                {p.name}（{p.role || "—"}）NT$ {p.target_price || "—"}
              </option>
            ))}
          </select>
        </Field>

        {/* Product B */}
        <Field label="商品 B" required>
          <select value={skuB} onChange={e => setSkuB(e.target.value)} className={selectCls}>
            <option value="">— 選擇商品 B —</option>
            {liveProducts.filter(p => p.sku !== skuA).map(p => (
              <option key={p.sku} value={p.sku}>
                {p.name}（{p.role || "—"}）NT$ {p.target_price || "—"}
              </option>
            ))}
          </select>
        </Field>

        {/* Preview card */}
        {prodA && prodB && (
          <div className="rounded-[12px] p-4 space-y-3" style={{ background: "var(--bg-2)", border: "1px solid var(--border)" }}>
            {/* Products */}
            <div className="space-y-1.5">
              {[prodA, prodB].map((p, i) => (
                <div key={i} className="flex items-center gap-2 text-[12px]">
                  <span className="px-1.5 py-0.5 rounded-full text-[10px] font-600"
                    style={{ background: SH.light, color: SH.primary }}>
                    {p.role || "—"}
                  </span>
                  <span className="font-600 text-[var(--text-1)] flex-1">{p.name}</span>
                  <span className="text-[var(--text-3)]">NT$ {p.target_price || "—"}</span>
                  {p.gross_margin_est != null && (
                    <span className="font-600" style={{ color: marginColor(p.gross_margin_est) }}>
                      {(p.gross_margin_est * 100).toFixed(0)}%
                    </span>
                  )}
                </div>
              ))}
            </div>
            {/* Economics */}
            <div className="pt-2 border-t border-[var(--border)] grid grid-cols-3 gap-2 text-[11px]">
              <div>
                <div className="text-[var(--text-3)]">單品總和</div>
                <div className="font-600">NT$ {basePriceSum}</div>
              </div>
              <div>
                <div className="text-[var(--text-3)]">建議組合價</div>
                <div className="font-700" style={{ color: SH.primary }}>NT$ {bundlePrice}</div>
              </div>
              <div>
                <div className="text-[var(--text-3)]">折扣 / 預估毛利</div>
                <div className="font-600">
                  省 {discountPct}%
                  {avgMargin > 0 && (
                    <span className="ml-1" style={{ color: marginColor(avgMargin) }}>
                      · {(avgMargin * 100).toFixed(0)}%毛利
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Bundle type */}
        <Field label="組合類型">
          <ShToggleGroup value={bundleType} onChange={setBundleType} options={BUNDLE_TYPE_OPTIONS} />
        </Field>

        {/* Scene */}
        <Field label="場景備註" hint="例：辦公室桌面 / 居家氛圍">
          <input
            type="text"
            value={scene}
            onChange={e => setScene(e.target.value)}
            placeholder="選填"
            className={selectCls}
          />
        </Field>

        {/* Notes */}
        <Field label="備註">
          <input
            type="text"
            value={notes}
            onChange={e => setNotes(e.target.value)}
            placeholder="選填，說明這組組合的設計考量"
            className={selectCls}
          />
        </Field>

        <ModalActions
          onCancel={onClose}
          onConfirm={handleSave}
          disabled={!canSave || saving}
          label={saving ? "儲存中..." : "儲存組合"}
        />
      </div>
    </Modal>
  );
}
