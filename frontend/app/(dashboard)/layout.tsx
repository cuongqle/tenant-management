import { AuthGate } from "@/components/layout/auth-gate";
import { Header } from "@/components/layout/header";
import { Sidebar } from "@/components/layout/sidebar";

export default function DashboardGroupLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGate>
      <div className="relative flex min-h-full bg-slate-100">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_rgba(99,102,241,0.12),_transparent_40%),radial-gradient(ellipse_at_bottom_left,_rgba(14,165,233,0.08),_transparent_45%)]" />
        <Sidebar />
        <div className="relative flex min-w-0 flex-1 flex-col">
          <Header />
          <main className="flex-1 p-6">{children}</main>
        </div>
      </div>
    </AuthGate>
  );
}
