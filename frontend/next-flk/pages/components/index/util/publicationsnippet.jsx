import useSWR from 'swr'
import ArticlesPreview from './articlesPreview'

function PublicationSnippet(publicationId) {
  const fetcher = (...args) => fetch(...args).then((res) => res.json())
  const { data, error, isLoading } = useSWR(
    '/api/publication/' + publicationId.publicationId,
    fetcher
  )

  if (error) return <div>failed to load</div>
  if (isLoading) return <div>loading...</div>
  return data.map((publicationData) => (
    <ArticlesPreview articleData={publicationData} />
  ))
}

export default PublicationSnippet
