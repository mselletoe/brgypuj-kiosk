import api from './http'

/**
 * Fetch all available equipment items for kiosk display
 * @returns {Promise<Array>} array of equipment inventory items
 */
export const getAvailableEquipment = async () => {
  try {
    const response = await api.get('/kiosk/equipment/inventory')
    return response.data
  } catch (err) {
    console.error('Failed to fetch equipment inventory:', err)
    throw err
  }
}

/**
 * Get autofill data for a resident
 * @param {number} residentId - The resident's ID
 * @returns {Promise<Object>} autofill data including borrower name, contact info
 */
export const getAutofillData = async (residentId) => {
  try {
    const response = await api.get(`/kiosk/equipment/autofill/${residentId}`)
    return response.data
  } catch (err) {
    console.error('Failed to fetch autofill data:', err)
    throw err
  }
}

/**
 * Submit an equipment borrowing request
 * @param {Object} payload - Request payload
 * @param {number|null} payload.resident_id - Resident ID (null for guest mode)
 * @param {string} payload.contact_person - Contact person name
 * @param {string} payload.contact_number - Contact phone number
 * @param {string} payload.purpose - Purpose of borrowing
 * @param {string} payload.borrow_date - ISO datetime string for borrow date
 * @param {string} payload.return_date - ISO datetime string for return date
 * @param {Array} payload.items - Array of {item_id, quantity}
 * @param {boolean} payload.use_autofill - Whether autofill was used
 * @returns {Promise<Object>} transaction number and total cost
 */
export const createEquipmentRequest = async (payload) => {
  try {
    const response = await api.post('/kiosk/equipment/requests', payload)
    return response.data
  } catch (err) {
    console.error('Failed to create equipment request:', err)
    throw err
  }
}

/**
 * Fetch equipment borrowing history for a resident
 * @param {number} residentId - The resident's ID
 * @returns {Promise<Array>} array of equipment requests
 */
export const getRequestHistory = async (residentId) => {
  try {
    const response = await api.get(`/kiosk/equipment/requests/history/${residentId}`)
    return response.data
  } catch (err) {
    console.error('Failed to fetch request history:', err)
    throw err
  }
}