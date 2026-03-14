import api from './http'


/**
 * Fetch all feedbacks for admin dashboard
 * @returns {Promise<Array>} array of feedback records
 */
export const getAllFeedbacks = async () => {
  try {
    const response = await api.get('/admin/feedbacks')
    return response.data
  } catch (err) {
    console.error('Failed to fetch feedbacks:', err)
    throw err
  }
}

/**
 * Delete a specific feedback record
 * @param {number} feedbackId
 * @returns {Promise<Object>} deletion confirmation
 */
export const deleteFeedback = async (feedbackId) => {
  try {
    const response = await api.delete(`/admin/feedbacks/${feedbackId}`)
    return response.data
  } catch (err) {
    console.error('Failed to delete feedback:', err)
    throw err
  }
}

/**
 * Bulk delete feedback records
 * @param {Array<number>} ids - array of feedback IDs to delete
 * @returns {Promise<Object>} deletion count confirmation
 */
export const bulkDeleteFeedbacks = async (ids) => {
  try {
    const response = await api.post('/admin/feedbacks/bulk-delete', ids)
    return response.data
  } catch (err) {
    console.error('Failed to bulk delete feedbacks:', err)
    throw err
  }
}