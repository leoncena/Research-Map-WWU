import Accordion from '@mui/material/Accordion'
import AccordionSummary from '@mui/material/AccordionSummary'
import AccordionDetails from '@mui/material/AccordionDetails'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import Link from 'next/link'
import { useGlobalTabContext } from '../../../../contexts/tabContext'
import { useGlobalTabPrevContext } from '../../../../contexts/tabPrevContext'
import { useGlobalPublicationContext } from '../../../../contexts/publicationContext'
import { useGlobalSearchContext } from '../../../../contexts/searchContext'
import { useGlobalAuthorContext } from '../../../../contexts/authorContext'

function ArticlesPreview({ articleData }) {
  const { tab, setTab } = useGlobalTabContext()
  const { setTabPrev } = useGlobalTabPrevContext()
  const { setPublication } = useGlobalPublicationContext()
  const { setQuery } = useGlobalSearchContext()
  const { setAuthor } = useGlobalAuthorContext()

  function switchToPublication(publicationId) {
    setPublication(publicationId)
    setTabPrev(tab)
    setTab('publication')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
  function switchToSearch(query) {
    setQuery(query)
    setTabPrev(tab)
    setTab('search')
  }
  function switchToAuthor(authorId) {
    setAuthor(authorId)
    setTabPrev(tab)
    setTab('author')
  }

  return (
    <div className="my-4">
      {' '}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon fontSize="large" />}>
          <div className="flex flex-col">
            <p className="mt-2 text-[#A9B8D6] hover:underline">
              {articleData.srcAuthors}
            </p>
            <p
              className="text-3xl font-bold text-[#647fb5] hover:underline"
              onClick={() => switchToPublication(articleData.id)}
            >
              {articleData.cfTitle}
            </p>
            {articleData.cfAbstr == undefined &&
            articleData.publYear == null ? (
              <div></div>
            ) : (
              <div className="text-[#A9B8D6]">
                published: {articleData.publYear}
              </div>
            )}
            {/* Placeholder if keywords not given*/}
            <div className="flex flex-row">
              {articleData.keywords === null ||
              Array.isArray(articleData.keywords) === false ? (
                <div></div>
              ) : (
                articleData.keywords.slice(0, 5).map((keyword) => (
                  <button
                    type="button"
                    className="p-1 m-1 bg-gray-400 rounded-lg text-warticleDatae hover:bg-gray-600"
                    onClick={() => switchToSearch(keyword)}
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
            <div className="text-[#A9B8D6] font-medium mr-1">WWU-Autoren:</div>
            {articleData.cfAbstr != undefined &&
            articleData.authorList === null ? (
              <div></div>
            ) : (
              articleData.authorList.map((author) => (
                <button
                  className=" text-[#A9B8D6] mr-2  hover:underline hover:font-bold"
                  onClick={() => switchToAuthor(author.id)}
                >
                  {author.cfFirstNames} {author.cfFamilyNames}
                </button>
              ))
            )}
          </div>
          {/* Placeholder if abstract is not there */}
          {articleData.cfAbstr == null ? (
            <div className="mt-2 mb-2">
              No Abstract available in the database.
            </div>
          ) : (
            <div className="mt-2 mb-2">{articleData.cfAbstr}</div>
          )}
          {/* Placeholder if doi is not there */}
          {articleData.doi == null ? (
            <div></div>
          ) : (
            <Link
              className="font-bold hover:underline"
              href={'https://www.doi.org/' + articleData.doi}
              target="_blank"
            >
              www.doi.org/{articleData.doi}
            </Link>
          )}
        </AccordionDetails>
      </Accordion>
    </div>
  )
}

export default ArticlesPreview
