// app/layout.tsx
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './global.css';
import QueryProvider from '../components/providers/query-provider';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Investment Portfolio',
  description: 'Manage your investment portfolio',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>
        <QueryProvider>
          {children}
        </QueryProvider>
      </body>
    </html>
  );
}