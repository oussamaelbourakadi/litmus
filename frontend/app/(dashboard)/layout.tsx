import Link from "next/link";
import type { ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <nav className="flex items-center gap-6 border-b border-slate-800 px-6 py-3">
        <Link href="/" className="font-semibold text-brand">
          Litmus
        </Link>
        <Link href="/projects" className="text-sm text-slate-300 transition hover:text-white">
          Projects
        </Link>
      </nav>
      <div className="mx-auto max-w-6xl px-6 py-8">{children}</div>
    </div>
  );
}
