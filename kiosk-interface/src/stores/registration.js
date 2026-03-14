/**
 * @file registration.js
 * @description Pinia store bridging the new RFID registration flow across screens.
 *
 * Import path: @/stores/registration
 * Store ID:    'registration'
 *
 * State flows:
 *   ScanRFID.vue  → setPendingRfidUid(uid)  → isAdminMode=true  → /auth-pin
 *   AuthPIN.vue   → reads isAdminMode, on success clearAdminMode() → /register
 *   Register.vue  → reads pendingRfidUid, on done clearAll()       → /login
 */

import { defineStore } from 'pinia'

export const useRfidRegistrationStore = defineStore('registration', {
  state: () => ({
    /** UID of the newly scanned unregistered card. */
    pendingRfidUid: null,

    /** When true, AuthPIN renders in admin passcode mode instead of resident PIN mode. */
    isAdminMode: false,
  }),

  actions: {
    /** Called by ScanRFID when the card is new. Sets UID + activates admin mode. */
    setPendingRfidUid(uid) {
      this.pendingRfidUid = uid
      this.isAdminMode = true
    },

    /** Called by AuthPIN after passcode accepted. Keeps UID but drops admin mode flag. */
    clearAdminMode() {
      this.isAdminMode = false
    },

    /** Full reset. Called on cancel, go back, or after successful linking. */
    clearAll() {
      this.pendingRfidUid = null
      this.isAdminMode = false
    },
  },
})