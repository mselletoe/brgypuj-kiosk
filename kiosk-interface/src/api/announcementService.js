import api from './http'

/**
 * Fetch all active announcements for kiosk display
 * @returns {Promise<Array>} array of active announcement records with base64 images
 */
export const getActiveAnnouncements = async () => {
  try {
    const response = await api.get('/kiosk/announcements')
    return response.data
  } catch (err) {
    console.error('Failed to fetch announcements:', err)
    throw err
  }
}