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
  completed_at: string | null
  repo_full_name: string
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    completed: "bg-green-900 text-green-300",
    in_progress: "bg-blue-900 text-blue-300",
    pending: "bg-yellow-900 text-yellow-300",
    failed: "bg-red-900 text-red-300",
  }
  return (
    <span
      className={`text-xs px-2 py-1 rounded ${styles[status] || "bg-gray-800 text-gray-300"}`}
    >
      {status.replace("_", " ")}
    </span>
  )
}

function timeAgo(dateStr: string): string {
  const seconds = Math.floor(
    (Date.now() - new Date(dateStr).getTime()) / 1000
  )
  if (seconds < 60) return "just now"
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

export default function ReviewsPage() {
  const [reviews, setReviews] = useState<Review[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    api
      .getReviews()
      .then(setReviews)
      .catch((err: any) => setError(err.message || "Failed to load reviews"))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <main className="max-w-3xl mx-auto p-8">
        <p className="text-gray-500">Loading reviews...</p>
      </main>
    )
  }

  return (
    <main className="max-w-3xl mx-auto p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Reviews</h1>
        <Link href="/" className="text-sm text-gray-400 hover:text-white">
          ← Back
        </Link>
      </div>

      {error && <p className="text-red-400 mb-4">{error}</p>}

      {reviews.length === 0 ? (
        <p className="text-gray-500">
          No reviews yet. Connect a repo and open a pull request to get started.
        </p>
      ) : (
        <ul className="space-y-3">
          {reviews.map((review) => (
            <li key={review.id}>
              <Link
                href={`/reviews/${review.id}`}
                className="block p-4 bg-gray-900 border border-gray-800 rounded-lg hover:border-gray-600 transition"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <p className="font-medium truncate">
                      #{review.pr_number} {review.pr_title}
                    </p>
                    <p className="text-sm text-gray-400 mt-1">
                      {review.repo_full_name} · by {review.pr_author} ·{" "}
                      {timeAgo(review.created_at)}
                    </p>
                  </div>
                  <StatusBadge status={review.status} />
                </div>
                {review.summary && (
                  <p className="text-sm text-gray-500 mt-2 line-clamp-2">
                    {review.summary}
                  </p>
                )}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  )
}
