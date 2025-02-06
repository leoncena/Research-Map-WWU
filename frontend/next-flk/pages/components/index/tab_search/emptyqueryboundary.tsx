import { useInstantSearch } from 'react-instantsearch-hooks-web'

function EmptyQueryBoundary({ children, fallback }: any) {
  const { indexUiState } = useInstantSearch()

  if (!indexUiState.query) {
    return fallback
  }

  return children
}
export default EmptyQueryBoundary
