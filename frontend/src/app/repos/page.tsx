"use client"

import { useEffect, useState } from "react"
import { api } from "@/lib/api"
import Link from "next/link"

interface Repo {
  id: string
  full_name: string
  name: string
  webhook_active: boolean
}

export default function ReposPage() {
  const [repos, setRepos] = useState<Repo[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    loadRepos()
  }, [])

  async function loadRepos() {
    try {
      const data = await api.getRepos()
      setRepos(data)
    } catch {
      // not logged in or backend down
    }
  }

  async function handleConnect(e: React.FormEvent) {
    e.preventDefault()
    if (!input.trim()) return

    setLoading(true)
    setError("")

    try {
      await api.connectRepo(input.trim())
      setInput("")
      await loadRepos()
    } catch (err: any) {
      setError(err.message || "Failed to connect repo")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-2xl mx-auto p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Repositories</h1>
        <Link href="/" className="text-sm text-gray-400 hover:text-white">
          ← Back
        </Link>
      </div>

      {/* Connect form */}
      <form onSubmit={handleConnect} className="flex gap-3 mb-8">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="owner/repo-name"
          className="flex-1 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-gray-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-5 py-2 bg-white text-black font-medium rounded-lg hover:bg-gray-200 disabled:opacity-50 transition"
        >
          {loading ? "..." : "Connect"}
        </button>
      </form>

      {error && <p className="text-red-400 mb-4">{error}</p>}

      {/* Repo list */}
      {repos.length === 0 ? (
        <p className="text-gray-500">No repos connected yet.</p>
      ) : (
        <ul className="space-y-3">
          {repos.map((repo) => (
            <li
              key={repo.id}
              className="flex items-center justify-between p-4 bg-gray-900 border border-gray-800 rounded-lg"
            >
              <div>
                <p className="font-medium">{repo.full_name}</p>
              </div>
              <span
                className={`text-xs px-2 py-1 rounded ${
                  repo.webhook_active
                    ? "bg-green-900 text-green-300"
                    : "bg-yellow-900 text-yellow-300"
                }`}
              >
                {repo.webhook_active ? "Webhook active" : "Manual only"}
              </span>
            </li>
          ))}
        </ul>
      )}
    </main>
  )
}
