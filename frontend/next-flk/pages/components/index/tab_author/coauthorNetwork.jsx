import useSWR from 'swr'
import { useGlobalAuthorContext } from '../../../../contexts/authorContext'
import CoauthorNetworkChart from './coauthor_networkchart'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'
import IconButton from '@mui/material/IconButton'
import Tooltip from '@mui/material/Tooltip'

function CoauthorNetwork() {
  const NETWORK_DESCRIPTION =
    'This network represents with which researchers the author has collaborated.'
  const { author } = useGlobalAuthorContext()
  const fetcher = (...args) => fetch(...args).then((res) => res.json())

  const { data, error, isLoading } = useSWR('/api/coauthor/' + author, fetcher)
  if (error) return <div>failed to load</div>
  if (isLoading) return <div>loading...</div>
  return (
    <div className="flex flex-col">
      <div className="flex justify-end">
        <Tooltip title={NETWORK_DESCRIPTION} placement="bottom">
          <IconButton>
            <HelpOutlineIcon />
          </IconButton>
        </Tooltip>
      </div>

      <CoauthorNetworkChart networkData={data} />
    </div>
  )
}
export default CoauthorNetwork
