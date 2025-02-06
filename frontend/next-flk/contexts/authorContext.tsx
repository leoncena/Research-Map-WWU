import { createContext, useContext } from 'react'

/* Purpose of this context:
* This context saves the id of the last selected author. If the user clicks on the "author"-tab, the program
* loads the information from the author that corresponds to the authorID that is saved in this context.
* 
* Valid entries:
* This context is initialized with the value 'none'. After that this context is assigned only with values that match an authorID
* from the FLK-Web-database.
*
* In order to see, which of these entries corresponds to which views, read the frontend-chapter of the documentation.
*/

export const GlobalAuthorContext = createContext<{
  author: string
  setAuthor: (newAuthor: string) => void
}>({
  author: 'none',
  setAuthor: () => {},
})

export const useGlobalAuthorContext = () =>
  useContext(GlobalAuthorContext)
