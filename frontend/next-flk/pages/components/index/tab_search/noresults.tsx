import React from 'react'
import { useInstantSearch } from 'react-instantsearch-hooks-web'

function NoResults() {
  const { indexUiState } = useInstantSearch()

  return (
    <div className="mt-4 border-t-2">
      <p>
        No results for <q>{indexUiState.query}</q>.
      </p>
    </div>
  )
}

export default NoResults
