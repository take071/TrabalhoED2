import { cn } from '@/lib/utils'

export function BrandMark({ className }: { className?: string }) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        'relative inline-flex size-8 items-center justify-center rounded-lg bg-gradient-to-br from-azure to-azure-600 shadow-glow',
        className,
      )}
    >
      <span className="grid size-4 grid-cols-2 gap-px overflow-hidden rounded-[3px] bg-gold-600 p-px">
        <span className="rounded-[1px] bg-gold" />
        <span className="rounded-[1px] bg-gold" />
        <span className="rounded-[1px] bg-gold" />
        <span className="rounded-[1px] bg-gold" />
      </span>
      <span className="absolute -top-0.5 -right-0.5 size-2 rounded-full bg-cyan ring-2 ring-navy" />
    </span>
  )
}

export function BrandLogo({ className, tone = 'light' }: { className?: string; tone?: 'light' | 'dark' }) {
  return (
    <span className={cn('inline-flex items-center gap-2.5', className)}>
      <BrandMark />
      <span
        className={cn(
          'font-heading text-lg font-bold tracking-tight',
          tone === 'light' ? 'text-white' : 'text-navy-900',
        )}
      >
        Global<span className="text-sky">SIM</span>
      </span>
    </span>
  )
}
