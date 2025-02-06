import dynamic from 'next/dynamic'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'
import IconButton from '@mui/material/IconButton'
import Tooltip from '@mui/material/Tooltip'

const MyResponsiveBar = dynamic(() => import('./research_output-barchart'), {
  ssr: false,
})

interface Props {
  barData: Array<Object>
}

const BarChart = ({ barData }: Props) => {
  const BAR_DESCRIPTION =
    'This bar chart represents the number of published publications of the Institute of Information Systems per year. The number of publications per year is broken down for each chair individually.'
  return (
    <div className="h-[60vh] md:h-[80vh] xl:h-[60vh]">
      <div className="flex justify-end">
        <Tooltip title={BAR_DESCRIPTION} placement="left" className="justify-end">
          <IconButton>
            <HelpOutlineIcon />
          </IconButton>
        </Tooltip>
      </div>
      <MyResponsiveBar Data={barData} />
    </div>
  )
}
export default BarChart
