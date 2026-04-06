import api from './http'

export const getAllNotifications = async () => {
  try {
    const response = await api.get('/admin/notifications')
    return response.data
  } catch (err) {
    console.error('Failed to fetch notifications:', err)
    throw err
  }
}

export const markNotificationRead = async (notificationId) => {
  try {
    const response = await api.patch(`/admin/notifications/${notificationId}/read`)
    return response.data
  } catch (err) {
    console.error('Failed to mark notification as read:', err)
    throw err
  }
}

export const bulkMarkRead = async (ids) => {
  try {
    const response = await api.post('/admin/notifications/mark-read', ids)
    return response.data
  } catch (err) {
    console.error('Failed to bulk mark notifications as read:', err)
    throw err
  }
}

export const bulkDeleteNotifications = async (ids) => {
  try {
    const response = await api.post('/admin/notifications/bulk-delete', ids)
    return response.data
  } catch (err) {
    console.error('Failed to bulk delete notifications:', err)
    throw err
  }
}