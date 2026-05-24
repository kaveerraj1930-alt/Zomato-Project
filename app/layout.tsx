import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Zomato AI Recommendation',
  description: 'AI-powered restaurant recommendations',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-[#111]">{children}</body>
    </html>
  );
}
