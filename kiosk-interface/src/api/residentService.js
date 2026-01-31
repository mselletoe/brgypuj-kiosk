/**
 * Resident Service
 * Handles API calls for resident data
 */
import api from './http'

/**
 * Fetch resident data for form autofill
 * @param {number} residentId - The resident's ID
 * @returns {Promise<Object>} Resident autofill data
 */
export const getResidentAutofillData = async (residentId) => {
  try {
    const response = await api.get(`/kiosk/residents/${residentId}/autofill`)
    return response.data
  } catch (err) {
    console.error('Failed to fetch resident autofill data:', err)
    throw err
  }
}

/**
 * Get resident by ID
 * @param {number} residentId - The resident's ID
 * @returns {Promise<Object>} Resident data
 */
export const getResidentById = async (residentId) => {
  try {
    const response = await api.get(`/kiosk/residents/${residentId}`)
    return response.data
  } catch (err) {
    console.error('Failed to fetch resident:', err)
    throw err
  }
}