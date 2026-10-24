"use client";

import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";
import { apiRequest } from "@/lib/api-client";

type CreatedPrescription = { id: string };

export function PrescriptionBuilder() {
  const { user } = useAuth();
  const [patientId, setPatientId] = useState("");
  const [medication, setMedication] = useState("");
  const [dose, setDose] = useState("");
  const [frequency, setFrequency] = useState("");
  const [status, setStatus] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!user) return;
    setStatus("");
    try {
      const result = await apiRequest<CreatedPrescription>("/prescriptions", user.access_token, {
        method: "POST",
        body: JSON.stringify({
          patient_id: patientId,
          payload: {
            resourceType: "MedicationRequest",
            status: "active",
            intent: "order",
            medication: [{ medication, dose, route: "oral", frequency, refills: 0 }]
          }
        })
      });
      setStatus(`Saved prescription ${result.id}.`);
    } catch (cause) {
      setStatus(cause instanceof Error ? cause.message : "Unable to save prescription");
    }
  }

  return (
    <form onSubmit={submit} className="max-w-2xl space-y-4 rounded-xl border bg-white p-6">
      <label className="block text-sm font-medium">
        Patient ID
        <input required value={patientId} onChange={(event) => setPatientId(event.target.value)} className="mt-1 w-full rounded-md border px-3 py-2" />
      </label>
      <label className="block text-sm font-medium">
        Medication
        <input required value={medication} onChange={(event) => setMedication(event.target.value)} className="mt-1 w-full rounded-md border px-3 py-2" />
      </label>
      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block text-sm font-medium">
          Dose
          <input required value={dose} onChange={(event) => setDose(event.target.value)} className="mt-1 w-full rounded-md border px-3 py-2" placeholder="e.g. 250 mg" />
        </label>
        <label className="block text-sm font-medium">
          Frequency
          <input required value={frequency} onChange={(event) => setFrequency(event.target.value)} className="mt-1 w-full rounded-md border px-3 py-2" placeholder="e.g. twice daily" />
        </label>
      </div>
      <p className="text-xs text-muted-foreground">
        Orders must be reviewed by an authorized clinician. The builder stores a JSON MedicationRequest-style payload.
      </p>
      {status && <p role="status" className="text-sm">{status}</p>}
      <Button>Save prescription</Button>
    </form>
  );
}
