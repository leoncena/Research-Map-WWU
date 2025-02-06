import React from 'react'
import Link from 'next/link'
import { useGlobalTabContext } from '../../../../contexts/tabContext'
import { useGlobalTabPrevContext } from '../../../../contexts/tabPrevContext'
import { useGlobalPublicationContext } from '../../../../contexts/publicationContext'
import { useGlobalAuthorContext } from '../../../../contexts/authorContext'

function Tabs() {
  const { tab, setTab } = useGlobalTabContext()
  const { setTabPrev } = useGlobalTabPrevContext()
  const { publication } = useGlobalPublicationContext()
  const { author } = useGlobalAuthorContext()

  function changeToTab(newTab: string) {
    const currentTab = tab
    setTab(newTab)
    setTabPrev(currentTab)
  }

  return (
    <div className="flex flex-row mt-6">
      <Link href="" onClick={() => changeToTab('browse')}>
        <div
          className={
            'py-2 px-6 rounded-tl-lg text-white hover:bg-[#3d4d76]' +
            (tab == 'browse' ? ' bg-[#485c8c]' : ' bg-[#687ba0]')
          }
        >
          Charts
        </div>
      </Link>
      <Link href="" onClick={() => changeToTab('search')}>
        <div
          className={
            'py-2 px-6 text-white hover:bg-[#3d4d76]' +
            (tab == 'search' ? ' bg-[#485c8c]' : ' bg-[#687ba0]') +
            (publication == 'none' && author == 'none' ? ' rounded-tr-lg' : '')
          }
        >
          Search
        </div>
      </Link>
      {publication == 'none' ? (
        ''
      ) : (
        <Link href="" onClick={() => changeToTab('publication')}>
          <div
            className={
              'py-2 px-6 text-white hover:bg-[#3d4d76]' +
              (tab == 'publication' ? ' bg-[#485c8c]' : ' bg-[#687ba0]') +
              (author == 'none' ? ' rounded-tr-lg' : '')
            }
          >
            Publication
          </div>
        </Link>
      )}
      {author == 'none' ? (
        ''
      ) : (
        <Link href="" onClick={() => changeToTab('author')}>
          <div
            className={
              'py-2 px-6 rounded-tr-lg text-white hover:bg-[#3d4d76]' +
              (tab == 'author' ? ' bg-[#485c8c]' : ' bg-[#687ba0]')
            }
          >
            Author
          </div>
        </Link>
      )}
    </div>
  )
}

export default Tabs
