export function PageHeader({
  eyebrow,
  title,
  description,
  children,
}: {
  eyebrow: string
  title: string
  description: string
  children?: React.ReactNode
}) {
  return (
    <section className="relative overflow-hidden bg-navy">
      <div aria-hidden="true" className="bg-grid-navy absolute inset-0 [mask-image:radial-gradient(ellipse_at_top,black,transparent_70%)]" />
      <div className="relative mx-auto flex max-w-7xl flex-col gap-6 px-4 py-12 sm:px-6 md:flex-row md:items-end md:justify-between lg:px-8 lg:py-16">
        <div className="flex max-w-2xl flex-col gap-3">
          <p className="font-mono text-xs font-medium tracking-widest text-cyan uppercase">{eyebrow}</p>
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">{title}</h1>
          <p className="text-base leading-relaxed text-slate-300">{description}</p>
        </div>
        {children}
      </div>
    </section>
  )
}
