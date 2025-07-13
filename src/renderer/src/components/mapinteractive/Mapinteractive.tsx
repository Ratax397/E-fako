import { JSX, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet'
import { FiMapPin } from 'react-icons/fi'
import L from 'leaflet'
import marqueurdedéchet from '../../images/bac.png'
import 'leaflet/dist/leaflet.css'

const customIcon = L.icon({
  iconUrl: marqueurdedéchet,
  iconSize: [40, 40],
  iconAnchor: [20, 40],
  popupAnchor: [0, -40]
})

type MarkerType = {
  id: number
  position: [number, number]
  city: string
}

const ClickHandler = ({ onClick }: { onClick: (latlng: [number, number]) => void }) => {
  useMapEvents({
    click(e) {
      onClick([e.latlng.lat, e.latlng.lng])
    }
  })
  return null
}

function Mapinteractive(): JSX.Element {
  const [markers, setMarkers] = useState<MarkerType[]>([])
  const [newPosition, setNewPosition] = useState<[number, number] | null>(null)
  const [cityInput, setCityInput] = useState('')
  const [showModal, setShowModal] = useState(false)

  const handleMapClick = (position: [number, number]) => {
    setNewPosition(position)
    setShowModal(true)
  }

  const handleAddMarker = () => {
    if (newPosition && cityInput.trim()) {
      setMarkers((prev) => [...prev, { id: Date.now(), position: newPosition, city: cityInput }])
      setCityInput('')
      setNewPosition(null)
      setShowModal(false)
    }
  }

  const removeMarker = (id: number) => {
    setMarkers((prev) => prev.filter((marker) => marker.id !== id))
  }

  return (
    <div className="bg-white p-6 rounded-2xl shadow-lg h-full">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-[#2F855A]">Emplacement des poubelles</h2>
        <FiMapPin className="text-[#2F855A]" size={24} />
      </div>

      <div className="rounded-xl overflow-hidden h-[300px] relative">
        <MapContainer
          center={[-18.8792, 47.5079]}
          zoom={6}
          scrollWheelZoom={true}
          className="w-full h-full z-0"
        >
          <TileLayer
            attribution="&copy; OpenStreetMap"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <ClickHandler onClick={handleMapClick} />

          {markers.map((marker) => (
            <Marker key={marker.id} position={marker.position} icon={customIcon}>
              <Popup>
                <div className="space-y-1 text-sm">
                  <div>
                    <strong>Ville :</strong> {marker.city}
                  </div>
                  <div>
                    <strong>Latitude:</strong> {marker.position[0].toFixed(4)}
                  </div>
                  <div>
                    <strong>Longitude:</strong> {marker.position[1].toFixed(4)}
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation() 
                      removeMarker(marker.id)
                    }}
                    className="mt-2 px-3 py-1 text-white bg-red-500 hover:bg-red-600 rounded"
                  >
                    Supprimer
                  </button>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>

        {/* Modal d'entrée de ville */}
        {showModal && (
          <div className="absolute inset-0 flex items-center justify-center bg-[#2F855A] bg-opacity-40 z-10">
            <form
              className="bg-white rounded-lg p-6 shadow-xl w-[90%] max-w-md"
              onClick={(e) => {
                e.preventDefault()
                handleAddMarker()
              }}
            >
              <h3 className="text-lg font-semibold text-[#2F855A] mb-3">Nom de la ville</h3>
              <input
                type="text"
                className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#2F855A]"
                placeholder="Ex: Antananarivo"
                value={cityInput}
                onChange={(e) => setCityInput(e.target.value)}
              />
              <div className="flex cursor-pointer justify-end gap-3 mt-4">
                <button
                  className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
                  onClick={() => {
                    setShowModal(false)
                    setCityInput('')
                    setNewPosition(null)
                  }}
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-[#2F855A] cursor-pointer text-white rounded hover:bg-green-700"
                >
                  Ajouter
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  )
}

export default Mapinteractive
