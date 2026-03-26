"use client";
import { useEffect, useState } from "react";
import { RefreshCw, AlertTriangle, Layers, Star, FileText, ChevronRight, Plus, Brain, Link2 } from "lucide-react";
import { BundleSuggestion, Portfolio, Product, Report, Lesson, Modal, Field, ModalActions, inputCls, SH, ROLE_COLOR, fmt } from "./ecommerce-shared";
import BundleBuilderModal from "./BundleBuilderModal";

type ProductBundle = {
  sku: string; source_name: string; source_role: string; source_price: number;
  relations: { id: number; related_sku: string; related_name: string; relation_type: string; scene: string; notes: string }[];
};

const RELATION_LABELS: Record<string, string> = {
  bundle: "組合包", cross_sell: "搭配推薦", upsell: "升級品", scene_partner: "場景搭檔",
};
const RELATION_COLORS: Record<string, string> = {
  bundle: "bg-violet-50 text-violet-600", cross_sell: "bg-blue-50 text-blue-600",
  upsell: "bg-emerald-50 text-emerald-600", scene_partner: "bg-amber-50 text-amber-600",
};

// ── BundlesTab ────────────────────────────────────────────────────────────────
export function BundlesTab({ bundleSuggestions, portfolio, loadBundles, products }: {
  bundleSuggestions: BundleSuggestion[];
  portfolio: Portfolio | null;
  loadBundles: () => void;
  products: Product[];
}) {
  const [productBundles, setProductBundles] = useState<ProductBundle[]>([]);
  const [showBuilder, setShowBuilder] = useState(false);

  useEffect(() => {
    fetch("/api/ecommerce/bundles").then(r => r.json()).then(setProductBundles).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-[17px] font-700 text-[var(--text-1)]">組合設計</h2>
        <div className="flex items-center gap-2">
          <button onClick={() => setShowBuilder(true)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-[10px] text-[13px] font-medium text-white"
            style={{ background: SH.primary }}>
            <Plus size={13} /> 自建組合
          </button>
          <button onClick={loadBundles}
            className="flex items-center gap-1.5 px-4 py-2 rounded-[10px] text-[13px] font-medium border border-[var(--border)] text-[var(--text-2)] hover:bg-[var(--bg-2)]">
            <RefreshCw size={13} /> 重新分析
          </button>
        </div>
      </div>

      {showBuilder && (
        <BundleBuilderModal
          products={products}
          onClose={() => setShowBuilder(false)}
          onSaved={() => {
            setShowBuilder(false);
            fetch("/api/ecommerce/bundles").then(r => r.json()).then(setProductBundles).catch(() => {});
          }}
        />
      )}

      {/* ── Section A: 實際商品組合（fl_product_relations）── */}
      {productBundles.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Link2 size={13} style={{ color: SH.primary }} />
            <span className="text-[13px] font-700" style={{ color: SH.primary }}>已設定組合</span>
            <span className="text-[11px] text-[var(--text-3)]">{productBundles.length} 件主商品有關聯</span>
          </div>
          {productBundles.map(b => (
            <div key={b.sku} className="rounded-[14px] p-4 space-y-3" style={{ background: "var(--surface)", border: `1.5px solid ${SH.border}` }}>
              <div className="flex items-center gap-2">
                <span className="font-700 text-[14px] text-[var(--text-1)]">{b.source_name}</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${ROLE_COLOR[b.source_role] || "bg-gray-50 text-gray-500"}`}>{b.source_role}</span>
                {b.source_price && <span className="text-[12px] text-[var(--text-3)] ml-auto">NT$ {fmt(b.source_price)}</span>}
              </div>
              <div className="space-y-1.5">
                {b.relations.map(r => (
                  <div key={r.id} className="flex items-center gap-2.5 px-3 py-2 rounded-[8px]" style={{ background: "var(--bg-2)" }}>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-600 shrink-0 ${RELATION_COLORS[r.relation_type] || "bg-gray-50 text-gray-500"}`}>
                      {RELATION_LABELS[r.relation_type] || r.relation_type}
                    </span>
                    <span className="text-[13px] font-600 text-[var(--text-1)]">{r.related_name}</span>
                    {r.scene && <span className="text-[11px] text-[var(--text-3)]">· {r.scene}</span>}
                    {r.notes && <span className="text-[11px] text-[var(--text-4)] ml-auto truncate max-w-[140px]">{r.notes}</span>}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Section B: 系統推薦（三種組合類型）── */}
      {bundleSuggestions.length > 0 && (() => {
        const BUNDLE_TYPE_CONFIG = {
          traffic: { label: "流量組合", desc: "引流款帶主力款，衝客流", color: "#1d4ed8", bg: "#eff6ff", border: "#bfdbfe" },
          profit:  { label: "利潤組合", desc: "毛利款互補，保護客單毛利", color: "#15803d", bg: "#f0fdf4", border: "#bbf7d0" },
          scene:   { label: "場景組合", desc: "同場景/同系列，提升連帶購買", color: "#7c3aed", bg: "#f5f3ff", border: "#ddd6fe" },
          cleanup: { label: "清庫存組合", desc: "高庫存品搭引流款，去化不傷定價", color: "#b45309", bg: "#fffbeb", border: "#fde68a" },
        };
        const SOURCE_LABEL: Record<string, string> = {
          relation: "手動設定", family: "同系列", role: "角色互補", candidate: "候選品",
        };

        const liveSuggestions = bundleSuggestions.filter(b => b.source !== "candidate");
        const candidateSuggestions = bundleSuggestions.filter(b => b.source === "candidate");

        const BundleCard = ({ b, i }: { b: BundleSuggestion; i: number }) => {
          const btype = (b.bundle_type || "scene") as "traffic" | "profit" | "scene" | "cleanup";
          const cfg = BUNDLE_TYPE_CONFIG[btype];
          const [saving, setSaving] = useState(false);
          const [saved, setSaved] = useState(false);

          const canSave = b.source !== "candidate"
            && b.products.length >= 2
            && !!b.products[0].sku && !!b.products[1].sku;

          const saveRelation = async () => {
            if (!canSave || saving || saved) return;
            setSaving(true);
            const p0 = b.products[0], p1 = b.products[1];
            try {
              await fetch(`/api/ecommerce/products/${p0.sku}/relations`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  related_sku: p1.sku,
                  related_name: p1.name,
                  relation_type: "bundle",
                  scene: b.scene || null,
                  is_bundle_candidate: true,
                  notes: b.suggestion_reason?.slice(0, 200) || null,
                }),
              });
              setSaved(true);
            } catch {
              // silently ignore; user can retry
            } finally {
              setSaving(false);
            }
          };

          return (
            <div key={i} className="rounded-[14px] p-4 space-y-3"
              style={{ background: "var(--surface)", border: `1.5px solid ${cfg.border}` }}>
              {/* Header */}
              <div className="flex items-start gap-2 flex-wrap">
                <span className="text-[10px] font-700 px-2 py-0.5 rounded-full shrink-0"
                  style={{ color: cfg.color, background: cfg.bg }}>{cfg.label}</span>
                {b.source && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-[var(--bg-2)] text-[var(--text-3)] shrink-0">
                    {SOURCE_LABEL[b.source] || b.source}
                  </span>
                )}
                <span className="text-[13px] font-700 text-[var(--text-1)] flex-1 leading-snug">{b.bundle_name}</span>
                {b.viability_score != null && (
                  <span className="text-[9px] text-[var(--text-4)] shrink-0">評分 {b.viability_score.toFixed(1)}</span>
                )}
              </div>
              {/* Products */}
              <div className="flex gap-2">
                {b.products.map((p, pi) => (
                  <div key={pi} className="flex-1 rounded-[8px] px-3 py-2" style={{ background: cfg.bg }}>
                    <div className="text-[11px] font-600" style={{ color: cfg.color }}>{p.role}</div>
                    <div className="text-[12px] font-700 text-[var(--text-1)] leading-snug mt-0.5">{p.name}</div>
                    <div className="text-[11px] text-[var(--text-3)] mt-0.5 flex gap-2">
                      {p.price > 0 && <span>NT$ {p.price}</span>}
                      {p.stock != null && <span>庫存 {p.stock}</span>}
                      {p.gross_margin != null && p.gross_margin > 0 && (
                        <span style={{ color: p.gross_margin >= 0.4 ? "#16a34a" : p.gross_margin >= 0.25 ? "#d97706" : "#dc2626" }}>
                          {(p.gross_margin * 100).toFixed(0)}%毛利
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              {/* Economics */}
              <div className="grid grid-cols-4 gap-2 text-[11px]">
                <div><div className="text-[var(--text-3)]">單品總和</div><div className="font-600">NT$ {b.base_price_sum}</div></div>
                <div><div className="text-[var(--text-3)]">組合價</div><div className="font-700" style={{ color: cfg.color }}>NT$ {b.bundle_price}</div></div>
                <div><div className="text-[var(--text-3)]">折扣</div><div className="font-600">{(b.discount_pct * 100).toFixed(0)}% off</div></div>
                <div><div className="text-[var(--text-3)]">預估毛利</div>
                  <div className="font-700" style={{ color: b.estimated_margin >= 0.4 ? "#16a34a" : b.estimated_margin >= 0.25 ? "#d97706" : "#dc2626" }}>
                    {(b.estimated_margin * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
              {/* Reason + Action */}
              <div className="space-y-1">
                <p className="text-[11px] text-[var(--text-3)] leading-relaxed">{b.suggestion_reason}</p>
                {b.bundle_action && (
                  <p className="text-[11px] font-600" style={{ color: cfg.color }}>→ {b.bundle_action}</p>
                )}
              </div>
              {/* Save action */}
              {canSave && (
                <button
                  onClick={saveRelation}
                  disabled={saving || saved}
                  className="w-full py-2 rounded-[10px] text-[12px] font-600 transition-all disabled:opacity-50"
                  style={saved
                    ? { background: "#f0fdf4", color: "#15803d", border: "1px solid #bbf7d0" }
                    : { background: cfg.bg, color: cfg.color, border: `1px solid ${cfg.border}` }
                  }>
                  {saved ? "已存入關聯" : saving ? "儲存中..." : "存為組合關聯"}
                </button>
              )}
            </div>
          );
        };

        return (
          <div className="space-y-4">
            {/* Live product bundles grouped by type */}
            {(["traffic", "profit", "scene", "cleanup"] as const).map(btype => {
              const group = liveSuggestions.filter(b => (b.bundle_type || "scene") === btype);
              if (group.length === 0) return null;
              const cfg = BUNDLE_TYPE_CONFIG[btype];
              return (
                <div key={btype} className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-700 px-2.5 py-1 rounded-[8px]"
                      style={{ color: cfg.color, background: cfg.bg }}>{cfg.label}</span>
                    <span className="text-[11px] text-[var(--text-3)]">{cfg.desc}</span>
                  </div>
                  {group.map((b, i) => <BundleCard key={i} b={b} i={i} />)}
                </div>
              );
            })}

            {/* Candidate fallback (collapsed if live suggestions exist) */}
            {candidateSuggestions.length > 0 && (
              <details className="group">
                <summary className="flex items-center gap-1.5 cursor-pointer select-none list-none text-[11px] font-600 py-1"
                  style={{ color: "var(--text-3)" }}>
                  <span className="transition-transform group-open:rotate-90 text-[9px]">▶</span>
                  候選品建議（尚未上架）{candidateSuggestions.length} 組
                </summary>
                <div className="mt-2 space-y-2">
                  {candidateSuggestions.map((b, i) => <BundleCard key={i} b={b} i={i} />)}
                </div>
              </details>
            )}
          </div>
        );
      })()}

      {/* 空白提示 */}
      {productBundles.length === 0 && bundleSuggestions.length === 0 && (
        <div className="rounded-[16px] p-10 text-center" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
          <Layers size={32} className="mx-auto mb-3 text-[var(--text-3)]" />
          <p className="text-[14px] text-[var(--text-2)] font-500">尚無組合建議</p>
          <p className="text-[13px] text-[var(--text-3)] mt-1">點「重新分析」讓系統從在售商品生成組合建議；或在商品抽屜的「操作」頁籤手動設定商品關聯</p>
        </div>
      )}
    </div>
  );
}

// ── ReportsTab ────────────────────────────────────────────────────────────────
export function ReportsTab({ reports, selectedReport, setSelectedReport }: {
  reports: Report[];
  selectedReport: { id: number; report_markdown: string; report_title: string } | null;
  setSelectedReport: (r: { id: number; report_markdown: string; report_title: string } | null) => void;
}) {
  return (
    <div className="space-y-4">
      <h2 className="text-[17px] font-700 text-[var(--text-1)]">選品報告</h2>
      {reports.length === 0 ? (
        <div className="rounded-[16px] p-10 text-center" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
          <FileText size={32} className="mx-auto mb-3 text-[var(--text-3)]" />
          <p className="text-[14px] text-[var(--text-2)] font-500">尚無報告</p>
          <p className="text-[13px] text-[var(--text-3)] mt-1">在評分分析完成後點擊「生成選品報告」</p>
        </div>
      ) : (
        <div className="space-y-2">
          {reports.map(r => (
            <div key={r.id} className="rounded-[12px] px-5 py-4 flex items-center justify-between cursor-pointer hover:bg-[var(--bg-2)] transition-colors"
              style={{ background: "var(--surface)", border: "1px solid var(--border)" }}
              onClick={() => fetch(`/api/ecommerce/selection/reports/${r.id}`).then(res => res.json()).then(setSelectedReport)}>
              <div>
                <div className="text-[14px] font-600 text-[var(--text-1)]">{r.report_title}</div>
                <div className="text-[12px] text-[var(--text-3)] mt-0.5">by {r.created_by_agent} · {r.created_at?.slice(0,10)}</div>
              </div>
              <ChevronRight size={16} className="text-[var(--text-3)]" />
            </div>
          ))}
        </div>
      )}
      {selectedReport && (
        <Modal title={selectedReport.report_title} onClose={() => setSelectedReport(null)}>
          <pre className="text-[12px] text-[var(--text-2)] whitespace-pre-wrap leading-relaxed overflow-auto max-h-[60vh]">
            {selectedReport.report_markdown}
          </pre>
        </Modal>
      )}
    </div>
  );
}

// ── LessonsTab ────────────────────────────────────────────────────────────────
export function LessonsTab({ lessons, showAddLesson, setShowAddLesson, newLessonForm, setNewLessonForm, loadLessons }: {
  lessons: Lesson[];
  showAddLesson: boolean;
  setShowAddLesson: (v: boolean) => void;
  newLessonForm: { theme: string; lesson_type: string; lesson_text: string };
  setNewLessonForm: React.Dispatch<React.SetStateAction<{ theme: string; lesson_type: string; lesson_text: string }>>;
  loadLessons: () => void;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-[17px] font-700 text-[var(--text-1)]">學習記憶</h2>
        </div>
        <button onClick={() => setShowAddLesson(true)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-[10px] text-[13px] font-medium border border-[var(--border)] text-[var(--text-2)] hover:bg-[var(--bg-2)]">
          <Plus size={14} /> 新增記憶
        </button>
      </div>
      {lessons.length === 0 ? (
        <div className="rounded-[16px] p-10 text-center" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
          <Brain size={32} className="mx-auto mb-3 text-[var(--text-3)]" />
          <p className="text-[14px] text-[var(--text-2)] font-500">尚無學習記憶</p>
          <p className="text-[13px] text-[var(--text-3)] mt-1">累積多次選品後，系統會自動萃取模式</p>
        </div>
      ) : (
        <div className="space-y-2">
          {lessons.map(l => (
            <div key={l.id} className="rounded-[12px] px-5 py-4" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
              <div className="flex items-center gap-2 mb-1">
                <span className={`px-2 py-0.5 rounded-full text-[11px] font-600 ${
                  l.lesson_type === "winning_pattern" ? "bg-emerald-50 text-emerald-600" :
                  l.lesson_type === "rejection_pattern" ? "bg-red-50 text-red-500" :
                  l.lesson_type === "margin_rule" ? "bg-blue-50 text-blue-600" :
                  "bg-violet-50 text-violet-600"}`}>
                  {l.lesson_type}
                </span>
                <span className="text-[13px] font-600 text-[var(--text-1)]">{l.theme}</span>
                <span className="ml-auto text-[12px] text-[var(--text-3)]">信心 {(l.confidence * 100).toFixed(0)}%</span>
              </div>
              <p className="text-[13px] text-[var(--text-2)] leading-relaxed">{l.lesson_text}</p>
            </div>
          ))}
        </div>
      )}
      {showAddLesson && (
        <Modal title="新增學習記憶" onClose={() => setShowAddLesson(false)}>
          <Field label="主題">
            <input className={inputCls} placeholder="例：不適合進電子類商品" value={newLessonForm.theme}
              onChange={e => setNewLessonForm(f => ({ ...f, theme: e.target.value }))} />
          </Field>
          <Field label="記憶類型">
            <select className={inputCls} value={newLessonForm.lesson_type}
              onChange={e => setNewLessonForm(f => ({ ...f, lesson_type: e.target.value }))}>
              <option value="rejection_pattern">拒絕模式</option>
              <option value="winning_pattern">成功模式</option>
              <option value="margin_rule">毛利原則</option>
              <option value="brand_rule">品牌原則</option>
            </select>
          </Field>
          <Field label="記憶內容">
            <textarea className={inputCls} rows={3} placeholder="具體描述這個規律..."
              value={newLessonForm.lesson_text}
              onChange={e => setNewLessonForm(f => ({ ...f, lesson_text: e.target.value }))} />
          </Field>
          <ModalActions
            onCancel={() => setShowAddLesson(false)}
            onConfirm={async () => {
              await fetch("/api/ecommerce/selection/lessons", {
                method: "POST", headers: { "Content-Type": "application/json" },
                body: JSON.stringify(newLessonForm),
              });
              setShowAddLesson(false);
              setNewLessonForm({ theme: "", lesson_type: "rejection_pattern", lesson_text: "" });
              loadLessons();
            }}
            disabled={!newLessonForm.theme || !newLessonForm.lesson_text}
            label="儲存記憶" />
        </Modal>
      )}
    </div>
  );
}
