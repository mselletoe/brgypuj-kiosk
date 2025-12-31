import { defineStore } from "pinia"

export const useAuthStore = defineStore("auth", {
  state: () => ({
    mode: null,
    resident: null,
    rfidUid: null
  }),

  getters: {
    isGuest: (s) => s.mode === "guest",
    isRFID: (s) => s.mode === "rfid",
    isAuthenticated: (s) => !!s.mode,

    residentId: (s) => s.resident?.id || null,

    userName: (s) =>
      s.mode === "rfid"
        ? `${s.resident.first_name} ${s.resident.last_name}`
        : "Guest"
  },

  actions: {
    setGuest() {
      this.mode = "guest"
      this.resident = null
      this.rfidUid = null
      this.persist()
    },

    setRFID(resident, uid) {
      this.mode = "rfid"
      this.resident = resident
      this.rfidUid = uid
      this.persist()
    },

    logout() {
      this.$reset()
      localStorage.removeItem("kiosk_auth")
    },

    restore() {
      const stored = localStorage.getItem("kiosk_auth")
      if (stored) Object.assign(this, JSON.parse(stored))
    },

    persist() {
      localStorage.setItem(
        "kiosk_auth",
        JSON.stringify({
          mode: this.mode,
          resident: this.resident,
          rfidUid: this.rfidUid
        })
      )
    }
  }
})