import { cn } from '@/lib/utils'

export function CountryFlag({
  code,
  name,
  className,
}: {
  code: string
  name: string
  className?: string
}) {
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={`https://flagcdn.com/w80/${code.toLowerCase()}.png`}
      alt={`Bandeira: ${name}`}
      width={40}
      height={30}
      loading="lazy"
      className={cn('h-6 w-8 rounded-[3px] object-cover ring-1 ring-black/10', className)}
    />
  )
}
