import type { Metadata } from 'next'
import { Plus, Search } from 'lucide-react'
import { BrandLogo, BrandMark } from '@/components/brand-logo'
import { PageHeader } from '@/components/page-header'
import { NetworkBadge, StatusBadge } from '@/components/status-badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

export const metadata: Metadata = {
  title: 'Design System',
  description: 'Tokens de cor, tipografia, elevação e componentes do GlobalSIM.',
}

const COLORS = [
  { name: 'Deep Navy', token: 'navy', hex: '#0A192F', className: 'bg-navy', use: 'Fundos de hero, nav e painéis técnicos' },
  { name: 'Slate 900', token: 'navy-900', hex: '#0F172A', className: 'bg-navy-900', use: 'Texto principal e blocos de código' },
  { name: 'Azure', token: 'azure', hex: '#2563EB', className: 'bg-azure', use: 'Ações primárias e links' },
  { name: 'Electric Cyan', token: 'cyan', hex: '#00D2FF', className: 'bg-cyan', use: 'Estados ativos, rede ao vivo, bucket atual' },
  { name: 'Sky', token: 'sky', hex: '#38BDF8', className: 'bg-sky', use: 'Destaques secundários e nós visitados' },
  { name: 'Chip Gold', token: 'gold', hex: '#F59E0B', className: 'bg-gold', use: 'Chip SIM, colisões e chave-alvo' },
  { name: 'Canvas', token: 'canvas', hex: '#F8FAFC', className: 'bg-canvas border border-border', use: 'Fundo das páginas claras' },
  { name: 'Success', token: 'success', hex: '#059669', className: 'bg-success', use: 'Cobertura confirmada' },
]

const TYPE = [
  { label: 'Display · Plus Jakarta Sans 800', className: 'font-heading text-5xl font-extrabold tracking-tight', sample: 'Conecte-se em O(1)' },
  { label: 'Título · Plus Jakarta Sans 700', className: 'font-heading text-2xl font-bold', sample: 'Gerenciamento de países' },
  { label: 'Corpo · Inter 400', className: 'text-base leading-relaxed', sample: 'Um único eSIM para todos os destinos da sua viagem.' },
  { label: 'Dados · JetBrains Mono 500', className: 'font-mono text-sm font-medium', sample: 'h("BR") = 3 · α = 1.76' },
]

const SHADOWS = [
  { name: 'elev-1', className: 'shadow-elev-1', use: 'Cards em repouso' },
  { name: 'elev-2', className: 'shadow-elev-2', use: 'Hover e tabelas' },
  { name: 'elev-3', className: 'shadow-elev-3', use: 'Resultados e diálogos' },
  { name: 'glow', className: 'shadow-glow', use: 'Estado ativo de rede' },
]

function Section({ id, title, children }: { id: string; title: string; children: React.ReactNode }) {
  return (
    <section aria-labelledby={id} className="flex flex-col gap-6">
      <h2 id={id} className="border-b border-border pb-3 text-xl font-bold text-navy-900">
        {title}
      </h2>
      {children}
    </section>
  )
}

export default function DesignSystemPage() {
  return (
    <>
      {/* v0 Design System Showcase Page */}
      <PageHeader
        eyebrow="Design System"
        title="GlobalSIM · fundamentos visuais"
        description="Uma linguagem que combina a sobriedade de uma operadora de telecom com a precisão de uma estrutura de dados: navy profundo, azul elétrico e o dourado do chip SIM."
      >
        <div className="flex items-center gap-4 rounded-2xl border border-white/10 bg-white/5 p-5">
          <BrandMark className="size-12" />
          <BrandLogo />
        </div>
      </PageHeader>

      <div className="mx-auto flex max-w-7xl flex-col gap-16 px-4 py-14 sm:px-6 lg:px-8">
        <Section id="ds-colors" title="Cores">
          <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {COLORS.map((c) => (
              <li key={c.token} className="overflow-hidden rounded-2xl border border-border bg-card shadow-elev-1">
                <div className={`h-24 ${c.className}`} />
                <div className="flex flex-col gap-1 p-4">
                  <div className="flex items-center justify-between">
                    <p className="font-semibold text-navy-900">{c.name}</p>
                    <span className="font-mono text-xs text-muted-foreground">{c.hex}</span>
                  </div>
                  <p className="font-mono text-xs text-azure">{`--${c.token}`}</p>
                  <p className="text-xs text-muted-foreground">{c.use}</p>
                </div>
              </li>
            ))}
          </ul>
        </Section>

        <Section id="ds-type" title="Tipografia">
          <ul className="flex flex-col divide-y divide-border rounded-2xl border border-border bg-card">
            {TYPE.map((t) => (
              <li key={t.label} className="flex flex-col gap-2 p-6 md:flex-row md:items-baseline md:gap-10">
                <span className="w-64 shrink-0 font-mono text-xs text-muted-foreground">{t.label}</span>
                <span className={`text-navy-900 ${t.className}`}>{t.sample}</span>
              </li>
            ))}
          </ul>
        </Section>

        <Section id="ds-elevation" title="Elevação">
          <ul className="grid grid-cols-2 gap-6 lg:grid-cols-4">
            {SHADOWS.map((s) => (
              <li key={s.name} className={`flex h-32 flex-col justify-end rounded-2xl border border-border bg-card p-4 ${s.className}`}>
                <p className="font-mono text-sm font-semibold text-navy-900">{s.name}</p>
                <p className="text-xs text-muted-foreground">{s.use}</p>
              </li>
            ))}
          </ul>
        </Section>

        <Section id="ds-components" title="Componentes">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-6">
              <p className="text-sm font-semibold text-navy-900">Botões</p>
              <div className="flex flex-wrap gap-3">
                <Button className="bg-azure text-white hover:bg-azure/90">Verificar cobertura</Button>
                <Button variant="outline" className="gap-2">
                  <Plus aria-hidden="true" /> Novo país
                </Button>
                <Button variant="ghost">Cancelar</Button>
                <Button className="bg-destructive text-white hover:bg-destructive/90">Remover</Button>
              </div>
            </div>

            <div className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-6">
              <p className="text-sm font-semibold text-navy-900">Badges de status</p>
              <div className="flex flex-wrap gap-2">
                <NetworkBadge has5G />
                <NetworkBadge has5G={false} />
                <StatusBadge variant="success" dot>Coberto</StatusBadge>
                <StatusBadge variant="warning">2 colisões</StatusBadge>
                <StatusBadge variant="danger">Sem cobertura</StatusBadge>
                <StatusBadge variant="code">BR</StatusBadge>
              </div>
            </div>

            <div className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-6">
              <label htmlFor="ds-input" className="text-sm font-semibold text-navy-900">
                Campo de busca
              </label>
              <div className="relative">
                <Search aria-hidden="true" className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
                <Input id="ds-input" placeholder="Digite um código ISO" className="h-10 pl-9" />
              </div>
            </div>

            <div className="flex flex-col gap-4 rounded-2xl bg-navy p-6">
              <p className="text-sm font-semibold text-white">Nós da lista encadeada</p>
              <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
                <span className="rounded-md border border-cyan bg-cyan/15 px-2.5 py-1.5 font-semibold text-cyan shadow-glow">[03]</span>
                <span className="text-slate-500">{'→'}</span>
                <span className="rounded-md border border-sky/60 bg-sky/10 px-2.5 py-1.5 text-sky">AR</span>
                <span className="text-slate-500">{'→'}</span>
                <span className="rounded-md border border-gold bg-gold/15 px-2.5 py-1.5 text-gold">BR</span>
                <span className="text-slate-500">{'→ null'}</span>
              </div>
            </div>
          </div>
        </Section>
      </div>
    </>
  )
}
