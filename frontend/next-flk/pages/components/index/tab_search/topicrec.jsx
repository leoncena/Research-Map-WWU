import useSWR from 'swr'
import SearchRecommendation from './searchrecommendation'

function Topicrec() {
  const fetcher = (...args) => fetch(...args).then((res) => res.json())

  const { data, error, isLoading } = useSWR('/api/searchrec/topicrec', fetcher)

  if (error) return <div>failed to load</div>
  if (isLoading) return <div>loading...</div>
  return (
    <div>
      {data.map((topic) => (
        <SearchRecommendation query={topic.keywords[0]} />
      ))}
    </div>
  )
}

export default Topicrec
