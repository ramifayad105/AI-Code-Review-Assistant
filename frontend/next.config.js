/** @type {import('next').NextConfig} */
const nextConfig = {
  // Emit a minimal standalone server bundle for production Docker images
  output: "standalone",
}

module.exports = nextConfig
