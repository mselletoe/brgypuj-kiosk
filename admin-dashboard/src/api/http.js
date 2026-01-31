/**
 * @file http.js
 * @description Centralized Axios instance with JWT authentication logic.
 * This module configures the primary API client for the Admin Dashboard,
 * including an interceptor that automatically attaches the access token
 * to every outgoing request for secure communication.
 */
import axios from 'axios'
import { useAdminAuthStore } from '@/stores/auth'

/**
 * Custom Axios instance with pre-configured defaults.
 * @type {import('axios').AxiosInstance}
 * @property {string} baseURL - The root URL for all API calls. 
 * Defaults to localhost if the environment variable is not set.
 * @property {number} timeout - Request timeout in milliseconds (10 seconds).
 * @property {Object} headers - Default headers sent with every request.
 */
const api = axios.create({
  // Priority 1: Environment variable from .env file (VITE_API_URL)
  // Priority 2: Hardcoded fallback for local development
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * Request Interceptor for Automatic Authentication.
 * This function runs before every request is sent to the server.
 * It checks the Admin Pinia store for a valid JWT and injects it into the 
 * Authorization header using the Bearer scheme.
 */
api.interceptors.request.use(
  (config) => {
    const auth = useAdminAuthStore()

    // Attach JWT automatically if the token exists in the store
    if (auth.token) {
      config.headers.Authorization = `Bearer ${auth.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

export default api