import { JSX, useState } from 'react'
import { FaDollarSign, FaEye, FaUserCircle } from 'react-icons/fa'
import { useFilterData } from '@renderer/hooks/useFilterData'
import Searchbar from '@renderer/components/searchbar/Searchbar'
import { userData } from '@renderer/data/Userdata'
import Moduleinfouse from '@renderer/components/Moduleinfouser/Moduleinfouse'

function UtilisateurPage(): JSX.Element {
  const [searchuser, setsearchuser] = useState('')
  const handlesearchuser = (datauser: string) => {
    setsearchuser(datauser)
  }
  const filtereusers = useFilterData(userData, searchuser, ['nom', 'prenom'])
  const [selecteduser, setSelecteduser] = useState(null)
    const handleViewUser = (user) => {
      setSelecteduser(user)
    }

    const handleCloseModule = () => {
      setSelecteduser(null)
    }

  return (
    <div
      className={`Rigth bg-[#E6E6FA] w-full min-h-screen pl-6 pt-4 pr-4 transition-all duration-600`}
    >
      <div className="p-6 space-y-6">
        <Searchbar onSearch={handlesearchuser} />

        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 px-6 py-5">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-extrabold text-[#2F855A] tracking-tight">
              Utilisateurs connectés
            </h2>
            <span className="bg-[#2F855A] text-white text-sm font-semibold rounded-full px-4 py-1 select-none shadow-sm">
              {filtereusers.length}
            </span>
          </div>

          <div className="hidden md:flex text-sm bg-[#2F855A] text-white px-4 py-2 rounded-lg font-semibold select-none">
            <div className="w-24 flex items-center justify-center">Photo</div>
            <div className="w-40 flex items-center pl-2">Nom</div>
            <div className="w-36 flex items-center pl-2">Prénom</div>
            <div className="w-44 flex items-center pl-2">Email</div>
            <div className="w-36 flex items-center pl-2">Déchet</div>
            <div className="w-36 flex items-center pl-2">Portefeuille</div>
            <div className="w-20 flex items-center justify-center">Voir</div>
            <div className="w-28 mx-auto flex items-center justify-center">Actions</div>
          </div>

          <div className="space-y-2 mt-2 max-h-80 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-gray-300">
            {filtereusers.length === 0 ? (
              <div className="text-center py-6 text-gray-500 text-sm">Aucun utilisateur trouvé</div>
            ) : (
              filtereusers.map((users, index) => (
                <div
                  key={index}
                  className={`flex items-center px-4 py-2 rounded-xl text-sm ${
                    index % 2 === 0 ? 'bg-gray-50' : 'bg-white'
                  } hover:bg-green-50 border-l-2 border-transparent hover:border-[#2F855A] transition-all duration-300`}
                >
                  <div className="w-24 flex items-center justify-center">
                    <div className="bg-[#2F855A] p-2 rounded-full">
                      <FaUserCircle className="text-2xl text-white" />
                    </div>
                  </div>

                  <div className="w-40 flex items-center pl-2 font-semibold text-gray-800 truncate">
                    {users.nom}
                  </div>
                  <div className="w-36 flex items-center pl-2 text-gray-700 truncate">
                    {users.prenom}
                  </div>
                  <div className="w-44 flex items-center pl-2 text-gray-700 truncate">
                    {users.email}
                  </div>
                  <div className="w-36 flex items-center pl-2 text-gray-600 truncate">
                    {users.dechets}
                  </div>
                  <div className="w-36 flex items-center pl-2 text-gray-600 truncate">
                    {users.wallet} Ar
                  </div>

                  <div className="w-20 flex items-center justify-center text-[#9f7126]">
                    <FaEye
                      onClick={() => handleViewUser(users)}
                      className="cursor-pointer hover:text-black transition"
                    />
                  </div>

                  <div className="w-28 m-auto h-10 flex items-center  px-12  hover:text-[#ffffff]  text-[#2F855A] hover:bg-[#276749] rounded-lg shadow-md cursor-pointer  transition-colors duration-300">
                    <FaDollarSign className=" text-xl   " />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {selecteduser && <Moduleinfouse user={selecteduser} onClose={handleCloseModule} />}
    </div>
  )
}

export default UtilisateurPage
