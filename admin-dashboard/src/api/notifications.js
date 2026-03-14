import api from './http'

/**
 * Fetch all notifications for admin dashboard
 * @returns {Promise<Array>} array of notification records
 */
export const getAllNotifications = async () => {
  try {
    const response = await api.get('/admin/notifications')
    return response.data
  } catch (err) {
    console.error('Failed to fetch notifications:', err)
    throw err
  }
}

/**
 * Mark a single notification as read
 * @param {number} notificationId
 * @returns {Promise<Object>} confirmation
 */
export const markNotificationRead = async (notificationId) => {
  try {
    const response = await api.patch(`/admin/notifications/${notificationId}/read`)
    return response.data
  } catch (err) {
    console.error('Failed to mark notification as read:', err)
    throw err
  }
}

/**
 * Bulk mark notifications as read
 * @param {Array<number>} ids - array of notification IDs
 * @returns {Promise<Object>} confirmation
 */
export const bulkMarkRead = async (ids) => {
  try {
    const response = await api.post('/admin/notifications/mark-read', ids)
    return response.data
  } catch (err) {
    console.error('Failed to bulk mark notifications as read:', err)
    throw err
  }
}

/**
 * Bulk delete notification records
 * @param {Array<number>} ids - array of notification IDs to delete
 * @returns {Promise<Object>} deletion count confirmation
 */
export const bulkDeleteNotifications = async (ids) => {
  try {
    const response = await api.post('/admin/notifications/bulk-delete', ids)
    return response.data
  } catch (err) {
    console.error('Failed to bulk delete notifications:', err)
    throw err
  }
}