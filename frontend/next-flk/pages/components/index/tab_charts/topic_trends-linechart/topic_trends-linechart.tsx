import React, { useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import Box from '@mui/material/Box'
import InputLabel from '@mui/material/InputLabel'
import MenuItem from '@mui/material/MenuItem'
import Select, { SelectChangeEvent } from '@mui/material/Select'
import FormControl from '@mui/material/FormControl'
import PublicationSnippet from '../../util/publicationsnippet'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

function TopicTrendLineChart({ Data }: any) {
  //States that define the clicked coordinate
  const [clicked, setClicked] = useState(false)

  // Current selected article IDS
  const emptyIds: string[] = []
  const [articleIds, setArticleIds] = useState(emptyIds)

  // State for current topic and year
  const [topic, setTopic] = useState('none')
  const [year, setYear] = useState('none')

  // States for current topics and labes selected in dropdown menu
  const [topicDrop1, setTopicDrop1] = useState('Select a topic')
  const [topicDrop2, setTopicDrop2] = useState('Select a topic')
  const [topicDrop3, setTopicDrop3] = useState('Select a topic')
  const [labelDrop1, setLabelDrop1] = useState('Select a topic')
  const [labelDrop2, setLabelDrop2] = useState('Select a topic')
  const [labelDrop3, setLabelDrop3] = useState('Select a topic')

  //Data for all three lines
  const data = {
    datasets: [
      {
        //label of selected topic from first dropdown menu
        label: `${labelDrop1}`,
        data: Data,
        //use topic from first dropdown menu
        parsing: {
          xAxisKey: 'year',
          yAxisKey: `keywords.${topicDrop1}.count`,
        },
        //line color first dropdown
        borderColor: 'rgb(100, 64, 170)',
        backgroundColor: 'rgb(100, 64, 170)',
      },
      {
        //label of selected topic from second dropdown menu
        label: `${labelDrop2}`,
        data: Data,
        //use topic from second dropdown menu
        parsing: {
          xAxisKey: 'year',
          yAxisKey: `keywords.${topicDrop2}.count`,
        },
        //line color second dropdown
        borderColor: 'rgb(33, 227, 155',
        backgroundColor: 'rgb(33, 227, 155)',
      },
      {
        //label of selected topic from third dropdown menu
        label: `${labelDrop3}`,
        data: Data,
        //use topic from third dropdown menu
        parsing: {
          xAxisKey: 'year',
          yAxisKey: `keywords.${topicDrop3}.count`,
        },
        //line color third dropdown
        borderColor: 'rgb(255, 127, 65',
        backgroundColor: 'rgb(255, 127, 65)',
      },
    ],
  }
  //const keywords = (data.datasets[0].data[0].keywords)
  //console.log(Object.keys(keywords))
  //console.log(Object.entries(keywords).flat().)

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: false,
        text: 'Topic Trends in publications',
      },
    },
    scales: {
      //text y-axis
      y: {
        title: {
          display: true,
          text: 'number of publications',
        },
      },
      //text x-axis
      x: {
        title: {
          display: true,
          text: 'year',
        },
      },
    },
    onClick: (event: any, elements: any) => {
      if (elements.length > 0) {
        const clickedElement = elements[0]
        console.log(clickedElement)
        const datasetIndex = clickedElement.datasetIndex
        const index = clickedElement.index
        const year = data.datasets[datasetIndex].data[index].year
        const label = data.datasets[datasetIndex].label
        extractPublicationIds(year, label)
      }
    },
  }

  function extractPublicationIds(year: string, label: string) {
    // update year and topic to show in heading
    setYear(year)
    setTopic(label)

    const newIds: string[] = []
    Data.forEach((obj: any) => {
      if (obj.year === year && Object.keys(obj.keywords).includes(label)) {
        const value = obj.keywords[label]
        newIds.push(...value.article_id.map(String))
      }
    })

    setArticleIds(newIds)

    // Set clicked to true in order to render Publicationsnippets
    setClicked(true)
    console.log(clicked)
    console.log(articleIds)
    console.log(articleIds[0])
  }

  return (
    <div>
      <div className="flex flex-col justify-center mt-4 mb-6 border-t-2 lg:flex-row">
        <div className="flex justify-center w-1/3 mt-4 bg-white rounded">
          <Box sx={{ width: '1/3', minWidth: 150, maxWidth: 150 }}>
            <FormControl fullWidth>
              <InputLabel id="demo-simple-select-label">Topic</InputLabel>
              <Select
                //save selected topic of first dropdown menu in state to show line of selected topic
                onChange={(e) => {
                  const topic = e.target.value as string
                  setTopicDrop1(topic)
                  setLabelDrop1(topic)
                }}
                label="Topic"
              >
                <MenuItem value="Select a topic">Select a Topic</MenuItem>
                {Object.keys(data.datasets[0].data[40].keywords).map(
                  (label) => (
                    <MenuItem value={label}>{label}</MenuItem>
                  )
                )}
              </Select>
            </FormControl>
          </Box>
        </div>

        <div className="flex justify-center w-1/3 mt-4 bg-white rounded">
          <Box sx={{ width: '1/3', minWidth: 150, maxWidth: 150 }}>
            <FormControl fullWidth>
              <InputLabel id="demo-simple-select-label">Topic</InputLabel>
              <Select
                //save selected topic of second dropdown menu in state to show line of selected topic
                onChange={(e) => {
                  const topic = e.target.value as string
                  setTopicDrop2(topic)
                  setLabelDrop2(topic)
                }}
                label="Topic"
              >
                <MenuItem value="Select a topic">Select a Topic</MenuItem>
                {Object.keys(data.datasets[0].data[40].keywords).map(
                  (label) => (
                    <MenuItem value={label}>{label}</MenuItem>
                  )
                )}
              </Select>
            </FormControl>
          </Box>
        </div>

        <div className="flex justify-center w-1/3 mt-4 bg-white rounded">
          <Box sx={{ width: '1/3', minWidth: 150, maxWidth: 150 }}>
            <FormControl fullWidth>
              <InputLabel id="demo-simple-select-label">Topic</InputLabel>
              <Select
                //save selected topic of third dropdown menu in state to show line of selected topic
                onChange={(e) => {
                  const topic = e.target.value as string
                  setTopicDrop3(topic)
                  setLabelDrop3(topic)
                }}
                label="Topic"
              >
                <MenuItem value="Select a topic">Select a Topic</MenuItem>
                {Object.keys(data.datasets[0].data[40].keywords).map(
                  (label) => (
                    <MenuItem value={label}>{label}</MenuItem>
                  )
                )}
              </Select>
            </FormControl>
          </Box>
        </div>
      </div>
      <div>
        <Line options={options} data={data} />
      </div>
      <div>
        {clicked === true ? (
          <div>
            <div className="flex mb-2 text-2xl font-bold">
              Corresponding documents from {year} and topic "{topic}"
            </div>
            {articleIds.map((id) => (
              <PublicationSnippet publicationId={id} />
            ))}
          </div>
        ) : (
          <div></div>
        )}
      </div>
      <div></div>
    </div>
  )
}

export default TopicTrendLineChart
