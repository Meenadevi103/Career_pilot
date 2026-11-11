import React from "react"
import ReactDOM from "react-dom/client"
import { BrowserRouter } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { AuthProvider } from "@/context/AuthContext"
import App from "./App"
import "./index.css"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {/*
      QueryClientProvider must be the outermost wrapper because
      AuthProvider uses useQuery internally.
    */}
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {/*
          AuthProvider wraps everything so any component can call useAuth()
          to get the current user, login, or logout.
        */}
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
)
