import Link from 'next/link'
import { ArrowRight } from 'lucide-react'

const CODE = `int hash(String k) {
  int h = 0;
  for (char c : k.toCharArray())
    h = (h * 31 + c) % M;   // M = 17
  return h;
}`

export function AcademicCta() {
  return (
    <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
      <div className="relative grid grid-cols-1 gap-10 overflow-hidden rounded-3xl bg-navy p-8 shadow-elev-3 sm:p-12 lg:grid-cols-2 lg:items-center">
        <div aria-hidden="true" className="absolute -right-24 -bottom-24 size-80 rounded-full bg-cyan/20 blur-3xl" />
        <div className="relative flex flex-col gap-5">
          <p className="font-mono text-xs font-medium tracking-widest text-cyan uppercase">Estruturas de Dados II</p>
          <h2 className="text-3xl font-bold tracking-tight text-white">Veja a tabela hash funcionando em tempo real.</h2>
          <p className="leading-relaxed text-slate-300">
            Acompanhe capacidade, fator de carga α e colisões enquanto você insere, edita e remove países. Cada
            operação mostra o bucket calculado e o percurso na lista encadeada.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link
              href="/instrumentacao"
              className="inline-flex h-10 items-center gap-2 rounded-lg bg-azure px-5 text-sm font-semibold text-white hover:bg-azure/90"
            >
              Abrir instrumentação
              <ArrowRight aria-hidden="true" className="size-4" />
            </Link>
            <Link
              href="/cobertura"
              className="inline-flex h-10 items-center rounded-lg border border-white/15 px-5 text-sm font-semibold text-white hover:bg-white/5"
            >
              Gerenciar países
            </Link>
          </div>
        </div>
        <pre className="relative overflow-x-auto rounded-2xl border border-white/10 bg-navy-900 p-6 font-mono text-sm leading-relaxed text-slate-300">
          <code>{CODE}</code>
        </pre>
      </div>
    </section>
  )
}
