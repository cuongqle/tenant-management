export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative flex min-h-full items-center justify-center overflow-hidden bg-slate-950 px-4 py-16">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(99,102,241,0.28),_transparent_55%),radial-gradient(ellipse_at_bottom_right,_rgba(14,165,233,0.18),_transparent_45%)]" />
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.04)_1px,transparent_1px)] bg-[length:48px_48px]" />
      <div className="pointer-events-none absolute -left-24 top-24 h-72 w-72 rounded-full bg-indigo-500/20 blur-3xl" />
      <div className="pointer-events-none absolute -right-16 bottom-10 h-80 w-80 rounded-full bg-cyan-400/10 blur-3xl" />
      <div className="relative z-10 w-full max-w-md">{children}</div>
    </div>
  );
}
