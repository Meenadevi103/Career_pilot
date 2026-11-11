/**
 * Centralized API Client for CareerPilot AI
 *
 * Rules enforced here:
 *  - Single source of truth for the backend URL (from VITE_API_URL env var).
 *  - credentials: "include" on every request so the browser sends the
 *    httpOnly cookie automatically (Rule 5 — tokens go in httpOnly cookies).
 *  - Standardized error parsing: server detail field → human-readable message.
 *
 * Usage:
 *   import { api } from "@/services/api"
 *   const user = await api.auth.me()
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

// ── Shared types ───────────────────────────────────────────────────────────────

export interface ApiError {
  status: number
  message: string
  details?: unknown
}

export interface HealthStatus {
  status: string
  database: string
}

/** Mirrors the backend UserResponse Pydantic schema. */
export interface UserResponse {
  id: string
  name: string
  email: string
  role: "student" | "coordinator" | "admin"
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  name: string
  email: string
  password: string
}

// ── Core fetch wrapper ─────────────────────────────────────────────────────────

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    credentials: "include", // Always send/receive httpOnly cookies
  })

  if (!response.ok) {
    let errorMessage = `HTTP error ${response.status}`
    let errorDetails: unknown = null
    try {
      const body = await response.json()
      // FastAPI uses `detail` for error messages
      errorMessage = body.detail || body.message || errorMessage
      errorDetails = body
    } catch {
      // Non-JSON error body — keep the default message
    }
    const err: ApiError = { status: response.status, message: errorMessage, details: errorDetails }
    throw err
  }

  if (response.status === 204) {
    return {} as T
  }

  return response.json() as Promise<T>
}

// ── API surface ────────────────────────────────────────────────────────────────

export const api = {
  // Generic HTTP verbs (used by future feature modules)
  get: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: "GET" }),

  post: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: "POST",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),

  put: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    request<T>(endpoint, {
      ...options,
      method: "PUT",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(endpoint: string, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: "DELETE" }),

  // ── Health check ─────────────────────────────────────────────────────────────
  checkHealth: () => request<HealthStatus>("/health"),

  // ── Authentication ───────────────────────────────────────────────────────────
  auth: {
    /**
     * GET /api/auth/me
     * Returns the currently authenticated user.
     * Throws ApiError (status 401) if not logged in.
     */
    me: () => request<UserResponse>("/api/auth/me"),

    /**
     * POST /api/auth/login
     * Sets httpOnly access_token cookie on success.
     * Throws ApiError (status 400) for invalid credentials.
     */
    login: (payload: LoginRequest) =>
      request<UserResponse>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify(payload),
      }),

    /**
     * POST /api/auth/register
     * Creates a new account and sets the cookie.
     * Throws ApiError (status 400) for duplicate email, 422 for validation.
     */
    register: (payload: RegisterRequest) =>
      request<UserResponse>("/api/auth/register", {
        method: "POST",
        body: JSON.stringify(payload),
      }),

    /**
     * POST /api/auth/logout
     * Clears the httpOnly cookie on the server.
     */
    logout: () =>
      request<{ message: string }>("/api/auth/logout", { method: "POST" }),
  },
}
