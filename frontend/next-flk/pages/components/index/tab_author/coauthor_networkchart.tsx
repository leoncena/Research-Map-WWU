import dynamic from 'next/dynamic'

const MyResponsiveNetwork = dynamic(
  () => import('../tab_charts/coauthor-network/coauthor-network'),
  {
    ssr: false,
  }
)

const CoauthorNetworkChart = ({ networkData }: any) => {
  return (
    <MyResponsiveNetwork Data={networkData} />
  )
}
export default CoauthorNetworkChart
