import Navbar from './components/navbar'
import Content from './components/index/organization/content'
import Layout from './components/layout'
import clientPromise from '../lib/mongodb'
import React from 'react'

interface Props {
  sunburstData: Array<Object>
  networkData: Array<Object>
  wordcloudData: Array<Object>
  trendData: Array<Object>
  barData: Array<Object>
}

export default function Home({
  sunburstData,
  networkData,
  wordcloudData,
  trendData,
  barData,
}: Props) {
  return (
    <div className="flex mb-4">
      <Layout>
        <Navbar />
        <Content
          sunburstData={sunburstData}
          networkData={networkData}
          wordcloudData={wordcloudData}
          trendData={trendData}
          barData={barData}
        />
      </Layout>
    </div>
  )
}

export async function getServerSideProps(context: any) {
  try {
    const client = await clientPromise
    const db = client.db('FLK_Web')

    const sunburstData = await db.collection('inst_wi_hrchy').find({}).toArray()

    const networkData = await db.collection('network').find({}).toArray()

    const wordcloudData = await db
      .collection('wordcloud_institut')
      .find({})
      .limit(150)
      .toArray()

    const trendData = await db
      .collection('data_for_trends_with_id')
      .find({})
      .sort({ year: 1 })
      .toArray()

    const barData = await db
      .collection('data_bar_chart_research_output')
      .find({ Jahr: { $gte: '1990' } })
      .sort({ Jahr: 1 })
      .toArray()

    return {
      props: {
        sunburstData: JSON.parse(JSON.stringify(sunburstData[0])),
        networkData: JSON.parse(JSON.stringify(networkData[0])),
        barData: JSON.parse(JSON.stringify(barData)),
        wordcloudData: JSON.parse(JSON.stringify(wordcloudData)),
        trendData: JSON.parse(JSON.stringify(trendData)),
      },
    }
  } catch (e) {
    console.error(e)
  }
}
