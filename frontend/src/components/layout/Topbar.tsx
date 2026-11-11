/**
 * Topbar — top navigation bar shown inside the authenticated layout.
 *
 * Shows:
 *  - Page breadcrumb (left side)
 *  - Backend health indicator (green dot = online, red = offline)
 *  - User's name + Logout button when logged in
 *    (no Log In / Sign Up buttons — the user is always authenticated here
 *     because Topbar is only rendered inside ProtectedRoute → AppLayout)
 */

import React from "react"
import { useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { Activity, LogOut, User } from "lucide-react"
import { api } from "@/services/api"
import { useAuth } from "@/context/AuthContext"
import { Button } from "@/components/ui/button"

export const Topbar: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const { data: health, isError } = useQuery({
    queryKey: ["health"],
    queryFn: api.checkHealth,
    refetchInterval: 30_000,
    retry: false,
  })

  const handleLogout = async () => {
    await logout()
    navigate("/login", { replace: true })
  }

  return (
    <header className="h-16 border-b bg-card/60 backdrop-blur-sm px-6 flex items-center justify-between shrink-0">
      {/* Left: breadcrumb */}
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-semibold text-foreground">Student Workspace</h2>
        <span className="text-muted-foreground">/</span>
        <span className="text-xs text-muted-foreground">Career Management</span>
      </div>

      {/* Right: health + user */}
      <div className="flex items-center gap-4">
        {/* Backend health pill */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border bg-background">
          <Activity
            className={`w-3.5 h-3.5 ${
              health?.status === "ok"
                ? "text-emerald-500"
                : isError
                ? "text-destructive"
                : "text-amber-500"
            }`}
          />
          <span className="text-muted-foreground">Backend:</span>
          <span
            className={
              health?.status === "ok"
                ? "text-emerald-600 font-semibold"
                : isError
                ? "text-destructive font-semibold"
                : "text-amber-600"
            }
          >
            {health?.status === "ok" ? "Online" : isError ? "Offline" : "Checking…"}
          </span>
        </div>

        {/* User info + logout */}
        {user && (
          <div className="flex items-center gap-3">
            {/* Avatar circle with initials */}
            <div className="flex items-center gap-2 text-sm">
              <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-semibold text-xs">
                {user.name
                  .split(" ")
                  .map((n) => n[0])
                  .slice(0, 2)
                  .join("")
                  .toUpperCase()}
              </div>
              <span className="font-medium text-foreground hidden sm:block">
                {user.name}
              </span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="gap-1.5 text-muted-foreground hover:text-destructive"
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:block">Logout</span>
            </Button>
          </div>
        )}

        {/* Fallback avatar when user isn't loaded yet */}
        {!user && (
          <div className="w-8 h-8 rounded-full bg-accent border flex items-center justify-center text-muted-foreground">
            <User className="w-4 h-4" />
          </div>
        )}
      </div>
    </header>
  )
}
