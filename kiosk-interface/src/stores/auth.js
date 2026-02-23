/**
 * @file auth.js
 * @description Pinia store for managing Kiosk authentication state.
 * This store handles the transitions between Guest and RFID modes and 
 * ensures session persistence using the browser's LocalStorage.
 * 
 * Authentication Flow:
 * 1. User scans RFID → setTemporaryRFIDData() stores resident info in temp state
 * 2. User completes PIN (setup or verify) → confirmRFIDLogin() promotes temp → permanent state
 * 3. Session persisted to LocalStorage for page refresh survival
 */

import { defineStore } from "pinia"

export const useAuthStore = defineStore("auth", {
  /**
   * @state
   * @property {string|null} mode - Current session type ('guest', 'rfid', or null).
   * @property {Object|null} resident - Contains basic profile data (id, names) for RFID users.
   * @property {string|null} rfidUid - The hardware UID of the currently scanned tag.
   * 
   * Temporary state (used during the scan → PIN → home transition):
   * @property {Object|null} tempResident - Resident data held while PIN is being entered.
   * @property {string|null} tempUid - RFID UID held while PIN is being entered.
   * @property {boolean} tempHasPin - Whether the resident has a configured PIN or needs setup.
   */
  state: () => ({
    // Permanent session state
    mode: null,
    resident: null,
    rfidUid: null,

    // Temporary state — bridges scan screen → PIN screen
    // Cleared after successful PIN entry or on logout
    tempResident: null,
    tempUid: null,
    tempHasPin: false,
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

    /**
     * @returns {string} 
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
     * Stores resident data temporarily after a successful RFID scan.
     * Does NOT commit a session yet — the user must still pass PIN verification.
     * 
     * @param {Object} payload
     * @param {Object} payload.resident - Basic resident profile (id, first_name, last_name).
     * @param {string} payload.uid - The hardware UID from the scanned card.
     * @param {boolean} payload.has_pin - Whether the resident has a configured PIN.
     */
    setTemporaryRFIDData({ resident, uid, has_pin }) {
      this.tempResident = resident
      this.tempUid = uid
      this.tempHasPin = has_pin
    },

    /**
     * Promotes temporary state to a permanent authenticated session.
     * Called by AuthPIN.vue after successful PIN verification or setup.
     * Clears temp state and persists the confirmed session to LocalStorage.
     */
    confirmRFIDLogin() {
      this.mode = "rfid"
      this.resident = this.tempResident
      this.rfidUid = this.tempUid

      // Clean up temp state — no longer needed
      this.tempResident = null
      this.tempUid = null
      this.tempHasPin = false

      this.persist()
    },

    /**
     * Initializes an RFID-authenticated session directly.
     * @param {Object} resident - The resident profile returned from the backend.
     * @param {string} uid - The hardware UID scanned from the card.
     * 
     * @deprecated Kept for compatibility. Prefer setTemporaryRFIDData() + confirmRFIDLogin()
     * to enforce PIN verification before granting session access.
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
     * Usually called in App.vue or main.js on application mount.
     */
    restore() {
      const stored = localStorage.getItem("kiosk_auth")
      if (stored) Object.assign(this, JSON.parse(stored))
    },

    /**
     * Synchronizes the permanent Pinia state with the browser's LocalStorage.
     * Temp state is intentionally excluded — it should not survive a page refresh.
     */
    persist() {
      localStorage.setItem(
        "kiosk_auth",
        JSON.stringify({
          mode: this.mode,
          resident: this.resident,
          rfidUid: this.rfidUid
          // tempResident, tempUid, tempHasPin are deliberately omitted
        })
      )
    }
  }
})