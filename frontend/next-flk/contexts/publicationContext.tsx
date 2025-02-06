import { createContext, useContext } from 'react'

/* Purpose of this context:
* This context saves the id of the last selected publication. If the user clicks on the "publication"-tab, the program
* loads the information from the publication that corresponds to the publicationID that is saved in this context.
* 
* Valid entries:
* This context is initialized with the value 'none'. After that this context is assigned only with values that match a publicationID
* from the FLK-Web-database.
*
* In order to see, which of these entries corresponds to which views, read the frontend-chapter of the documentation.
*/

export const GlobalPublicationContext = createContext<{
  publication: any
  setPublication: (newPublication: string) => void
}>({
  publication: 'none',
  setPublication: () => {},
})

export const useGlobalPublicationContext = () =>
  useContext(GlobalPublicationContext)
