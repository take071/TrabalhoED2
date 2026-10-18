import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight, Zap } from 'lucide-react'
import { CoverageChecker } from '@/components/coverage/coverage-checker'

const STATS = [
  { value: 'O(1)', label: 'busca de cobertura' },
  { value: '< 60s', label: 'ativação do eSIM' },
  { value: '5G', label: 'nas principais rotas' },
]

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-navy">
      <div aria-hidden="true" className="bg-grid-navy absolute inset-0 [mask-image:radial-gradient(ellipse_at_center,black,transparent_75%)]" />
      <div aria-hidden="true" className="absolute -top-40 left-1/2 h-[480px] w-[900px] -translate-x-1/2 rounded-full bg-azure/25 blur-[120px]" />

      <div className="relative mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 px-4 pt-16 pb-20 sm:px-6 lg:grid-cols-[1.05fr_1fr] lg:px-8 lg:pt-24 lg:pb-28">
        <div className="flex flex-col gap-8">
          <span className="inline-flex w-fit items-center gap-2 rounded-full border border-gold/30 bg-gold/10 px-3 py-1 text-xs font-semibold text-gold">
            <Zap aria-hidden="true" className="size-3.5" />
            Ativação instantânea via QR Code
          </span>

          <div className="flex flex-col gap-5">
            <h1 className="text-4xl leading-[1.05] font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl">
              Dados móveis no mundo inteiro,{' '}
              <span className="bg-gradient-to-r from-sky to-cyan bg-clip-text text-transparent">roteados na velocidade da luz.</span>
            </h1>
            <p className="max-w-xl text-lg leading-relaxed text-slate-300">
              Um único eSIM para todos os destinos da sua viagem. Otimizamos automaticamente a rota de dados entre
              operadoras locais — e verificamos a cobertura em tempo constante.
            </p>
          </div>

          <CoverageChecker variant="dark" />

          <dl className="grid max-w-lg grid-cols-3 gap-6 border-t border-white/10 pt-6">
            {STATS.map((s) => (
              <div key={s.label} className="flex flex-col gap-1">
                <dt className="order-2 text-xs text-slate-400">{s.label}</dt>
                <dd className="order-1 font-mono text-2xl font-semibold text-white">{s.value}</dd>
              </div>
            ))}
          </dl>
        </div>

        <div className="relative hidden lg:block">
          <div className="relative aspect-square w-full">
            <Image
              src="/images/globe-routes.png"
              alt="Globo digital com rotas de dados conectando cidades ao redor do mundo"
              fill
              priority
              sizes="(min-width: 1024px) 560px, 100vw"
              className="object-contain [mask-image:radial-gradient(circle,black_55%,transparent_72%)]"
            />
          </div>
          <div className="absolute top-10 right-0 flex items-center gap-3 rounded-xl border border-white/10 bg-navy-900/80 px-4 py-3 shadow-elev-3 backdrop-blur">
            <span className="size-2 rounded-full bg-cyan shadow-glow" />
            <div className="flex flex-col">
              <span className="font-mono text-xs text-slate-400">{'GRU → LIS → FCO'}</span>
              <span className="text-sm font-semibold text-white">3 destinos · 1 eSIM</span>
            </div>
          </div>
          <Link
            href="/instrumentacao"
            className="absolute bottom-12 left-0 flex items-center gap-3 rounded-xl border border-white/10 bg-navy-900/80 px-4 py-3 shadow-elev-3 backdrop-blur transition-colors hover:border-cyan/40"
          >
            <span className="font-mono text-sm font-semibold text-gold">{'h("BR") = 3'}</span>
            <span className="text-sm text-slate-300">Ver tabela hash</span>
            <ArrowRight aria-hidden="true" className="size-4 text-slate-400" />
          </Link>
        </div>
      </div>
    </section>
  )
}
