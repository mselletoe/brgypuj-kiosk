/**
 * @file admin-interface/api/announcementService.js
 * @description API service functions for admin announcement management.
 * Covers fetching, creating, updating, status toggling, and deletion.
 */

import api from './http'


// =================================================================================
// GET ANNOUNCEMENTS
// =================================================================================
export const getAllAnnouncements = async () => {
  try {
    const response = await api.get('/admin/announcements')
    return response.data
  } catch (err) {
    console.error('Failed to fetch announcements:', err)
    throw err
  }
}

export const getAnnouncementById = async (announcementId) => {
  try {
    const response = await api.get(`/admin/announcements/${announcementId}`)
    return response.data
  } catch (err) {
    console.error('Failed to fetch announcement details:', err)
    throw err
  }
}

// =================================================================================
// CREATE/UPDATE ANNOUNCEMENTS
// =================================================================================
export const createAnnouncement = async (announcementData, imageFile = null) => {
  try {
    const formData = new FormData()
    
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

export const updateAnnouncement = async (
  announcementId,
  announcementData,
  imageFile = null,
  removeImage = false
) => {
  try {
    const formData = new FormData()
    
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

// =================================================================================
// ANNOUNCEMENTS STATUS
// =================================================================================
export const toggleAnnouncementStatus = async (announcementId) => {
  try {
    const response = await api.patch(`/admin/announcements/${announcementId}/toggle-status`)
    return response.data
  } catch (err) {
    console.error('Failed to toggle announcement status:', err)
    throw err
  }
}

// =================================================================================
// DELETE ANNOUNCEMENTS
// =================================================================================
export const deleteAnnouncement = async (announcementId) => {
  try {
    const response = await api.delete(`/admin/announcements/${announcementId}`)
    return response.data
  } catch (err) {
    console.error('Failed to delete announcement:', err)
    throw err
  }
}

export const bulkDeleteAnnouncements = async (ids) => {
  try {
    const response = await api.post('/admin/announcements/bulk-delete', ids)
    return response.data
  } catch (err) {
    console.error('Failed to bulk delete announcements:', err)
    throw err
  }
}