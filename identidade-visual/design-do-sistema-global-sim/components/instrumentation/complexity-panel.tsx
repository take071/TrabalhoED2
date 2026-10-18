const ROWS = [
  { op: 'Busca', avg: 'O(1 + α)', worst: 'O(n)', note: 'Percorre apenas a cadeia do bucket h(k).' },
  { op: 'Inserção', avg: 'O(1)', worst: 'O(n)', note: 'Verifica duplicata e insere na cabeça da lista.' },
  { op: 'Remoção', avg: 'O(1 + α)', worst: 'O(n)', note: 'Desencadeia o nó ajustando o ponteiro next.' },
  { op: 'Busca por nome', avg: 'O(n)', worst: 'O(n)', note: 'Nome não é chave: varredura completa.' },
]

export function ComplexityPanel() {
  return (
    <section aria-labelledby="complexity-title" className="overflow-hidden rounded-2xl border border-border bg-card shadow-elev-1">
      <header className="border-b border-border px-5 py-4">
        <h2 id="complexity-title" className="font-heading text-base font-semibold text-navy-900">
          Análise assintótica
        </h2>
        <p className="text-sm text-muted-foreground">Custos esperados com hashing uniforme simples.</p>
      </header>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[560px] text-left text-sm">
          <thead className="bg-secondary/70 text-xs tracking-wide text-muted-foreground uppercase">
            <tr>
              <th scope="col" className="px-5 py-2.5 font-semibold">Operação</th>
              <th scope="col" className="px-5 py-2.5 font-semibold">Caso médio</th>
              <th scope="col" className="px-5 py-2.5 font-semibold">Pior caso</th>
              <th scope="col" className="px-5 py-2.5 font-semibold">Observação</th>
            </tr>
          </thead>
          <tbody>
            {ROWS.map((r) => (
              <tr key={r.op} className="border-t border-border odd:bg-white even:bg-canvas">
                <th scope="row" className="px-5 py-3 font-medium text-navy-900">{r.op}</th>
                <td className="px-5 py-3 font-mono font-semibold text-azure">{r.avg}</td>
                <td className="px-5 py-3 font-mono text-gold-600">{r.worst}</td>
                <td className="px-5 py-3 text-muted-foreground">{r.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
