import { defineStore } from 'pinia'

export const useRfidRegistrationStore = defineStore('registration', {
  state: () => ({
    pendingRfidUid: null,

    isAdminMode: false,
  }),

  actions: {
    setPendingRfidUid(uid) {
      this.pendingRfidUid = uid
      this.isAdminMode = true
    },

    clearAdminMode() {
      this.isAdminMode = false
    },

    clearAll() {
      this.pendingRfidUid = null
      this.isAdminMode = false
    },
  },
})