import dynamic from 'next/dynamic'

const MyResponsiveLine = dynamic(
  () => import('./topic_trends-linechart'),
  {
    ssr: false,
  }
)

interface Props {
  trendData: Array<Object>
}

const LineChart = ({ trendData }: Props) => {
  return (
    <div className="h-full">
      <MyResponsiveLine Data={trendData} />
    </div>
  )
}
export default LineChart
