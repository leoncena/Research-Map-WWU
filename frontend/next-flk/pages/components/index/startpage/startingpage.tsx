import React from 'react'
import StartingPageElement from './startingpagegraph'
import Dashboard from './dashboard'

function StartingPage() {
  return (
    <div className="flex flex-col mb-2 border-2 border-gray-300 shadow-lg rounded-b-xl rounded-tr-xl">
      <Dashboard />
      <div className="flex mx-8 border-b-2 border-gray-300"></div>
      <div className="flex flex-col">
        <div className="grid grid-cols-3 gap-2 m-4">
          <StartingPageElement charttype="sunburst" />
          <StartingPageElement charttype="network" />
          <StartingPageElement charttype="linechart" />
        </div>
        <div className="grid grid-cols-2 gap-2 m-4">
          <StartingPageElement charttype="wordcloud" />
          <StartingPageElement charttype="barchart" />
        </div>
      </div>
    </div>
  )
}

export default StartingPage
