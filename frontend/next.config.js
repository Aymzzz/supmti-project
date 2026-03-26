/** @type {import('next').NextConfig} */
const backendBaseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.BACKEND_URL || 'http://127.0.0.1:8000';

const nextConfig = {
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: `${backendBaseUrl}/api/:path*`,
            },
            {
                source: '/ws/:path*',
                destination: `${backendBaseUrl}/ws/:path*`,
            },
        ];
    },
};

module.exports = nextConfig;
