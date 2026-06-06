import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'PM協会テスト診断システム',
  description: 'PM適性診断を自動化するAIエージェントシステム',
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
        <div className="flex flex-col min-h-screen">
          {/* Header */}
          <header className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <h1 className="text-2xl font-bold text-blue-600">
                PM協会テスト診断システム
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                AI エージェントによる PM 適性診断
              </p>
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 w-full">
            {children}
          </main>

          {/* Footer */}
          <footer className="bg-gray-50 border-t border-gray-200 mt-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-sm text-gray-600">
              <p>PM協会テスト診断システム v1.0.0</p>
              <p className="mt-2">© 2026 PM Association. All rights reserved.</p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  )
}
