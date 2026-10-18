'use client'

import { useState } from 'react'
import { ArrowRight, Play } from 'lucide-react'
import { useHashTable } from '@/components/hash-table-provider'
import { Button } from '@/components/ui/button'
import { hashSteps } from '@/lib/hash-table'
import { cn } from '@/lib/utils'

export function BucketGrid() {
  const { table, search } = useHashTable()
  const [probe, setProbe] = useState('')
  const buckets = table.buckets()
  const trace = table.lastTrace
  const steps = trace ? hashSteps(trace.key, table.capacity) : []

  function runProbe(e: React.FormEvent) {
    e.preventDefault()
    const key = probe.trim().toUpperCase()
    if (/^[A-Z]{2}$/.test(key)) search(key)
  }

  return (
    <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1fr_340px]">
      <section aria-labelledby="buckets-title" className="overflow-hidden rounded-2xl border border-white/10 bg-navy text-slate-200 shadow-elev-3">
        <header className="flex flex-col gap-3 border-b border-white/10 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 id="buckets-title" className="font-heading text-base font-semibold text-white">
              {'Tabela hash · encadeamento separado'}
            </h2>
            <p className="font-mono text-xs text-slate-400">{'NoHash[] tabela = new NoHash[17]'}</p>
          </div>
          <Legend />
        </header>

        <ol className="flex flex-col divide-y divide-white/5">
          {buckets.map((chain, index) => {
            const active = trace?.index === index
            return (
              <li
                key={index}
                className={cn(
                  'flex items-center gap-3 overflow-x-auto px-5 py-2.5 transition-colors',
                  active && 'bg-cyan/[0.07]',
                )}
              >
                <span
                  className={cn(
                    'flex h-8 w-12 shrink-0 items-center justify-center rounded-md border font-mono text-xs font-semibold',
                    active ? 'border-cyan bg-cyan/15 text-cyan shadow-glow' : 'border-white/15 bg-white/5 text-slate-300',
                  )}
                >
                  [{String(index).padStart(2, '0')}]
                </span>
                <ArrowRight aria-hidden="true" className="size-3.5 shrink-0 text-slate-600" />
                {chain.map((node, pos) => {
                  const isTarget = active && trace?.key === node.key && trace.found
                  const visited = active && trace !== null && pos < trace.comparisons
                  return (
                    <span key={node.key} className="flex shrink-0 items-center gap-3">
                      <span
                        className={cn(
                          'flex h-8 items-stretch overflow-hidden rounded-md border font-mono text-xs',
                          isTarget
                            ? 'border-gold bg-gold/15 text-gold'
                            : visited
                              ? 'border-sky/60 bg-sky/10 text-sky'
                              : 'border-azure/40 bg-azure/15 text-slate-100',
                        )}
                        title={`${node.value.name} (${node.key})`}
                      >
                        <span className="flex items-center px-2.5 font-semibold">{node.key}</span>
                        <span className="flex items-center border-l border-current/30 px-1.5 opacity-60">
                          {'•'}
                        </span>
                      </span>
                      <ArrowRight aria-hidden="true" className="size-3.5 shrink-0 text-slate-600" />
                    </span>
                  )
                })}
                <span className="shrink-0 font-mono text-xs text-slate-500">null</span>
                {chain.length > 1 && (
                  <span className="ml-auto shrink-0 rounded-full bg-gold/10 px-2 py-0.5 font-mono text-[10px] font-semibold text-gold">
                    {chain.length - 1} {chain.length - 1 === 1 ? 'colisão' : 'colisões'}
                  </span>
                )}
              </li>
            )
          })}
        </ol>
      </section>

      <aside className="flex flex-col gap-6">
        <form onSubmit={runProbe} className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-5 shadow-elev-1">
          <label htmlFor="probe-key" className="font-heading text-sm font-semibold text-navy-900">
            Simular busca
          </label>
          <p className="text-xs text-muted-foreground">Digite uma chave ISO para visualizar o percurso na cadeia.</p>
          <div className="flex gap-2">
            <input
              id="probe-key"
              value={probe}
              maxLength={2}
              onChange={(e) => setProbe(e.target.value.replace(/[^a-zA-Z]/g, '').toUpperCase())}
              placeholder="PT"
              className="h-9 w-full rounded-lg border border-input bg-background px-3 font-mono text-sm uppercase outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/30"
            />
            <Button type="submit" className="h-9 gap-1.5 bg-azure text-white hover:bg-azure/90">
              <Play aria-hidden="true" />
              Buscar
            </Button>
          </div>
        </form>

        <section aria-labelledby="trace-title" aria-live="polite" className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-5 shadow-elev-1">
          <h2 id="trace-title" className="font-heading text-sm font-semibold text-navy-900">
            Última operação
          </h2>
          {trace ? (
            <>
              <dl className="grid grid-cols-2 gap-3 text-sm">
                <TraceItem label="Operação" value={OP_LABEL[trace.kind]} />
                <TraceItem label="Chave" value={trace.key} mono />
                <TraceItem label="Bucket" value={`[${trace.index}]`} mono />
                <TraceItem label="Comparações" value={String(trace.comparisons)} mono />
                <TraceItem
                  label="Resultado"
                  value={trace.kind === 'insert' ? (trace.collided ? 'Colisão' : 'Bucket livre') : trace.found ? 'Encontrado' : 'Não encontrado'}
                />
                <TraceItem label="Complexidade" value={trace.comparisons <= 1 ? 'O(1)' : `O(1 + α)`} mono />
              </dl>
              <div className="flex flex-col gap-2 rounded-lg bg-navy p-3 font-mono text-xs text-slate-300">
                <span className="text-slate-500">{'// h = (h · 31 + c) mod 17'}</span>
                {steps.map((s, i) => (
                  <span key={i}>
                    {`'${s.char}' (${s.code}) → h = `}
                    <span className="text-cyan">{s.hash}</span>
                  </span>
                ))}
                <span className="text-gold">{`índice final = ${trace.index}`}</span>
              </div>
            </>
          ) : (
            <p className="text-sm text-muted-foreground">
              Nenhuma operação registrada ainda. Use a busca acima ou edite países na página de Cobertura.
            </p>
          )}
        </section>
      </aside>
    </div>
  )
}

const OP_LABEL = { insert: 'Inserção', update: 'Atualização', delete: 'Remoção', search: 'Busca' } as const

function TraceItem({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex flex-col gap-0.5">
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className={cn('font-semibold text-navy-900', mono && 'font-mono')}>{value}</dd>
    </div>
  )
}

function Legend() {
  return (
    <ul className="flex flex-wrap gap-3 text-xs text-slate-400">
      <li className="flex items-center gap-1.5">
        <span aria-hidden="true" className="size-2.5 rounded-sm border border-azure/40 bg-azure/30" /> Nó
      </li>
      <li className="flex items-center gap-1.5">
        <span aria-hidden="true" className="size-2.5 rounded-sm border border-sky/60 bg-sky/20" /> Visitado
      </li>
      <li className="flex items-center gap-1.5">
        <span aria-hidden="true" className="size-2.5 rounded-sm border border-gold bg-gold/30" /> Alvo
      </li>
    </ul>
  )
}
