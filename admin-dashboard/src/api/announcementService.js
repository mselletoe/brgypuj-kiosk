import api from './http'

/**
 * Fetch all announcements for admin dashboard
 * @returns {Promise<Array>} array of announcement records
 */
export const getAllAnnouncements = async () => {
  try {
    const response = await api.get('/admin/announcements')
    return response.data
  } catch (err) {
    console.error('Failed to fetch announcements:', err)
    throw err
  }
}

/**
 * Fetch a single announcement by ID with full details
 * @param {number} announcementId
 * @returns {Promise<Object>} announcement details including image
 */
export const getAnnouncementById = async (announcementId) => {
  try {
    const response = await api.get(`/admin/announcements/${announcementId}`)
    return response.data
  } catch (err) {
    console.error('Failed to fetch announcement details:', err)
    throw err
  }
}

/**
 * Create a new announcement
 * @param {Object} announcementData - announcement fields
 * @param {File} imageFile - optional image file
 * @returns {Promise<Object>} created announcement
 */
export const createAnnouncement = async (announcementData, imageFile = null) => {
  try {
    const formData = new FormData()
    
    // Append announcement fields
    formData.append('title', announcementData.title)
    if (announcementData.description) {
      formData.append('description', announcementData.description)
    }
    formData.append('event_date', announcementData.event_date)
    if (announcementData.event_time) {
      formData.append('event_time', announcementData.event_time)
    }
    formData.append('location', announcementData.location)
    formData.append('is_active', announcementData.is_active ?? true)
    
    // Append image if provided
    if (imageFile) {
      formData.append('image', imageFile)
    }
    
    const response = await api.post('/admin/announcements', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  } catch (err) {
    console.error('Failed to create announcement:', err)
    throw err
  }
}

/**
 * Update an existing announcement
 * @param {number} announcementId
 * @param {Object} announcementData - fields to update
 * @param {File} imageFile - optional new image file
 * @param {boolean} removeImage - whether to remove existing image
 * @returns {Promise<Object>} updated announcement
 */
export const updateAnnouncement = async (
  announcementId,
  announcementData,
  imageFile = null,
  removeImage = false
) => {
  try {
    const formData = new FormData()
    
    // Append only provided fields
    if (announcementData.title !== undefined) {
      formData.append('title', announcementData.title)
    }
    if (announcementData.description !== undefined) {
      formData.append('description', announcementData.description)
    }
    if (announcementData.event_date !== undefined) {
      formData.append('event_date', announcementData.event_date)
    }
    if (announcementData.event_time !== undefined) {
      formData.append('event_time', announcementData.event_time)
    }
    if (announcementData.location !== undefined) {
      formData.append('location', announcementData.location)
    }
    if (announcementData.is_active !== undefined) {
      formData.append('is_active', announcementData.is_active)
    }
    
    // Handle image operations
    if (removeImage) {
      formData.append('remove_image', 'true')
    } else if (imageFile) {
      formData.append('image', imageFile)
    }
    
    const response = await api.put(`/admin/announcements/${announcementId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  } catch (err) {
    console.error('Failed to update announcement:', err)
    throw err
  }
}

/**
 * Toggle the active status of an announcement
 * @param {number} announcementId
 * @returns {Promise<Object>} updated announcement
 */
export const toggleAnnouncementStatus = async (announcementId) => {
  try {
    const response = await api.patch(`/admin/announcements/${announcementId}/toggle-status`)
    return response.data
  } catch (err) {
    console.error('Failed to toggle announcement status:', err)
    throw err
  }
}

/**
 * Delete a specific announcement record
 * @param {number} announcementId
 * @returns {Promise<Object>} deletion confirmation
 */
export const deleteAnnouncement = async (announcementId) => {
  try {
    const response = await api.delete(`/admin/announcements/${announcementId}`)
    return response.data
  } catch (err) {
    console.error('Failed to delete announcement:', err)
    throw err
  }
}

/**
 * Bulk delete announcement records
 * @param {Array<number>} ids - array of announcement IDs to delete
 * @returns {Promise<Object>} deletion count confirmation
 */
export const bulkDeleteAnnouncements = async (ids) => {
  try {
    const response = await api.post('/admin/announcements/bulk-delete', ids)
    return response.data
  } catch (err) {
    console.error('Failed to bulk delete announcements:', err)
    throw err
  }
}