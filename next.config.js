/** @type {import('next').NextConfig} */
const nextConfig = {
  // Remove output: 'standalone' as it's for Docker deployments
  // Remove rewrites as frontend now calls backend API directly via lib/api.ts
};

module.exports = nextConfig;
