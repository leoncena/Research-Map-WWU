import React from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { useGlobalChartContext } from '../../../../contexts/chartContext'

function StartingPageElement({ charttype }: { charttype: string }) {
  const { setChart } = useGlobalChartContext()

  function handleButtonClick() {
    setChart(charttype)
  }

  function getNameFromIdentifier(identifier: String) {
    switch (identifier) {
      case 'sunburst':
        return 'Structure of IS Department'
      case 'network':
        return 'Topic Network'
      case 'linechart':
        return 'Topic Trends'
      case 'wordcloud':
        return 'Topic Overview'
      case 'barchart':
        return 'Research Output'
    }

    return 'startingpage'
  }

  return (
    <Link href="" onClick={handleButtonClick} shallow>
      <div className="delay-50 text-700 rounded-xl bg-transparent p-2 font-semibold transition ease-in-out hover:scale-105 hover:shadow-xl">
        <div className="flex justify-center p-4">
          {charttype === 'sunburst' ? (
            <Image
              src={require('../../../../public/images/sunburst.JPG')}
              alt="wwu"
              width={300}
              height={300}
            />
          ) : (
            ''
          )}
          {charttype === 'network' ? (
            <Image
              src={require('../../../../public/images/network.JPG')}
              alt="wwu"
              width={300}
              height={300}
            />
          ) : (
            ''
          )}
          {charttype === 'linechart' ? (
            <Image
              src={require('../../../../public/images/line.jpg')}
              alt="wwu"
              width={300}
              height={300}
            />
          ) : (
            ''
          )}
          {charttype === 'wordcloud' ? (
            <Image
              src={require('../../../../public/images/wordcloud.jpg')}
              alt="wwu"
              width={300}
              height={300}
            />
          ) : (
            ''
          )}
          {charttype === 'barchart' ? (
            <Image
              src={require('../../../../public/images/output.jpg')}
              alt="wwu"
              width={300}
              height={300}
            />
          ) : (
            ''
          )}
        </div>
        <div className="text-l flex justify-center font-bold">
          {' '}
          {getNameFromIdentifier(charttype)}{' '}
        </div>
      </div>
    </Link>
  )
}

export default StartingPageElement
