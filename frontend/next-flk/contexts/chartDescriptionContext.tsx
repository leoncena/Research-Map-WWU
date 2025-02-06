import { createContext, useContext } from 'react'
import React from 'react'

export const GlobalChartDescriptionContext = createContext<{
  ChartDescription: string
  setChartDescription: (newTab: string) => void
}>({
  ChartDescription: 'none',
  setChartDescription: () => {},
})

export const useGlobalChartDescriptionContext = () =>
  useContext(GlobalChartDescriptionContext)
