'use client'

import { useState } from 'react'
import { useHashTable } from '@/components/hash-table-provider'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { REGIONS } from '@/lib/countries-seed'
import { hashKey, type Country } from '@/lib/hash-table'

type Props = {
  open: boolean
  onOpenChange: (open: boolean) => void
  initial?: Country | null
  onSaved?: (message: string) => void
}

const EMPTY: Country = { code: '', name: '', region: 'Europa', carriers: [], has5G: true, pricePerGB: 4 }

export function CountryFormDialog({ open, onOpenChange, initial, onSaved }: Props) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        {open && (
          <CountryForm
            key={initial?.code ?? 'new'}
            initial={initial ?? null}
            onDone={(message) => {
              onSaved?.(message)
              onOpenChange(false)
            }}
            onCancel={() => onOpenChange(false)}
          />
        )}
      </DialogContent>
    </Dialog>
  )
}

function CountryForm({
  initial,
  onDone,
  onCancel,
}: {
  initial: Country | null
  onDone: (message: string) => void
  onCancel: () => void
}) {
  const { table, upsert } = useHashTable()
  const base = initial ?? EMPTY
  const [code, setCode] = useState(base.code)
  const [name, setName] = useState(base.name)
  const [region, setRegion] = useState(base.region)
  const [carriers, setCarriers] = useState(base.carriers.join(', '))
  const [has5G, setHas5G] = useState(base.has5G)
  const [price, setPrice] = useState(String(base.pricePerGB))
  const [error, setError] = useState<string | null>(null)

  const normalizedCode = code.trim().toUpperCase()
  const validCode = /^[A-Z]{2}$/.test(normalizedCode)
  const isEdit = initial !== null

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const priceNumber = Number(price.replace(',', '.'))
    const carrierList = carriers
      .split(',')
      .map((c) => c.trim())
      .filter(Boolean)
      .slice(0, 8)

    if (!validCode) return setError('O código ISO deve ter exatamente 2 letras (ex.: BR).')
    if (name.trim().length < 2 || name.trim().length > 60) return setError('Informe um nome entre 2 e 60 caracteres.')
    if (carrierList.length === 0) return setError('Informe ao menos uma operadora.')
    if (!Number.isFinite(priceNumber) || priceNumber <= 0 || priceNumber > 100)
      return setError('Preço por GB deve ser um número entre 0 e 100.')
    if (normalizedCode !== initial?.code && table.peek(normalizedCode))
      return setError(`O código ${normalizedCode} já está cadastrado.`)

    upsert(
      { code: normalizedCode, name: name.trim(), region, carriers: carrierList, has5G, pricePerGB: priceNumber },
      initial?.code,
    )
    onDone(isEdit ? `${name.trim()} atualizado.` : `${name.trim()} inserido no bucket ${hashKey(normalizedCode)}.`)
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
      <DialogHeader>
        <DialogTitle className="font-heading text-lg font-semibold">
          {isEdit ? `Editar ${initial.name}` : 'Adicionar novo país'}
        </DialogTitle>
        <DialogDescription>
          {'A chave é o código ISO 3166-1 alfa-2, que define o bucket via h(k) mod 17.'}
        </DialogDescription>
      </DialogHeader>

      <div className="grid grid-cols-3 gap-3">
        <div className="col-span-1 flex flex-col gap-1.5">
          <Label htmlFor="cf-code">Código ISO</Label>
          <Input
            id="cf-code"
            value={code}
            maxLength={2}
            onChange={(e) => setCode(e.target.value.replace(/[^a-zA-Z]/g, ''))}
            className="font-mono uppercase"
            placeholder="BR"
            required
          />
        </div>
        <div className="col-span-2 flex flex-col gap-1.5">
          <Label htmlFor="cf-name">Nome do país</Label>
          <Input id="cf-name" value={name} maxLength={60} onChange={(e) => setName(e.target.value)} placeholder="Brasil" required />
        </div>
      </div>

      <div className="flex items-center justify-between rounded-lg border border-dashed border-border bg-secondary/60 px-3 py-2 font-mono text-xs text-muted-foreground">
        <span>{'bucket de destino'}</span>
        <span className="font-semibold text-azure">{validCode ? `h("${normalizedCode}") = ${hashKey(normalizedCode)}` : '—'}</span>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="cf-region">Região</Label>
          <select
            id="cf-region"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
          >
            {REGIONS.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="cf-price">Preço por GB (USD)</Label>
          <Input id="cf-price" inputMode="decimal" value={price} onChange={(e) => setPrice(e.target.value)} />
        </div>
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="cf-carriers">Operadoras (separadas por vírgula)</Label>
        <Input id="cf-carriers" value={carriers} onChange={(e) => setCarriers(e.target.value)} placeholder="Vivo, Claro, TIM" />
      </div>

      <label className="flex items-center gap-3 rounded-lg border border-border px-3 py-2.5 text-sm">
        <input type="checkbox" checked={has5G} onChange={(e) => setHas5G(e.target.checked)} className="size-4 accent-azure" />
        <span className="font-medium">Rede 5G disponível</span>
      </label>

      {error && (
        <p role="alert" className="text-sm font-medium text-destructive">
          {error}
        </p>
      )}

      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancelar
        </Button>
        <Button type="submit" className="bg-azure text-white hover:bg-azure/90">
          {isEdit ? 'Salvar alterações' : 'Inserir país'}
        </Button>
      </DialogFooter>
    </form>
  )
}
