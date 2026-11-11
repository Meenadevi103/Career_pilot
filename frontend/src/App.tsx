/**
 * App.tsx — Route configuration for CareerPilot AI
 *
 * Route structure:
 *
 *  PublicRoute (redirects to /dashboard if already logged in)
 *    /login     → Login page
 *    /register  → Register page
 *
 *  ProtectedRoute (redirects to /login if NOT logged in)
 *    AppLayout (sidebar + topbar shell)
 *      /dashboard    → Dashboard page
 *      /applications → Applications tracker
 *
 *  Catch-all → redirect to /dashboard
 *    (ProtectedRoute will then redirect to /login if not authed)
 */

import { Routes, Route, Navigate } from "react-router-dom"
import { ProtectedRoute, PublicRoute } from "@/components/auth/ProtectedRoute"
import { AppLayout } from "@/components/layout/AppLayout"
import { Dashboard } from "@/pages/Dashboard"
import { Applications } from "@/pages/Applications"
import { Login } from "@/pages/Login"
import { Register } from "@/pages/Register"

export function App() {
  return (
    <Routes>
      {/* Public routes — redirect to /dashboard if already authenticated */}
      <Route element={<PublicRoute />}>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Route>

      {/* Protected routes — redirect to /login if NOT authenticated */}
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/applications" element={<Applications />} />
        </Route>
      </Route>

      {/* Any unknown URL → /dashboard (ProtectedRoute handles auth redirect) */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
