/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@seraaj/ui'],
  experimental: {
    externalDir: true,
  },
  i18n: {
    locales: ['en', 'ar'],
    defaultLocale: 'en',
    localeDetection: true,
  },
};

export default nextConfig;