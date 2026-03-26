"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import {
  LayoutDashboard, BarChart2, BookOpen, FileText, Brain,
  ListChecks, Building2, ShoppingBag, Terminal, CalendarDays,
  MessageSquare, ClipboardCheck, Sun, Bell, Layers, Package,
} from "lucide-react";

// ── Nav structure: grouped by domain ─────────────────────────────────────────
const NAV_GROUPS = [
  {
    label: "指揮",
    items: [
      { href: "/chat",    label: "CEO Console", icon: MessageSquare },
      { href: "/morning", label: "晨報",         icon: Sun },
      { href: "/review",  label: "審核佇列",     icon: ClipboardCheck },
    ],
  },
  {
    label: "內容",
    items: [
      { href: "/",         label: "今日總覽", icon: LayoutDashboard },
      { href: "/picks",    label: "精選清單", icon: ListChecks },
      { href: "/calendar", label: "內容日曆", icon: CalendarDays },
      { href: "/library",  label: "素材庫",   icon: BookOpen },
    ],
  },
  {
    label: "數據",
    items: [
      { href: "/metrics",  label: "績效中心", icon: BarChart2 },
      { href: "/insights", label: "受眾洞察", icon: Brain },
      { href: "/reports",  label: "週報",     icon: FileText },
    ],
  },
  {
    label: "系統",
    items: [
      { href: "/flowlab",   label: "Flow Lab",  icon: Layers },
      { href: "/ecommerce", label: "電商管理",  icon: Package },
      { href: "/office",    label: "AI Office", icon: Building2 },
      { href: "/system",    label: "系統日誌",  icon: Terminal },
    ],
  },
];

const DIVIDER = <span className="w-px h-4 bg-[var(--border)] shrink-0" aria-hidden />;

export default function TopNav() {
  const pathname = usePathname();
  const [healthy, setHealthy] = useState<boolean | null>(null);
  const [scrolled, setScrolled] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);

  // System health check
  useEffect(() => {
    const check = async () => {
      try {
        const r = await fetch("/api/health", { cache: "no-store" });
        setHealthy(r.ok);
      } catch { setHealthy(false); }
    };
    check();
    const iv = setInterval(check, 30_000);
    return () => clearInterval(iv);
  }, []);

  // Scroll shadow
  useEffect(() => {
    const el = document.querySelector("main");
    if (!el) return;
    const onScroll = () => setScrolled(el.scrollTop > 8);
    el.addEventListener("scroll", onScroll);
    return () => el.removeEventListener("scroll", onScroll);
  }, []);

  // Pending badge — review_items only (approval_requests is workflow-internal, not user-facing)
  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch("/api/review-queue/stats", { cache: "no-store" });
        if (res.ok) {
          const s = await res.json();
          setPendingCount(s.pending ?? 0);
        }
      } catch { /* silent */ }
    };
    check();
    const iv = setInterval(check, 20_000);
    return () => clearInterval(iv);
  }, []);

  return (
    <header
      className="fixed top-0 left-0 right-0 z-20 transition-all duration-200"
      style={{
        background: scrolled ? "rgba(250,249,247,0.92)" : "rgba(250,249,247,0.97)",
        backdropFilter: "blur(24px)",
        WebkitBackdropFilter: "blur(24px)",
        borderBottom: scrolled ? "1px solid rgba(0,0,0,0.07)" : "1px solid transparent",
      }}
    >
      <div className="max-w-[1440px] mx-auto px-6 h-[58px] flex items-center gap-5">

        {/* ── Logo ── */}
        <Link href="/" className="flex items-center gap-2.5 shrink-0 group mr-1">
          <div
            className="w-8 h-8 rounded-[10px] flex items-center justify-center shadow-sm"
            style={{ background: "linear-gradient(135deg, #7c5cbf 0%, #9b6bdf 100%)" }}
          >
            <span className="text-white text-[11px] font-black tracking-tight">AC</span>
          </div>
          <span className="text-[15px] font-[700] text-[var(--text-1)] tracking-tight hidden sm:block">
            AntiClaude
          </span>
        </Link>

        {/* ── Nav Groups ── */}
        <nav className="flex items-center gap-1 flex-1 overflow-x-auto no-scrollbar">
          {NAV_GROUPS.map((group, gi) => (
            <div key={group.label} className="flex items-center gap-1 shrink-0">
              {gi > 0 && DIVIDER}
              {/* Group label — only on wider screens */}
              <span className="hidden xl:block text-[10px] font-semibold text-[var(--text-3)] uppercase tracking-[0.15em] px-1.5 select-none">
                {group.label}
              </span>
              {group.items.map(({ href, label, icon: Icon }) => {
                const active = pathname === href || (href !== "/" && pathname.startsWith(href));
                return (
                  <Link
                    key={href}
                    href={href}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-[10px] text-[13px] font-medium transition-all duration-150 shrink-0 whitespace-nowrap ${
                      active
                        ? "bg-[var(--accent-soft)] text-[var(--accent)]"
                        : "text-[var(--text-2)] hover:text-[var(--text-1)] hover:bg-[var(--bg-2)]"
                    }`}
                  >
                    <Icon size={13} />
                    <span className="hidden lg:block">{label}</span>
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        {/* ── Trailing: approval bell + health ── */}
        <div className="flex items-center gap-2 shrink-0">

          {/* Pending approvals bell */}
          <Link
            href="/office"
            className="relative flex items-center justify-center w-8 h-8 rounded-full transition-colors hover:bg-[var(--bg-2)]"
            title={pendingCount > 0 ? `${pendingCount} 個待審核` : "無待審核"}
          >
            <Bell
              size={15}
              className={pendingCount > 0 ? "text-amber-500" : "text-[var(--text-3)]"}
            />
            {pendingCount > 0 && (
              <span
                className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full text-[9px] font-bold text-white flex items-center justify-center"
                style={{ background: "#dc2626" }}
              >
                {pendingCount > 9 ? "9+" : pendingCount}
              </span>
            )}
          </Link>

          {/* System health */}
          <div
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[12px] font-medium"
            style={{
              background: healthy === true ? "rgba(22,163,74,0.08)" : "var(--bg-2)",
              color: healthy === true ? "var(--green)" : "var(--text-3)",
            }}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                healthy === null ? "bg-gray-300 animate-pulse" :
                healthy ? "bg-green-500" : "bg-red-400"
              }`}
            />
            <span className="hidden sm:block">
              {healthy === null ? "連線中" : healthy ? "運行中" : "離線"}
            </span>
          </div>
        </div>

      </div>
    </header>
  );
}
