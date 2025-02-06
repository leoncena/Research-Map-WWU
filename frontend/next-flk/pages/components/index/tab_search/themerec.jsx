import useSWR from 'swr'
import SearchRecommendation from './searchrecommendation'

function Themerec() {
  const fetcher = (...args) => fetch(...args).then((res) => res.json())

  const { data, error, isLoading } = useSWR('/api/searchrec/themerec', fetcher)

  if (error) return <div>failed to load</div>
  if (isLoading) return <div>loading...</div>
  return (
    <div>
      {data.map((theme) => (
        <SearchRecommendation query={theme.cfTitle} />
      ))}
    </div>
  )
}

export default Themerec
