/**
 * AuthContext — global authentication state for CareerPilot AI.
 *
 * How it works (simple explanation):
 *  - On app start, we call GET /api/auth/me using TanStack Query.
 *  - If the backend returns a user object → the user is logged in.
 *  - If it returns 401 → the user is not logged in.
 *  - `login`, `register`, and `logout` call the backend and then
 *    update the React Query cache so every component sees the change
 *    immediately without a full page reload.
 */

import React, { createContext, useContext, useCallback } from "react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { api } from "@/services/api"
import type { UserResponse, LoginRequest, RegisterRequest } from "@/services/api"

// ── Types ──────────────────────────────────────────────────────────────────────

interface AuthContextValue {
  /** The currently authenticated user, or null if not logged in. */
  user: UserResponse | null
  /** True while we are still checking authentication status on page load. */
  isLoading: boolean
  /** Call to log in. Throws ApiError on failure. */
  login: (payload: LoginRequest) => Promise<void>
  /** Call to register. Throws ApiError on failure. */
  register: (payload: RegisterRequest) => Promise<void>
  /** Call to log out. */
  logout: () => Promise<void>
}

// ── Context ────────────────────────────────────────────────────────────────────

const AuthContext = createContext<AuthContextValue | null>(null)

// ── Provider ───────────────────────────────────────────────────────────────────

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient()

  /**
   * The "who am I?" query. Runs once when the app loads.
   * - retry: false → don't retry on 401 (user is just not logged in)
   * - staleTime: 5 min → don't re-fetch on every component mount
   */
  const { data: user = null, isLoading } = useQuery<UserResponse | null>({
    queryKey: ["me"],
    queryFn: async () => {
      try {
        return await api.auth.me()
      } catch {
        // 401 means not authenticated — that's fine, return null
        return null
      }
    },
    retry: false,
    staleTime: 5 * 60 * 1000,
  })

  const login = useCallback(
    async (payload: LoginRequest) => {
      const user = await api.auth.login(payload)
      // Update the cache so components immediately see the logged-in user
      queryClient.setQueryData<UserResponse>(["me"], user)
    },
    [queryClient]
  )

  const register = useCallback(
    async (payload: RegisterRequest) => {
      const user = await api.auth.register(payload)
      queryClient.setQueryData<UserResponse>(["me"], user)
    },
    [queryClient]
  )

  const logout = useCallback(async () => {
    await api.auth.logout()
    // Clear the user from cache immediately
    queryClient.setQueryData(["me"], null)
    // Remove any other cached queries that contain private data
    queryClient.removeQueries({ queryKey: ["me"] })
  }, [queryClient])

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

// ── Hook ───────────────────────────────────────────────────────────────────────

/**
 * useAuth — consume the AuthContext.
 *
 * Usage:
 *   const { user, login, logout } = useAuth()
 */
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error("useAuth must be used inside <AuthProvider>")
  }
  return ctx
}
