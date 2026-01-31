/**
 * @file auth.js
 * @description Pinia store for managing Kiosk authentication state.
 * This store handles the transitions between Guest and RFID modes and 
 * ensures session persistence using the browser's LocalStorage.
 */

import { defineStore } from "pinia"

export const useAuthStore = defineStore("auth", {
  /**
   * @state
   * @property {string|null} mode - Current session type ('guest', 'rfid', or null).
   * @property {Object|null} resident - Contains basic profile data (id, names) for RFID users.
   * @property {string|null} rfidUid - The hardware UID of the currently scanned tag.
   */
  state: () => ({
    mode: null,
    resident: null,
    rfidUid: null
  }),

  /**
   * @getters
   * Reactive derived state for cleaner component templates.
   */
  getters: {
    isGuest: (s) => s.mode === "guest",
    isRFID: (s) => s.mode === "rfid",
    isAuthenticated: (s) => !!s.mode,

    residentId: (s) => s.resident?.id || null,

    /** * @returns {string} 
     * Dynamically determines the greeting name displayed in the UI.
     */
    userName: (s) =>
      s.mode === "rfid"
        ? `${s.resident.first_name} ${s.resident.last_name}`
        : "Guest"
  },

  /**
   * @actions
   * Methods used to mutate state and handle side effects (like API calls or LocalStorage).
   */
  actions: {
    /**
     * Initializes a Guest session.
     * Clears any existing resident data and persists the 'guest' mode.
     */
    setGuest() {
      this.mode = "guest"
      this.resident = null
      this.rfidUid = null
      this.persist()
    },

    /**
     * Initializes an RFID-authenticated session.
     * @param {Object} resident - The resident profile returned from the backend.
     * @param {string} uid - The hardware UID scanned from the card.
     */
    setRFID(resident, uid) {
      this.mode = "rfid"
      this.resident = resident
      this.rfidUid = uid
      this.persist()
    },

    /**
     * Clears the current session.
     * Resets the store state to defaults and purges the LocalStorage entry.
     */
    logout() {
      this.$reset()
      localStorage.removeItem("kiosk_auth")
    },

    /**
     * Rehydrates the store state.
     * Loads the 'kiosk_auth' string from LocalStorage and parses it back into the state.
     * Usually called in the App.vue or main.js on application mount.
     */
    restore() {
      const stored = localStorage.getItem("kiosk_auth")
      if (stored) Object.assign(this, JSON.parse(stored))
    },

    /**
     * Synchronizes the Pinia state with the browser's LocalStorage.
     * This ensures the user remains logged in even if the page is refreshed.
     */
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