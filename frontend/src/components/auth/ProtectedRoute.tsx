/**
 * Route guards for CareerPilot AI.
 *
 * ProtectedRoute — if the user is NOT logged in, redirect to /login.
 *                  Renders an <Outlet /> (child route) when authenticated.
 *
 * PublicRoute   — if the user IS already logged in, redirect to /dashboard.
 *                 Used for /login and /register so a logged-in user doesn't
 *                 see the auth pages again.
 */

import { Navigate, Outlet } from "react-router-dom"
import { useAuth } from "@/context/AuthContext"

// ── ProtectedRoute ─────────────────────────────────────────────────────────────

export function ProtectedRoute() {
  const { user, isLoading } = useAuth()

  // While checking /me on page load, show nothing (avoids a flicker)
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  // Not authenticated → send to login
  if (!user) {
    return <Navigate to="/login" replace />
  }

  // Authenticated → render the nested route
  return <Outlet />
}

// ── PublicRoute ────────────────────────────────────────────────────────────────

export function PublicRoute() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  // Already authenticated → redirect to dashboard
  if (user) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}
