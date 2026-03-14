import api from './http'

/**
 * Fetch all available document types for kiosk
 * @returns {Promise<Array>} array of document types
 */
export const getDocumentTypes = async () => {
  try {
    const response = await api.get('/kiosk/documents/types')
    return response.data
  } catch (err) {
    console.error('Failed to fetch document types:', err)
    throw err
  }
}

/**
 * Submit a document request for the kiosk
 * @param {Object} payload { doctype_id, form_data, resident_id }
 * @returns {Promise<Object>} transaction number
 */
export const createDocumentRequest = async (payload) => {
  try {
    const response = await api.post('/kiosk/documents/requests', payload)
    return response.data
  } catch (err) {
    console.error('Failed to create document request:', err)
    throw err
  }
}

/**
 * Check if a resident is eligible to request a specific document type.
 * Returns a breakdown of each requirement (passed/failed/informational).
 * @param {number} doctypeId
 * @param {number} residentId
 * @returns {Promise<Object>} { eligible, resident_id, doctype_id, checks[] }
 */
export const checkEligibility = async (doctypeId, residentId) => {
  try {
    const response = await api.get(`/kiosk/documents/types/${doctypeId}/eligibility`, {
      params: { resident_id: residentId }
    })
    return response.data
  } catch (err) {
    console.error('Failed to check eligibility:', err)
    throw err
  }
}