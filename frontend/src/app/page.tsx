import Link from "next/link";
import {
  Activity,
  ArrowRight,
  CalendarDays,
  ClipboardList,
  HeartPulse,
  LockKeyhole,
  Stethoscope,
  UsersRound
} from "lucide-react";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <main className="min-h-screen overflow-hidden bg-white">
      <header className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-6 py-5 lg:px-8">
        <Link href="/" className="flex items-center gap-2.5" aria-label="AponCare home">
          <span className="grid size-10 place-items-center rounded-xl bg-primary text-white">
            <HeartPulse size={22} strokeWidth={2.2} />
          </span>
          <span className="text-xl font-semibold tracking-tight">aponcare</span>
        </Link>
        <nav className="flex items-center gap-3">
          <Link
            href="/patient-signup"
            className="hidden px-3 py-2 text-sm font-medium text-slate-600 transition hover:text-slate-950 sm:inline-flex"
          >
            Patient sign up
          </Link>
          <Button asChild variant="outline" size="sm">
            <Link href="/login">Sign in</Link>
          </Button>
        </nav>
      </header>

      <section className="relative mx-auto grid max-w-7xl items-center gap-14 px-6 pb-20 pt-12 sm:pt-16 lg:grid-cols-[1fr_0.95fr] lg:gap-10 lg:px-8 lg:pb-28 lg:pt-20">
        <div className="relative z-10 max-w-2xl">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-emerald-100 bg-emerald-50 px-3.5 py-1.5 text-sm font-medium text-emerald-800">
            <span className="size-1.5 rounded-full bg-emerald-600" />
            A calmer way to coordinate care
          </div>
          <h1 className="text-5xl font-semibold leading-[1.08] tracking-tight text-slate-950 sm:text-6xl lg:text-[4.35rem]">
            Better organized care
            <span className="block text-primary">starts here.</span>
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-8 text-slate-600">
            AponCare brings patient records, care encounters, and prescriptions into one
            clear workspace—so care teams can spend less time chasing information and
            more time focused on people.
          </p>
          <div className="mt-9 flex flex-col gap-3 sm:flex-row">
            <Button asChild size="lg" className="gap-2 shadow-sm">
              <Link href="/login">
                Open your workspace <ArrowRight size={17} />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/patient-signup">Create a patient account</Link>
            </Button>
          </div>
          <div className="mt-8 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-slate-500">
            <span className="inline-flex items-center gap-2">
              <LockKeyhole size={15} className="text-primary" />
              Organization-aware access
            </span>
            <span className="hidden size-1 rounded-full bg-slate-300 sm:block" />
            <span>Designed for care teams and patients</span>
          </div>
        </div>

        <div className="relative mx-auto w-full max-w-xl lg:ml-auto">
          <div className="absolute -right-12 -top-10 size-56 rounded-full bg-emerald-100/70 blur-3xl" />
          <div className="absolute -bottom-12 -left-8 size-48 rounded-full bg-teal-100/70 blur-3xl" />
          <div className="relative rounded-2xl border border-slate-200 bg-white p-3 shadow-[0_30px_80px_-35px_rgba(15,60,49,0.32)] sm:p-4">
            <div className="overflow-hidden rounded-xl border border-slate-100 bg-slate-50">
              <div className="flex items-center justify-between border-b border-slate-200 bg-white px-5 py-4">
                <div>
                  <p className="text-xs font-medium uppercase tracking-[0.14em] text-slate-400">
                    Care workspace
                  </p>
                  <p className="mt-1 font-semibold text-slate-900">Good morning, team</p>
                </div>
                <div className="grid size-9 place-items-center rounded-full bg-emerald-50 text-primary">
                  <Activity size={18} />
                </div>
              </div>
              <div className="grid gap-3 p-4 sm:grid-cols-2 sm:p-5">
                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <div className="flex items-center justify-between">
                    <span className="grid size-9 place-items-center rounded-lg bg-emerald-50 text-primary">
                      <UsersRound size={18} />
                    </span>
                    <span className="rounded-full bg-emerald-50 px-2 py-1 text-[11px] font-medium text-emerald-700">
                      Records
                    </span>
                  </div>
                  <p className="mt-5 text-sm text-slate-500">Patient profiles</p>
                  <p className="mt-1 text-xl font-semibold tracking-tight text-slate-900">
                    All in one place
                  </p>
                </div>
                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <div className="flex items-center justify-between">
                    <span className="grid size-9 place-items-center rounded-lg bg-sky-50 text-sky-700">
                      <CalendarDays size={18} />
                    </span>
                    <span className="rounded-full bg-sky-50 px-2 py-1 text-[11px] font-medium text-sky-700">
                      Encounters
                    </span>
                  </div>
                  <p className="mt-5 text-sm text-slate-500">Care, connected</p>
                  <p className="mt-1 text-xl font-semibold tracking-tight text-slate-900">
                    Context for every visit
                  </p>
                </div>
                <div className="rounded-xl border border-slate-200 bg-white p-4 sm:col-span-2">
                  <div className="flex items-center gap-3">
                    <span className="grid size-10 place-items-center rounded-lg bg-violet-50 text-violet-700">
                      <ClipboardList size={19} />
                    </span>
                    <div>
                      <p className="text-sm font-semibold text-slate-900">A more connected workflow</p>
                      <p className="mt-0.5 text-xs text-slate-500">
                        Patient records · Clinical encounters · Prescriptions
                      </p>
                    </div>
                    <ArrowRight size={17} className="ml-auto text-slate-400" />
                  </div>
                  <div className="mt-4 flex items-center gap-2">
                    <div className="h-1.5 flex-1 rounded-full bg-emerald-100">
                      <div className="h-full w-3/4 rounded-full bg-primary" />
                    </div>
                    <span className="text-[11px] text-slate-400">One workspace</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2 border-t border-slate-200 bg-white px-5 py-3 text-xs text-slate-500">
                <Stethoscope size={15} className="text-primary" />
                Built around the people behind every care journey
              </div>
            </div>
          </div>
          <div className="absolute -left-5 top-1/2 hidden -translate-y-1/2 items-center gap-3 rounded-xl border border-slate-100 bg-white px-4 py-3 shadow-lg sm:flex">
            <span className="grid size-9 place-items-center rounded-full bg-emerald-50 text-primary">
              <HeartPulse size={18} />
            </span>
            <span>
              <span className="block text-sm font-semibold text-slate-900">Care, coordinated</span>
              <span className="mt-0.5 block text-xs text-slate-500">A shared view for your team</span>
            </span>
          </div>
        </div>
      </section>

      <section className="border-y border-slate-100 bg-slate-50/70">
        <div className="mx-auto grid max-w-7xl gap-10 px-6 py-16 lg:grid-cols-[0.75fr_1.25fr] lg:items-center lg:px-8 lg:py-20">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.16em] text-primary">
              One connected workspace
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
              The details of care, brought together.
            </h2>
          </div>
          <div className="grid gap-7 sm:grid-cols-3">
            <article>
              <UsersRound size={21} className="text-primary" />
              <h3 className="mt-4 font-semibold text-slate-900">Patient records</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Keep essential patient information accessible to the right people.
              </p>
            </article>
            <article>
              <CalendarDays size={21} className="text-primary" />
              <h3 className="mt-4 font-semibold text-slate-900">Care encounters</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Give teams a clearer view of clinical visits and ongoing care.
              </p>
            </article>
            <article>
              <ClipboardList size={21} className="text-primary" />
              <h3 className="mt-4 font-semibold text-slate-900">Prescriptions</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                Create and review prescription records in the same workspace.
              </p>
            </article>
          </div>
        </div>
      </section>

      <section className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-16 sm:flex-row sm:items-center sm:justify-between lg:px-8 lg:py-20">
        <div className="max-w-2xl">
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-primary">
            Your care, your account
          </p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
            A simpler way to stay connected with your clinic.
          </h2>
          <p className="mt-3 leading-7 text-slate-600">
            Patients can create an account using the organization ID shared by their clinic,
            or get help registering at the front desk.
          </p>
        </div>
        <Button asChild size="lg" variant="outline" className="shrink-0 gap-2">
          <Link href="/patient-signup">
            Patient sign up <ArrowRight size={17} />
          </Link>
        </Button>
      </section>

      <footer className="border-t border-slate-100">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-6 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between lg:px-8">
          <Link href="/" className="flex items-center gap-2 font-semibold text-slate-800">
            <HeartPulse size={18} className="text-primary" />
            aponcare
          </Link>
          <p>Thoughtful tools for connected care.</p>
          <div className="flex gap-5">
            <Link href="/login" className="transition hover:text-primary">Sign in</Link>
            <Link href="/patient-signup" className="transition hover:text-primary">Patient sign up</Link>
          </div>
        </div>
      </footer>
    </main>
  );
}
