"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useAuth, type AuthUser } from "@/lib/auth-context";
import { apiRequest } from "@/lib/api-client";

export default function LoginPage() {
  const [tenantId, setTenantId] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [totpCode, setTotpCode] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { setUser } = useAuth();
  const router = useRouter();

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const user = await apiRequest<AuthUser>("/auth/login", "", {
        method: "POST",
        headers: {},
        body: JSON.stringify({
          tenant_id: tenantId,
          email,
          password,
          ...(totpCode ? { totp_code: totpCode } : {})
        })
      });
      setUser(user);
      router.replace(user.password_change_required ? "/change-password" : "/dashboard");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to sign in");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center p-6">
      <form onSubmit={submit} className="w-full max-w-md space-y-4 rounded-xl border bg-white p-8 shadow-sm">
        <div>
          <h1 className="text-2xl font-bold">Welcome to AponCare</h1>
          <p className="mt-1 text-sm text-muted-foreground">Sign in to your care workspace.</p>
        </div>
        <label className="block text-sm font-medium">
          Tenant ID
          <input
            required
            value={tenantId}
            onChange={(event) => setTenantId(event.target.value)}
            className="mt-1 w-full rounded-md border px-3 py-2"
            placeholder="UUID provided by your organization"
          />
        </label>
        <label className="block text-sm font-medium">
          Email
          <input
            required
            type="email"
            autoComplete="username"
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
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="mt-1 w-full rounded-md border px-3 py-2"
          />
        </label>
        <label className="block text-sm font-medium">
          Authenticator code (if enabled)
          <input
            inputMode="numeric"
            value={totpCode}
            onChange={(event) => setTotpCode(event.target.value)}
            className="mt-1 w-full rounded-md border px-3 py-2"
          />
        </label>
        {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
        <Button className="w-full" disabled={busy}>
          {busy ? "Signing in..." : "Sign in"}
        </Button>
        <p className="text-center text-sm text-muted-foreground">
          New patient?{" "}
          <Link href="/patient-signup" className="font-medium text-primary underline">
            Create a patient account
          </Link>
        </p>
      </form>
    </main>
  );
}
