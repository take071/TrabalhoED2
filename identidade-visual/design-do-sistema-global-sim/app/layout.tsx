import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import { Inter, JetBrains_Mono, Plus_Jakarta_Sans } from 'next/font/google'
import { HashTableProvider } from '@/components/hash-table-provider'
import { SiteFooter } from '@/components/site-footer'
import { SiteNav } from '@/components/site-nav'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const jakarta = Plus_Jakarta_Sans({ subsets: ['latin'], variable: '--font-jakarta' })
const jetbrains = JetBrains_Mono({ subsets: ['latin'], variable: '--font-jetbrains' })

export const metadata: Metadata = {
  title: {
    default: 'GlobalSIM — eSIM internacional e roteamento de dados',
    template: '%s · GlobalSIM',
  },
  description:
    'eSIM de viagem com ativação instantânea e otimização de dados multidestino. Verificação de cobertura em O(1) com tabela hash de encadeamento separado.',
  generator: 'v0.app',
  icons: {
    icon: [
      { url: '/icon-light-32x32.png', media: '(prefers-color-scheme: light)' },
      { url: '/icon-dark-32x32.png', media: '(prefers-color-scheme: dark)' },
      { url: '/icon.svg', type: 'image/svg+xml' },
    ],
    apple: '/apple-icon.png',
  },
}

export const viewport: Viewport = {
  colorScheme: 'light',
  themeColor: '#0a192f',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="pt-BR" className={`${inter.variable} ${jakarta.variable} ${jetbrains.variable}`}>
      <body className="flex min-h-dvh flex-col antialiased">
        <HashTableProvider>
          <SiteNav />
          <main className="flex-1">{children}</main>
          <SiteFooter />
        </HashTableProvider>
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
