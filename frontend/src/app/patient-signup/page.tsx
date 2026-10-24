"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { apiRequest } from "@/lib/api-client";
import { useAuth, type AuthUser } from "@/lib/auth-context";

export default function PatientSignupPage() {
  const [tenantId, setTenantId] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [phone, setPhone] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { setUser } = useAuth();
  const router = useRouter();

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const user = await apiRequest<AuthUser>("/auth/patient-signup", "", {
        method: "POST",
        body: JSON.stringify({
          tenant_id: tenantId,
          full_name: fullName,
          email,
          password,
          ...(dateOfBirth ? { date_of_birth: dateOfBirth } : {}),
          ...(phone ? { phone } : {})
        })
      });
      setUser(user);
      router.replace("/dashboard");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to create patient account");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center p-6">
      <form
        onSubmit={submit}
        className="w-full max-w-lg space-y-4 rounded-xl border bg-white p-8 shadow-sm"
      >
        <div>
          <h1 className="text-2xl font-bold">Create your patient account</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Enter the organization ID provided by your clinic.
          </p>
        </div>
        <label className="block text-sm font-medium">
          Organization ID
          <input
            required
            value={tenantId}
            onChange={(event) => setTenantId(event.target.value)}
            className="mt-1 w-full rounded-md border px-3 py-2"
            placeholder="UUID provided by your clinic"
          />
        </label>
        <label className="block text-sm font-medium">
          Full name
          <input
            required
            autoComplete="name"
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
            className="mt-1 w-full rounded-md border px-3 py-2"
          />
        </label>
        <label className="block text-sm font-medium">
          Email
          <input
            required
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="mt-1 w-full rounded-md border px-3 py-2"
          />
        </label>
        <label className="block text-sm font-medium">
          Password
          <input
            required
            type="password"
            minLength={12}
            autoComplete="new-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 w-full rounded-md border px-3 py-2"
          />
          <span className="mt-1 block text-xs text-muted-foreground">
            Use at least 12 characters.
          </span>
        </label>
        <label className="block text-sm font-medium">
          Date of birth (optional)
          <input
            type="date"
            value={dateOfBirth}
            onChange={(event) => setDateOfBirth(event.target.value)}
            className="mt-1 w-full rounded-md border px-3 py-2"
          />
        </label>
        <label className="block text-sm font-medium">
          Phone (optional)
          <input
            type="tel"
            autoComplete="tel"
            value={phone}
            onChange={(event) => setPhone(event.target.value)}
            className="mt-1 w-full rounded-md border px-3 py-2"
          />
        </label>
        {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
        <Button className="w-full" disabled={busy}>
          {busy ? "Creating account..." : "Create patient account"}
        </Button>
        <p className="text-center text-sm text-muted-foreground">
          Already registered?{" "}
          <Link href="/login" className="font-medium text-primary underline">
            Sign in
          </Link>
        </p>
      </form>
    </main>
  );
}
