import Link from 'next/link'
import { BrandLogo } from '@/components/brand-logo'

export function SiteFooter() {
  return (
    <footer className="border-t border-white/10 bg-navy text-slate-400">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-10 sm:px-6 md:flex-row md:items-center md:justify-between lg:px-8">
        <div className="flex flex-col gap-2">
          <BrandLogo />
          <p className="max-w-sm text-sm leading-relaxed">
            Projeto acadêmico de Estruturas de Dados II — tabela hash com encadeamento separado aplicada ao roteamento
            de eSIM internacional.
          </p>
        </div>
        <nav aria-label="Rodapé">
          <ul className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
            <li><Link className="hover:text-white" href="/cobertura">Cobertura</Link></li>
            <li><Link className="hover:text-white" href="/instrumentacao">Instrumentação</Link></li>
            <li><Link className="hover:text-white" href="/design-system">Design System</Link></li>
          </ul>
        </nav>
        <p className="font-mono text-xs">{'h(k) = Σ k[i]·31^(n-i-1) mod 17'}</p>
      </div>
    </footer>
  )
}
