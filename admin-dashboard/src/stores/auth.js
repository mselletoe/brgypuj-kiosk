import { defineStore } from 'pinia'
import { getCurrentAdmin } from '@/api/authService'

export const useAdminAuthStore = defineStore('adminAuth', {
  state: () => ({
    token: null,
    admin: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isSuperAdmin:    (state) => state.admin?.system_role === 'superadmin',
  },

  actions: {
    // Call this right after a successful login
    async initSession(token) {
      this.token = token
      localStorage.setItem('admin_token', token)

      // Fetch the full profile so system_role is available immediately
      const profile = await getCurrentAdmin()
      this.admin = profile
      localStorage.setItem('admin_profile', JSON.stringify(profile))
    },

    loadAuth() {
      const token   = localStorage.getItem('admin_token')
      const profile = localStorage.getItem('admin_profile')
      if (token && profile) {
        this.token = token
        this.admin = JSON.parse(profile)
      }
    },

    logout() {
      this.token = null
      this.admin = null
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_profile')
    },
  },
})