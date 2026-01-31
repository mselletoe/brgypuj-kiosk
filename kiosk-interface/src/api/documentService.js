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