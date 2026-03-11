import api from './http'

// ──────────────────────────────────────────────────────────────
// SHARED — RESIDENT SEARCH
// ──────────────────────────────────────────────────────────────

/**
 * Search residents by last name and first name prefix.
 * Query format: "LastPrefix, FirstPrefix" (e.g. "del, max")
 * Single term (e.g. "del") searches by last name prefix only.
 * @param {string} query
 * @returns {Promise}
 */
export function searchResidents(query) {
  return api.get('/kiosk/id-services/residents/search', { params: { query } })
}


// ──────────────────────────────────────────────────────────────
// APPLY FOR ID
// ──────────────────────────────────────────────────────────────

/**
 * Fetch the admin-configured fields for the ID Application form.
 * Used by the kiosk details phase to render the correct form fields.
 * @returns {Promise}
 */
export function getIDApplicationFields() {
  return api.get('/kiosk/id-services/apply/fields')
}

/**
 * Step 1 — Verify resident identity via birthdate before applying.
 * @param {{ resident_id: number, birthdate: string }} payload - birthdate format: "YYYY-MM-DD"
 * @returns {Promise}
 */
export function verifyBirthdate(payload) {
  return api.post('/kiosk/id-services/apply/verify-birthdate', payload)
}

/**
 * Step 2 — Submit the ID application after birthdate is verified.
 * Works for both guest (rfid_uid: null) and authenticated sessions.
 * @param {{ resident_id: number|null, applicant_resident_id: number, rfid_uid: string|null, photo: string|null, use_manual_data: boolean, manual_data: object|null }} payload
 * @returns {Promise}
 */
export function applyForID(payload) {
  return api.post('/kiosk/id-services/apply', payload)
}


// ──────────────────────────────────────────────────────────────
// CHANGE PASSCODE / PIN  (authenticated sessions only)
// ──────────────────────────────────────────────────────────────

/**
 * Step 1 verification — confirm the resident's current PIN before allowing
 * them to set a new one. Read-only: does NOT change anything.
 * @param {{ resident_id: number, pin: string }} payload
 * @returns {Promise}
 */
export function verifyPin(payload) {
  return api.post('/kiosk/id-services/verify-pin', payload)
}

/**
 * Change the resident's 4-digit security PIN.
 * Only available to residents logged in via RFID.
 * @param {{ resident_id: number, current_pin: string, new_pin: string }} payload
 * @returns {Promise}
 */
export function changePin(payload) {
  return api.post('/kiosk/id-services/change-pin', payload)
}


// ──────────────────────────────────────────────────────────────
// REPORT LOST CARD
// ──────────────────────────────────────────────────────────────

/**
 * Get the resident's active RFID card status before confirming the report.
 * Used to determine if the "Submit Report" button should be enabled.
 * @param {number} residentId
 * @returns {Promise}
 */
export function getReportCardInfo(residentId) {
  return api.get(`/kiosk/id-services/report-lost/info/${residentId}`)
}

/**
 * Submit a lost card report.
 * Verifies the resident's PIN, deactivates their active RFID card,
 * and creates an RFIDReport record in the admin dashboard.
 * @param {{ resident_id: number, pin: string, rfid_uid: string|null }} payload
 * @returns {Promise}
 */
export function reportLostCard(payload) {
  return api.post('/kiosk/id-services/report-lost', payload)
}

// ──────────────────────────────────────────────────────────────
// KIOSK — GENERATE BRGY ID NUMBER
// ──────────────────────────────────────────────────────────────

/**
 * Check whether a resident meets all ID Application requirements.
 * Called after birthdate verification succeeds, before proceeding to details.
 * Returns { eligible: bool, checks: Array<{ id, label, type, passed, message }> }
 * @param {number} residentId
 * @returns {Promise}
 */
export function checkIDRequirements(residentId) {
  return api.get(`/kiosk/id-services/apply/requirements-check/${residentId}`)
}

/**
 * Generates and returns the next sequential Barangay ID number.
 * Called when entering the details phase so the number can be
 * displayed on the camera screen and submitted with the application.
 * @returns {Promise<{ brgy_id_number: string }>}
 */
export function generateBrgyID() {
  return api.get('/kiosk/id-services/apply/generate-brgy-id')
}