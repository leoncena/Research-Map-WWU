import useSWR from 'swr'
import { useGlobalAuthorContext } from '../../../../contexts/authorContext'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'
import IconButton from '@mui/material/IconButton'
import Tooltip from '@mui/material/Tooltip'
import Wordcloud_author from '../tab_charts/topic-overview/wordcloud_author'

function WordCloud() {
  const WORDCLOUD_DESCRIPTION =
    'The Wordcloud shows which topics the author has dealt with in the last years. The more often a word appears in his publications, the more prominently it is displayed. The period of the considered publications can be selected via the slider.'
  const { author } = useGlobalAuthorContext()
  const fetcher = (...args) => fetch(...args).then((res) => res.json())

  const { data, error, isLoading } = useSWR(
    '/api/wcloudauthor/' + author,
    fetcher
  )
  if (error) return <div>failed to load</div>
  if (isLoading) return <div>loading...</div>
  return (
    <div className="flex flex-col">
      <div className="flex justify-end">
        <Tooltip title={WORDCLOUD_DESCRIPTION} placement="bottom">
          <IconButton>
            <HelpOutlineIcon />
          </IconButton>
        </Tooltip>
      </div>

      <Wordcloud_author dataInput={data} />
    </div>
  )
}
export default WordCloud
