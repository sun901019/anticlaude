"use client";
import { BookOpen } from "lucide-react";
import { SH } from "./ecommerce-shared";

export function ManualTab() {
  return (
    <div className="max-w-[780px] space-y-5">

      {/* ── 快速開始 ── */}
      <div className="rounded-[14px] p-6 space-y-3" style={{ background: "var(--surface)" }}>
        <h3 className="text-[15px] font-700 text-[var(--text-1)] flex items-center gap-2">
          <BookOpen size={15} style={{ color: SH.primary }} /> 快速開始
        </h3>
        {[
          { step: "1", title: "新增商品", desc: "在售商品 → 點「新增商品」→ 填 SKU、名稱、進貨成本（人民幣）、境內運費 → 選採購模式（1688 / QQL）→ 提交後立即出現在商品列表" },
          { step: "2", title: "查看建議售價", desc: "點商品列 → 右側 Drawer 開啟 → 「定價決策」tab 查看引流底價、核心定價、毛利定價三段建議" },
          { step: "3", title: "記錄補貨", desc: "點「補貨入庫」→ 選商品、填進貨成本與數量 → 系統即時顯示落地成本、進貨後庫存可撐天數與補貨建議" },
          { step: "4", title: "每週更新銷售", desc: "在售商品 → 右下角點 ↺ → 填售價、7天銷量、廣告花費 → 系統計算毛利率、ROAS、下一步策略" },
          { step: "5", title: "週績效總覽", desc: "週績效表 → 查看所有商品毛利率、ROAS、庫存風險與策略建議" },
        ].map(({ step, title, desc }) => (
          <div key={step} className="flex gap-4 py-2 border-b border-[var(--border)] last:border-0">
            <span className="w-6 h-6 rounded-full text-[11px] font-700 flex items-center justify-center shrink-0 mt-0.5" style={{ background: SH.light, color: SH.primary }}>{step}</span>
            <div>
              <div className="text-[13px] font-700 text-[var(--text-1)]">{title}</div>
              <div className="text-[12px] text-[var(--text-3)] mt-0.5 leading-relaxed">{desc}</div>
            </div>
          </div>
        ))}
      </div>

      {/* ── 商品角色定義 ── */}
      <div className="rounded-[14px] p-6 space-y-3" style={{ background: "var(--surface)" }}>
        <h3 className="text-[15px] font-700 text-[var(--text-1)]">商品角色定義</h3>
        <p className="text-[12px] text-[var(--text-3)]">系統根據毛利率自動判斷角色，也可在商品 Drawer 手動覆蓋。</p>
        {[
          { role: "引流款", badge: "bg-blue-50 text-blue-700",   threshold: "毛利 ≥ 25%", desc: "低價切入帶流量，用廣告搶曝光" },
          { role: "主力款", badge: "bg-violet-50 text-violet-700", threshold: "毛利 ≥ 40%", desc: "穩定出貨，撐起每月營收基本盤" },
          { role: "毛利款", badge: "bg-emerald-50 text-emerald-700", threshold: "毛利 ≥ 55%", desc: "高毛利款，以品質/差異化維持溢價" },
          { role: "不適合", badge: "bg-red-50 text-red-600",     threshold: "毛利 < 25%", desc: "目前定價下虧損或接近保本，需重新評估" },
        ].map(row => (
          <div key={row.role} className="flex items-start gap-4 py-2.5 border-b border-[var(--border)] last:border-0">
            <span className={`text-[12px] px-2.5 py-1 rounded-full font-600 ${row.badge} w-[68px] text-center shrink-0 mt-0.5`}>{row.role}</span>
            <div className="flex-1">
              <div className="text-[13px] font-700 text-[var(--text-1)]">{row.threshold}</div>
              <div className="text-[12px] text-[var(--text-3)] mt-0.5">{row.desc}</div>
            </div>
          </div>
        ))}
      </div>

      {/* ── 定價邏輯 ── */}
      <div className="rounded-[14px] p-6 space-y-3" style={{ background: "var(--surface)" }}>
        <h3 className="text-[15px] font-700 text-[var(--text-1)]">定價邏輯</h3>
        <p className="text-[12px] text-[var(--text-3)]">系統同時計算三個建議售價，讓你依策略選擇。</p>
        <div className="space-y-3 text-[13px]">
          {[
            { label: "引流底價", formula: "落地成本 ÷ (1 - 引流毛利門檻 - 平台費)，適合引流活動或首批測試" },
            { label: "核心定價", formula: "落地成本 ÷ (1 - 主力毛利門檻 - 平台費)，日常穩定銷售定價" },
            { label: "毛利定價", formula: "落地成本 ÷ (1 - 毛利門檻 - 平台費)，追求高毛利時使用" },
            { label: "毛利率估算", formula: "(售價 - 落地成本 - 平台費) ÷ 售價" },
            { label: "ROAS", formula: "7天營收 ÷ 廣告花費（無廣告時顯示 —）" },
          ].map(({ label, formula }) => (
            <div key={label} className="flex gap-3 py-2 border-b border-[var(--border)] last:border-0">
              <span className="font-700 w-[90px] shrink-0" style={{ color: SH.primary }}>{label}</span>
              <span className="text-[var(--text-3)] leading-relaxed">{formula}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── 採購與進貨 ── */}
      <div className="rounded-[14px] p-6 space-y-3" style={{ background: "var(--surface)" }}>
        <h3 className="text-[15px] font-700 text-[var(--text-1)]">採購與進貨</h3>
        <p className="text-[12px] text-[var(--text-3)]">系統支援兩種採購模式，落地成本計算方式不同。</p>
        {[
          { mode: "1688 直採", desc: "商品成本（人民幣）+ 境內運費，乘以匯率換算台幣，再加跨境集運費、包材費。" },
          { mode: "QQL 代購", desc: "（成本 + 境內運）× QQL 匯率 × (1 + 服務費) 得到採購成本，再加 max(實重, 體積重) × 海快費率。" },
        ].map(row => (
          <div key={row.mode} className="flex gap-4 py-2.5 border-b border-[var(--border)] last:border-0">
            <span className="text-[12px] font-700 shrink-0 pt-0.5 w-[80px]" style={{ color: SH.primary }}>{row.mode}</span>
            <div className="text-[12px] text-[var(--text-3)] leading-relaxed">{row.desc}</div>
          </div>
        ))}
        <div className="text-[12px] text-[var(--text-3)] mt-2 pt-2 border-t border-[var(--border)]">
          <span className="font-600 text-[var(--text-2)]">體積重：</span>長(cm) × 寬 × 高 ÷ 6000。若體積重 &gt; 實重，以體積重計費。
        </div>
      </div>

      {/* ── 績效判讀 ── */}
      <div className="rounded-[14px] p-6 space-y-3" style={{ background: "var(--surface)" }}>
        <h3 className="text-[15px] font-700 text-[var(--text-1)]">績效判讀與補貨決策</h3>
        {[
          { label: "放大廣告", cond: "毛利率 ≥ 主力門檻 且 ROAS ≥ 2", desc: "繼續跑廣告，考慮調高預算" },
          { label: "補貨優先", cond: "庫存 ≤ 7 天可撐", desc: "庫存偏低，立即安排進貨避免斷貨" },
          { label: "調整定價", cond: "毛利偏低但仍在銷", desc: "試調高售價，或重新評估採購成本" },
          { label: "設定售價", cond: "尚未設定目標售價", desc: "先到商品 Drawer 設定目標售價再做決策" },
          { label: "停售評估", cond: "毛利率持續為負", desc: "確認成本結構，決定是否下架或改價" },
        ].map(row => (
          <div key={row.label} className="flex items-start gap-4 py-2.5 border-b border-[var(--border)] last:border-0">
            <span className="text-[11px] px-2 py-0.5 rounded-full font-600 shrink-0 mt-0.5" style={{ background: SH.light, color: SH.primary }}>{row.label}</span>
            <div>
              <div className="text-[12px] font-600 text-[var(--text-2)]">{row.cond}</div>
              <div className="text-[12px] text-[var(--text-3)] mt-0.5">{row.desc}</div>
            </div>
          </div>
        ))}
      </div>

      {/* ── 蝦皮費率術語 ── */}
      <div className="rounded-[14px] p-6 space-y-3" style={{ background: "var(--surface)" }}>
        <h3 className="text-[15px] font-700 text-[var(--text-1)]">蝦皮費率術語</h3>
        <div className="space-y-0 text-[13px]">
          {[
            { term: "佣金",        en: "Commission",         desc: "蝦皮對每筆交易抽的基本費率（2026 年 3%）" },
            { term: "金流費",      en: "Transaction Fee",    desc: "線上支付手續費，約 2%" },
            { term: "FSS",         en: "Free Shipping",      desc: "免運活動費率，分普通 / 加碼兩段" },
            { term: "CCB",         en: "Coin Cashback",      desc: "蝦皮幣返現計畫，分基礎 / 加碼 / 超加碼" },
            { term: "促銷日",      en: "Promo Day",          desc: "雙日活動（如 11/11），平台另收額外費率" },
            { term: "備貨懲罰",    en: "Long-prep Penalty",  desc: "備貨天數過長（通常 > 3 天）加收罰款費率" },
          ].map(({ term, en, desc }) => (
            <div key={term} className="flex gap-3 py-2.5 border-b border-[var(--border)] last:border-0 items-start">
              <div className="w-[80px] shrink-0">
                <div className="font-700" style={{ color: SH.primary }}>{term}</div>
                <div className="text-[10px] text-[var(--text-3)]">{en}</div>
              </div>
              <span className="text-[var(--text-3)] leading-relaxed">{desc}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── FAQ ── */}
      <div className="rounded-[14px] p-6 space-y-3" style={{ background: "var(--surface)" }}>
        <h3 className="text-[15px] font-700 text-[var(--text-1)]">常見問題 FAQ</h3>
        {[
          { q: "建議售價跟我填的目標售價不一樣，要聽誰的？", a: "建議售價是系統依成本和門檻算出的最低健康價；目標售價是你希望上架的價格。兩者可以不同，但若目標售價低於引流底價，系統會警示毛利不足。" },
          { q: "我換了 Settings 裡的費率，Drawer 的建議售價有更新嗎？", a: "有，Settings 費率是全域來源，Drawer 每次開啟時都會重新計算，反映最新設定。" },
          { q: "補貨入庫的落地成本和商品 Drawer 裡顯示的落地成本不一樣？", a: "補貨入庫使用這次進貨的新成本計算；Drawer 使用商品表的現有成本。若這批進貨成本不同，請在 Drawer 更新後再對比。" },
          { q: "QQL 體積重怎麼填？", a: "在新增商品或商品 Drawer 的成本物流區，填入長/寬/高（公分）即可。系統自動計算體積重（L×W×H÷6000）並與實重取大值計費。" },
        ].map(({ q, a }) => (
          <div key={q} className="py-3 border-b border-[var(--border)] last:border-0">
            <div className="text-[13px] font-700 text-[var(--text-1)] mb-1.5">{q}</div>
            <div className="text-[12px] text-[var(--text-3)] leading-relaxed">{a}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
