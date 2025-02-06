import React from 'react'
import { useGlobalPublicationContext } from '../../../../../contexts/publicationContext'
import { useGlobalTabContext } from '../../../../../contexts/tabContext'
import { useGlobalTabPrevContext } from '../../../../../contexts/tabPrevContext'
import { useEffect } from 'react'

interface Props {
  publicationId: string
}

function PublicationContextSetter({ publicationId }: Props) {
  const { setPublication } = useGlobalPublicationContext()
  const { setTab } = useGlobalTabContext()
  const { setTabPrev } = useGlobalTabPrevContext()

  useEffect(() => {
    setPublication(publicationId)
    setTab('publication')
    setTabPrev('browse')
  }, [publicationId])

  return <div></div>
}

export default PublicationContextSetter
