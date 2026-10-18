'use client'

import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { CountryFlag } from '@/components/country-flag'
import { useHashTable } from '@/components/hash-table-provider'
import { NetworkBadge } from '@/components/status-badge'

const FEATURED = ['PT', 'US', 'JP', 'IT', 'FR', 'GB', 'AR', 'TH']

export function PopularDestinations() {
  const { table } = useHashTable()
  const countries = FEATURED.map((code) => table.peek(code)).filter((c) => c !== null)

  return (
    <section aria-labelledby="destinations-title" className="border-y border-border bg-white">
      <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div className="flex flex-col gap-3">
            <p className="font-mono text-xs font-medium tracking-widest text-azure uppercase">Destinos populares</p>
            <h2 id="destinations-title" className="text-3xl font-bold tracking-tight text-navy-900">
              Planos a partir do preço por GB
            </h2>
          </div>
          <Link href="/cobertura" className="inline-flex items-center gap-1.5 text-sm font-semibold text-azure hover:underline">
            Ver todos os países
            <ArrowRight aria-hidden="true" className="size-4" />
          </Link>
        </div>

        <ul className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {countries.map((c) => (
            <li key={c.code}>
              <article className="group flex h-full flex-col gap-5 rounded-2xl border border-border bg-canvas p-5 transition-all hover:-translate-y-0.5 hover:border-azure/40 hover:bg-white hover:shadow-elev-2">
                <div className="flex items-center justify-between">
                  <CountryFlag code={c.code} name={c.name} className="h-8 w-11 rounded-md" />
                  <span className="font-mono text-xs font-semibold text-muted-foreground">{c.code}</span>
                </div>
                <div className="flex flex-col gap-1">
                  <h3 className="font-semibold text-navy-900">{c.name}</h3>
                  <p className="text-xs text-muted-foreground">{c.carriers.slice(0, 2).join(' · ')}</p>
                </div>
                <div className="mt-auto flex items-end justify-between">
                  <p className="flex flex-col">
                    <span className="text-xs text-muted-foreground">a partir de</span>
                    <span className="font-heading text-xl font-bold text-navy-900">
                      {c.pricePerGB.toLocaleString('pt-BR', { style: 'currency', currency: 'USD' })}
                      <span className="text-sm font-medium text-muted-foreground">/GB</span>
                    </span>
                  </p>
                  <NetworkBadge has5G={c.has5G} />
                </div>
              </article>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
