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