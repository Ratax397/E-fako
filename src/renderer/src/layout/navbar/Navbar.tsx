import React from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '../../redux/Store'
import { toggleCloseBar } from '../../redux/slice/activeLinkSlice'
import { AiOutlineMenu } from 'react-icons/ai'

const Navbar: React.FC = () => {
  const dispatch = useDispatch()
  const activeName = useSelector((state: RootState) => state.activeLink.activeName)
  const user = useSelector((state: RootState) => state.user)
  console.log("user dans Navbar:", user);

  return (
    <header className="w-full px-6 py-3 flex justify-between items-center bg-white shadow-md border-b border-gray-100">

      <div className="flex items-center gap-4">
        <button
          onClick={() => dispatch(toggleCloseBar())}
          className="text-[#2F855A] hover:opacity-80 transition"
        >
          <AiOutlineMenu size={26} />
        </button>
        <h1 className="text-xl font-semibold text-[#2F855A]">{activeName}</h1>
      </div>

      <div className="flex items-center gap-4">

        <div className="h-11 w-11 rounded-full bg-[#ECC94B] flex items-center justify-center text-white font-bold text-lg shadow-sm">
          {user.name?.charAt(0).toUpperCase() || 'U'}
        </div>

        <div className="flex flex-col">
          <span className="text-sm font-medium text-gray-800">{user.name ? user.name : "utilisateur"}</span>
        </div>
      </div>
    </header>
  )
}

export default Navbar
