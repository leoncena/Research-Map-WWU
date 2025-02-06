import React from 'react'
import { useGlobalAuthorContext } from '../../../../contexts/authorContext'
import CoauthorNetwork from './coauthorNetwork'
import WordCloud from './wordcloud'
import ArticlesPreview from '../util/articlesPreview'
import useSWR from 'swr'

function Author() {
  const { author } = useGlobalAuthorContext()

  const fetcher = (...args) => fetch(...args).then((res) => res.json())

  const { data, error, isLoading } = useSWR(
    '/api/latestPublications/' + author,
    fetcher
  )
  if (error) return <div>failed to load</div>
  if (isLoading) return <div>loading...</div>

  return (
    <div className="flex flex-col p-8 mb-4 border-2 border-gray-300 shadow-lg rounded-b-xl rounded-tr-xl">
      <div className="mb-6 text-4xl font-bold">
        {data.cfFirstNames} {data.cfFamilyNames}
      </div>
      <div className="flex justify-between">
        <div className="flex-grow w-1/2 mr-2 border-2 border-gray-200 rounded-md shadow-lg">
          <CoauthorNetwork />
        </div>
        <div className="flex-grow w-1/2 ml-2 border-2 border-gray-200 rounded-md shadow-lg">
          <WordCloud />
        </div>
      </div>
      <div className="flex flex-col">
        <div className="mt-12 mb-6 text-4xl font-bold">
          Latest articles from this author
        </div>
        {data.publicationList.slice(0, 5).map((publication) => (
          <ArticlesPreview articleData={publication} />
        ))}
      </div>
    </div>
  )
}

export default Author
