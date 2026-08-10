import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "AI Code Review",
  description: "Automated code review for GitHub pull requests",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  )
}
