import api from './http'

/**
 * Submit feedback from the kiosk
 * @param {Object} payload { resident_id (optional), category, rating, additional_comments }
 * @returns {Promise<Object>} confirmation message
 */
export const submitFeedback = async (payload) => {
  try {
    const response = await api.post('/kiosk/feedbacks', payload)
    return response.data
  } catch (err) {
    console.error('Failed to submit feedback:', err)
    throw err
  }
}