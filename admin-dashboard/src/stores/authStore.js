/*
 * =================================================================================
 * File: stores/authStore.js
 * Description: 
 * State management for User Authentication using Pinia.
 * - Stores the JWT Access Token.
 * - Decodes user information from the token (e.g., User ID, Role).
 * - Persists login state using LocalStorage so users stay logged in on refresh.
 * =================================================================================
 */

import { defineStore } from 'pinia'
import { jwtDecode } from 'jwt-decode'

export const useAuth = defineStore('auth', {
  state: () => ({
    token: null,
    user: null
  }),
  actions: {
    setToken(token) {
      this.token = token
      try {
        this.user = jwtDecode(token)
      } catch {
        this.user = null
      }
      localStorage.setItem('token', token)
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    },
    loadToken() {
      const token = localStorage.getItem('token')
      if (token) this.setToken(token)
    }
  }
})