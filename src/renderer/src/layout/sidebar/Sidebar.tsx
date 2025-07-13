import { useState, useEffect , ReactNode } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { setActiveName } from '@renderer/redux/slice/activeLinkSlice'
import { RootState } from '@renderer/redux/Store'
import { Link } from 'react-router-dom'
import { LuLayoutDashboard, LuUser } from 'react-icons/lu'
import { MdSettings, MdHistory } from 'react-icons/md'
import { FiLogOut } from 'react-icons/fi'
import Weathercard from '@renderer/components/weathercard/Weathercard'
import { useNavigate } from 'react-router-dom'

interface Menu {
  name: string
  path?: string
  icon: ReactNode
}

const Sidebar: React.FC = () => {
  const [, setActiveMenu] = useState<string | null>(null)

  const dispatch = useDispatch()
  const closeBar = useSelector((state: RootState) => state.activeLink.closeBar)
  const activeName = useSelector((state: RootState) => state.activeLink.activeName)
  const navigate= useNavigate()

  const menus: Menu[] = [
    {
      name: 'Dashboard',
      path: '/home',
      icon: <LuLayoutDashboard size={25} />
    },
    {
      name: 'Utilisateurs',
      path: '/home/utilisateur',
      icon: <LuUser size={25} />
    },
    {
      name: 'Historiques',
      path: '/home/historique',
      icon: <MdHistory size={25} />
    }
  ]

 

  useEffect(() => {
    if (closeBar) {
      setActiveMenu(null)
    }
  }, [closeBar])

  return (
    <aside
      className={`fixed top-0 left-0 z-40 h-screen duration-500 ease-in-out ${
        closeBar ? 'w-[5rem]' : 'w-64'
      } bg-[#2F855A] text-white shadow-xl`}
    >
      <div className="flex items-center gap-2 p-4 bg-[#2F855A]">
        <p className={`${closeBar ? 'hidden' : 'text-xl font-semibold'}`}>TRI-FAKO</p>
      </div>

      <div className="h-full overflow-y-auto px-3 py-4">
        <ul className="space-y-2">
          {menus.map((menu, index) => (
            <li key={index}>
              <Link
                to={menu.path || '#'}
                onClick={() => dispatch(setActiveName(menu.name))}
                className={`flex items-center gap-3 p-2 rounded-lg hover:bg-[#276749] transition ${
                  activeName === menu.name ? 'bg-[#276749] font-semibold' : ''
                } ${closeBar ? 'justify-center' : ''}`}
              >
                {menu.icon}
                {!closeBar && <span>{menu.name}</span>}
              </Link>
            </li>
          ))}
        </ul>

        <div className="mt-28 hidden sm:block lg:block">
          {!closeBar && <Weathercard />} 
        </div>
      </div>

      <div className="absolute bottom-4 left-0 w-full px-4 space-y-3">
        <Link
          to="/settings"
          className={`flex items-center gap-3 p-2 bg-white text-[#2F855A] hover:bg-[#276749] hover:text-white rounded-lg shadow-md transition ${
            closeBar ? 'justify-center' : ''
          }`}
        >
          <MdSettings size={22} />
          {!closeBar && <span>Paramètres</span>}
        </Link>

        <button
          onClick={()=>navigate("/")}
          className={` w-full flex items-center gap-3 p-2 bg-white text-[#2F855A] hover:bg-[#276749] hover:text-white rounded-lg shadow-md transition ${
            closeBar ? 'justify-center' : ''
          }`}
        >
          <FiLogOut size={22} />
          {!closeBar && <span>Se déconnecter</span>}
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
