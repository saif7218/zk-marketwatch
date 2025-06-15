/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': __dirname + '/src',
    };
    return config;
  },
  images: {
    domains: ['localhost'],
  },
  // Enable TypeScript type checking in development
  typescript: {
    ignoreBuildErrors: false,
  },
  // Enable ESLint in development
  eslint: {
    ignoreDuringBuilds: false,
  },
};

module.exports = nextConfig;
