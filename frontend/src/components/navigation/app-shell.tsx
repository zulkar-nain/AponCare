"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Sidebar } from "@/components/navigation/sidebar";
import { Button } from "@/components/ui/button";
import { apiRequest } from "@/lib/api-client";
import { useAuth } from "@/lib/auth-context";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, setUser } = useAuth();
  const router = useRouter();
  const [logoutError, setLogoutError] = useState("");

  useEffect(() => {
    if (user?.password_change_required) {
      router.replace("/change-password");
    }
  }, [router, user]);

  if (user?.password_change_required) {
    return null;
  }

  if (!user) {
    return (
      <main className="grid min-h-screen place-items-center p-6">
        <section className="max-w-md rounded-xl border bg-white p-8 text-center shadow-sm">
          <h1 className="text-xl font-semibold">Sign in to AponCare</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Your secure session is not available in this browser tab.
          </p>
          <Button className="mt-5" onClick={() => router.replace("/login")}>
            Continue to login
          </Button>
        </section>
      </main>
    );
  }

  return (
    <div className="min-h-screen md:flex">
      <Sidebar role={user.user_role} />
      <div className="min-w-0 flex-1">
        <header className="flex items-center justify-between border-b bg-white px-6 py-4">
          <div>
            <p className="font-semibold">{user.tenant_name}</p>
            <p className="text-xs capitalize text-muted-foreground">
              {user.user_name} · {user.user_role.replaceAll("_", " ")}
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={async () => {
              if (!user) return;
              setLogoutError("");
              try {
                await apiRequest<{ logged_out: boolean }>("/auth/logout", user.access_token, {
                  method: "POST"
                });
                setUser(null);
                router.replace("/login");
              } catch (cause) {
                setLogoutError(
                  cause instanceof Error ? cause.message : "Unable to end the session"
                );
              }
            }}
          >
            Sign out
          </Button>
        </header>
        {logoutError && (
          <p role="alert" className="px-6 pt-4 text-sm text-red-700">{logoutError}</p>
        )}
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
