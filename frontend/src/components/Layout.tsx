import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { Wrench, Home, Bolt, MessageCircle, CalendarClock } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { checkHealth } from "@/lib/api";

const NAV_ITEMS = [
  { to: "/", label: "Home", icon: Home, end: true },
  { to: "/parts", label: "Part Sourcing", icon: Bolt, end: false },
  { to: "/chat", label: "Quick Chat", icon: MessageCircle, end: false },
  { to: "/assistant", label: "Workday Help", icon: CalendarClock, end: false },
];

export function Layout() {
  const [backendUp, setBackendUp] = useState<boolean | null>(null);

  useEffect(() => {
    checkHealth()
      .then(() => setBackendUp(true))
      .catch(() => setBackendUp(false));
  }, []);

  return (
    <div className="min-h-screen bg-background flex">
      <aside className="w-64 shrink-0 bg-slate-900 text-slate-200 p-4 flex flex-col gap-4">
        <div>
          <h1 className="text-lg font-bold flex items-center gap-2 text-white">
            <Wrench className="h-5 w-5 text-primary" /> Engineer's Workday Assistant
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Part sourcing, quick chat, and workday help — three tools at one workbench.
          </p>
        </div>

        <nav className="flex flex-col gap-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white",
                )
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-auto">
          {backendUp === null ? null : backendUp ? (
            <Badge className="bg-emerald-600 text-white border-transparent hover:bg-emerald-600">
              Backend connected
            </Badge>
          ) : (
            <Badge variant="destructive">Backend unreachable</Badge>
          )}
        </div>
      </aside>

      <main className="flex-1 p-8 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
