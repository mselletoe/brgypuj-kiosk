import api from './api'

/**
 * Fetch resident data for pre-filling forms
 * @param {string} token - JWT token from auth store
 * @returns {Promise<Object>} Resident data object
 */
export const fetchResidentData = async (token) => {
  try {
    const response = await api.get(`/requests/resident-data`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    return response.data
  } catch (error) {
    console.error('Failed to fetch resident data:', error)
    throw error
  }
}

export default {
  fetchResidentData
}