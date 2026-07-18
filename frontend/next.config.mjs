/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**" },
    ],
  },
  async rewrites() {
    const apiBase = process.env.BACKEND_API_URL;
    if (!apiBase) return [];
    return [{ source: "/api/backend/:path*", destination: `${apiBase}/:path*` }];
  },
};

export default nextConfig;
