import React from 'react'
import Themerec from './themerec'
import Topicrec from './topicrec'
import Authorrec from './authorrec'

function EmptyQuery() {
  return (
    <div>
      <div className="flex justify-center mt-4 border-t-2">
        <h1 className="my-4 text-3xl font-bold">Search for a ...</h1>
      </div>
      <div className="flex flex-row items-stretch">
        <div className="flex justify-center w-1/3 mr-2 border-2 rounded-lg shadow-lg">
          <div>
            <div className="flex justify-center">
              <h1 className="text-2xl font-bold">Researcher</h1>
            </div>
            <Authorrec />
          </div>
        </div>
        <div className="flex justify-center w-1/3 border-2 rounded-lg shadow-lg">
          <div>
            <div className="flex justify-center">
              <h1 className="text-2xl font-bold">Topic</h1>
            </div>
            <Topicrec />
          </div>
        </div>
        <div className="flex justify-center w-1/3 ml-2 border-2 rounded-lg shadow-lg">
          <div>
            <div className="flex justify-center">
              <h1 className="text-2xl font-bold">Title</h1>
            </div>
            <Themerec />
          </div>
        </div>
      </div>
    </div>
  )
}

export default EmptyQuery
