"use client"

import { useEffect, useState } from "react"

const GITHUB_CLIENT_ID = process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID || ""

export default function Home() {
  const [token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    // Check if we already have a token saved
    const saved = localStorage.getItem("token")
    if (saved) {
      setToken(saved)
      fetchUser(saved)
    }
  }, [])

  async function fetchUser(jwt: string) {
    try {
      const res = await fetch("http://localhost:8000/auth/me", {
        headers: { Authorization: `Bearer ${jwt}` },
      })
      if (res.ok) {
        const data = await res.json()
        setUser(data)
      } else {
        // Token expired or invalid
        localStorage.removeItem("token")
        setToken(null)
      }
    } catch {
      // Backend not reachable
    }
  }

  function handleLogin() {
    const redirectUri = `${window.location.origin}/auth/callback`
    window.location.href =
      `https://github.com/login/oauth/authorize?client_id=${GITHUB_CLIENT_ID}&scope=repo&redirect_uri=${redirectUri}`
  }

  function handleLogout() {
    localStorage.removeItem("token")
    setToken(null)
    setUser(null)
  }

  if (user) {
    return (
      <main className="flex flex-col items-center justify-center min-h-screen gap-6">
        <div className="flex items-center gap-4">
          {user.avatar_url && (
            <img
              src={user.avatar_url}
              alt="avatar"
              className="w-12 h-12 rounded-full"
            />
          )}
          <div>
            <p className="text-lg font-medium">{user.username}</p>
            <p className="text-sm text-gray-400">{user.email || "No email"}</p>
          </div>
        </div>
        <p className="text-green-400">Logged in</p>
        <div className="flex gap-3">
          <a
            href="/repos"
            className="px-4 py-2 bg-white text-black font-medium rounded hover:bg-gray-200 transition"
          >
            Repositories
          </a>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-gray-800 rounded hover:bg-gray-700 transition"
          >
            Logout
          </button>
        </div>
      </main>
    )
  }

  return (
    <main className="flex flex-col items-center justify-center min-h-screen gap-6">
      <h1 className="text-3xl font-bold">AI Code Review</h1>
      <p className="text-gray-400">Automated PR reviews powered by AI</p>
      <button
        onClick={handleLogin}
        className="px-6 py-3 bg-white text-black font-medium rounded-lg hover:bg-gray-200 transition"
      >
        Login with GitHub
      </button>
    </main>
  )
}
