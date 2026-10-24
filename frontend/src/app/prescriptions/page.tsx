import { AppShell } from "@/components/navigation/app-shell";
import { PrescriptionBuilder } from "@/components/prescription-builder";

export default function PrescriptionsPage() {
  return (
    <AppShell>
      <h1 className="mb-2 text-2xl font-bold">Prescription builder</h1>
      <p className="mb-5 text-muted-foreground">
        Compose an electronic medication request and print it from its generated PDF endpoint.
      </p>
      <PrescriptionBuilder />
    </AppShell>
  );
}
