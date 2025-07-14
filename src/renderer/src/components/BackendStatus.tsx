/**
 * Composant pour afficher le statut de connexion avec le backend MySQL
 */

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FaCheckCircle, FaTimesCircle, FaSpinner, FaDatabase } from 'react-icons/fa'
import apiService from '../services/apiService'

interface BackendStatusProps {
  className?: string
  showDetails?: boolean
}

const BackendStatus: React.FC<BackendStatusProps> = ({ 
  className = '', 
  showDetails = false 
}) => {
  const [isConnected, setIsConnected] = useState<boolean | null>(null)
  const [isChecking, setIsChecking] = useState(false)
  const [lastChecked, setLastChecked] = useState<Date | null>(null)

  const checkConnection = async () => {
    setIsChecking(true)
    try {
      const connected = await apiService.testConnection()
      setIsConnected(connected)
      setLastChecked(new Date())
    } catch (error) {
      console.error('Erreur lors du test de connexion:', error)
      setIsConnected(false)
    } finally {
      setIsChecking(false)
    }
  }

  // Vérifier la connexion au montage du composant
  useEffect(() => {
    checkConnection()
  }, [])

  const getStatusIcon = () => {
    if (isChecking) {
      return <FaSpinner className="animate-spin text-blue-500" />
    }
    
    if (isConnected === true) {
      return <FaCheckCircle className="text-green-500" />
    }
    
    if (isConnected === false) {
      return <FaTimesCircle className="text-red-500" />
    }
    
    return <FaDatabase className="text-gray-400" />
  }

  const getStatusText = () => {
    if (isChecking) {
      return 'Vérification en cours...'
    }
    
    if (isConnected === true) {
      return 'Backend connecté'
    }
    
    if (isConnected === false) {
      return 'Backend déconnecté'
    }
    
    return 'Statut inconnu'
  }

  const getStatusColor = () => {
    if (isChecking) return 'text-blue-600'
    if (isConnected === true) return 'text-green-600'
    if (isConnected === false) return 'text-red-600'
    return 'text-gray-600'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex items-center gap-2 ${className}`}
    >
      <div className="flex items-center gap-2">
        {getStatusIcon()}
        <span className={`text-sm font-medium ${getStatusColor()}`}>
          {getStatusText()}
        </span>
      </div>
      
      {showDetails && (
        <div className="flex items-center gap-2">
          {lastChecked && (
            <span className="text-xs text-gray-500">
              (dernière vérification: {lastChecked.toLocaleTimeString()})
            </span>
          )}
          
          <button
            onClick={checkConnection}
            disabled={isChecking}
            className="text-xs text-blue-500 hover:text-blue-700 underline disabled:opacity-50"
          >
            Actualiser
          </button>
        </div>
      )}
      
      {isConnected === false && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700"
        >
          <p className="font-medium">Backend non accessible</p>
          <p className="text-xs mt-1">
            Vérifiez que le serveur backend est démarré sur http://localhost:8000
          </p>
          <p className="text-xs mt-1">
            Commande: <code className="bg-red-100 px-1 rounded">python -m uvicorn app.main:app --reload</code>
          </p>
        </motion.div>
      )}
    </motion.div>
  )
}

export default BackendStatus