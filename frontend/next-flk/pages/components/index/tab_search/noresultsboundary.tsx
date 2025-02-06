import React from 'react'
import { useInstantSearch } from 'react-instantsearch-hooks-web'

function NoResultsBoundary({ children, fallback }: any) {
  const { results } = useInstantSearch()

  // The `__isArtificial` flag makes sure not to display the No Results message
  // when no hits have been returned yet.
  if (!results.__isArtificial && results.nbHits === 0) {
    return (
      <>
        {fallback}
        <div hidden>{children}</div>
      </>
    )
  }

  return children
}

export default NoResultsBoundary
