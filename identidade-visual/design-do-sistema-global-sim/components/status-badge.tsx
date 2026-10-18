import { cn } from '@/lib/utils'

type Variant = '5g' | '4g' | 'success' | 'warning' | 'danger' | 'info' | 'code'

const VARIANTS: Record<Variant, string> = {
  '5g': 'border-cyan/40 bg-cyan/10 text-azure-600',
  '4g': 'border-slate-300 bg-slate-100 text-slate-600',
  success: 'border-emerald-200 bg-emerald-50 text-success',
  warning: 'border-amber-200 bg-amber-50 text-gold-600',
  danger: 'border-red-200 bg-red-50 text-destructive',
  info: 'border-blue-200 bg-blue-50 text-azure',
  code: 'border-border bg-white font-mono text-navy-900',
}

export function StatusBadge({
  variant,
  children,
  dot = false,
  className,
}: {
  variant: Variant
  children: React.ReactNode
  dot?: boolean
  className?: string
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold whitespace-nowrap',
        VARIANTS[variant],
        className,
      )}
    >
      {dot && <span aria-hidden="true" className="size-1.5 rounded-full bg-current" />}
      {children}
    </span>
  )
}

export function NetworkBadge({ has5G }: { has5G: boolean }) {
  return has5G ? (
    <StatusBadge variant="5g" dot>
      5G ativo
    </StatusBadge>
  ) : (
    <StatusBadge variant="4g" dot>
      4G LTE
    </StatusBadge>
  )
}
