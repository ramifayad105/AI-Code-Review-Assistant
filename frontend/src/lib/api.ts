const API_BASE = "http://localhost:8000"

function getToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem("token")
}

async function request(path: string, options: RequestInit = {}) {
  const token = getToken()
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers })

  if (res.status === 401) {
    // Token expired, clear it
    localStorage.removeItem("token")
    window.location.href = "/"
    throw new Error("Unauthorized")
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed: ${res.status}`)
  }

  return res.json()
}

export const api = {
  getUser: () => request("/auth/me"),
  getRepos: () => request("/repos"),
  connectRepo: (fullName: string) =>
    request("/repos/connect", {
      method: "POST",
      body: JSON.stringify({ full_name: fullName }),
    }),
  getReviews: () => request("/reviews"),
  getReview: (id: string) => request(`/reviews/${id}`),
  getStats: () => request("/stats"),
}
