import {
  RangeInput,
  ClearRefinements,
  RefinementList,
} from 'react-instantsearch-hooks-web'

function Filter() {
  return (
    <div className="mt-2 mr-2 border-gray-200 rounded-md shadow-md">
      <div className="flex flex-row items-end justify-between m-2">
        <h1 className="text-xl font-medium">Filters</h1>
        <ClearRefinements
          classNames={{
            button: 'hover:underline',
            disabledButton: 'text-gray-300',
          }}
          translations={{
            resetButtonText: 'Clear',
          }}
        />
      </div>
      <div className="m-2 border-t-2">
        <div className="mt-2 text-sm font-medium">Publication Year</div>
        <RangeInput
          attribute="publYear"
          min={1973}
          max={2023}
          classNames={{
            root: 'my-2',
            form: 'flex flex-row',
            submit:
              'bg-gray-400 rounded-md hover:bg-gray-600 px-2 ml-2 text-sm',
            separator: 'mx-2',
            input: 'rounded-md border-2 border-gray-200 text-sm',
          }}
          translations={{
            separatorElementText: '–',
          }}
        />
        <div className="mt-2 text-sm font-medium">Publication type</div>
        <RefinementList
          attribute="publicationType"
          limit={4}
          showMore={true}
          classNames={{
            item: 'text-sm my-2',
            count: 'text-sm font-medium ml-1',
            checkbox: 'mr-1',
            showMore: 'bg-gray-400 rounded-md hover:bg-gray-600 px-2 text-sm',
          }}
        />
      </div>
    </div>
  )
}

export default Filter
