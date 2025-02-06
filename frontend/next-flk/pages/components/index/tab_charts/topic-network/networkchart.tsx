import dynamic from 'next/dynamic'
import React from 'react';

const MyResponsiveNetwork = dynamic(() => import('./topic-network'), {
  ssr: false,
})

const NetworkChart = ({ networkData }:any) => {
  return (
      <MyResponsiveNetwork Data={networkData} />
  )
}
export default NetworkChart;
