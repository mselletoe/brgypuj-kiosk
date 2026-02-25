import api from './http'

// =========================================================
// SHARED — RESIDENT SEARCH
// =========================================================

/**
 * Search residents by last name and first name prefix.
 * Query format: "LastPrefix, FirstPrefix" (e.g. "del, max")
 * Single term (e.g. "del") searches by last name prefix only.
 *
 * @param {string} query - Comma-separated last/first name prefix string
 * @returns {Promise<Array>} List of matched residents with has_rfid flag
 */
export const searchResidents = async (query) => {
  try {
    const response = await api.get('/kiosk/id-services/residents/search', {
      params: { query }
    })
    return response.data
  } catch (err) {
    console.error('Failed to search residents:', err)
    throw err
  }
}

// =========================================================
// APPLY FOR ID
// =========================================================

/**
 * Step 1 — Verify resident identity via birthdate before applying.
 *
 * @param {Object} payload
 * @param {number} payload.resident_id
 * @param {string} payload.birthdate - Format: "YYYY-MM-DD"
 * @returns {Promise<{ verified: boolean }>}
 */
export const verifyBirthdate = async (payload) => {
  try {
    const response = await api.post('/kiosk/id-services/apply/verify-birthdate', payload)
    return response.data
  } catch (err) {
    console.error('Failed to verify birthdate:', err)
    throw err
  }
}

/**
 * Step 2 — Submit the ID application after birthdate is verified.
 * Works for both guest (rfid_uid: null) and authenticated sessions.
 *
 * @param {Object} payload
 * @param {number} payload.resident_id
 * @param {string|null} payload.rfid_uid - null if guest session
 * @returns {Promise<{ transaction_no: string, resident_first_name: string, resident_last_name: string, requested_at: string }>}
 */
export const applyForID = async (payload) => {
  try {
    const response = await api.post('/kiosk/id-services/apply', payload)
    return response.data
  } catch (err) {
    console.error('Failed to submit ID application:', err)
    throw err
  }
}

// =========================================================
// CHANGE PASSCODE / PIN  (authenticated sessions only)
// =========================================================

/**
 * Change the resident's 4-digit security PIN.
 * Only available to residents logged in via RFID.
 *
 * @param {Object} payload
 * @param {number} payload.resident_id
 * @param {string} payload.current_pin
 * @param {string} payload.new_pin
 * @returns {Promise<{ success: boolean, message: string }>}
 */
export const changePin = async (payload) => {
  try {
    const response = await api.post('/kiosk/id-services/change-pin', payload)
    return response.data
  } catch (err) {
    console.error('Failed to change PIN:', err)
    throw err
  }
}

// =========================================================
// REPORT LOST CARD
// =========================================================

/**
 * Get the resident's active RFID card status before confirming the report.
 * Used to determine if the "Submit Report" button should be enabled.
 *
 * @param {number} residentId
 * @returns {Promise<{ resident_id: number, first_name: string, last_name: string, rfid_uid: string|null, has_rfid: boolean }>}
 */
export const getReportCardInfo = async (residentId) => {
  try {
    const response = await api.get(`/kiosk/id-services/report-lost/info/${residentId}`)
    return response.data
  } catch (err) {
    console.error('Failed to get RFID card info:', err)
    throw err
  }
}

/**
 * Submit a lost card report.
 * Verifies the resident's PIN, deactivates their active RFID card,
 * and creates an RFIDReport record in the admin dashboard.
 *
 * @param {Object} payload
 * @param {number} payload.resident_id
 * @param {string} payload.pin - Current PIN for identity confirmation
 * @param {string|null} payload.rfid_uid - null if guest session
 * @returns {Promise<{ report_id: number, resident_first_name: string, resident_last_name: string, rfid_uid: string, reported_at: string }>}
 */
export const reportLostCard = async (payload) => {
  try {
    const response = await api.post('/kiosk/id-services/report-lost', payload)
    return response.data
  } catch (err) {
    console.error('Failed to submit lost card report:', err)
    throw err
  }
}