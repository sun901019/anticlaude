import type { Metadata } from "next";
import { Noto_Sans_TC } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const notoSansTC = Noto_Sans_TC({
  subsets: ["latin"],
  weight: ["400", "500", "700"],
  variable: "--font-noto",
  display: "swap",
});

export const metadata: Metadata = {
  title: "AntiClaude",
  description: "個人品牌內容自動化系統",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-TW">
      <body className={`${notoSansTC.variable} min-h-screen`} style={{ background: "var(--bg)" }}>
        <Sidebar />
        <main className="ml-[220px] min-h-screen overflow-auto">
          <div className="max-w-[1200px] mx-auto px-8 py-8">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
