'use client'

import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { COUNTRIES_SEED } from '@/lib/countries-seed'
import { HashTable, type Country } from '@/lib/hash-table'

type HashTableContextValue = {
  table: HashTable
  version: number
  upsert: (country: Country, previousCode?: string) => 'inserted' | 'updated'
  remove: (code: string) => boolean
  search: (code: string) => Country | null
  reset: () => void
}

const HashTableContext = createContext<HashTableContextValue | null>(null)

function createSeededTable() {
  const table = new HashTable()
  for (const country of COUNTRIES_SEED) table.insert(country)
  table.lastTrace = null
  return table
}

export function HashTableProvider({ children }: { children: React.ReactNode }) {
  const [table, setTable] = useState(createSeededTable)
  const [version, setVersion] = useState(0)
  const bump = useCallback(() => setVersion((v) => v + 1), [])

  const upsert = useCallback(
    (country: Country, previousCode?: string) => {
      if (previousCode && previousCode.toUpperCase() !== country.code.toUpperCase()) {
        table.remove(previousCode)
      }
      const result = table.insert(country)
      bump()
      return result
    },
    [table, bump],
  )

  const remove = useCallback(
    (code: string) => {
      const ok = table.remove(code)
      bump()
      return ok
    },
    [table, bump],
  )

  const search = useCallback(
    (code: string) => {
      const result = table.search(code)
      bump()
      return result
    },
    [table, bump],
  )

  const reset = useCallback(() => {
    setTable(createSeededTable())
    bump()
  }, [bump])

  const value = useMemo(
    () => ({ table, version, upsert, remove, search, reset }),
    [table, version, upsert, remove, search, reset],
  )

  return <HashTableContext.Provider value={value}>{children}</HashTableContext.Provider>
}

export function useHashTable() {
  const ctx = useContext(HashTableContext)
  if (!ctx) throw new Error('useHashTable deve ser usado dentro de HashTableProvider')
  return ctx
}
