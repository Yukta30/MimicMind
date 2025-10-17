import '../styles/globals.css'

export const metadata = { title: 'MimicMind Demo', description: 'Code like you' }

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">{children}</body>
    </html>
  )
}
