"use client";

import Link from "next/link";

import { Card } from "@/components/ui/card";
import { useAsyncList } from "@/hooks/use-async-list";
import {
  environmentsApi,
  organizationsApi,
  projectsApi,
  usersApi,
} from "@/lib/resources";

export function OverviewStats() {
  const organizations = useAsyncList(organizationsApi.list);
  const users = useAsyncList(usersApi.list);
  const projects = useAsyncList(projectsApi.list);
  const environments = useAsyncList(environmentsApi.list);

  const cards = [
    {
      label: "Organizations",
      value: organizations.items.length,
      loading: organizations.loading,
      href: "/organizations",
      hint: "Tenants in this workspace",
      accent: "from-indigo-500 to-violet-500",
    },
    {
      label: "Users",
      value: users.items.length,
      loading: users.loading,
      href: "/users",
      hint: "People with access",
      accent: "from-fuchsia-500 to-pink-500",
    },
    {
      label: "Projects",
      value: projects.items.length,
      loading: projects.loading,
      href: "/projects",
      hint: "Active workstreams",
      accent: "from-sky-500 to-cyan-500",
    },
    {
      label: "Environments",
      value: environments.items.length,
      loading: environments.loading,
      href: "/environments",
      hint: "Runtime targets",
      accent: "from-emerald-500 to-teal-500",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="overflow-hidden rounded-2xl bg-gradient-to-r from-slate-950 via-indigo-950 to-slate-900 p-6 text-white shadow-lg">
        <p className="text-sm text-indigo-200">Welcome back</p>
        <h2 className="mt-1 text-2xl font-semibold">Your workspace at a glance</h2>
        <p className="mt-2 max-w-xl text-sm text-slate-300">
          Create organizations, manage users, attach projects, and define
          environments from one place.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => (
          <Link key={card.href} href={card.href}>
            <Card className="p-5 transition-all hover:-translate-y-0.5 hover:shadow-md">
              <div className={`mb-4 h-1.5 w-12 rounded-full bg-gradient-to-r ${card.accent}`} />
              <p className="text-sm font-medium text-slate-500">{card.label}</p>
              <p className="mt-3 text-3xl font-semibold text-slate-900">
                {card.loading ? "—" : card.value}
              </p>
              <p className="mt-2 text-xs text-slate-400">{card.hint}</p>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
