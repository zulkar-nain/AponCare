"use client";

import { FormEvent, useEffect, useState } from "react";
import { AppShell } from "@/components/navigation/app-shell";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";
import { apiRequest } from "@/lib/api-client";

type Patient = {
  id: string;
  full_name: string;
  date_of_birth: string | null;
  phone: string | null;
};

type AssistedSignup = {
  patient: Patient;
  email: string;
  temporary_password: string;
  password_change_required: boolean;
};

export default function PatientsPage() {
  const { user } = useAuth();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [error, setError] = useState("");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [phone, setPhone] = useState("");
  const [busy, setBusy] = useState(false);
  const [createdAccount, setCreatedAccount] = useState<AssistedSignup | null>(null);

  useEffect(() => {
    if (!user) return;
    apiRequest<Patient[]>("/patients", user.access_token)
      .then(setPatients)
      .catch((cause: unknown) => setError(cause instanceof Error ? cause.message : "Unable to load patients"));
  }, [user]);

  async function createPortalAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!user) return;
    setBusy(true);
    setError("");
    setCreatedAccount(null);
    try {
      const result = await apiRequest<AssistedSignup>("/patients/register-portal", user.access_token, {
        method: "POST",
        body: JSON.stringify({
          full_name: fullName,
          email,
          ...(dateOfBirth ? { date_of_birth: dateOfBirth } : {}),
          ...(phone ? { phone } : {})
        })
      });
      setCreatedAccount(result);
      setPatients((current) => [result.patient, ...current]);
      setFullName("");
      setEmail("");
      setDateOfBirth("");
      setPhone("");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to create patient account");
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell>
      <h1 className="mb-5 text-2xl font-bold">Patients</h1>
      {error && <p role="alert" className="mb-4 text-sm text-red-700">{error}</p>}
      {user && ["org_admin", "staff", "super_admin"].includes(user.user_role) && (
        <form
          onSubmit={createPortalAccount}
          className="mb-6 max-w-3xl space-y-4 rounded-xl border bg-white p-5"
        >
          <div>
            <h2 className="text-lg font-semibold">Register a patient with portal access</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Give the patient the temporary password shown after registration. They must change it at first sign-in.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="block text-sm font-medium">
              Full name
              <input
                required
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
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                className="mt-1 w-full rounded-md border px-3 py-2"
              />
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
                value={phone}
                onChange={(event) => setPhone(event.target.value)}
                className="mt-1 w-full rounded-md border px-3 py-2"
              />
            </label>
          </div>
          <Button disabled={busy}>{busy ? "Registering..." : "Register patient"}</Button>
          {createdAccount && (
            <div role="status" className="rounded-md border border-amber-300 bg-amber-50 p-4 text-sm">
              <h3 className="font-semibold">Share these credentials with the patient now</h3>
              <p className="mt-2">Email: <strong>{createdAccount.email}</strong></p>
              <p className="break-all">Temporary password: <strong>{createdAccount.temporary_password}</strong></p>
              <p className="mt-2 text-amber-900">
                This password is displayed only now. The patient must change it after signing in.
              </p>
            </div>
          )}
        </form>
      )}
      <div className="overflow-hidden rounded-lg border bg-white">
        {patients.map((patient) => (
          <article key={patient.id} className="border-b p-4 last:border-0">
            <h2 className="font-medium">{patient.full_name}</h2>
            <p className="text-sm text-muted-foreground">
              {patient.date_of_birth ?? "Date of birth not recorded"} · {patient.phone ?? "No phone"}
            </p>
          </article>
        ))}
        {!error && patients.length === 0 && (
          <p className="p-5 text-sm text-muted-foreground">No patient records found.</p>
        )}
      </div>
    </AppShell>
  );
}
