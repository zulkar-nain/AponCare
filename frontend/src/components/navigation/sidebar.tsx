"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, ClipboardPlus, LayoutDashboard, Users } from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["all"] },
  {
    href: "/patients",
    label: "Patients",
    icon: Users,
    roles: ["super_admin", "org_admin", "staff", "medical_team", "patient_portal"]
  },
  {
    href: "/prescriptions",
    label: "Prescriptions",
    icon: ClipboardPlus,
    roles: ["super_admin", "org_admin", "staff", "medical_team", "patient_portal"]
  }
];

export function Sidebar({ role }: { role: string }) {
  const pathname = usePathname();
  const items = navigation.filter((item) => item.roles.includes("all") || item.roles.includes(role));

  return (
    <aside className="w-full border-b border-border bg-white p-4 md:min-h-screen md:w-64 md:border-b-0 md:border-r">
      <Link href="/dashboard" className="mb-6 flex items-center gap-2 font-bold text-primary">
        <Activity size={22} /> AponCare
      </Link>
      <nav className="flex gap-2 md:flex-col">
        {items.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm hover:bg-muted",
              pathname === href && "bg-muted font-semibold text-primary"
            )}
          >
            <Icon size={18} />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
