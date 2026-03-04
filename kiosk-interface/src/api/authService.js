import api from './http'

// =========================================================
// KIOSK AUTHENTICATION SERVICE
// =========================================================

/**
 * Authenticate a resident by RFID UID.
 * Returns resident profile and whether they have a configured PIN.
 *
 * @param {string} rfidUid - The hardware UID from the scanned card.
 * @returns {Promise<{ mode: string, resident_id: number, first_name: string, middle_name: string|null, last_name: string, address: string|null, has_pin: boolean }>}
 */
export const loginByRfid = async (rfidUid) => {
  try {
    const response = await api.post('/kiosk/auth/rfid', { rfid_uid: rfidUid })
    return response.data
  } catch (err) {
    console.error('Failed to authenticate RFID:', err)
    throw err
  }
}

/**
 * Set a new 4-digit PIN for a resident (first-time setup).
 * Called when has_pin is false after RFID scan.
 *
 * @param {Object} payload
 * @param {number} payload.resident_id
 * @param {string} payload.pin      - The new 4-digit PIN chosen by the resident.
 * @param {string} payload.rfid_uid - The UID of the card being set up.
 * @returns {Promise<void>}
 */
export const setupPin = async (payload) => {
  try {
    const response = await api.post('/kiosk/auth/set-pin', payload)
    return response.data
  } catch (err) {
    console.error('Failed to set PIN:', err)
    throw err
  }
}

/**
 * Verify a resident's existing 4-digit PIN during standard login.
 *
 * @param {Object} payload
 * @param {number} payload.resident_id
 * @param {string} payload.pin - The PIN entered by the resident.
 * @returns {Promise<{ valid: boolean }>}
 */
export const verifyPin = async (payload) => {
  try {
    const response = await api.post('/kiosk/auth/verify-pin', payload)
    return response.data
  } catch (err) {
    console.error('Failed to verify PIN:', err)
    throw err
  }
}