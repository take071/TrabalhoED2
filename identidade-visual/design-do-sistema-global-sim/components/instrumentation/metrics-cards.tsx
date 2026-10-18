'use client'

import { useHashTable } from '@/components/hash-table-provider'
import { cn } from '@/lib/utils'

export function MetricsCards() {
  const { table } = useHashTable()
  const alpha = table.loadFactor
  const alphaTone = alpha <= 0.75 ? 'text-success' : alpha <= 1.5 ? 'text-gold-600' : 'text-destructive'
  const alphaLabel = alpha <= 0.75 ? 'Saudável' : alpha <= 1.5 ? 'Atenção · cadeias crescendo' : 'Crítico · considere rehash'

  const metrics = [
    { label: 'Capacidade', symbol: 'M', value: String(table.capacity), hint: 'Número primo de buckets', accent: 'bg-azure' },
    { label: 'Tamanho', symbol: 'N', value: String(table.size), hint: 'Chaves armazenadas', accent: 'bg-cyan' },
    {
      label: 'Fator de carga',
      symbol: 'α = N/M',
      value: alpha.toFixed(2),
      hint: alphaLabel,
      hintClass: alphaTone,
      accent: 'bg-gold',
    },
    {
      label: 'Colisões totais',
      symbol: 'Σc',
      value: String(table.totalCollisions),
      hint: `Maior cadeia: ${table.longestChain()} · ${table.emptyBuckets()} buckets vazios`,
      accent: 'bg-navy-900',
    },
  ]

  return (
    <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {metrics.map((m) => (
        <li key={m.label} className="relative overflow-hidden rounded-2xl border border-border bg-card p-5 shadow-elev-1">
          <span aria-hidden="true" className={cn('absolute inset-x-0 top-0 h-1', m.accent)} />
          <div className="flex items-start justify-between gap-2">
            <p className="text-sm font-medium text-muted-foreground">{m.label}</p>
            <span className="rounded-md bg-secondary px-1.5 py-0.5 font-mono text-xs text-navy-900">{m.symbol}</span>
          </div>
          <p className="mt-3 font-heading text-4xl font-bold tracking-tight text-navy-900 tabular-nums">{m.value}</p>
          <p className={cn('mt-1 text-xs', m.hintClass ?? 'text-muted-foreground')}>{m.hint}</p>
        </li>
      ))}
    </ul>
  )
}
