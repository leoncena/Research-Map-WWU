import React from 'react'
import Tabs from './tabs'
import TabContent from './tabcontent'
import { useState } from 'react'
import { GlobalTabPrevContext } from '../../../../contexts/tabPrevContext'
import { GlobalTabContext } from '../../../../contexts/tabContext'
import { GlobalPublicationContext } from '../../../../contexts/publicationContext'
import { GlobalSearchContext } from '../../../../contexts/searchContext'
import { GlobalAuthorContext } from '../../../../contexts/authorContext'
import { GlobalChartContext } from '../../../../contexts/chartContext'

interface Props {
  sunburstData: Array<Object>
  networkData: Array<Object>
  wordcloudData: Array<Object>
  trendData: Array<Object>
  barData: Array<Object>
}

function Content({ sunburstData, networkData, wordcloudData, trendData, barData }: Props) {
  const [tab, setTab] = useState<string>('browse')
  const [tabPrev, setTabPrev] = useState<string>('browse')
  const [dquery, setQuery] = useState<string>('')
  const [publication, setPublication] = useState<string>('none')
  const [author, setAuthor] = useState<string>('none')
  const [chart, setChart] = useState<string>('startingpage')

  return (
    <GlobalAuthorContext.Provider value={{ author, setAuthor }}>
      <GlobalPublicationContext.Provider
        value={{ publication, setPublication }}
      >
        <GlobalTabContext.Provider value={{ tab, setTab }}>
          <GlobalTabPrevContext.Provider value= {{ tabPrev, setTabPrev}}>
          <GlobalSearchContext.Provider value={{ dquery, setQuery }}>
            <GlobalChartContext.Provider value={{ chart, setChart }}>
              <Tabs />
              <TabContent
                sunburstData={sunburstData}
                networkData={networkData}
                wordcloudData={wordcloudData}
                trendData={trendData}
                barData={barData}
              />
            </GlobalChartContext.Provider>
          </GlobalSearchContext.Provider>
          </GlobalTabPrevContext.Provider>
        </GlobalTabContext.Provider>
      </GlobalPublicationContext.Provider>
    </GlobalAuthorContext.Provider>
  )
}

export default Content
