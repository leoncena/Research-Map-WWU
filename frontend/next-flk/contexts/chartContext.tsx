import { createContext, useContext } from 'react'

/* Purpose of this context:
* This context saves the type of the last selected chart in the "chart"-tab. When the user clicks on the "chart"-tab, the interactive research map
* the chart thats corresponds to the type that is saved in this context.
* 
* Valid entries:
* - startingpage
* - sunburst
* - network
* - linechart
* - wordcloud
* - barchart
* 
* In order to see, which type of chart corresponds to which view, read the frontend-chapter of the documentation.
*/

export const GlobalChartContext = createContext<{
  chart: string
  setChart: (newChart: string) => void
}>({
  chart: 'sunburst',
  setChart: () => {},
})

export const useGlobalChartContext = () => useContext(GlobalChartContext)