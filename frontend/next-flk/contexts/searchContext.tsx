import { createContext, useContext } from 'react'

export const GlobalSearchContext = createContext<{
  dquery: string
  setQuery: (newTab: string) => void
}>({
  dquery: '',
  setQuery: () => {},
})

export const useGlobalSearchContext = () => useContext(GlobalSearchContext)
