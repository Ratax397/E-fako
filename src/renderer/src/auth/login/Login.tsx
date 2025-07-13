import { FaEnvelope, FaLock, FaEye, FaEyeSlash, FaUserShield } from 'react-icons/fa'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import * as yup from 'yup'
import { yupResolver } from '@hookform/resolvers/yup'
import { JSX, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import deco2 from "../../images/deco/2.png"



function Login(): JSX.Element {
  const [showPassword, setShowPassword] = useState(false)
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
  } = useForm({ resolver: yupResolver(ValidationSchema) })

  const onSubmit = (data: any) => {
    console.log(data)
    navigate('/home')
    reset()
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
      </div>

      <div className="w-1/2 relative flex items-center justify-center overflow-hidden">
        <div className={`absolute bg-[#6a2e3e] `}></div>

        <div className="relative z-10 w-full max-w-md p-10 text-white clip-trapeze">
          <h2 className="text-4xl font-bold text-[#2F855A] text-center mb-8">Connexion Admin</h2>
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
                />
                <button
                  type="button"
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500"
                  onClick={() => setShowPassword((prev) => !prev)}
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
              className="w-full bg-[#2F855A] text-white p-3 rounded-lg hover:bg-[#276749] transition duration-300 font-medium"
            >
              Connexion
            </button>

            <div className="mt-3  text-[#2F855A]  flex justify-center">
              <p>Vous n'avez pas de compte?</p>
              <Link to="/register" className=" text-[#2F855A]  font-semibold hover:underline ml-2">
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
