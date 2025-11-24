// src/api/api.js
import axios from 'axios'
import { auth } from '@/stores/auth'  // Import logout directly

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000', // FastAPI backend
  timeout: 10000,
})

// Request interceptor - automatically add JWT token to all requests
api.interceptors.request.use(
  (config) => {
    // Get token from auth store
    const token = auth.token
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear auth and redirect to login
      logout()  // Use the imported logout function
      
      // Only redirect if not already on login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api