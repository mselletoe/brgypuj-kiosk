/**
 * @file http.js
 * @description Centralized Axios instance configuration.
 * This module initializes the base API client used for all network requests.
 * It handles base URL configuration, timeout settings, and default headers 
 * to ensure consistency across the application.
 */

import axios from 'axios'

/**
 * Custom Axios instance with pre-configured defaults.
 * * @type {import('axios').AxiosInstance}
 * * @property {string} baseURL - The root URL for all API calls. 
 * Defaults to localhost if the environment variable is not set.
 * * @property {number} timeout - Request timeout in milliseconds (10 seconds).
 * Prevents requests from hanging indefinitely in case of network issues.
 * * @property {Object} headers - Default headers sent with every request.
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

export default api