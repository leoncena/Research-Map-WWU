import * as React from 'react'
import Accordion from '@mui/material/Accordion'
import AccordionSummary from '@mui/material/AccordionSummary'
import AccordionDetails from '@mui/material/AccordionDetails'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import { useInstantSearch } from 'react-instantsearch-hooks-web'
import Link from 'next/link'
import { useGlobalTabContext } from '../../../../contexts/tabContext'
import { useGlobalTabPrevContext } from '../../../../contexts/tabPrevContext'
import { useGlobalPublicationContext } from '../../../../contexts/publicationContext'
import { useGlobalAuthorContext } from '../../../../contexts/authorContext'

function Hit({ hit }: any) {
  const { setIndexUiState } = useInstantSearch()
  const { setTab } = useGlobalTabContext()
  const { setAuthor } = useGlobalAuthorContext()
  const { setTabPrev } = useGlobalTabPrevContext()
  const { setPublication } = useGlobalPublicationContext()

  function switchToPublication(publicationId: string) {
    setPublication(publicationId)
    setTabPrev('search')
    setTab('publication')
  }

  function switchToAuthor(authorId: string) {
    setAuthor(authorId)
    setTabPrev('search')
    setTab('author')
  }

  function newKeyword(keyword: string) {
    setIndexUiState((prevIndexUiState) => ({
      ...prevIndexUiState,
      query: keyword,
    }))
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
  return (
    <div className="mt-2">
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon fontSize="large" />}>
          <div className="flex flex-col">
            <p className="mt-2 text-[#A9B8D6]">{hit.srcAuthors}</p>
            <p
              className="text-3xl font-bold text-[#647fb5] hover:underline"
              onClick={() => switchToPublication(hit.id)}
            >
              {hit.cfTitle}
            </p>
            {hit.cfAbstr != undefined && hit.publYear.length === 0 ? (
              <div></div>
            ) : (
              <div className="text-[#A9B8D6]">published: {hit.publYear}</div>
            )}
            {/* Placeholder if keywords not given*/}
            <div className="flex flex-row">
              {(hit.cfAbstr != undefined && hit.keywords.length === 0) ||
              Array.isArray(hit.keywords) === false ? (
                <div></div>
              ) : (
                hit.keywords.slice(0, 5).map((keyword: any) => (
                  <button
                    type="button"
                    className="p-1 m-1 text-white bg-gray-400 rounded-lg hover:bg-gray-600"
                    onClick={() => newKeyword(keyword)}
                  >
                    {keyword}
                  </button>
                ))
              )}
            </div>
          </div>
        </AccordionSummary>
        <AccordionDetails>
          <div className="flex flex-row">
            <div className="text-[#A9B8D6] font-medium mr-1">WWU-Authors:</div>
            {(hit.cfAbstr != undefined && hit.authorList.length === 0) ||
            Array.isArray(hit.authorList) === false ? (
              <div></div>
            ) : (
              hit.authorList.map((author: any) => (
                <div
                  className=" text-[#A9B8D6] mr-2  hover:underline hover:font-bold"
                  onClick={() => switchToAuthor(author.id)}
                >
                  {author.cfFirstNames} {author.cfFamilyNames}
                </div>
              ))
            )}
          </div>
          {/* Placeholder if abstract is not there */}
          {hit.cfAbstr != undefined && hit.cfAbstr.length === 0 ? (
            <div className="mt-2 mb-2">
              No Abstract available in the database.
            </div>
          ) : (
            <div className="mt-2 mb-2">{hit.cfAbstr}</div>
          )}
          {/* Placeholder if doi is not there */}
          {hit.cfAbstr != undefined && hit.doi.length === 0 ? (
            <div></div>
          ) : (
            <Link
              className="font-bold hover:underline"
              href={'https://www.doi.org/' + hit.doi}
              target="_blank"
            >
              www.doi.org/{hit.doi}
            </Link>
          )}
        </AccordionDetails>
      </Accordion>
    </div>
  )
}

export default Hit
