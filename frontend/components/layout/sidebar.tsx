import Link from "next/link";

import { NavLinks } from "@/components/navigation/nav-links";

export function Sidebar() {
  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-white/10 bg-slate-950 p-5 text-white">
      <Link href="/dashboard" className="mb-8 flex items-center gap-3 px-2">
        <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-400 to-indigo-600 text-sm font-bold shadow-lg shadow-indigo-500/30">
          TM
        </span>
        <span>
          <span className="block text-sm font-semibold">TenantMng</span>
          <span className="block text-xs text-slate-400">Workspace</span>
        </span>
      </Link>
      <p className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-500">
        Manage
      </p>
      <NavLinks />
      <div className="mt-auto rounded-xl border border-white/10 bg-white/5 p-3">
        <p className="text-xs font-medium text-slate-200">Signed in</p>
        <p className="mt-1 truncate text-xs text-slate-400">admin@example.com</p>
      </div>
    </aside>
  );
}
