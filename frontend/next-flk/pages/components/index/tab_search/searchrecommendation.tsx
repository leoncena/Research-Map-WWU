import React from 'react'
import { useInstantSearch } from 'react-instantsearch-hooks-web'

interface Props {
  query: string
}
function SearchRecommendation(props: Props) {
  const { setIndexUiState } = useInstantSearch()
  return (
    <div>
      <button
        type="button"
        className="flex-auto p-1 mx-2 my-1 text-white bg-gray-400 rounded-lg hover:bg-gray-600"
        onClick={() => {
          setIndexUiState((prevIndexUiState) => ({
            ...prevIndexUiState,
            query: props.query,
          }))
        }}
      >
        {props.query}
      </button>
    </div>
  )
}

export default SearchRecommendation
