import './globals.css'
import type { Metadata } from 'next'
import { Sidebar } from '@/components/Sidebar'
import ErrorBoundary from '@/components/ErrorBoundary'
import { Toaster } from '@/components/ui/sonner'

export const metadata: Metadata = {
  title: 'FinanceHub - Personal Dashboard',
  description: 'Personal finance tracking and analysis platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-white">
        <ErrorBoundary>
          <div className="flex min-h-screen">
            <Sidebar />
            <main className="flex-1 ml-[240px] bg-white">
              {children}
            </main>
          </div>
        </ErrorBoundary>
        <Toaster richColors position="top-right" />
      </body>
    </html>
  )
}