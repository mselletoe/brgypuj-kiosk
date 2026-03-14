/**
 * Resident Service
 * Handles API calls for resident data
 */
import api from './http'

/**
 * Fetch resident data for form autofill.
 * @param {number} residentId
 * @returns {Promise}
 */
export function getResidentAutofillData(residentId) {
  return api.get(`/kiosk/residents/${residentId}/autofill`)
}

/**
 * Get resident by ID.
 * @param {number} residentId
 * @returns {Promise}
 */
export function getResidentById(residentId) {
  return api.get(`/kiosk/residents/${residentId}`)
}