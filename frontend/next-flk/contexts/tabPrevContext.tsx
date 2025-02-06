import { createContext, useContext } from 'react'
import React from 'react'

/* Purpose of this context:
* This context is similar to the "tabContext.tsx". The main purpose of this context is make the program able to restore the last visited tab.
* In order to do that, the program saves the previous tab in this context, whenever a tab-swtich takes place. In some views, there are
* "arrowback"-buttons included. When the user clicks on this button, the programm loads the tab saved in this context into the "tabContext" and
* the context saved in "tabContext" into this context. Consequently, the last visited tab is displayed, because it is loaded into the
* "tabContext". Due to this Context, the user is able to navigate backwards in some views.
* 
* Valid entries:
* - browse
* - search
* - publication
* - author
* 
* In order to see, which of these entries corresponds to which views, read the frontend-chapter of the documentation.
*/

export const GlobalTabPrevContext = createContext<{
  tabPrev: string
  setTabPrev: (newTab: string) => void
}>({
  tabPrev: 'browse',
  setTabPrev: () => {},
})

export const useGlobalTabPrevContext = () =>
  useContext(GlobalTabPrevContext)