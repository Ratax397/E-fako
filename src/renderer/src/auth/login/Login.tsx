import { FaEnvelope, FaLock, FaEye, FaEyeSlash, FaUserShield } from 'react-icons/fa'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import * as yup from 'yup'
import { yupResolver } from '@hookform/resolvers/yup'
import { JSX, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import deco2 from "../../images/deco/2.png"
import apiService, { ApiError, UserLoginData } from '../../services/apiService'

function Login(): JSX.Element {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [apiError, setApiError] = useState<string>('')
  const navigate = useNavigate()

  const ValidationSchema = yup.object({
    email: yup.string().email('Email invalide').required('Veuillez entrer votre email'),
    password: yup.string().min(6, 'Au moins 6 caractères').required('Mot de passe requis')
  })

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset
  } = useForm<UserLoginData>({ resolver: yupResolver(ValidationSchema) })

  const onSubmit = async (data: UserLoginData) => {
    setIsLoading(true)
    setApiError('')
    
    try {
      console.log('🔐 Tentative de connexion...', { email: data.email })
      
      // Test de connexion avec le backend
      const isBackendConnected = await apiService.testConnection()
      if (!isBackendConnected) {
        throw new Error('Backend non accessible. Vérifiez que le serveur est démarré sur http://localhost:8000')
      }
      
      // Tentative de connexion
      const loginResponse = await apiService.login(data)
      
      console.log('✅ Connexion réussie!', loginResponse)
      
      // Redirection vers le dashboard
      navigate('/home')
      reset()
      
    } catch (error) {
      console.error('❌ Erreur de connexion:', error)
      
      if (error instanceof ApiError) {
        setApiError(error.message)
      } else if (error instanceof Error) {
        setApiError(error.message)
      } else {
        setApiError('Erreur de connexion inattendue')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const testBackendConnection = async () => {
    try {
      const isConnected = await apiService.testConnection()
      if (isConnected) {
        setApiError('')
        alert('✅ Connexion au backend réussie!')
      } else {
        setApiError('❌ Backend non accessible. Vérifiez que le serveur est démarré.')
      }
    } catch (error) {
      console.error('Test de connexion échoué:', error)
      setApiError('❌ Impossible de tester la connexion au backend')
    }
  }

  return (
    <div className="flex h-screen bg-white">
      <div className="w-1/2 bg-[#2F855A] text-white flex flex-col justify-center items-start pl-20 pr-10">
        <div className="mb-6 flex items-center gap-3">
          <FaUserShield size={45} className="text-white" />
          <h1 className="text-3xl font-extrabold tracking-wide">Espace Admin</h1>
        </div>

        <p className="text-lg leading-relaxed max-w-md">
          Bienvenue sur votre interface d'administration sécurisée. Veuillez vous connecter pour
          gérer les utilisateurs, consulter les statistiques et superviser les activités de tri.
        </p>

        <p className="mt-4 text-sm text-green-100 italic">
          * Accès réservé aux administrateurs et super administrateurs.
        </p>
        
        {/* Bouton de test de connexion backend */}
        <button
          onClick={testBackendConnection}
          className="mt-6 bg-green-700 hover:bg-green-800 text-white px-4 py-2 rounded-lg text-sm transition duration-300"
        >
          🔗 Tester la connexion backend
        </button>
      </div>

      <div className="w-1/2 relative flex items-center justify-center overflow-hidden">
        <div className={`absolute bg-[#6a2e3e] `}></div>

        <div className="relative z-10 w-full max-w-md p-10 text-white clip-trapeze">
          <h2 className="text-4xl font-bold text-[#2F855A] text-center mb-8">Connexion Admin</h2>
          
          {/* Affichage des erreurs API */}
          {apiError && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-sm"
            >
              {apiError}
            </motion.div>
          )}
          
          <form className="space-y-5" onSubmit={handleSubmit(onSubmit)}>
            <div className="relative flex flex-col">
              <div className="relative">
                <FaEnvelope className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#2F855A]" />
                <input
                  autoComplete="username"
                  type="email"
                  className={`w-full pl-10 p-3 border rounded-lg text-black outline-none  bg-white focus:ring-2 focus:ring-[#2F855A] ${
                    errors.email ? 'border-red-400 ' : 'border-gray-300'
                  }`}
                  placeholder="Votre e-mail"
                  {...register('email')}
                  disabled={isLoading}
                />
              </div>
              {errors.email && (
                <motion.p
                  className="text-sm text-red-400 mt-1"
                  initial={{ opacity: 0, y: -3 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  {errors.email.message}
                </motion.p>
              )}
            </div>

            <div className="relative flex flex-col">
              <div className="relative">
                <FaLock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#2F855A]" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  className={`bg-white text-black w-full p-3 pl-10 border rounded-lg focus:ring-2 focus:ring-[#2F855A] outline-none ${
                    errors.password ? 'border-red-400' : 'border-gray-300'
                  }`}
                  placeholder="Votre mot de passe"
                  {...register('password')}
                  disabled={isLoading}
                />
                <button
                  type="button"
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500"
                  onClick={() => setShowPassword((prev) => !prev)}
                  disabled={isLoading}
                >
                  {showPassword ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
              {errors.password && (
                <motion.p
                  className="text-sm text-red-400 mt-1"
                  initial={{ opacity: 0, y: -3 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  {errors.password.message}
                </motion.p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className={`w-full p-3 rounded-lg font-medium transition duration-300 ${
                isLoading 
                  ? 'bg-gray-400 text-gray-200 cursor-not-allowed' 
                  : 'bg-[#2F855A] text-white hover:bg-[#276749]'
              }`}
            >
              {isLoading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Connexion en cours...
                </div>
              ) : (
                'Connexion'
              )}
            </button>

            <div className="mt-3  text-[#2F855A]  flex justify-center">
              <p>Vous n'avez pas de compte?</p>
              <Link 
                to="/register" 
                className="text-[#2F855A] font-semibold hover:underline ml-2"
              >
                Inscription
              </Link>
            </div>
          </form>
        </div>
        <img className="absolute -top-14 rotate-[100deg] -right-10" src={deco2} width={200} />
        <img
          className={`absolute -bottom-20 rotate-[190deg] -right-10`}
          src={deco2}
          width={225}
          alt=""
        />
      </div>
    </div>
  )
}

export default Login
