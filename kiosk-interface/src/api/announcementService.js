/**
 * @file kiosk-interface/api/announcementService.js
 * @description API service functions for fetching announcements on the kiosk.
 */

import api from './http'

// =================================================================================
// GET ANNOUNCEMENTS
// =================================================================================
export const getActiveAnnouncements = async () => {
  try {
    const response = await api.get('/kiosk/announcements')
    return response.data
  } catch (err) {
    console.error('Failed to fetch announcements:', err)
    throw err
  }
}