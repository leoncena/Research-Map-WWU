import React from 'react'
import {
  InstantSearch,
  SearchBox,
  Hits,
  Configure,
  Pagination,
  HitsPerPage,
} from 'react-instantsearch-hooks-web'
import Hit from './hit'
import EmptyQueryBoundary from './emptyqueryboundary'
import EmptyQuery from './emptyquery'
import NoResultsBoundary from './noresultsboundary'
import NoResults from './noresults'
import Filter from './filter'

import { instantMeiliSearch } from '@meilisearch/instant-meilisearch'
import { useGlobalSearchContext } from '../../../../contexts/searchContext'

const apiKey: string = process.env.NEXT_PUBLIC_MS_API_KEY!
const searchAdd: string = process.env.NEXT_PUBLIC_MS_URI!
const searchClient = instantMeiliSearch(searchAdd, apiKey)
const indexName = 'publications'

function Search() {
  const { dquery } = useGlobalSearchContext()

  return (
    <div className="flex flex-col">
      <InstantSearch
        indexName={indexName}
        searchClient={searchClient}
        initialUiState={{
          [indexName]: {
            query: dquery,
          },
        }}
      >
        <Configure hitsPerPage={8} />
        <SearchBox
          classNames={{
            root: 'flex justify-center xl:min-w-[1210px]',
            form: 'w-full flex justify-center flex-row shadow-md border-gray-100 border-2 rounded-md',
            input: 'order-2 h-14 pl-5 w-full pr-5',
            submit: 'order-1 flex items-center pl-4',
            submitIcon: 'h-7 w-7 stroke-[#647fb5]',
            reset: 'order-3 flex items-center pr-4 pl-2 ',
            resetIcon: 'h-4 w-4 stroke-[#647fb5]',
          }}
          placeholder="Search for researcher, title, topic ..."
          autoFocus={false}
        />
        <NoResultsBoundary fallback={<NoResults />}>
          <EmptyQueryBoundary fallback={<EmptyQuery />}>
            <div className="flex flex-row">
              <Filter />
              <div className="flex flex-col mt-5 mb-2">
                <div className="flex justify-content-end">
                  <HitsPerPage
                    items={[
                      { label: '10 hits per page', value: 10, default: true },
                      { label: '25 hits per page', value: 25 },
                      { label: '50 hits per page', value: 50 },
                    ]}
                  />
                </div>
                <div className="mt-2 border-t-2 border-gray-200">
                  <Hits hitComponent={Hit} />
                </div>
              </div>
            </div>
            <Pagination
              padding={2}
              showFirst={false}
              showPrevious={true}
              showNext={true}
              showLast={false}
              classNames={{
                root: 'flex justify-center mt-2 border-t-2',
                list: 'flex flex-row mt-4 justify-center',
                item: 'flex justify-center h-12 w-12 border-gray-200 border-2 hover:bg-[#3d4d76] hover:text-white mr-0.5 ml-0.5 rounded-md items-center',
                selectedItem: 'bg-[#687ba0] text-white',
                link: 'h-full w-full flex justify-center items-center',
              }}
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            />
          </EmptyQueryBoundary>
        </NoResultsBoundary>
      </InstantSearch>
    </div>
  )
}

export default Search
