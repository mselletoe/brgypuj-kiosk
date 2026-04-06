import api from './http'

export const submitFeedback = async (payload) => {
  try {
    const response = await api.post('/kiosk/feedbacks', payload)
    return response.data
  } catch (err) {
    console.error('Failed to submit feedback:', err)
    throw err
  }
}