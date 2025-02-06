import useSWR from 'swr'
import SearchRecommendation from './searchrecommendation'

function Authorrec() {
  const fetcher = (...args) => fetch(...args).then((res) => res.json())

  const { data, error, isLoading } = useSWR('/api/searchrec/authorrec', fetcher)

  if (error) return <div>failed to load</div>
  if (isLoading) return <div>loading...</div>
  return (
    <div>
      {data.map((author) => (
        <SearchRecommendation
          query={author.cfFirstNames + ' ' + author.cfFamilyNames}
        />
      ))}
    </div>
  )
}

export default Authorrec
