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
  info: "bg-gray-700 text-gray-300",
}

const categoryColors: Record<string, string> = {
  bug: "bg-red-900/50 text-red-400",
  security: "bg-purple-900/50 text-purple-400",
  performance: "bg-orange-900/50 text-orange-400",
  style: "bg-cyan-900/50 text-cyan-400",
  duplication: "bg-yellow-900/50 text-yellow-400",
  best_practice: "bg-green-900/50 text-green-400",
}

const statusStyles: Record<string, string> = {
  completed: "bg-green-900 text-green-300",
  in_progress: "bg-blue-900 text-blue-300",
  pending: "bg-yellow-900 text-yellow-300",
  failed: "bg-red-900 text-red-300",
}

export default function ReviewDetailPage() {
  const params = useParams()
  const [review, setReview] = useState<ReviewDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    if (!params.id) return
    api
      .getReview(params.id as string)
      .then(setReview)
      .catch((err: any) => setError(err.message || "Failed to load review"))
      .finally(() => setLoading(false))
  }, [params.id])

  if (loading) {
    return (
      <main className="max-w-4xl mx-auto p-8">
        <p className="text-gray-500">Loading review...</p>
      </main>
    )
  }

  if (error || !review) {
    return (
      <main className="max-w-4xl mx-auto p-8">
        <p className="text-red-400">{error || "Review not found"}</p>
        <Link
          href="/reviews"
          className="text-sm text-gray-400 hover:text-white mt-4 inline-block"
        >
          ← Back to reviews
        </Link>
      </main>
    )
  }

  return (
    <main className="max-w-4xl mx-auto p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <Link
          href="/reviews"
          className="text-sm text-gray-400 hover:text-white"
        >
          ← Back to reviews
        </Link>
        <span
          className={`text-xs px-2 py-1 rounded ${statusStyles[review.status] || "bg-gray-800 text-gray-300"}`}
        >
          {review.status.replace("_", " ")}
        </span>
      </div>

      {/* PR info */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold">
          #{review.pr_number} {review.pr_title}
        </h1>
        <p className="text-sm text-gray-400 mt-2">
          {review.repo_full_name} · by {review.pr_author} ·{" "}
          {new Date(review.created_at).toLocaleDateString()}
          {review.completed_at &&
            ` · completed ${new Date(review.completed_at).toLocaleDateString()}`}
        </p>
      </div>

      {/* Summary */}
      {review.summary && (
        <div className="p-4 bg-gray-900 border border-gray-800 rounded-lg mb-8">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-2">
            Summary
          </h2>
          <p className="text-gray-200">{review.summary}</p>
        </div>
      )}

      {/* Findings */}
      <div>
        <h2 className="text-lg font-semibold mb-4">
          Findings{" "}
          <span className="text-gray-500 font-normal">
            ({review.findings.length})
          </span>
        </h2>

        {review.findings.length === 0 ? (
          <p className="text-gray-500">No issues found. Looks good!</p>
        ) : (
          <ul className="space-y-4">
            {review.findings.map((finding) => (
              <li
                key={finding.id}
                className="p-4 bg-gray-900 border border-gray-800 rounded-lg"
              >
                {/* Finding header */}
                <div className="flex items-start justify-between gap-3 mb-2">
                  <h3 className="font-medium">{finding.title}</h3>
                  <div className="flex gap-2 shrink-0">
                    <span
                      className={`text-xs px-2 py-0.5 rounded ${severityColors[finding.severity] || "bg-gray-800 text-gray-300"}`}
                    >
                      {finding.severity}
                    </span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded ${categoryColors[finding.category] || "bg-gray-800 text-gray-300"}`}
                    >
                      {finding.category.replace("_", " ")}
                    </span>
                  </div>
                </div>

                {/* Location */}
                <p className="text-xs text-gray-500 mb-2">
                  {finding.file_path}:{finding.line_number}
                </p>

                {/* Description */}
                <p className="text-sm text-gray-300 mb-3">
                  {finding.description}
                </p>

                {/* Code snippet */}
                {finding.code_snippet && (
                  <pre className="text-xs bg-gray-950 border border-gray-800 rounded p-3 overflow-x-auto mb-3">
                    <code>{finding.code_snippet}</code>
                  </pre>
                )}

                {/* Suggestion */}
                {finding.suggestion && (
                  <div className="text-sm bg-green-950/30 border border-green-900/50 rounded p-3">
                    <span className="text-green-400 font-medium">
                      Suggestion:{" "}
                    </span>
                    <span className="text-gray-300">
                      {finding.suggestion}
                    </span>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </main>
  )
}
