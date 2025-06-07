import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { useTranslation } from 'react-i18next';
import { usePathname } from 'next/navigation';
import { Suspense } from 'react';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Apon Family Mart - Price Intelligence Dashboard',
  description: 'Real-time price monitoring and intelligence dashboard for Apon Family Mart',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { i18n } = useTranslation();

  return (
    <html lang={i18n.language}>
      <body className={inter.className}>
        <Suspense fallback={<div>Loading...</div>}>
          <Providers>
            {children}
          </Providers>
        </Suspense>
      </body>
    </html>
  );
}
