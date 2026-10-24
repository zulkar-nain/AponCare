"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/navigation/app-shell";
import { useAuth } from "@/lib/auth-context";
import { apiRequest } from "@/lib/api-client";

type Patient = {
  id: string;
  full_name: string;
  date_of_birth: string | null;
  phone: string | null;
};

export default function PatientsPage() {
  const { user } = useAuth();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!user) return;
    apiRequest<Patient[]>("/patients", user.access_token)
      .then(setPatients)
      .catch((cause: unknown) => setError(cause instanceof Error ? cause.message : "Unable to load patients"));
  }, [user]);

  return (
    <AppShell>
      <h1 className="mb-5 text-2xl font-bold">Patients</h1>
      {error && <p role="alert" className="mb-4 text-sm text-red-700">{error}</p>}
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
