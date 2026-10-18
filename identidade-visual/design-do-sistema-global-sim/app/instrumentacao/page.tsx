import type { Metadata } from 'next'
import { BucketGrid } from '@/components/instrumentation/bucket-grid'
import { ComplexityPanel } from '@/components/instrumentation/complexity-panel'
import { MetricsCards } from '@/components/instrumentation/metrics-cards'
import { PageHeader } from '@/components/page-header'

export const metadata: Metadata = {
  title: 'Instrumentação',
  description: 'Painel acadêmico da tabela hash: capacidade, fator de carga, colisões e visualização dos 17 buckets.',
}

export default function InstrumentationPage() {
  return (
    <>
      <PageHeader
        eyebrow="Painel de instrumentação"
        title="Tabela hash com encadeamento separado"
        description="Métricas em tempo real da estrutura que indexa os países por código ISO. Cada bucket aponta para uma lista ligada de NoHash, terminada em null."
      />
      <div className="mx-auto flex max-w-7xl flex-col gap-8 px-4 py-12 sm:px-6 lg:px-8">
        <MetricsCards />
        <BucketGrid />
        <ComplexityPanel />
      </div>
    </>
  )
}
