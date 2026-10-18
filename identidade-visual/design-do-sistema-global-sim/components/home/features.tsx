import { Gauge, QrCode, Route } from 'lucide-react'

const FEATURES = [
  {
    icon: QrCode,
    title: 'Ativação instantânea',
    body: 'Escaneie o QR Code e conecte-se assim que o avião pousar. Sem chip físico, sem fila na loja da operadora.',
  },
  {
    icon: Route,
    title: 'Roteamento multidestino',
    body: 'Viaja por vários países? O GlobalSIM escolhe a melhor operadora local em cada fronteira automaticamente.',
  },
  {
    icon: Gauge,
    title: 'Cobertura em O(1)',
    body: 'Cada país é indexado pelo código ISO em uma tabela hash de 17 buckets com encadeamento separado.',
  },
]

export function Features() {
  return (
    <section aria-labelledby="features-title" className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
      <div className="flex max-w-2xl flex-col gap-3">
        <p className="font-mono text-xs font-medium tracking-widest text-azure uppercase">Por que GlobalSIM</p>
        <h2 id="features-title" className="text-3xl font-bold tracking-tight text-navy-900 sm:text-4xl">
          Conectividade de telecom com a precisão de uma estrutura de dados.
        </h2>
      </div>
      <ul className="mt-12 grid grid-cols-1 gap-6 md:grid-cols-3">
        {FEATURES.map(({ icon: Icon, title, body }) => (
          <li key={title} className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-6 shadow-elev-1 transition-shadow hover:shadow-elev-2">
            <span className="flex size-11 items-center justify-center rounded-xl bg-accent text-azure-600">
              <Icon aria-hidden="true" className="size-5" />
            </span>
            <h3 className="text-lg font-semibold text-navy-900">{title}</h3>
            <p className="text-sm leading-relaxed text-muted-foreground">{body}</p>
          </li>
        ))}
      </ul>
    </section>
  )
}
