import React from 'react'
import SearchContainer from '../tab_search/searchcontainer'
import Search from '../tab_search/search'
import SelectChart from '../startpage/selectchart'
import { useGlobalTabContext } from '../../../../contexts/tabContext'
import Publications from '../tab_publications/publications.jsx'
import Author from '../tab_author/author'
import { useGlobalChartContext } from '../../../../contexts/chartContext'
import StartingPage from '../startpage/startingpage'

interface Props {
  sunburstData: any
  networkData: any
  wordcloudData: any
  trendData: any
  barData: any
}

function TabContent({
  sunburstData,
  networkData,
  wordcloudData,
  trendData,
  barData,
}: Props) {
  const { tab } = useGlobalTabContext()
  const { chart } = useGlobalChartContext()
  return (
    <div>
      {/* Chart Section */}
      {tab === 'browse' && chart === 'startingpage' ? <StartingPage /> : ''}
      {tab === 'browse' && chart != 'startingpage' ? (
        <SelectChart
          sunburstData={sunburstData}
          networkData={networkData}
          wordcloudData={wordcloudData}
          trendData={trendData}
          barData={barData}
        />
      ) : (
        ''
      )}
      {tab === 'search' ? (
        <SearchContainer>
          <Search />
        </SearchContainer>
      ) : (
        ''
      )}
      {tab === 'publication' ? <Publications /> : ''}
      {tab === 'author' ? <Author /> : ''}
    </div>
  )
}

export default TabContent
