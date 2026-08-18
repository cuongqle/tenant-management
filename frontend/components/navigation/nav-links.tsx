"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const links = [
  { href: "/dashboard", label: "Overview" },
  { href: "/organizations", label: "Organizations" },
  { href: "/users", label: "Users" },
  { href: "/projects", label: "Projects" },
  { href: "/environments", label: "Environments" },
  { href: "/settings", label: "Settings" },
];

export function NavLinks() {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-1">
      {links.map((link) => {
        const active =
          pathname === link.href ||
          (link.href !== "/dashboard" && pathname.startsWith(`${link.href}/`));
        return (
          <Link
            key={link.href}
            href={link.href}
            className={cn(
              "rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              active
                ? "bg-white/10 text-white"
                : "text-slate-300 hover:bg-white/5 hover:text-white",
            )}
          >
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}
