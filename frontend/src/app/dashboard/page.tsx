"use client"

import { useEffect, useState } from "react"
import { api } from "@/lib/api"
import Link from "next/link"

interface Stats {
  repos: number
  reviews: number
  findings: number
  by_severity: {
    critical: number
    high: number
    medium: number
    low: number
    info: number
  }
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .getStats()
      .then(setStats)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <main className="max-w-3xl mx-auto p-8">
        <p className="text-gray-500">Loading...</p>
      </main>
    )
  }

  if (!stats) {
    return (
      <main className="max-w-3xl mx-auto p-8">
        <p className="text-red-400">Could not load stats.</p>
      </main>
    )
  }

  return (
    <main className="max-w-3xl mx-auto p-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <Link href="/" className="text-sm text-gray-400 hover:text-white">
          ← Back
        </Link>
      </div>

      {/* Top-level stats */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <StatCard label="Repos" value={stats.repos} />
        <StatCard label="Reviews" value={stats.reviews} />
        <StatCard label="Findings" value={stats.findings} />
      </div>

      {/* Severity breakdown */}
      <h2 className="text-lg font-semibold mb-4">Findings by severity</h2>
      <div className="grid grid-cols-5 gap-3">
        <SeverityCard
          label="Critical"
          value={stats.by_severity.critical}
          color="text-red-400"
        />
        <SeverityCard
          label="High"
          value={stats.by_severity.high}
          color="text-orange-400"
        />
        <SeverityCard
          label="Medium"
          value={stats.by_severity.medium}
          color="text-yellow-400"
        />
        <SeverityCard
          label="Low"
          value={stats.by_severity.low}
          color="text-blue-400"
        />
        <SeverityCard
          label="Info"
          value={stats.by_severity.info}
          color="text-gray-400"
        />
      </div>

      {/* Quick links */}
      <div className="flex gap-4 mt-10">
        <Link
          href="/repos"
          className="px-4 py-2 bg-gray-800 rounded hover:bg-gray-700 transition"
        >
          Manage repos
        </Link>
        <Link
          href="/reviews"
          className="px-4 py-2 bg-gray-800 rounded hover:bg-gray-700 transition"
        >
          View reviews
        </Link>
      </div>
    </main>
  )
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="p-4 bg-gray-900 border border-gray-800 rounded-lg text-center">
      <p className="text-3xl font-bold">{value}</p>
      <p className="text-sm text-gray-400 mt-1">{label}</p>
    </div>
  )
}

function SeverityCard({
  label,
  value,
  color,
}: {
  label: string
  value: number
  color: string
}) {
  return (
    <div className="p-3 bg-gray-900 border border-gray-800 rounded-lg text-center">
      <p className={`text-2xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  )
}
