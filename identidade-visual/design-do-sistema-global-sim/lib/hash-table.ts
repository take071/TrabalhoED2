export type Country = {
  code: string
  name: string
  region: string
  carriers: string[]
  has5G: boolean
  pricePerGB: number
}

export type HashNode = {
  key: string
  value: Country
  next: HashNode | null
}

export type OperationKind = 'insert' | 'update' | 'delete' | 'search'

export type OperationTrace = {
  kind: OperationKind
  key: string
  index: number
  comparisons: number
  found: boolean
  collided: boolean
  at: number
}

export const DEFAULT_CAPACITY = 17

/**
 * Polynomial rolling hash (base 31) reduced modulo M at every step
 * to keep intermediate values small and the distribution uniform for a prime M.
 */
export function hashKey(key: string, capacity: number = DEFAULT_CAPACITY): number {
  let hash = 0
  for (let i = 0; i < key.length; i++) {
    hash = (hash * 31 + key.charCodeAt(i)) % capacity
  }
  return hash
}

export function hashSteps(key: string, capacity: number = DEFAULT_CAPACITY) {
  const steps: { char: string; code: number; hash: number }[] = []
  let hash = 0
  for (let i = 0; i < key.length; i++) {
    hash = (hash * 31 + key.charCodeAt(i)) % capacity
    steps.push({ char: key[i], code: key.charCodeAt(i), hash })
  }
  return steps
}

export class HashTable {
  readonly capacity: number
  private table: (HashNode | null)[]
  private count = 0
  private collisions = 0
  lastTrace: OperationTrace | null = null

  constructor(capacity: number = DEFAULT_CAPACITY) {
    this.capacity = capacity
    this.table = Array.from({ length: capacity }, () => null)
  }

  get size() {
    return this.count
  }

  get totalCollisions() {
    return this.collisions
  }

  get loadFactor() {
    return this.count / this.capacity
  }

  private normalize(key: string) {
    return key.trim().toUpperCase()
  }

  private trace(t: Omit<OperationTrace, 'at'>) {
    this.lastTrace = { ...t, at: Date.now() }
  }

  insert(country: Country): 'inserted' | 'updated' {
    const key = this.normalize(country.code)
    const index = hashKey(key, this.capacity)
    let node = this.table[index]
    let comparisons = 0

    while (node) {
      comparisons++
      if (node.key === key) {
        node.value = { ...country, code: key }
        this.trace({ kind: 'update', key, index, comparisons, found: true, collided: false })
        return 'updated'
      }
      node = node.next
    }

    const collided = this.table[index] !== null
    if (collided) this.collisions++

    this.table[index] = { key, value: { ...country, code: key }, next: this.table[index] }
    this.count++
    this.trace({ kind: 'insert', key, index, comparisons, found: false, collided })
    return 'inserted'
  }

  search(rawKey: string): Country | null {
    const key = this.normalize(rawKey)
    const index = hashKey(key, this.capacity)
    let node = this.table[index]
    let comparisons = 0

    while (node) {
      comparisons++
      if (node.key === key) {
        this.trace({ kind: 'search', key, index, comparisons, found: true, collided: false })
        return node.value
      }
      node = node.next
    }

    this.trace({ kind: 'search', key, index, comparisons, found: false, collided: false })
    return null
  }

  peek(rawKey: string): Country | null {
    const key = this.normalize(rawKey)
    let node = this.table[hashKey(key, this.capacity)]
    while (node) {
      if (node.key === key) return node.value
      node = node.next
    }
    return null
  }

  remove(rawKey: string): boolean {
    const key = this.normalize(rawKey)
    const index = hashKey(key, this.capacity)
    let node = this.table[index]
    let prev: HashNode | null = null
    let comparisons = 0

    while (node) {
      comparisons++
      if (node.key === key) {
        if (prev) prev.next = node.next
        else this.table[index] = node.next
        this.count--
        this.trace({ kind: 'delete', key, index, comparisons, found: true, collided: false })
        return true
      }
      prev = node
      node = node.next
    }

    this.trace({ kind: 'delete', key, index, comparisons, found: false, collided: false })
    return false
  }

  buckets(): HashNode[][] {
    return this.table.map((head) => {
      const chain: HashNode[] = []
      let node = head
      while (node) {
        chain.push(node)
        node = node.next
      }
      return chain
    })
  }

  values(): Country[] {
    return this.buckets()
      .flat()
      .map((n) => n.value)
      .sort((a, b) => a.name.localeCompare(b.name, 'pt-BR'))
  }

  longestChain(): number {
    return Math.max(0, ...this.buckets().map((b) => b.length))
  }

  emptyBuckets(): number {
    return this.buckets().filter((b) => b.length === 0).length
  }
}
