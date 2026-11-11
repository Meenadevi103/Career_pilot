import React from "react"
import { NavLink } from "react-router-dom"
import {
  LayoutDashboard,
  Briefcase,
  Compass,
  FileText,
  UserCheck,
} from "lucide-react"
import { cn } from "@/lib/utils"

const navigationItems = [
  {
    name: "Dashboard",
    to: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Applications",
    to: "/applications",
    icon: Briefcase,
  },
]

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 border-r bg-card flex flex-col h-screen shrink-0">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b gap-3">
        <div className="p-2 rounded-lg bg-primary text-primary-foreground">
          <Compass className="w-5 h-5" />
        </div>
        <div>
          <h1 className="font-bold text-base tracking-tight leading-none text-foreground">
            CareerPilot AI
          </h1>
          <span className="text-xs text-muted-foreground">Placement & Prep</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4 space-y-1">
        <div className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Student Portal
        </div>
        {navigationItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.name}</span>
            </NavLink>
          )
        })}

        {/* Future Modules Preview */}
        <div className="pt-6 px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          Coming Soon
        </div>
        <div className="space-y-1 opacity-60">
          <div className="flex items-center gap-3 px-3 py-2 text-sm text-muted-foreground">
            <FileText className="w-4 h-4" />
            <span>AI Resume Reviewer</span>
          </div>
          <div className="flex items-center gap-3 px-3 py-2 text-sm text-muted-foreground">
            <UserCheck className="w-4 h-4" />
            <span>Mock AI Interview</span>
          </div>
        </div>
      </nav>

      {/* Footer System Status */}
      <div className="p-4 border-t text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>Foundation v0.1.0</span>
        </div>
      </div>
    </aside>
  )
}
