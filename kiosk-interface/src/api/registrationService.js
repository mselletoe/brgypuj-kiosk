import api from './http'

// =========================================================
// RFID REGISTRATION SERVICE
// =========================================================

/**
 * Check whether a scanned RFID UID is new (unregistered) or already linked.
 * Called immediately after a card is scanned in ScanRFID.vue.
 *
 * @param {string} rfidUid - The hardware UID from the scanner.
 * @returns {Promise<{ is_new: boolean }>}
 */
export const checkRfidStatus = async (rfidUid) => {
  try {
    const response = await api.get(`/kiosk/rfid-registration/check/${rfidUid}`)
    return response.data
  } catch (err) {
    console.error('Failed to check RFID status:', err)
    throw err
  }
}

/**
 * Validate the admin passcode entered on the AuthPIN screen (admin mode).
 *
 * @param {string} passcode - The 4-digit passcode entered by the admin.
 * @returns {Promise<{ valid: boolean }>}
 */
export const verifyAdminPasscode = async (passcode) => {
  try {
    const response = await api.post('/kiosk/rfid-registration/verify-passcode', { passcode })
    return response.data
  } catch (err) {
    console.error('Failed to verify admin passcode:', err)
    throw err
  }
}

/**
 * Fetch all approved ID Applications that are still awaiting an RFID card.
 * Displayed in the Register screen's left panel as selectable transaction cards.
 *
 * @returns {Promise<Array>} List of approved applications with resident details.
 */
export const getApprovedApplications = async () => {
  try {
    const response = await api.get('/kiosk/rfid-registration/approved-applications')
    return response.data
  } catch (err) {
    console.error('Failed to fetch approved applications:', err)
    throw err
  }
}

/**
 * Link a newly scanned RFID card to an approved ID Application resident.
 * Creates the ResidentRFID record and marks the DocumentRequest as Completed.
 *
 * @param {Object} payload
 * @param {string} payload.rfid_uid            - The new card's hardware UID.
 * @param {number} payload.resident_id         - The applicant resident to link.
 * @param {number} payload.document_request_id - The approved ID Application being fulfilled.
 * @returns {Promise<{ success: boolean, rfid_uid: string, resident_first_name: string, resident_last_name: string, transaction_no: string, linked_at: string }>}
 */
export const linkRfidToResident = async (payload) => {
  try {
    const response = await api.post('/kiosk/rfid-registration/link', payload)
    return response.data
  } catch (err) {
    console.error('Failed to link RFID to resident:', err)
    throw err
  }
}