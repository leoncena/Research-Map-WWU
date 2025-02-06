import { createContext, useContext } from 'react'
import React from 'react'

/* Purpose of this context:
* This context defines, what is displayed to the user on a top-level. The context is initialized with "browse". The context is changed,
* when the user clicks on one of the tabs to change the view. When the user clicks on a tab-button, the corresponding entry is
* loaded into this context and the user sees a different view.
* 
* Valid entries:
* - browse
* - search
* - publication
* - author
* 
* In order to see, which of these entries corresponds to which views, read the frontend-chapter of the documentation.
*/


export const GlobalTabContext = createContext<{
  tab: string,
  setTab: (newTab: string) => void
}>({
  tab: 'browse',
  setTab: () => { }
})


export const useGlobalTabContext = () => useContext(GlobalTabContext)
