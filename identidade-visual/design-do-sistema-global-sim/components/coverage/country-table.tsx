'use client'

import { useState } from 'react'
import { Pencil, Plus, RotateCcw, Search, Trash2 } from 'lucide-react'
import { CountryFlag } from '@/components/country-flag'
import { CountryFormDialog } from '@/components/coverage/country-form-dialog'
import { useHashTable } from '@/components/hash-table-provider'
import { NetworkBadge } from '@/components/status-badge'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { hashKey, type Country } from '@/lib/hash-table'

type NetworkFilter = 'all' | '5g' | '4g'

export function CountryTable() {
  const { table, remove, reset } = useHashTable()
  const [filter, setFilter] = useState('')
  const [network, setNetwork] = useState<NetworkFilter>('all')
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<Country | null>(null)
  const [deleting, setDeleting] = useState<Country | null>(null)
  const [notice, setNotice] = useState<string | null>(null)

  const q = filter.trim().toLocaleLowerCase('pt-BR')
  const rows = table.values().filter((c) => {
    if (network === '5g' && !c.has5G) return false
    if (network === '4g' && c.has5G) return false
    if (!q) return true
    return (
      c.code.toLowerCase().includes(q) ||
      c.name.toLocaleLowerCase('pt-BR').includes(q) ||
      c.carriers.some((carrier) => carrier.toLowerCase().includes(q))
    )
  })

  return (
    <section aria-labelledby="crud-title" className="overflow-hidden rounded-2xl border border-border bg-card shadow-elev-2">
      <div className="flex flex-col gap-4 border-b border-border p-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-col gap-1">
          <h2 id="crud-title" className="text-lg font-semibold text-navy-900">
            Gerenciamento de países
          </h2>
          <p className="text-sm text-muted-foreground">
            {table.size} {'países armazenados · inserção, edição e remoção em O(1) médio'}
          </p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <div className="relative">
            <Search aria-hidden="true" className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
            <label htmlFor="table-filter" className="sr-only">
              Filtrar países
            </label>
            <input
              id="table-filter"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              placeholder="Filtrar por nome, código ou operadora"
              className="h-9 w-full rounded-lg border border-input bg-background pr-3 pl-9 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/30 sm:w-72"
            />
          </div>
          <div role="group" aria-label="Filtrar por rede" className="inline-flex rounded-lg border border-border bg-secondary p-0.5">
            {(['all', '5g', '4g'] as const).map((value) => (
              <button
                key={value}
                type="button"
                aria-pressed={network === value}
                onClick={() => setNetwork(value)}
                className={`rounded-md px-3 py-1.5 text-xs font-semibold transition-colors ${
                  network === value ? 'bg-white text-navy-900 shadow-elev-1' : 'text-muted-foreground hover:text-navy-900'
                }`}
              >
                {value === 'all' ? 'Todos' : value.toUpperCase()}
              </button>
            ))}
          </div>
          <Button variant="outline" className="h-9 gap-2" onClick={() => { reset(); setNotice('Tabela restaurada ao estado inicial.') }}>
            <RotateCcw aria-hidden="true" />
            Restaurar
          </Button>
          <Button
            className="h-9 gap-2 bg-azure text-white hover:bg-azure/90"
            onClick={() => {
              setEditing(null)
              setFormOpen(true)
            }}
          >
            <Plus aria-hidden="true" />
            Novo país
          </Button>
        </div>
      </div>

      <p aria-live="polite" className={notice ? 'border-b border-border bg-accent px-5 py-2 text-sm text-accent-foreground' : 'sr-only'}>
        {notice}
      </p>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[760px] text-left text-sm">
          <thead className="bg-secondary/70 text-xs tracking-wide text-muted-foreground uppercase">
            <tr>
              <th scope="col" className="px-5 py-3 font-semibold">País</th>
              <th scope="col" className="px-5 py-3 font-semibold">Chave</th>
              <th scope="col" className="px-5 py-3 font-semibold">Bucket</th>
              <th scope="col" className="px-5 py-3 font-semibold">Operadoras</th>
              <th scope="col" className="px-5 py-3 font-semibold">Rede</th>
              <th scope="col" className="px-5 py-3 text-right font-semibold">Preço/GB</th>
              <th scope="col" className="px-5 py-3 text-right font-semibold">
                <span className="sr-only">Ações</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((c) => (
              <tr key={c.code} className="border-t border-border odd:bg-white even:bg-canvas hover:bg-accent/50">
                <td className="px-5 py-3">
                  <div className="flex items-center gap-3">
                    <CountryFlag code={c.code} name={c.name} />
                    <div className="flex flex-col">
                      <span className="font-medium text-navy-900">{c.name}</span>
                      <span className="text-xs text-muted-foreground">{c.region}</span>
                    </div>
                  </div>
                </td>
                <td className="px-5 py-3 font-mono font-semibold text-navy-900">{c.code}</td>
                <td className="px-5 py-3 font-mono text-azure">[{String(hashKey(c.code)).padStart(2, '0')}]</td>
                <td className="max-w-56 truncate px-5 py-3 text-muted-foreground">{c.carriers.join(', ')}</td>
                <td className="px-5 py-3">
                  <NetworkBadge has5G={c.has5G} />
                </td>
                <td className="px-5 py-3 text-right font-mono text-navy-900">
                  {c.pricePerGB.toLocaleString('pt-BR', { style: 'currency', currency: 'USD' })}
                </td>
                <td className="px-5 py-3">
                  <div className="flex justify-end gap-1">
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      aria-label={`Editar ${c.name}`}
                      onClick={() => {
                        setEditing(c)
                        setFormOpen(true)
                      }}
                    >
                      <Pencil />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      aria-label={`Remover ${c.name}`}
                      className="text-destructive hover:bg-red-50 hover:text-destructive"
                      onClick={() => setDeleting(c)}
                    >
                      <Trash2 />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td colSpan={7} className="px-5 py-12 text-center text-muted-foreground">
                  Nenhum país encontrado com os filtros atuais.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <CountryFormDialog open={formOpen} onOpenChange={setFormOpen} initial={editing} onSaved={setNotice} />

      <Dialog open={deleting !== null} onOpenChange={(open) => !open && setDeleting(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="font-heading text-lg font-semibold">Remover {deleting?.name}?</DialogTitle>
            <DialogDescription>
              {'O nó com chave '}
              <span className="font-mono font-semibold">{deleting?.code}</span>
              {' será desencadeado do bucket '}
              <span className="font-mono font-semibold">{deleting ? hashKey(deleting.code) : ''}</span>.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleting(null)}>
              Cancelar
            </Button>
            <Button
              className="bg-destructive text-white hover:bg-destructive/90"
              onClick={() => {
                if (deleting) {
                  remove(deleting.code)
                  setNotice(`${deleting.name} removido da tabela.`)
                }
                setDeleting(null)
              }}
            >
              Remover
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </section>
  )
}
