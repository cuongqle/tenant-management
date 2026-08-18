"use client";

import { usePathname, useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { clearAccessToken } from "@/lib/auth";

const titles: Record<string, { title: string; subtitle: string }> = {
  "/dashboard": {
    title: "Overview",
    subtitle: "Workspace snapshot",
  },
  "/organizations": {
    title: "Organizations",
    subtitle: "Tenants and accounts",
  },
  "/users": {
    title: "Users",
    subtitle: "Accounts and access",
  },
  "/projects": {
    title: "Projects",
    subtitle: "Workstreams by organization",
  },
  "/environments": {
    title: "Environments",
    subtitle: "Runtime targets",
  },
  "/settings": {
    title: "Settings",
    subtitle: "Session and preferences",
  },
};

function pageTitle(pathname: string): { title: string; subtitle: string } {
  if (titles[pathname]) {
    return titles[pathname];
  }
  if (pathname.startsWith("/organizations/")) {
    return { title: "Organization", subtitle: "Members and settings" };
  }
  if (pathname.startsWith("/projects/")) {
    return { title: "Project", subtitle: "Environments and settings" };
  }
  return { title: "Tenant Management", subtitle: "Dashboard" };
}

export function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const page = pageTitle(pathname);

  function signOut() {
    clearAccessToken();
    router.push("/login");
  }

  return (
    <header className="flex items-center justify-between border-b border-slate-200/80 bg-white/80 px-6 py-4 backdrop-blur">
      <div>
        <p className="text-xs font-medium uppercase tracking-[0.16em] text-indigo-500">
          {page.subtitle}
        </p>
        <h1 className="text-lg font-semibold text-slate-900">{page.title}</h1>
      </div>
      <Button variant="secondary" size="sm" onClick={signOut}>
        Sign out
      </Button>
    </header>
  );
}
