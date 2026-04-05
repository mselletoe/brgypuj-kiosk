import api from './http'

export const getAllFeedbacks = async () => {
  try {
    const response = await api.get('/admin/feedbacks')
    return response.data
  } catch (err) {
    console.error('Failed to fetch feedbacks:', err)
    throw err
  }
}

export const deleteFeedback = async (feedbackId) => {
  try {
    const response = await api.delete(`/admin/feedbacks/${feedbackId}`)
    return response.data
  } catch (err) {
    console.error('Failed to delete feedback:', err)
    throw err
  }
}

export const bulkDeleteFeedbacks = async (ids) => {
  try {
    const response = await api.post('/admin/feedbacks/bulk-delete', ids)
    return response.data
  } catch (err) {
    console.error('Failed to bulk delete feedbacks:', err)
    throw err
  }
}