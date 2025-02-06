import React from 'react'

interface Props {
  children: React.ReactNode
}

const Layout = ({ children }: Props) => {
  return (
    <div className="flex flex-col flex-grow px-6 m-auto overflow-auto max-w-7xl">
      <main>{children}</main>
    </div>
  )
}

export default Layout
