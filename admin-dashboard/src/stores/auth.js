import { defineStore } from 'pinia'

export const useAdminAuthStore = defineStore('adminAuth', {
  state: () => ({
    token: null,
    admin: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token
  },

  actions: {
    setAuth(token, admin) {
      this.token = token
      this.admin = admin

      localStorage.setItem('admin_token', token)
      localStorage.setItem('admin_profile', JSON.stringify(admin))
    },

    loadAuth() {
      const token = localStorage.getItem('admin_token')
      const admin = localStorage.getItem('admin_profile')

      if (token && admin) {
        this.token = token
        this.admin = JSON.parse(admin)
      }
    },

    logout() {
      this.token = null
      this.admin = null
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_profile')
    }
  }
})
