import api from './http'

/**
 * Fetch unified transaction history for a resident
 * @param {number} residentId - The authenticated resident's ID
 * @returns {Promise<Array>} List of transaction history entries ordered by most recent first
 */
export const getTransactionHistory = async (residentId) => {
  try {
    const response = await api.get(`/kiosk/transactions/history/${residentId}`)
    return response.data
  } catch (err) {
    console.error('Failed to fetch transaction history:', err)
    throw err
  }
}