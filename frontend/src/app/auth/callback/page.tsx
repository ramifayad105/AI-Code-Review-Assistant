"use client"

import { Suspense, useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"

function CallbackHandler() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [error, setError] = useState("")

  useEffect(() => {
    const code = searchParams.get("code")
    if (!code) {
      setError("No code received from GitHub")
      return
    }
    exchangeCode(code)
  }, [searchParams])

  async function exchangeCode(code: string) {
    try {
      const res = await fetch("http://localhost:8000/auth/github", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      })

      if (!res.ok) {
        setError("Login failed. Try again.")
        return
      }

      const data = await res.json()
      localStorage.setItem("token", data.access_token)
      router.push("/")
    } catch {
      setError("Could not reach backend")
    }
  }

  if (error) {
    return (
      <main className="flex flex-col items-center justify-center min-h-screen gap-4">
        <p className="text-red-400">{error}</p>
        <a href="/" className="text-blue-400 underline">
          Back to home
        </a>
      </main>
    )
  }

  return (
    <main className="flex items-center justify-center min-h-screen">
      <p className="text-gray-400">Logging in...</p>
    </main>
  )
}

export default function AuthCallback() {
  return (
    <Suspense fallback={<p className="text-gray-400">Loading...</p>}>
      <CallbackHandler />
    </Suspense>
  )
}
