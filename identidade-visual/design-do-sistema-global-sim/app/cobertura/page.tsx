import type { Metadata } from 'next'
import { CountryTable } from '@/components/coverage/country-table'
import { CoverageChecker } from '@/components/coverage/coverage-checker'
import { PageHeader } from '@/components/page-header'

export const metadata: Metadata = {
  title: 'Cobertura',
  description: 'Verifique a cobertura do eSIM por país em O(1) e gerencie o catálogo de países.',
}

export default function CoveragePage() {
  return (
    <>
      <PageHeader
        eyebrow="Verificador de cobertura · O(1)"
        title="Seu destino tem cobertura?"
        description="Digite o código ISO de duas letras para uma busca direta no bucket h(k). A busca por nome também funciona, mas exige varredura linear."
      />
      <div className="mx-auto flex max-w-7xl flex-col gap-12 px-4 py-12 sm:px-6 lg:px-8">
        <div className="relative z-10 -mt-20 max-w-3xl">
          <CoverageChecker />
        </div>
        <CountryTable />
      </div>
    </>
  )
}
