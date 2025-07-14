/**
 * Configuration API pour l'intégration avec le backend MySQL
 */

// Configuration de base de l'API
export const API_CONFIG = {
  // URL de base du backend
  BASE_URL: 'http://localhost:8000',
  
  // Version de l'API
  API_VERSION: 'v1',
  
  // Timeout par défaut (30 secondes)
  TIMEOUT: 30000,
  
  // Headers par défaut
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
} as const

// URL complète de l'API
export const API_BASE_URL = `${API_CONFIG.BASE_URL}/api/${API_CONFIG.API_VERSION}`

// Endpoints de l'API
export const API_ENDPOINTS = {
  // Authentification
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    FACE_LOGIN: '/auth/face-login',
    FACE_REGISTER: '/auth/face-register',
    REFRESH: '/auth/refresh',
    LOGOUT: '/auth/logout',
    ME: '/auth/me',
    VERIFY_TOKEN: '/auth/verify-token',
    PASSWORD_RESET: '/auth/password-reset',
    PASSWORD_RESET_CONFIRM: '/auth/password-reset-confirm'
  },
  
  // Utilisateurs
  USERS: {
    LIST: '/users',
    CREATE: '/users',
    GET: (id: string) => `/users/${id}`,
    UPDATE: (id: string) => `/users/${id}`,
    DELETE: (id: string) => `/users/${id}`,
    SEARCH: '/users/search',
    BULK_DELETE: '/users/bulk-delete'
  },
  
  // Gestion des déchets
  WASTE: {
    LIST: '/waste',
    CREATE: '/waste',
    GET: (id: string) => `/waste/${id}`,
    UPDATE: (id: string) => `/waste/${id}`,
    DELETE: (id: string) => `/waste/${id}`,
    SEARCH: '/waste/search',
    BY_USER: (userId: string) => `/waste/user/${userId}`,
    BY_TYPE: (type: string) => `/waste/type/${type}`,
    BY_STATUS: (status: string) => `/waste/status/${status}`,
    BULK_UPDATE: '/waste/bulk-update'
  },
  
  // Statistiques
  STATISTICS: {
    DASHBOARD: '/statistics/dashboard',
    WASTE_BY_TYPE: '/statistics/waste-by-type',
    WASTE_BY_USER: '/statistics/waste-by-user',
    ENVIRONMENTAL_IMPACT: '/statistics/environmental-impact',
    RECYCLING_RATES: '/statistics/recycling-rates',
    MONTHLY_TRENDS: '/statistics/monthly-trends',
    EXPORT: '/statistics/export'
  },
  
  // Notifications
  NOTIFICATIONS: {
    LIST: '/notifications',
    CREATE: '/notifications',
    GET: (id: string) => `/notifications/${id}`,
    UPDATE: (id: string) => `/notifications/${id}`,
    DELETE: (id: string) => `/notifications/${id}`,
    MARK_READ: (id: string) => `/notifications/${id}/read`,
    MARK_ALL_READ: '/notifications/mark-all-read',
    UNREAD_COUNT: '/notifications/unread-count'
  },
  
  // Health check
  HEALTH: '/health',
  ROOT: '/'
} as const

// Types pour les réponses API
export interface ApiResponse<T = any> {
  data?: T
  message?: string
  success: boolean
  errors?: string[]
}

export interface PaginatedResponse<T = any> {
  data: T[]
  total: number
  page: number
  per_page: number
  pages: number
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: {
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
}

// Configuration des statuts HTTP
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  INTERNAL_SERVER_ERROR: 500
} as const

// Messages d'erreur standardisés
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Erreur de connexion réseau',
  UNAUTHORIZED: 'Session expirée, veuillez vous reconnecter',
  FORBIDDEN: 'Accès non autorisé',
  NOT_FOUND: 'Ressource non trouvée',
  SERVER_ERROR: 'Erreur serveur, veuillez réessayer',
  VALIDATION_ERROR: 'Données invalides',
  UNKNOWN_ERROR: 'Une erreur inattendue s\'est produite'
} as const