import { useEffect, useState } from 'react'
import axios from 'axios'
import { motion } from 'framer-motion'
import { FiCloud } from 'react-icons/fi'

interface WeatherData {
  name: string
  weather: { icon: string; description: string }[]
  main: { temp: number; humidity: number }
  wind: { speed: number }
}

const Weathercard = () => {
  const [weather, setWeather] = useState<WeatherData | null>(null)
  const city = 'Antananarivo'
  const API_KEY = '515c2bde97eb02e46fed16fbe2fea419'

  useEffect(() => {
    axios
      .get(
        `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${API_KEY}&units=metric&lang=fr`
      )
      .then((res) => {
        setWeather(res.data)
      })
      .catch((err) => {
        console.log('Erreur de la weather :', err)
      })
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="mt-6 bg-gradient-to-br from-[#276749] to-[#1F5745] text-white p-4 rounded-2xl shadow-inner text-center border border-[#1e4f3f]"
    >
      {weather ? (
        <>
          <div className="flex items-center justify-center gap-2 mb-2">
            <img
              className="w-10 h-10"
              src={`https://openweathermap.org/img/wn/${weather.weather[0].icon}.png`}
              alt="weather icon"
            />
            <div className="text-left">
              <h2 className="text-sm font-bold">{weather.name}</h2>
              <p className="text-[11px] capitalize text-gray-200">
                {weather.weather[0].description}
              </p>
            </div>
          </div>

          <p className="text-2xl font-bold text-[#9f7126] mb-1">
            {Math.round(weather.main.temp)}°C
          </p>

          <div className="flex justify-between text-[11px] text-gray-300 mt-1 px-1">
            <p>💧 {weather.main.humidity}%</p>
            <p>💨 {weather.wind.speed} m/s</p>
          </div>
        </>
      ) : (
        <div className="flex items-center justify-center gap-2 text-gray-200">
          <FiCloud className="animate-spin" />
          <p>Chargement météo...</p>
        </div>
      )}
    </motion.div>
  )
}

export default Weathercard
