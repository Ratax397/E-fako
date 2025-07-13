import { Fragment } from 'react'
import { IoSearchSharp } from 'react-icons/io5'

type SearchBarProps = {
  onSearch: (searchCategorie: string) => void
}

const Searchbar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onSearch(event.target.value)
  }

  return (
    <Fragment>
      <div className="bg-white w-full max-w-md rounded-lg relative px-4 py-2 shadow-md mx-auto">
        <div className="flex items-center gap-3 bg-[#E6F0DA] rounded-lg px-4 py-2">
          <IoSearchSharp size={22} className="text-[#2F855A]" />
          <input
            type="text"
            placeholder="Recherche..."
            className="bg-transparent focus:outline-none text-[#2F855A] placeholder:text-[#799464] w-full text-base"
            onChange={handleSearchChange}
          />
        </div>
      </div>
    </Fragment>
  )
}

export default Searchbar
