import React from 'react'
import useSWR from 'swr'
import { useGlobalPublicationContext } from '../../../../contexts/publicationContext'
import Link from 'next/link'
import { useGlobalTabPrevContext } from '../../../../contexts/tabPrevContext'
import { useGlobalTabContext } from '../../../../contexts/tabContext'
import { useGlobalAuthorContext } from '../../../../contexts/authorContext'
import { useGlobalSearchContext } from '../../../../contexts/searchContext'
import IconButton from '@mui/material/IconButton'
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import PublicationSnippet from '../util/publicationsnippet'

function Publications() {
  const { publication } = useGlobalPublicationContext()
  const { tabPrev, setTabPrev } = useGlobalTabPrevContext()
  const { tab, setTab } = useGlobalTabContext()
  const { setAuthor } = useGlobalAuthorContext()
  const { setQuery } = useGlobalSearchContext()
  const fetcher = (...args) => fetch(...args).then((res) => res.json())

  const { data, error, isLoading } = useSWR(
    '/api/publication/' + publication,
    fetcher
  )

  if (error) return <div>failed to load</div>
  if (isLoading) return <div>loading...</div>

  function switchToSearch(query) {
    setQuery(query)
    setTabPrev('publication')
    setTab('search')
  }

  function switchToAuthor(authorId) {
    setAuthor(authorId)
    setTabPrev('publication')
    setTab('author')
  }

  function goBack() {
    const currentTab = tab
    setTab(tabPrev)
    setTabPrev(currentTab)
  }

  return data.map((publicationData) => (
    <div className="mb-4 flex flex-col rounded-b-xl rounded-tr-xl border-2 border-gray-300 p-8 shadow-lg">
      <div>
        <div className="flex flex-col justify-start">
          <div className="mb-4 mr-4 flex">
            <IconButton onClick={goBack}>
              <ArrowBackIcon fontSize="medium" />
            </IconButton>
          </div>
          <div className="mb-4 text-3xl font-bold">
            {publicationData.cfTitle}
          </div>
        </div>
        <div className="text-gray-400 ">{publicationData.srcAuthors}</div>
        <div className="mt-1 flex gap-2 text-gray-400">
          {publicationData.keywords === null ||
          Array.isArray(publicationData.keywords) === false
            ? ''
            : publicationData.keywords.slice(0, 5).map((keyword) => (
                <button
                  className="rounded-lg bg-gray-400 p-1 text-white hover:bg-gray-600"
                  onClick={() => switchToSearch(keyword)}
                >
                  {keyword}
                </button>
              ))}
        </div>
        <div className="mt-1 flex flex-row text-gray-400">
          <p className="font-medium">Published: {publicationData.publYear}</p>
        </div>
        <div className="flex flex-row">
          <div className="mr-1 font-medium text-gray-400">WWU-Authors:</div>
          {publicationData.authorList === null ? (
            <div></div>
          ) : (
            publicationData.authorList.map((author) => (
              <button
                className="mr-2 text-gray-400 hover:font-bold hover:underline"
                onClick={() => switchToAuthor(author.id)}
              >
                {author.cfFirstNames} {author.cfFamilyNames}
              </button>
            ))
          )}
        </div>
      </div>
      {publicationData.cfAbstr ? (
        <div className="mt-4">{publicationData.cfAbstr}</div>
      ) : (
        <div className="mt-4">No abstract available in database</div>
      )}
      {publicationData.doi === null ? (
        ''
      ) : (
        <div className="font-bold hover:underline">
          <Link
            href={'https://www.doi.org/' + publicationData.doi}
            target="_blank"
          >
            www.doi.org/{publicationData.doi}
          </Link>
        </div>
      )}

      <div className="mt-8 flex flex-col">
        <div className="mb-2 flex text-2xl font-bold">
          {' '}
          Similar Publications
        </div>
        {publicationData.similar_publications === null ? (
          <div></div>
        ) : (
          publicationData.similar_publications.map((pId) => (
            <PublicationSnippet publicationId={pId} />
          ))
        )}
      </div>
    </div>
  ))
}

export default Publications
