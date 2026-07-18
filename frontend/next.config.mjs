/** @type {import('next').NextConfig} */
const nextConfig = {
  // Standalone output keeps the Docker image small (only traced deps are copied).
  output: "standalone",
  reactStrictMode: true,
};

export default nextConfig;
