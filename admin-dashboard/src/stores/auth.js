/**
 * @file stores/auth.js
 * @description Pinia store for managing admin authentication state,
 * session persistence via localStorage, and profile hydration.
 */

import { defineStore } from 'pinia'
import { getCurrentAdmin } from '@/api/authService'

export const useAdminAuthStore = defineStore('adminAuth', {
  state: () => ({
    /** @type {string|null} JWT access token for the current admin session */
    token: null,

    /** @type {Object|null} Authenticated admin's profile data */
    admin: null,
  }),

  getters: {
    /** Returns true if an access token is present */
    isAuthenticated: (state) => !!state.token,

    /** Returns true if the authenticated admin has the superadmin system role */
    isSuperAdmin:    (state) => state.admin?.system_role === 'superadmin',
  },

  actions: {
    /**
     * Initializes a new admin session after a successful login.
     * Stores the access token, fetches the admin profile from the API,
     * and persists both to localStorage for session continuity.
     *
     * @param {string} token - JWT access token returned from the login API
     */
    async initSession(token) {
      this.token = token
      localStorage.setItem('admin_token', token)

      const profile = await getCurrentAdmin()
      this.admin = profile
      localStorage.setItem('admin_profile', JSON.stringify(profile))
    },

    /**
     * Restores the admin session from localStorage on app startup.
     * Should be called once in the app entry point or router guard.
     */
    loadAuth() {
      const token   = localStorage.getItem('admin_token')
      const profile = localStorage.getItem('admin_profile')
      if (token && profile) {
        this.token = token
        this.admin = JSON.parse(profile)
      }
    },
    
    /**
     * Clears the admin session from both the store and localStorage.
     * Should be called on explicit logout or when the token expires.
     */
    logout() {
      this.token = null
      this.admin = null
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_profile')
    },
  },
})