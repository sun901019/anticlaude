/** @type {import('next').NextConfig} */
const nextConfig = {
  // Disable HTTP keep-alive to prevent ECONNRESET from stale pooled connections
  // when the FastAPI backend restarts or is temporarily unavailable.
  httpAgentOptions: {
    keepAlive: false,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
  // Increase proxy timeout to prevent ECONNRESET on slow pipeline/LLM calls
  experimental: {
    proxyTimeout: 120_000,   // 120s — pipeline can take 60s+
  },
  // SSE streams bypass the proxy and connect directly to :8000 to avoid buffering.
};

module.exports = nextConfig;
