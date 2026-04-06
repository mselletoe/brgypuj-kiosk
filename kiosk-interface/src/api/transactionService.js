import api from './http'

export const getTransactionHistory = async (residentId) => {
  try {
    const response = await api.get(`/kiosk/transactions/history/${residentId}`)
    return response.data
  } catch (err) {
    console.error('Failed to fetch transaction history:', err)
    throw err
  }
}