/**
 * Hook personnalisé pour la gestion de l'authentification
 */

import { useState, useEffect, useCallback } from 'react'
import apiService, { ApiError, UserLoginData, UserRegisterData } from '../services/apiService'

export interface User {
  id: string
  email: string
  username: string
  first_name: string
  last_name: string
  role: string
  status: string
  is_active: boolean
  is_verified: boolean
}

export interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null
  })

  // Initialiser l'état d'authentification au démarrage
  useEffect(() => {
    initializeAuth()
  }, [])

  const initializeAuth = useCallback(async () => {
    try {
      setAuthState((prev: AuthState) => ({ ...prev, isLoading: true, error: null }))

      // Vérifier si un token existe
      if (!apiService.isAuthenticated()) {
        // Charger les données utilisateur depuis localStorage si disponibles
        const savedUser = localStorage.getItem('user')
        if (savedUser) {
          const user = JSON.parse(savedUser)
          setAuthState((prev: AuthState) => ({
            ...prev,
            user,
            isAuthenticated: true,
            isLoading: false
          }))
          return
        }

        setAuthState((prev: AuthState) => ({
          ...prev,
          user: null,
          isAuthenticated: false,
          isLoading: false
        }))
        return
      }

      // Valider le token avec le backend
      try {
        const currentUser = await apiService.getCurrentUser()
        setAuthState((prev: AuthState) => ({
          ...prev,
          user: currentUser,
          isAuthenticated: true,
          isLoading: false,
          error: null
        }))
      } catch (error) {
        // Token invalide, nettoyer l'état
        await apiService.logout()
        setAuthState((prev: AuthState) => ({
          ...prev,
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null
        }))
      }
    } catch (error) {
      console.error('Erreur lors de l\'initialisation de l\'authentification:', error)
      setAuthState((prev: AuthState) => ({
        ...prev,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: 'Erreur lors de l\'initialisation'
      }))
    }
  }, [])

  const login = useCallback(async (credentials: UserLoginData): Promise<void> => {
    try {
      setAuthState((prev: AuthState) => ({ ...prev, isLoading: true, error: null }))

      const loginResponse = await apiService.login(credentials)
      
      setAuthState((prev: AuthState) => ({
        ...prev,
        user: loginResponse.user,
        isAuthenticated: true,
        isLoading: false,
        error: null
      }))
    } catch (error) {
      let errorMessage = 'Erreur de connexion'
      
      if (error instanceof ApiError) {
        errorMessage = error.message
      } else if (error instanceof Error) {
        errorMessage = error.message
      }

      setAuthState((prev: AuthState) => ({
        ...prev,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: errorMessage
      }))
      
      throw error
    }
  }, [])

  const register = useCallback(async (userData: UserRegisterData): Promise<void> => {
    try {
      setAuthState((prev: AuthState) => ({ ...prev, isLoading: true, error: null }))

      await apiService.register(userData)
      
      setAuthState((prev: AuthState) => ({
        ...prev,
        isLoading: false,
        error: null
      }))
    } catch (error) {
      let errorMessage = 'Erreur lors de l\'inscription'
      
      if (error instanceof ApiError) {
        errorMessage = error.message
      } else if (error instanceof Error) {
        errorMessage = error.message
      }

      setAuthState((prev: AuthState) => ({
        ...prev,
        isLoading: false,
        error: errorMessage
      }))
      
      throw error
    }
  }, [])

  const logout = useCallback(async (): Promise<void> => {
    try {
      setAuthState((prev: AuthState) => ({ ...prev, isLoading: true }))

      await apiService.logout()
      
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      })
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error)
      // Forcer la déconnexion même en cas d'erreur
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      })
    }
  }, [])

  const clearError = useCallback(() => {
    setAuthState((prev: AuthState) => ({ ...prev, error: null }))
  }, [])

  const refreshUser = useCallback(async (): Promise<void> => {
    try {
      if (!apiService.isAuthenticated()) {
        return
      }

      const currentUser = await apiService.getCurrentUser()
      setAuthState((prev: AuthState) => ({
        ...prev,
        user: currentUser,
        error: null
      }))
    } catch (error) {
      console.error('Erreur lors de la mise à jour des données utilisateur:', error)
      // En cas d'erreur, déconnecter l'utilisateur
      await logout()
    }
  }, [logout])

  const checkBackendConnection = useCallback(async (): Promise<boolean> => {
    try {
      return await apiService.testConnection()
    } catch (error) {
      console.error('Erreur lors du test de connexion:', error)
      return false
    }
  }, [])

  return {
    // État d'authentification
    ...authState,
    
    // Actions
    login,
    register,
    logout,
    clearError,
    refreshUser,
    checkBackendConnection,
    
    // Utilitaires
    isAdmin: authState.user?.role === 'admin' || authState.user?.role === 'super_admin',
    isSuperAdmin: authState.user?.role === 'super_admin',
    fullName: authState.user ? `${authState.user.first_name} ${authState.user.last_name}` : null
  }
}