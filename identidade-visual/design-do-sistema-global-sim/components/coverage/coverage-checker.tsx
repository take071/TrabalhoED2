'use client'

import { useState } from 'react'
import { Antenna, Gauge, LocateFixed, Search, SearchX, Signal } from 'lucide-react'
import { CountryFlag } from '@/components/country-flag'
import { useHashTable } from '@/components/hash-table-provider'
import { NetworkBadge, StatusBadge } from '@/components/status-badge'
import { Button } from '@/components/ui/button'
import type { Country, OperationTrace } from '@/lib/hash-table'
import { cn } from '@/lib/utils'

const QUICK_PILLS = ['BR', 'US', 'JP', 'IT', 'PT', 'FR']

type Result = { query: string; country: Country | null; trace: OperationTrace | null; elapsedMs: number }

export function CoverageChecker({ variant = 'light' }: { variant?: 'light' | 'dark' }) {
  const { table, search } = useHashTable()
  const [query, setQuery] = useState('')
  const [result, setResult] = useState<Result | null>(null)

  const trimmed = query.trim()
  const nameMatches =
    trimmed.length > 2
      ? table
          .values()
          .filter((c) => c.name.toLocaleLowerCase('pt-BR').includes(trimmed.toLocaleLowerCase('pt-BR')))
          .slice(0, 5)
      : []

  function runSearch(code: string) {
    const normalized = code.trim().toUpperCase()
    if (!normalized) return
    const start = performance.now()
    const country = search(normalized)
    const elapsedMs = performance.now() - start
    setResult({ query: normalized, country, trace: table.lastTrace, elapsedMs })
  }

  function handleChange(value: string) {
    setQuery(value)
    if (/^[a-zA-Z]{2}$/.test(value.trim())) runSearch(value)
  }

  function detectLocation() {
    const locale = navigator.language || 'pt-BR'
    const region = new Intl.Locale(locale).maximize().region ?? 'BR'
    setQuery(region)
    runSearch(region)
  }

  const dark = variant === 'dark'

  return (
    <div className="flex flex-col gap-4">
      <form
        role="search"
        aria-label="Verificar cobertura por país"
        onSubmit={(e) => {
          e.preventDefault()
          if (nameMatches.length > 0 && trimmed.length > 2) runSearch(nameMatches[0].code)
          else runSearch(trimmed)
        }}
        className={cn(
          'flex flex-col gap-2 rounded-2xl border p-2 shadow-elev-3 sm:flex-row sm:items-center',
          dark ? 'border-white/10 bg-white/95' : 'border-border bg-card',
        )}
      >
        <label htmlFor="coverage-query" className="sr-only">
          Código ISO ou nome do país
        </label>
        <div className="relative flex flex-1 items-center">
          <Search aria-hidden="true" className="pointer-events-none absolute left-3 size-5 text-muted-foreground" />
          <input
            id="coverage-query"
            value={query}
            onChange={(e) => handleChange(e.target.value)}
            placeholder="Código ISO (BR) ou nome do país"
            autoComplete="off"
            className="h-12 w-full rounded-xl bg-transparent pr-3 pl-11 text-base text-foreground outline-none placeholder:text-muted-foreground"
          />
        </div>
        <div className="flex gap-2">
          <Button type="button" variant="outline" className="h-11 flex-1 gap-2 rounded-xl px-4 sm:flex-none" onClick={detectLocation}>
            <LocateFixed aria-hidden="true" />
            Detectar
          </Button>
          <Button type="submit" className="h-11 flex-1 rounded-xl bg-azure px-5 text-white hover:bg-azure/90 sm:flex-none">
            Verificar
          </Button>
        </div>
      </form>

      <div className="flex flex-wrap items-center gap-2">
        <span className={cn('text-sm', dark ? 'text-slate-400' : 'text-muted-foreground')}>Acesso rápido:</span>
        {QUICK_PILLS.map((code) => (
          <button
            key={code}
            type="button"
            onClick={() => {
              setQuery(code)
              runSearch(code)
            }}
            className={cn(
              'rounded-full border px-3 py-1 font-mono text-xs font-semibold transition-colors',
              result?.query === code
                ? 'border-azure bg-azure text-white'
                : dark
                  ? 'border-white/15 bg-white/5 text-slate-200 hover:border-cyan/50 hover:text-cyan'
                  : 'border-border bg-card text-navy-900 hover:border-azure hover:text-azure',
            )}
          >
            {code}
          </button>
        ))}
      </div>

      {nameMatches.length > 0 && !result?.country && (
        <ul aria-label="Sugestões por nome" className="flex flex-wrap gap-2">
          {nameMatches.map((c) => (
            <li key={c.code}>
              <button
                type="button"
                onClick={() => {
                  setQuery(c.code)
                  runSearch(c.code)
                }}
                className="inline-flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-1.5 text-sm hover:border-azure"
              >
                <CountryFlag code={c.code} name={c.name} className="h-4 w-5" />
                {c.name}
                <span className="font-mono text-xs text-muted-foreground">{c.code}</span>
              </button>
            </li>
          ))}
          <li className={cn('self-center font-mono text-xs', dark ? 'text-slate-400' : 'text-muted-foreground')}>
            {'busca por nome: O(n)'}
          </li>
        </ul>
      )}

      <div aria-live="polite">{result && <ResultCard result={result} />}</div>
    </div>
  )
}

function ResultCard({ result }: { result: Result }) {
  const { country, trace, query, elapsedMs } = result

  if (!country) {
    return (
      <div className="flex items-start gap-4 rounded-2xl border border-red-200 bg-white p-5 shadow-elev-2">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-red-50 text-destructive">
          <SearchX aria-hidden="true" className="size-5" />
        </span>
        <div className="flex flex-col gap-1">
          <p className="font-heading font-semibold text-navy-900">
            Sem cobertura para <span className="font-mono">{query}</span>
          </p>
          <p className="text-sm text-muted-foreground">
            {'Bucket '}
            <span className="font-mono">{trace?.index}</span>
            {' percorrido com '}
            <span className="font-mono">{trace?.comparisons}</span>
            {' comparação(ões). Cadastre o país na tabela abaixo.'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <article className="overflow-hidden rounded-2xl border border-border bg-white shadow-elev-3">
      <div className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <CountryFlag code={country.code} name={country.name} className="h-10 w-14 rounded-md" />
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <h3 className="text-xl font-bold text-navy-900">{country.name}</h3>
              <StatusBadge variant="code">{country.code}</StatusBadge>
            </div>
            <p className="text-sm text-muted-foreground">{country.region}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <NetworkBadge has5G={country.has5G} />
          <StatusBadge variant="success" dot>
            Coberto
          </StatusBadge>
        </div>
      </div>

      <dl className="grid grid-cols-1 gap-px border-t border-border bg-border sm:grid-cols-3">
        <div className="flex flex-col gap-2 bg-white p-5">
          <dt className="flex items-center gap-2 text-xs font-medium tracking-wide text-muted-foreground uppercase">
            <Antenna aria-hidden="true" className="size-4" /> Operadoras locais
          </dt>
          <dd className="flex flex-wrap gap-1.5">
            {country.carriers.map((carrier) => (
              <span key={carrier} className="rounded-md bg-secondary px-2 py-0.5 text-sm font-medium text-navy-900">
                {carrier}
              </span>
            ))}
          </dd>
        </div>
        <div className="flex flex-col gap-2 bg-white p-5">
          <dt className="flex items-center gap-2 text-xs font-medium tracking-wide text-muted-foreground uppercase">
            <Signal aria-hidden="true" className="size-4" /> Preço por GB
          </dt>
          <dd className="font-heading text-2xl font-bold text-navy-900">
            {country.pricePerGB.toLocaleString('pt-BR', { style: 'currency', currency: 'USD' })}
          </dd>
        </div>
        <div className="flex flex-col gap-2 bg-white p-5">
          <dt className="flex items-center gap-2 text-xs font-medium tracking-wide text-muted-foreground uppercase">
            <Gauge aria-hidden="true" className="size-4" /> Busca na tabela hash
          </dt>
          <dd className="flex flex-col gap-0.5 font-mono text-sm text-navy-900">
            <span>
              {'h("'}
              {country.code}
              {'") = '}
              <span className="font-semibold text-azure">{trace?.index}</span>
            </span>
            <span className="text-muted-foreground">
              {trace?.comparisons} {'comparação(ões) · '}
              {elapsedMs.toFixed(3)} {'ms · O(1)'}
            </span>
          </dd>
        </div>
      </dl>
    </article>
  )
}
