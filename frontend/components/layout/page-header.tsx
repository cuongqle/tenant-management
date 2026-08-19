import { ReactNode } from "react";

import { Button } from "@/components/ui/button";

type PageHeaderProps = {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  actions?: ReactNode;
};

export function PageHeader({
  title,
  description,
  actionLabel,
  onAction,
  actions,
}: PageHeaderProps) {
  return (
    <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
        <p className="mt-1 text-sm text-slate-500">{description}</p>
      </div>
      {actions ? (
        <div className="flex flex-wrap gap-2">{actions}</div>
      ) : actionLabel && onAction ? (
        <Button size="lg" onClick={onAction}>
          {actionLabel}
        </Button>
      ) : null}
    </div>
  );
}

export function EmptyState({ children }: { children: ReactNode }) {
  return (
    <div className="px-4 py-12 text-center text-sm text-slate-500">
      {children}
    </div>
  );
}
