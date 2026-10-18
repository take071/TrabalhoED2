import { AcademicCta } from '@/components/home/academic-cta'
import { Features } from '@/components/home/features'
import { Hero } from '@/components/home/hero'
import { PopularDestinations } from '@/components/home/popular-destinations'

export default function HomePage() {
  return (
    <>
      <Hero />
      <Features />
      <PopularDestinations />
      <AcademicCta />
    </>
  )
}
