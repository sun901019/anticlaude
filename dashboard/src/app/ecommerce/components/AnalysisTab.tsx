"use client";
import { FlaskConical, FileText, Zap } from "lucide-react";
import { Candidate, Analysis, Field, inputCls } from "./ecommerce-shared";

type AnalysisForm = {
  demand_score: string; competition_score: string; profit_score: string;
  pain_point_score: string; brand_fit_score: string;
  cost_rmb: string; decision_status: string; reasoning: string;
};

type Props = {
  candidates: Candidate[];
  selectedCandidate: Candidate | null;
  setSelectedCandidate: (c: Candidate) => void;
  candidateAnalysis: Analysis | null;
  analysisForm: AnalysisForm;
  setAnalysisForm: React.Dispatch<React.SetStateAction<AnalysisForm>>;
  analysisResult: Record<string, unknown> | null;
  setAnalysisResult: (r: Record<string, unknown> | null) => void;
  loadAnalysis: (id: string) => void;
  loadCandidates: () => void;
  loadReports: () => void;
};

export function AnalysisTab({
  candidates, selectedCandidate, setSelectedCandidate,
  candidateAnalysis, analysisForm, setAnalysisForm,
  analysisResult, setAnalysisResult, loadAnalysis, loadCandidates, loadReports,
}: Props) {
  return (
    <div className="space-y-4">
      <h2 className="text-[17px] font-700 text-[var(--text-1)]">評分分析</h2>
      <div className="grid grid-cols-3 gap-4">
        {/* 左欄：候選品列表 */}
        <div className="col-span-1 rounded-[16px] overflow-hidden" style={{ border: "1px solid var(--border)" }}>
          <div className="px-4 py-3 text-[13px] font-600 text-[var(--text-2)]" style={{ background: "var(--bg-2)" }}>選擇候選品</div>
          {candidates.length === 0 ? (
            <p className="px-4 py-6 text-[13px] text-[var(--text-3)]">先到候選池新增商品</p>
          ) : candidates.map((c, i) => (
            <button key={c.candidate_id} onClick={() => { setSelectedCandidate(c); setAnalysisResult(null); loadAnalysis(c.candidate_id); }}
              className={`w-full text-left px-4 py-3 text-[13px] transition-colors ${selectedCandidate?.candidate_id === c.candidate_id ? "bg-violet-50 text-violet-600 font-600" : "text-[var(--text-2)] hover:bg-[var(--bg-2)]"}`}
              style={{ borderTop: i > 0 ? "1px solid var(--border)" : undefined }}>
              <div className="font-500">{c.product_name}</div>
              <div className="text-[11px] mt-0.5 opacity-60">{c.category} · {c.selection_status}</div>
            </button>
          ))}
        </div>

        {/* 右欄：評分表單或結果 */}
        <div className="col-span-2 space-y-4">
          {!selectedCandidate ? (
            <div className="rounded-[16px] p-8 text-center" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
              <p className="text-[14px] text-[var(--text-3)]">從左側選擇候選品開始評分</p>
            </div>
          ) : (
            <div className="rounded-[16px] p-5 space-y-4" style={{ background: "var(--surface)", border: "1px solid var(--border)" }}>
              <div className="flex items-center justify-between">
                <h3 className="text-[15px] font-700 text-[var(--text-1)]">{selectedCandidate.product_name}</h3>
                {candidateAnalysis && (
                  <span className={`px-3 py-1 rounded-full text-[12px] font-700 ${
                    candidateAnalysis.viability_band === "strong" ? "bg-emerald-50 text-emerald-600" :
                    candidateAnalysis.viability_band === "viable" ? "bg-blue-50 text-blue-600" :
                    candidateAnalysis.viability_band === "watchlist" ? "bg-amber-50 text-amber-600" :
                    "bg-red-50 text-red-500"}`}>
                    上次評分：{candidateAnalysis.score_total} / {candidateAnalysis.viability_band?.toUpperCase()}
                  </span>
                )}
              </div>

              {/* AI 下一步建議卡片 */}
              {candidateAnalysis?.next_steps_json && (() => {
                try {
                  const ns = JSON.parse(candidateAnalysis.next_steps_json);
                  const recColor = ns.recommendation === "建議進樣" ? "border-emerald-200 bg-emerald-50" :
                                   ns.recommendation === "建議淘汰" ? "border-red-200 bg-red-50" :
                                   "border-amber-200 bg-amber-50";
                  const recText = ns.recommendation === "建議進樣" ? "text-emerald-700" :
                                  ns.recommendation === "建議淘汰" ? "text-red-600" : "text-amber-700";
                  return (
                    <div className={`rounded-[10px] border p-4 space-y-3 ${recColor}`}>
                      <div className="flex items-center gap-2">
                        <span className={`text-[14px] font-700 ${recText}`}>{ns.recommendation}</span>
                        <span className="text-[11px] text-[var(--text-3)]">信心度：{ns.confidence}</span>
                      </div>
                      {ns.reasons?.length > 0 && (
                        <div className="space-y-1">
                          {ns.reasons.map((r: string, i: number) => (
                            <div key={i} className="text-[12px] text-[var(--text-2)] flex gap-1.5"><span className="text-emerald-500 mt-0.5">✓</span>{r}</div>
                          ))}
                        </div>
                      )}
                      {ns.next_steps?.length > 0 && (
                        <div className="space-y-1 pt-2 border-t border-[var(--border)]">
                          <div className="text-[11px] font-600 text-[var(--text-3)] mb-1">下一步</div>
                          {ns.next_steps.map((s: string, i: number) => (
                            <div key={i} className="text-[12px] text-[var(--text-2)] flex gap-1.5"><span className="text-violet-400">{i+1}.</span>{s}</div>
                          ))}
                        </div>
                      )}
                      {ns.warnings?.length > 0 && (
                        <div className="pt-2 border-t border-[var(--border)] space-y-1">
                          {ns.warnings.map((w: string, i: number) => (
                            <div key={i} className="text-[11px] text-amber-600 flex gap-1.5"><span>⚠</span>{w}</div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                } catch { return null; }
              })()}

              <div className="grid grid-cols-5 gap-2">
                {[
                  { key: "demand_score", label: "需求強度", hint: "×2" },
                  { key: "competition_score", label: "競品環境", hint: "×1" },
                  { key: "profit_score", label: "獲利潛力", hint: "×2" },
                  { key: "pain_point_score", label: "痛點機會", hint: "×1" },
                  { key: "brand_fit_score", label: "品牌契合", hint: "×1" },
                ].map(({ key, label, hint }) => (
                  <div key={key} className="text-center">
                    <div className="text-[11px] text-[var(--text-3)] mb-1">{label}<span className="ml-1 text-violet-400">{hint}</span></div>
                    <input type="number" min="1" max="10"
                      className="w-full text-center px-2 py-2 rounded-[8px] text-[14px] font-700 border focus:outline-none focus:ring-2 focus:ring-violet-300"
                      style={{ borderColor: "var(--border)" }}
                      value={analysisForm[key as keyof typeof analysisForm]}
                      onChange={e => setAnalysisForm(f => ({ ...f, [key]: e.target.value }))} />
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-2 gap-3">
                <Field label="進貨成本（人民幣）" hint="選填，計算售價用">
                  <input className={inputCls} type="number" placeholder="¥" value={analysisForm.cost_rmb}
                    onChange={e => setAnalysisForm(f => ({ ...f, cost_rmb: e.target.value }))} />
                </Field>
                <Field label="決策狀態">
                  <select className={inputCls} value={analysisForm.decision_status}
                    onChange={e => setAnalysisForm(f => ({ ...f, decision_status: e.target.value }))}>
                    {["待評估","通過","拒絕","觀察"].map(s => <option key={s}>{s}</option>)}
                  </select>
                </Field>
              </div>
              <Field label="評估理由">
                <input className={inputCls} placeholder="為什麼值得進？或拒絕理由..." value={analysisForm.reasoning}
                  onChange={e => setAnalysisForm(f => ({ ...f, reasoning: e.target.value }))} />
              </Field>

              <button onClick={async () => {
                const body: Record<string, unknown> = {
                  demand_score: parseFloat(analysisForm.demand_score),
                  competition_score: parseFloat(analysisForm.competition_score),
                  profit_score: parseFloat(analysisForm.profit_score),
                  pain_point_score: parseFloat(analysisForm.pain_point_score),
                  brand_fit_score: parseFloat(analysisForm.brand_fit_score),
                  decision_status: analysisForm.decision_status,
                  reasoning: analysisForm.reasoning,
                };
                if (analysisForm.cost_rmb) body.financials = { cost_rmb: parseFloat(analysisForm.cost_rmb) };
                const res = await fetch(`/api/ecommerce/selection/analyze/${selectedCandidate.candidate_id}`, {
                  method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
                });
                const data = await res.json();
                setAnalysisResult(data);
                loadAnalysis(selectedCandidate.candidate_id);
                loadCandidates();
              }}
                className="w-full py-3 rounded-[12px] text-[14px] font-600 text-white transition-opacity hover:opacity-90"
                style={{ background: "var(--accent)" }}>
                <FlaskConical size={14} className="inline mr-2" />送出評分
              </button>

              {analysisResult && (
                <div className="rounded-[12px] p-4 space-y-2" style={{ background: "var(--bg-2)" }}>
                  <div className="flex items-center gap-3">
                    <span className="text-[22px] font-800 text-[var(--text-1)]">{String(analysisResult.score_total)}</span>
                    <span className="text-[13px] text-[var(--text-3)]">/ 50 分</span>
                    <span className={`px-2 py-0.5 rounded-full text-[12px] font-700 ${
                      analysisResult.viability_band === "strong" ? "bg-emerald-100 text-emerald-700" :
                      analysisResult.viability_band === "viable" ? "bg-blue-100 text-blue-700" :
                      analysisResult.viability_band === "watchlist" ? "bg-amber-100 text-amber-700" :
                      "bg-red-100 text-red-700"}`}>
                      {String(analysisResult.viability_band).toUpperCase()}
                    </span>
                    <span className="ml-auto text-[13px] font-600" style={{ color: "var(--accent)" }}>
                      建議角色：{String(analysisResult.recommended_role)}
                    </span>
                  </div>
                  {analysisResult.target_price && (
                    <div className="grid grid-cols-3 gap-2 text-[12px]">
                      <div><span className="text-[var(--text-3)]">落地成本</span> <span className="font-600">NT${String(analysisResult.landed_cost_twd)}</span></div>
                      <div><span className="text-[var(--text-3)]">建議售價</span> <span className="font-600 text-emerald-600">NT${String(analysisResult.target_price)}</span></div>
                      <div><span className="text-[var(--text-3)]">毛利率</span> <span className="font-600">{analysisResult.gross_margin ? `${(Number(analysisResult.gross_margin)*100).toFixed(1)}%` : "—"}</span></div>
                    </div>
                  )}
                  <button onClick={async () => {
                    if (!analysisResult.analysis_id) return;
                    await fetch(`/api/ecommerce/selection/reports/${analysisResult.analysis_id}`, {
                      method: "POST", headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({}),
                    });
                    loadReports();
                  }}
                    className="text-[12px] text-violet-500 hover:text-violet-700 flex items-center gap-1">
                    <FileText size={12} /> 生成選品報告
                  </button>

                  {/* 廣告投放建議 */}
                  {(() => {
                    const gm = analysisResult.gross_margin != null ? Number(analysisResult.gross_margin) : null;
                    const price = analysisResult.target_price != null ? Number(analysisResult.target_price) : null;
                    if (gm === null) return (
                      <div className="mt-2 rounded-[10px] px-4 py-3 bg-gray-50 border border-gray-200 text-[12px] text-gray-500 flex items-center gap-2">
                        <Zap size={13} className="shrink-0" />
                        <span>輸入進貨成本後可查看廣告投放建議</span>
                      </div>
                    );
                    const maxCpa = price ? Math.round(price * gm * 0.5) : null;
                    const targetRoas = gm > 0 ? Math.round((1 / gm) * 10) / 10 : null;
                    const { bg, border, textColor, label, advice } =
                      gm >= 0.30 ? {
                        bg: "bg-emerald-50", border: "border-emerald-200", textColor: "text-emerald-700",
                        label: "建議積極投放",
                        advice: `毛利充足（${(gm*100).toFixed(0)}%），可配置測試預算。目標 ROAS ≥ ${targetRoas ?? "—"}，CPA 上限 ≤ NT$${maxCpa ?? "—"}`,
                      } : gm >= 0.15 ? {
                        bg: "bg-blue-50", border: "border-blue-200", textColor: "text-blue-700",
                        label: "謹慎投放",
                        advice: `毛利偏低（${(gm*100).toFixed(0)}%），建議小預算測試（日預算 ≤ NT$500）。CPA 上限 ≤ NT$${maxCpa ?? "—"}，密切追蹤 ROAS`,
                      } : gm > 0 ? {
                        bg: "bg-amber-50", border: "border-amber-200", textColor: "text-amber-700",
                        label: "暫緩投放",
                        advice: `毛利太低（${(gm*100).toFixed(0)}%），廣告投報率風險高。建議先優化定價或降低成本後再評估`,
                      } : {
                        bg: "bg-red-50", border: "border-red-200", textColor: "text-red-600",
                        label: "不建議投放",
                        advice: `商品目前為虧損狀態（毛利 ${(gm*100).toFixed(0)}%），投廣告將擴大損失`,
                      };
                    return (
                      <div className={`mt-2 rounded-[10px] px-4 py-3 border ${bg} ${border} space-y-1`}>
                        <div className="flex items-center gap-2">
                          <Zap size={13} className={`shrink-0 ${textColor}`} />
                          <span className={`text-[12px] font-700 ${textColor}`}>廣告投放建議：{label}</span>
                        </div>
                        <p className="text-[12px] text-[var(--text-2)] pl-5">{advice}</p>
                      </div>
                    );
                  })()}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
