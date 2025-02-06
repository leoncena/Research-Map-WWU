import React from 'react'

function SearchContainer({ children }: any) {
  return (
    <div className="flex py-6 border border-gray-200 rounded-b-lg rounded-tr-lg shadow-md ">
      <div className="flex flex-row self-stretch justify-between flex-grow pt-4 pl-4 pr-4">
        <main>{children}</main>
      </div>
    </div>
  )
}

export default SearchContainer
