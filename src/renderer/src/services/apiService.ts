/**
 * Service API centralisé pour l'intégration avec le backend MySQL
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { 
  API_CONFIG, 
  API_BASE_URL, 
  API_ENDPOINTS, 
  LoginResponse, 
  HTTP_STATUS, 
  ERROR_MESSAGES 
} from '../config/api'

// Types pour les données utilisateur
export interface UserLoginData {
  email: string
  password: string
}

export interface UserRegisterData {
  email: string
  username: string
  password: string
  first_name: string
  last_name: string
  phone?: string
  address?: string
}

export interface FaceLoginData {
  face_image: string // Base64 encoded image
}

export interface FaceRegisterData {
  face_image: string // Base64 encoded image
}

// Classe pour gérer les erreurs API
export class ApiError extends Error {
  public status: number
  public data: any

  constructor(message: string, status: number, data?: any) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

// Classe principale du service API
class ApiService {
  private api: AxiosInstance
  private accessToken: string | null = null
  private refreshToken: string | null = null

  constructor() {
    // Créer l'instance axios
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: API_CONFIG.DEFAULT_HEADERS
    })

    // Configurer les intercepteurs
    this.setupInterceptors()
    
    // Charger les tokens depuis le localStorage
    this.loadTokensFromStorage()
  }

  private setupInterceptors(): void {
    // Intercepteur pour les requêtes
    this.api.interceptors.request.use(
      (config) => {
        // Ajouter le token d'authentification si disponible
        if (this.accessToken) {
          config.headers.Authorization = `Bearer ${this.accessToken}`
        }
        
        console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('❌ Request Error:', error)
        return Promise.reject(error)
      }
    )

    // Intercepteur pour les réponses
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`✅ API Response: ${response.status} ${response.config.url}`)
        return response
      },
      async (error: AxiosError) => {
        console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`)
        
        // Gestion de l'expiration du token
        if (error.response?.status === HTTP_STATUS.UNAUTHORIZED && this.refreshToken) {
          try {
            await this.refreshAccessToken()
            // Retry la requête originale
            return this.api.request(error.config!)
          } catch (refreshError) {
            this.logout()
            throw new ApiError(ERROR_MESSAGES.UNAUTHORIZED, HTTP_STATUS.UNAUTHORIZED)
          }
        }

        // Créer une erreur personnalisée
        const apiError = this.createApiError(error)
        return Promise.reject(apiError)
      }
    )
  }

  private createApiError(error: AxiosError): ApiError {
    if (error.response) {
      // Erreur de réponse du serveur
      const status = error.response.status
      const data = error.response.data as any

      let message: string
      
      switch (status) {
        case HTTP_STATUS.BAD_REQUEST:
          message = data?.message || ERROR_MESSAGES.VALIDATION_ERROR
          break
        case HTTP_STATUS.UNAUTHORIZED:
          message = ERROR_MESSAGES.UNAUTHORIZED
          break
        case HTTP_STATUS.FORBIDDEN:
          message = ERROR_MESSAGES.FORBIDDEN
          break
        case HTTP_STATUS.NOT_FOUND:
          message = ERROR_MESSAGES.NOT_FOUND
          break
        case HTTP_STATUS.INTERNAL_SERVER_ERROR:
          message = ERROR_MESSAGES.SERVER_ERROR
          break
        default:
          message = data?.message || ERROR_MESSAGES.UNKNOWN_ERROR
      }

      return new ApiError(message, status, data)
    } else if (error.request) {
      // Erreur de réseau
      return new ApiError(ERROR_MESSAGES.NETWORK_ERROR, 0)
    } else {
      // Erreur de configuration
      return new ApiError(error.message || ERROR_MESSAGES.UNKNOWN_ERROR, 0)
    }
  }

  private loadTokensFromStorage(): void {
    this.accessToken = localStorage.getItem('access_token')
    this.refreshToken = localStorage.getItem('refresh_token')
  }

  private saveTokensToStorage(tokens: { access_token: string; refresh_token: string }): void {
    this.accessToken = tokens.access_token
    this.refreshToken = tokens.refresh_token
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
  }

  private clearTokensFromStorage(): void {
    this.accessToken = null
    this.refreshToken = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  // Méthodes d'authentification
  async login(credentials: UserLoginData): Promise<LoginResponse> {
    const response = await this.api.post<LoginResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      credentials
    )
    
    const loginData = response.data
    this.saveTokensToStorage(loginData)
    
    // Sauvegarder les infos utilisateur
    localStorage.setItem('user', JSON.stringify(loginData.user))
    
    return loginData
  }

  async register(userData: UserRegisterData): Promise<any> {
    const response = await this.api.post(API_ENDPOINTS.AUTH.REGISTER, userData)
    return response.data
  }

  async faceLogin(faceData: FaceLoginData): Promise<LoginResponse> {
    const response = await this.api.post<LoginResponse>(
      API_ENDPOINTS.AUTH.FACE_LOGIN,
      faceData
    )
    
    const loginData = response.data
    this.saveTokensToStorage(loginData)
    localStorage.setItem('user', JSON.stringify(loginData.user))
    
    return loginData
  }

  async faceRegister(faceData: FaceRegisterData): Promise<any> {
    const response = await this.api.post(API_ENDPOINTS.AUTH.FACE_REGISTER, faceData)
    return response.data
  }

  async refreshAccessToken(): Promise<void> {
    if (!this.refreshToken) {
      throw new ApiError(ERROR_MESSAGES.UNAUTHORIZED, HTTP_STATUS.UNAUTHORIZED)
    }

    const response = await this.api.post(API_ENDPOINTS.AUTH.REFRESH, {}, {
      headers: {
        Authorization: `Bearer ${this.refreshToken}`
      }
    })
    
    this.saveTokensToStorage(response.data)
  }

  async logout(): Promise<void> {
    try {
      if (this.accessToken) {
        await this.api.post(API_ENDPOINTS.AUTH.LOGOUT)
      }
    } catch (error) {
      console.warn('Logout request failed:', error)
    } finally {
      this.clearTokensFromStorage()
    }
  }

  async getCurrentUser(): Promise<any> {
    const response = await this.api.get(API_ENDPOINTS.AUTH.ME)
    return response.data
  }

  // Méthodes utilitaires
  isAuthenticated(): boolean {
    return !!this.accessToken
  }

  getAccessToken(): string | null {
    return this.accessToken
  }

  // Méthodes génériques pour les requêtes
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.get<T>(url, config)
    return response.data
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.post<T>(url, data, config)
    return response.data
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.put<T>(url, data, config)
    return response.data
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.delete<T>(url, config)
    return response.data
  }

  // Test de connexion avec le backend
  async testConnection(): Promise<boolean> {
    try {
      const response = await this.api.get(API_ENDPOINTS.HEALTH)
      return response.status === HTTP_STATUS.OK
    } catch (error) {
      console.error('Backend connection test failed:', error)
      return false
    }
  }
}

// Export de l'instance singleton
export const apiService = new ApiService()
export default apiService