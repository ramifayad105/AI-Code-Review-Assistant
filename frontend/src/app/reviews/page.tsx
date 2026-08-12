"use client"

import { useEffect, useState } from "react"
import { api } from "@/lib/api"
import Link from "next/link"

interface Review {
  id: string
  pr_number: number
  pr_title: string
  pr_author: string
  status: string
  summary: string | null
  created_at: string
  repo_full_name: string
}

const statusColors: Record<string, string> = {
  completed: "bg-green-900 text-green-300",
  in_progress: "bg-blue-900 text-blue-300",
  pending: "bg-yellow-900 text-yellow-300",
  failed: "bg-red-900 text-red-300",
}

export default function ReviewsPage() {
  const [reviews, setReviews] = useState<Review[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .getReviews()
      .then(setReviews)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <main className="max-w-3xl mx-auto p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Reviews</h1>
        <Link href="/" className="text-sm text-gray-400 hover:text-white">
          ← Back
        </Link>
      </div>

      {loading && <p className="text-gray-500">Loading...</p>}

      {!loading && reviews.length === 0 && (
        <p className="text-gray-500">
          No reviews yet. Connect a repo and open a PR to get started.
        </p>
      )}

      <ul className="space-y-3">
        {reviews.map((r) => (
          <li key={r.id}>
            <Link
              href={`/reviews/${r.id}`}
              className="block p-4 bg-gray-900 border border-gray-800 rounded-lg hover:border-gray-600 transition"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <p className="font-medium truncate">
                    #{r.pr_number} {r.pr_title}
                  </p>
                  <p className="text-sm text-gray-400 mt-1">
                    {r.repo_full_name} · by {r.pr_author}
                  </p>
                </div>
                <span
                  className={`text-xs px-2 py-1 rounded whitespace-nowrap ${
                    statusColors[r.status] || "bg-gray-800 text-gray-300"
                  }`}
                >
                  {r.status}
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                {new Date(r.created_at).toLocaleDateString()}
              </p>
            </Link>
          </li>
        ))}
      </ul>
    </main>
  )
}
