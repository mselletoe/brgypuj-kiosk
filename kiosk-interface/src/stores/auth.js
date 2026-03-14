/**
 * @file stores/auth.js
 * @description Pinia store for kiosk authentication state.
 * Supports two session modes — guest and RFID — and persists
 * the active session to localStorage for page-refresh continuity.
 */

import { defineStore } from "pinia"

export const useAuthStore = defineStore("auth", {
  state: () => ({
    /** Current session mode: 'guest' | 'rfid' | null (unauthenticated) */
    mode: null,

    /** Authenticated resident's profile data, set after RFID login */
    resident: null,

    /** RFID card UID associated with the current session */
    rfidUid: null,

    /** Resident data held in staging until PIN is verified */
    tempResident: null,

    /** RFID UID held in staging until PIN is verified */
    tempUid: null,

    /** Whether the staged resident has set a custom PIN */
    tempHasPin: false,
  }),

  getters: {
    /** Returns true if the current session is a guest session */
    isGuest: (s) => s.mode === "guest",

    /** Returns true if the current session was authenticated via RFID */
    isRFID: (s) => s.mode === "rfid",

    /** Returns true if any session mode is active */
    isAuthenticated: (s) => !!s.mode,

    /** Returns the authenticated resident's ID, or null for guest sessions */
    residentId: (s) => s.resident?.id || null,

    /** Returns the resident's full name for RFID sessions, or 'Guest' otherwise */
    userName: (s) =>
      s.mode === "rfid" && s.resident
        ? `${s.resident.first_name} ${s.resident.last_name}`
        : "Guest"
  },

  actions: {

    /**
     * Starts an unauthenticated guest session and persists the state.
     */
    setGuest() {
      this.mode = "guest"
      this.resident = null
      this.rfidUid = null
      this.persist()
    },

    /**
     * Stages RFID scan data while awaiting PIN verification.
     * The session is not confirmed until confirmRFIDLogin() is called.
     *
     * @param {Object}  payload          - RFID scan result
     * @param {Object}  payload.resident - Resident profile from the API
     * @param {string}  payload.uid      - Scanned RFID card UID
     * @param {boolean} payload.has_pin  - Whether the resident has a custom PIN set
     */
    setTemporaryRFIDData({ resident, uid, has_pin }) {
      this.tempResident = resident
      this.tempUid = uid
      this.tempHasPin = has_pin
    },

    /**
     * Promotes staged RFID data into the active session after PIN is verified.
     * Clears all temporary staging fields and persists the confirmed session.
     */
    confirmRFIDLogin() {
      this.mode = "rfid"
      this.resident = this.tempResident
      this.rfidUid = this.tempUid

      // Clear staging fields now that the session is confirmed
      this.tempResident = null
      this.tempUid = null
      this.tempHasPin = false

      this.persist()
    },

    /**
     * Directly sets an RFID session, bypassing the PIN staging flow.
     * Used when PIN verification is not required.
     *
     * @param {Object} resident - Resident profile from the API
     * @param {string} uid      - Scanned RFID card UID
     */
    setRFID(resident, uid) {
      this.mode = "rfid"
      this.resident = resident
      this.rfidUid = uid
      this.persist()
    },

    /**
     * Clears the session from both the store and localStorage.
     */
    logout() {
      this.$reset()
      localStorage.removeItem("kiosk_auth")
    },

    /**
     * Restores a previously persisted session from localStorage.
     * Should be called once on app startup.
     */
    restore() {
      const stored = localStorage.getItem("kiosk_auth")
      if (stored) Object.assign(this, JSON.parse(stored))
    },

    /**
     * Persists the active session fields to localStorage.
     * Temporary staging fields are intentionally excluded.
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