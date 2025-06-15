/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8000'
  },
  images: {
    domains: ['www.shwapno.com', 'www.meenaclick.com', 'www.unimart.online'],
  }
}

module.exports = nextConfig 