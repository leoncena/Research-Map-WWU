import dynamic from 'next/dynamic'
import React from 'react'

const MyResponsiveSunburst = dynamic(() => import('./structure_IS_department-sunburst'), {
  ssr: false,
})

interface Props {
  sunburstData: Array<Object>
}

const SunburstChart = ({ sunburstData }: Props) => {
  return (
      <MyResponsiveSunburst Data={sunburstData} />
  )
}
export default SunburstChart
