import type { Country } from './hash-table'

export const REGIONS = [
  'América do Sul',
  'América do Norte',
  'Europa',
  'Ásia',
  'Oceania',
  'África',
  'Oriente Médio',
] as const

export const COUNTRIES_SEED: Country[] = [
  { code: 'BR', name: 'Brasil', region: 'América do Sul', carriers: ['Vivo', 'Claro', 'TIM'], has5G: true, pricePerGB: 4.5 },
  { code: 'US', name: 'Estados Unidos', region: 'América do Norte', carriers: ['AT&T', 'T-Mobile', 'Verizon'], has5G: true, pricePerGB: 4.9 },
  { code: 'JP', name: 'Japão', region: 'Ásia', carriers: ['NTT Docomo', 'SoftBank', 'KDDI au'], has5G: true, pricePerGB: 5.5 },
  { code: 'IT', name: 'Itália', region: 'Europa', carriers: ['TIM', 'Vodafone', 'WindTre'], has5G: true, pricePerGB: 3.9 },
  { code: 'PT', name: 'Portugal', region: 'Europa', carriers: ['MEO', 'NOS', 'Vodafone'], has5G: true, pricePerGB: 3.5 },
  { code: 'FR', name: 'França', region: 'Europa', carriers: ['Orange', 'SFR', 'Bouygues'], has5G: true, pricePerGB: 3.9 },
  { code: 'DE', name: 'Alemanha', region: 'Europa', carriers: ['Telekom', 'Vodafone', 'O2'], has5G: true, pricePerGB: 4.2 },
  { code: 'ES', name: 'Espanha', region: 'Europa', carriers: ['Movistar', 'Orange', 'Vodafone'], has5G: true, pricePerGB: 3.7 },
  { code: 'GB', name: 'Reino Unido', region: 'Europa', carriers: ['EE', 'Vodafone', 'O2', 'Three'], has5G: true, pricePerGB: 4.0 },
  { code: 'AR', name: 'Argentina', region: 'América do Sul', carriers: ['Personal', 'Claro', 'Movistar'], has5G: false, pricePerGB: 5.9 },
  { code: 'CL', name: 'Chile', region: 'América do Sul', carriers: ['Entel', 'Movistar', 'WOM'], has5G: true, pricePerGB: 5.2 },
  { code: 'MX', name: 'México', region: 'América do Norte', carriers: ['Telcel', 'AT&T México'], has5G: true, pricePerGB: 5.4 },
  { code: 'CA', name: 'Canadá', region: 'América do Norte', carriers: ['Rogers', 'Bell', 'Telus'], has5G: true, pricePerGB: 6.2 },
  { code: 'AU', name: 'Austrália', region: 'Oceania', carriers: ['Telstra', 'Optus', 'Vodafone'], has5G: true, pricePerGB: 5.8 },
  { code: 'KR', name: 'Coreia do Sul', region: 'Ásia', carriers: ['SK Telecom', 'KT', 'LG U+'], has5G: true, pricePerGB: 4.8 },
  { code: 'TH', name: 'Tailândia', region: 'Ásia', carriers: ['AIS', 'True', 'dtac'], has5G: true, pricePerGB: 3.2 },
  { code: 'IN', name: 'Índia', region: 'Ásia', carriers: ['Jio', 'Airtel', 'Vi'], has5G: true, pricePerGB: 2.9 },
  { code: 'ZA', name: 'África do Sul', region: 'África', carriers: ['Vodacom', 'MTN', 'Cell C'], has5G: false, pricePerGB: 6.5 },
  { code: 'AE', name: 'Emirados Árabes', region: 'Oriente Médio', carriers: ['Etisalat', 'du'], has5G: true, pricePerGB: 6.9 },
  { code: 'NL', name: 'Países Baixos', region: 'Europa', carriers: ['KPN', 'Vodafone', 'Odido'], has5G: true, pricePerGB: 3.8 },
  { code: 'EG', name: 'Egito', region: 'África', carriers: ['Vodafone', 'Orange', 'Etisalat'], has5G: false, pricePerGB: 5.6 },
]
