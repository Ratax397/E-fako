import { useEffect, useState, useRef } from 'react'
import { filterDatasearch } from '../utils/Ufilterdatasearch'

export function useFilterData<T>(data: T[], search: string, keys: (keyof T)[]): T[] {
  const [filtered, setFiltered] = useState<T[]>(data)
  const dataRef = useRef<T[]>(data)

  useEffect(() => {
    dataRef.current = data
  }, [data])

  useEffect(() => {
    const result = filterDatasearch(dataRef.current, search, keys)

    if (JSON.stringify(result) !== JSON.stringify(filtered)) {
      setFiltered(search === '' ? [...dataRef.current] : result)
    }
  }, [search, keys, filtered]) 

  return filtered
}
