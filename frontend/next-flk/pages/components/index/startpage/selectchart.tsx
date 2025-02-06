import React from 'react'
import Box from '@mui/material/Box'
import InputLabel from '@mui/material/InputLabel'
import MenuItem from '@mui/material/MenuItem'
import FormControl from '@mui/material/FormControl'
import Select, { SelectChangeEvent } from '@mui/material/Select'
import SunburstChart from '../tab_charts/structure_IS_department-sunburst/sunburstchart'
import NetworkChart from '../tab_charts/topic-network/networkchart'
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'
import IconButton from '@mui/material/IconButton'
import Tooltip from '@mui/material/Tooltip'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import { useGlobalChartContext } from '../../../../contexts/chartContext'
import LineChart from '../tab_charts/topic_trends-linechart/linechart'
import WordCloud from '../tab_charts/topic-overview/wordcloud_maincomponent'
import BarChart from '../tab_charts/research_output-barchart/barchart'

interface Props {
  sunburstData: Array<Object>
  networkData: Array<Object>
  wordcloudData: Array<{ text: string; size: number }>
  trendData: Array<Object>
  barData: Array<Object>
}

export default function SelectChart({
  sunburstData,
  networkData,
  wordcloudData,
  trendData,
  barData,
}: Props) {
  const SUNBURST_DESCRIPTION =
    'This sunburst chart shows the publications sorted by chairs at the top level. After the chair level, the publications are assigned to the professors. On the next level, the publications are categorized by year. On the lowest level the publications can be selected by clicking on them. Then a publication tab appears in which the publications are displayed.'
  const NETWORK_DESCRIPTION =
    'This network chart shows research topics in information systems and their connections. Similar topics are displayed close to each other.'
  const LINE_DESCRIPTION =
    'This linechart shows the number of publications per year on selected topics. A topic consists of three related keywords. Up to three topics can be displayed in the chart at the same time using the drop-down menus, showing the trend of the topics over the years. If a datapoint is clicked, the corresponding publications are revealed. '
  const WORDCLOUD_DESCRIPTION =
    "This wordcloud represents an overview of the institute's activities. The more frequently a word appears in the publications, the more prominently it is displayed."

  const { chart, setChart } = useGlobalChartContext()

  function handleChange(event: SelectChangeEvent) {
    setChart(event.target.value)
  }

  return (
    <div className="mb-8 flex flex-col rounded-b-xl rounded-tr-xl border-2 border-gray-300 p-6 pb-14 shadow-lg">
      <div className="flex flex-row items-center justify-between pb-4">
        <div className="flew-row flex items-center justify-start">
          <div>
            <IconButton onClick={() => setChart('startingpage')}>
              <ArrowBackIcon fontSize="medium" />
            </IconButton>
          </div>
          <div className="ml-8 flex justify-self-start rounded bg-white">
            <Box sx={{ minWidth: 300 }}>
              <FormControl fullWidth>
                <InputLabel id="demo-simple-select-label">Chart</InputLabel>
                <Select
                  labelId="chart-select-label"
                  id="chart-select"
                  value={chart}
                  label="Chart"
                  onChange={handleChange}
                >
                  <MenuItem value="sunburst">
                    Structure of IS Department
                  </MenuItem>
                  <MenuItem value="network">Topic Network</MenuItem>
                  <MenuItem value="linechart">Topic Trends</MenuItem>
                  <MenuItem value="wordcloud">Topic Overview</MenuItem>
                  <MenuItem value="barchart">Research Output</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </div>
        </div>
        <div>
          {chart == 'sunburst' ? (
            <Tooltip title={SUNBURST_DESCRIPTION} placement="left">
              <IconButton>
                <HelpOutlineIcon fontSize="medium" />
              </IconButton>
            </Tooltip>
          ) : (
            ''
          )}
          {chart == 'network' ? (
            <Tooltip title={NETWORK_DESCRIPTION} placement="left">
              <IconButton>
                <HelpOutlineIcon fontSize="medium" />
              </IconButton>
            </Tooltip>
          ) : (
            ''
          )}
          {chart == 'linechart' ? (
            <Tooltip title={LINE_DESCRIPTION} placement="left">
              <IconButton>
                <HelpOutlineIcon fontSize="medium" />
              </IconButton>
            </Tooltip>
          ) : (
            ''
          )}
          {chart == 'wordcloud' ? (
            <Tooltip title={WORDCLOUD_DESCRIPTION} placement="left">
              <IconButton>
                <HelpOutlineIcon fontSize="medium" />
              </IconButton>
            </Tooltip>
          ) : (
            ''
          )}
        </div>
      </div>
      {chart == 'sunburst' ? (
        <SunburstChart sunburstData={sunburstData} />
      ) : (
        <div></div>
      )}
      {chart == 'network' ? (
        <NetworkChart networkData={networkData} />
      ) : (
        <div></div>
      )}
      {chart == 'linechart' ? <LineChart trendData={trendData} /> : <div></div>}
      {chart == 'wordcloud' ? <WordCloud data={wordcloudData} /> : <div></div>}
      {chart == 'barchart' ? <BarChart barData={barData} /> : <div></div>}
    </div>
  )
}
