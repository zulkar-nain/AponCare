import { AppShell } from "@/components/navigation/app-shell";

export default function DashboardPage() {
  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="mt-1 text-muted-foreground">Your organization workspace at a glance.</p>
      </div>
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {[
          ["Patients", "Manage patient records"],
          ["Care encounters", "Review clinical activity"],
          ["Prescriptions", "Create and print medication orders"]
        ].map(([title, description]) => (
          <article key={title} className="rounded-xl border bg-white p-5 shadow-sm">
            <h2 className="font-semibold">{title}</h2>
            <p className="mt-2 text-sm text-muted-foreground">{description}</p>
          </article>
        ))}
      </section>
    </AppShell>
  );
}
