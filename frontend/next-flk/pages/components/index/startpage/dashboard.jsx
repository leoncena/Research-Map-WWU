import React from 'react'
import useSWR from 'swr'

function Dashboard() {
  const fetcher = (...args) => fetch(...args).then((res) => res.json())

  const { data, error, isLoading } = useSWR('/api/dashboard/dashboard', fetcher)

  if (error) return <div>failed to load</div>
  if (isLoading) return <div>loading...</div>

  return (
    <div className="flex flex-row">
      <div className="flex flex-col justify-center w-1/4 p-6">
        <div className="flex justify-center text-4xl font-bold">1</div>
        <div className="flex justify-center text-xl pt-2">Department</div>
      </div>
      <div className="flex flex-col justify-center w-1/4 p-6">
        <div className="flex justify-center text-4xl font-bold">{data[2]}</div>
        <div className="flex justify-center text-xl pt-2">Chairs</div>
      </div>
      <div className="flex flex-col justify-center w-1/4 p-6">
        <div className="flex justify-center text-4xl font-bold">{data[1]}</div>
        <div className="flex justify-center text-xl pt-2">Authors</div>
      </div>
      <div className="flex flex-col justify-center w-1/4 p-6">
        <div className="flex justify-center text-4xl font-bold">{data[0]}</div>
        <div className="flex justify-center text-xl pt-2">Publications</div>
      </div>
    </div>
  )
}

export default Dashboard
