"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { api } from "@/lib/api"
import Link from "next/link"

interface Finding {
  id: string
  file_path: string
  line_number: number
  severity: string
  category: string
  title: string
  description: string
  suggestion: string | null
  code_snippet: string | null
}

interface ReviewDetail {
  id: string
  pr_number: number
  pr_title: string
  pr_author: string
  status: string
  summary: string | null
  created_at: string
  completed_at: string | null
  repo_full_name: string
  findings: Finding[]
}

const severityColors: Record<string, string> = {
  critical: "bg-red-900 text-red-300",
  high: "bg-orange-900 text-orange-300",
  medium: "bg-yellow-900 text-yellow-300",
  low: "bg-blue-900 text-blue-300",
  info: "bg-gray-800 text-gray-300",
}

export default function ReviewDetailPage() {
  const params = useParams()
  const [review, setReview] = useState<ReviewDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    if (params.id) {
      api
        .getReview(params.id as string)
        .then(setReview)
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false))
    }
  }, [params.id])

  if (loading) {
    return (
      <main className="max-w-3xl mx-auto p-8">
        <p className="text-gray-500">Loading...</p>
      </main>
    )
  }

  if (error || !review) {
    return (
      <main className="max-w-3xl mx-auto p-8">
        <p className="text-red-400">{error || "Review not found"}</p>
        <Link href="/reviews" className="text-blue-400 underline mt-4 block">
          ← Back to reviews
        </Link>
      </main>
    )
  }

  return (
    <main className="max-w-3xl mx-auto p-8">
      <Link
        href="/reviews"
        className="text-sm text-gray-400 hover:text-white mb-6 block"
      >
        ← Back to reviews
      </Link>

      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold">
          #{review.pr_number} {review.pr_title}
        </h1>
        <p className="text-gray-400 mt-1">
          {review.repo_full_name} · by {review.pr_author}
        </p>
        <p className="text-xs text-gray-500 mt-1">
          {new Date(review.created_at).toLocaleString()}
        </p>
      </div>

      {/* Summary */}
      {review.summary && (
        <div className="p-4 bg-gray-900 border border-gray-800 rounded-lg mb-6">
          <p className="text-sm text-gray-300">{review.summary}</p>
        </div>
      )}

      {/* Findings */}
      <h2 className="text-lg font-semibold mb-4">
        Findings ({review.findings.length})
      </h2>

      {review.findings.length === 0 ? (
        <p className="text-gray-500">No issues found. Clean code.</p>
      ) : (
        <ul className="space-y-4">
          {review.findings.map((f) => (
            <li
              key={f.id}
              className="p-4 bg-gray-900 border border-gray-800 rounded-lg"
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <p className="font-medium">{f.title}</p>
                <div className="flex gap-2 shrink-0">
                  <span
                    className={`text-xs px-2 py-0.5 rounded ${
                      severityColors[f.severity] || "bg-gray-800"
                    }`}
                  >
                    {f.severity}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-400">
                    {f.category}
                  </span>
                </div>
              </div>

              <p className="text-sm text-gray-400 mb-2">
                {f.file_path}:{f.line_number}
              </p>

              <p className="text-sm text-gray-300">{f.description}</p>

              {f.suggestion && (
                <div className="mt-3 p-3 bg-gray-800 rounded text-sm">
                  <span className="text-green-400 font-medium">Suggestion: </span>
                  <span className="text-gray-300">{f.suggestion}</span>
                </div>
              )}

              {f.code_snippet && (
                <pre className="mt-3 p-3 bg-gray-800 rounded text-xs text-gray-300 overflow-x-auto">
                  {f.code_snippet}
                </pre>
              )}
            </li>
          ))}
        </ul>
      )}
    </main>
  )
}
