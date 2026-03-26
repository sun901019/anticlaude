"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { checkBackendHealth, fetchReviewStats } from "@/lib/api";
import {
  LayoutDashboard, BarChart2, BookOpen, FileText, Brain,
  ListChecks, Building2, ShoppingBag, Terminal, CalendarDays,
  MessageSquare, ClipboardCheck, Sun, Bell, Layers, Package, PenTool,
} from "lucide-react";

const NAV_GROUPS = [
  {
    label: "指揮",
    items: [
      { href: "/chat",    label: "CEO Console", icon: MessageSquare },
      { href: "/morning", label: "晨報",         icon: Sun },
      { href: "/review",  label: "審核佇列",     icon: ClipboardCheck, badge: true },
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
      { href: "/figma",     label: "Figma",     icon: PenTool },
      { href: "/office",    label: "AI Office", icon: Building2 },
      { href: "/system",    label: "系統日誌",  icon: Terminal },
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [healthy, setHealthy] = useState<boolean | null>(null);
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    const check = async () => { setHealthy(await checkBackendHealth()); };
    check();
    const iv = setInterval(check, 30_000);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    const check = async () => {
      try {
        const stats = await fetchReviewStats().catch(() => ({ pending: 0 }));
        setPendingCount(stats.pending ?? 0);
      } catch { /* silent */ }
    };
    check();
    const iv = setInterval(check, 20_000);
    return () => clearInterval(iv);
  }, []);

  return (
    <aside className="fixed left-0 top-0 h-full w-[220px] flex flex-col z-20 bg-white border-r border-[#ede8df]">
      {/* Logo */}
      <div className="px-5 h-[60px] flex items-center gap-3 border-b border-[#ede8df] shrink-0">
        <div
          className="w-8 h-8 rounded-[10px] flex items-center justify-center shrink-0"
          style={{ background: "linear-gradient(135deg, #7c5cbf 0%, #9b6bdf 100%)" }}
        >
          <span className="text-white text-[11px] font-black tracking-tight">AC</span>
        </div>
        <div>
          <div className="text-[14px] font-[700] text-[#1c1917] tracking-tight leading-tight">AntiClaude</div>
          <div className="text-[11px] text-[#a8a29e] leading-tight">@sunlee._.yabg</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-3 space-y-4">
        {NAV_GROUPS.map((group) => (
          <div key={group.label}>
            <p className="px-2 mb-1 text-[10px] font-semibold text-[#a8a29e] uppercase tracking-[0.12em]">
              {group.label}
            </p>
            <div className="space-y-0.5">
              {group.items.map(({ href, label, icon: Icon, badge }: any) => {
                const active = pathname === href || (href !== "/" && pathname.startsWith(href));
                return (
                  <Link
                    key={href}
                    href={href}
                    className={`group flex items-center justify-between px-2.5 py-2 rounded-lg text-[13px] font-medium transition-all duration-150 ${
                      active
                        ? "bg-[#f0ebfa] text-[#7c5cbf]"
                        : "text-[#78716c] hover:text-[#1c1917] hover:bg-[#f5f2ec]"
                    }`}
                  >
                    <span className="flex items-center gap-2.5">
                      <Icon
                        size={14}
                        className={active ? "text-[#7c5cbf]" : "text-[#a8a29e] group-hover:text-[#78716c]"}
                      />
                      {label}
                    </span>
                    {badge && pendingCount > 0 && (
                      <span className="min-w-[18px] h-[18px] px-1 rounded-full bg-red-500 text-white text-[10px] font-bold flex items-center justify-center">
                        {pendingCount > 99 ? "99+" : pendingCount}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-[#ede8df] shrink-0 space-y-2">
        {/* Bell shortcut */}
        <Link
          href="/review"
          className="flex items-center justify-between w-full px-2.5 py-2 rounded-lg hover:bg-[#f5f2ec] transition-colors group"
        >
          <span className="flex items-center gap-2.5 text-[13px] font-medium text-[#78716c] group-hover:text-[#1c1917]">
            <Bell size={14} className={pendingCount > 0 ? "text-amber-500" : "text-[#a8a29e] group-hover:text-[#78716c]"} />
            待審核
          </span>
          {pendingCount > 0 ? (
            <span className="text-[12px] font-semibold text-amber-600">{pendingCount}</span>
          ) : (
            <span className="text-[12px] text-[#a8a29e]">—</span>
          )}
        </Link>

        {/* Health */}
        <div className="flex items-center gap-2 px-2.5 py-1.5">
          <span className={`w-2 h-2 rounded-full shrink-0 ${
            healthy === null ? "bg-gray-300 animate-pulse" :
            healthy ? "bg-emerald-500" : "bg-red-400"
          }`} />
          <span className="text-[12px] text-[#a8a29e]">
            {healthy === null ? "連線中" : healthy ? "系統運行中" : "後端離線"}
          </span>
        </div>
      </div>
    </aside>
  );
}
