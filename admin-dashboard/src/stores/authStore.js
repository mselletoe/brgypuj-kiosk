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