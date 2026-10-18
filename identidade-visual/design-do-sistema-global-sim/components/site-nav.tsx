'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import { Menu, X } from 'lucide-react'
import { BrandLogo } from '@/components/brand-logo'
import { useHashTable } from '@/components/hash-table-provider'
import { cn } from '@/lib/utils'

const LINKS = [
  { href: '/', label: 'Início' },
  { href: '/cobertura', label: 'Cobertura' },
  { href: '/instrumentacao', label: 'Instrumentação' },
  { href: '/design-system', label: 'Design System' },
]

export function SiteNav() {
  const pathname = usePathname()
  const { table } = useHashTable()
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-40 border-b border-white/10 bg-navy/95 backdrop-blur-xl">
      <nav aria-label="Principal" className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-6 px-4 sm:px-6 lg:px-8">
        <Link href="/" aria-label="GlobalSIM — página inicial" className="shrink-0">
          <BrandLogo />
        </Link>

        <ul className="hidden items-center gap-1 md:flex">
          {LINKS.map((link) => {
            const active = pathname === link.href
            return (
              <li key={link.href}>
                <Link
                  href={link.href}
                  aria-current={active ? 'page' : undefined}
                  className={cn(
                    'rounded-md px-3 py-2 text-sm font-medium transition-colors',
                    active ? 'bg-white/10 text-white' : 'text-slate-300 hover:bg-white/5 hover:text-white',
                  )}
                >
                  {link.label}
                </Link>
              </li>
            )
          })}
        </ul>

        <div className="hidden items-center gap-3 md:flex">
          <span className="inline-flex items-center gap-2 rounded-full border border-cyan/25 bg-cyan/10 px-3 py-1 text-xs font-medium text-cyan">
            <span className="relative flex size-2">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-cyan opacity-60" />
              <span className="relative inline-flex size-2 rounded-full bg-cyan" />
            </span>
            Rede operacional
          </span>
          <span className="rounded-md border border-white/10 bg-white/5 px-2 py-1 font-mono text-xs text-slate-300">
            {'M='}
            {table.capacity} {'· N='}
            {table.size}
          </span>
        </div>

        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-controls="mobile-menu"
          className="inline-flex size-10 items-center justify-center rounded-md text-slate-200 hover:bg-white/10 md:hidden"
        >
          {open ? <X className="size-5" /> : <Menu className="size-5" />}
          <span className="sr-only">{open ? 'Fechar menu' : 'Abrir menu'}</span>
        </button>
      </nav>

      {open && (
        <div id="mobile-menu" className="border-t border-white/10 px-4 pb-4 md:hidden">
          <ul className="flex flex-col gap-1 pt-3">
            {LINKS.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  onClick={() => setOpen(false)}
                  aria-current={pathname === link.href ? 'page' : undefined}
                  className={cn(
                    'block rounded-md px-3 py-2 text-sm font-medium',
                    pathname === link.href ? 'bg-white/10 text-white' : 'text-slate-300',
                  )}
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </header>
  )
}
