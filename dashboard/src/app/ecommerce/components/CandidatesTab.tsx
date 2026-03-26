"use client";
import { Plus, Search, Zap, ChevronRight } from "lucide-react";
import { Candidate, Field, Modal, ModalActions, inputCls } from "./ecommerce-shared";

type CandidateForm = {
  product_name: string; source_platform: string; source_url: string;
  category: string; market_type: string; discovery_notes: string;
};

type Props = {
  candidates: Candidate[];
  showAddCandidate: boolean;
  setShowAddCandidate: (v: boolean) => void;
  newCandidateForm: CandidateForm;
  setNewCandidateForm: React.Dispatch<React.SetStateAction<CandidateForm>>;
  loadCandidates: () => void;
  setTab: (t: string) => void;
  setSelectedCandidate: (c: Candidate) => void;
  loadAnalysis: (id: string) => void;
  reload: () => void;
};

export function CandidatesTab({
  candidates, showAddCandidate, setShowAddCandidate,
  newCandidateForm, setNewCandidateForm, loadCandidates,
  setTab, setSelectedCandidate, loadAnalysis, reload,
}: Props) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-[17px] font-700 text-[var(--text-1)]">候選池</h2>
        </div>
        <div className="flex gap-2">
          <button onClick={async () => {
            if (!confirm("對所有未分析的候選品觸發批量 AI 分析？（背景執行，需數分鐘）")) return;
            const r = await fetch("/api/ecommerce/selection/batch-analyze", { method: "POST" });
            const d = await r.json();
            alert(d.message);
          }}
            className="flex items-center gap-1.5 px-3 py-2 rounded-[10px] text-[13px] font-medium border"
            style={{ background: "var(--surface)", borderColor: "var(--border)", color: "var(--text-2)" }}>
            <Zap size={13} /> 批量分析
          </button>
          <button onClick={() => setShowAddCandidate(true)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-[10px] text-[13px] font-medium text-white"
            style={{ background: "var(--accent)" }}>
            <Plus size={14} /> 新增候選品
          </button>
        </div>
      </div>

      {candidates.length === 0 ? (
        <div className="rounded-[16px] p-10 text-center" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
          <Search size={32} className="mx-auto mb-3 text-[var(--text-3)]" />
          <p className="text-[14px] text-[var(--text-2)] font-500">尚未加入任何候選品</p>
          <p className="text-[13px] text-[var(--text-3)] mt-1">按右上角「新增候選品」開始建立選品池</p>
        </div>
      ) : (
        <div className="rounded-[16px] overflow-hidden" style={{ border: "1px solid var(--border)" }}>
          <table className="w-full text-[13px]">
            <thead style={{ background: "var(--bg-2)" }}>
              <tr>
                {["商品名稱","類別","市場類型","來源","狀態","評估狀態","操作"].map(h => (
                  <th key={h} className="text-left px-4 py-3 font-600 text-[var(--text-2)]">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {candidates.map((c, i) => (
                <tr key={c.candidate_id} style={{ borderTop: i > 0 ? "1px solid var(--border)" : undefined }}>
                  <td className="px-4 py-3 font-500 text-[var(--text-1)]">{c.product_name}</td>
                  <td className="px-4 py-3 text-[var(--text-2)]">{c.category || "—"}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-[11px] font-600 ${
                      c.market_type === "problem" ? "bg-violet-50 text-violet-600" :
                      c.market_type === "demand" ? "bg-blue-50 text-blue-600" :
                      c.market_type === "trend" ? "bg-amber-50 text-amber-600" :
                      "bg-gray-100 text-gray-500"}`}>
                      {c.market_type || "未分類"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[var(--text-3)]">{c.source_platform}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-[11px] font-600 ${
                      c.status === "approved" ? "bg-emerald-50 text-emerald-600" :
                      c.status === "rejected" ? "bg-red-50 text-red-500" :
                      c.status === "shortlisted" ? "bg-blue-50 text-blue-600" :
                      "bg-gray-100 text-gray-500"}`}>
                      {c.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[var(--text-3)]">{c.selection_status}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <button onClick={() => { setSelectedCandidate(c); loadAnalysis(c.candidate_id); setTab("analysis"); }}
                        className="flex items-center gap-1 text-violet-500 hover:text-violet-700 text-[12px] font-500">
                        評分 <ChevronRight size={12} />
                      </button>
                      {c.status === "approved" && (
                        <button onClick={async () => {
                          const r = await fetch(`/api/ecommerce/selection/candidates/${c.candidate_id}/promote`, { method: "POST" });
                          const d = await r.json();
                          if (d.ok) { alert(`✅ ${d.message}`); reload(); }
                          else alert("升格失敗：" + (d.detail || "未知錯誤"));
                        }}
                          className="text-[11px] px-2 py-0.5 rounded-full font-600 bg-emerald-50 text-emerald-600 hover:bg-emerald-100 transition-colors">
                          升格 →
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal: 新增候選品 */}
      {showAddCandidate && (
        <Modal title="新增候選品" subtitle="加入選品候選池，待後續評分分析" onClose={() => setShowAddCandidate(false)}>
          <Field label="商品名稱" required>
            <input className={inputCls} placeholder="例：人體工學頸枕" value={newCandidateForm.product_name}
              onChange={e => setNewCandidateForm(f => ({ ...f, product_name: e.target.value }))} />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="類別">
              <input className={inputCls} placeholder="辦公舒適 / 睡眠改善..." value={newCandidateForm.category}
                onChange={e => setNewCandidateForm(f => ({ ...f, category: e.target.value }))} />
            </Field>
            <Field label="市場類型">
              <select className={inputCls} value={newCandidateForm.market_type}
                onChange={e => setNewCandidateForm(f => ({ ...f, market_type: e.target.value }))}>
                <option value="problem">problem（痛點型）</option>
                <option value="demand">demand（需求型）</option>
                <option value="trend">trend（趨勢型）</option>
                <option value="hybrid">hybrid（混合型）</option>
              </select>
            </Field>
            <Field label="來源平台">
              <select className={inputCls} value={newCandidateForm.source_platform}
                onChange={e => setNewCandidateForm(f => ({ ...f, source_platform: e.target.value }))}>
                {["manual","shopee","tiktok","amazon","instagram","taobao"].map(p => <option key={p}>{p}</option>)}
              </select>
            </Field>
            <Field label="來源連結">
              <input className={inputCls} placeholder="https://..." value={newCandidateForm.source_url}
                onChange={e => setNewCandidateForm(f => ({ ...f, source_url: e.target.value }))} />
            </Field>
          </div>
          <Field label="發現備註">
            <textarea className={inputCls} rows={2} placeholder="為什麼注意到這個商品？差評在哪？"
              value={newCandidateForm.discovery_notes}
              onChange={e => setNewCandidateForm(f => ({ ...f, discovery_notes: e.target.value }))} />
          </Field>
          <ModalActions
            onCancel={() => setShowAddCandidate(false)}
            onConfirm={async () => {
              await fetch("/api/ecommerce/selection/candidates", {
                method: "POST", headers: { "Content-Type": "application/json" },
                body: JSON.stringify(newCandidateForm),
              });
              setShowAddCandidate(false);
              setNewCandidateForm({ product_name: "", source_platform: "manual", source_url: "", category: "", market_type: "problem", discovery_notes: "" });
              loadCandidates();
            }}
            disabled={!newCandidateForm.product_name}
            label="加入候選池" />
        </Modal>
      )}
    </div>
  );
}
