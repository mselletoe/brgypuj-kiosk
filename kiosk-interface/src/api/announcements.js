import api from './api' // ✅ Reuse the same config

// ✅ Fetch all announcements (for display)
export const getAnnouncements = async () => {
  try {
    const response = await api.get('/announcements')
    console.log('✅ Announcements fetched:', response.data)
    return response.data
  } catch (error) {
    console.error('❌ Error fetching announcements:', error.message)
    if (error.response) {
      console.error('Status:', error.response.status)
      console.error('Data:', error.response.data)
    }
    throw error
  }
}

// ✅ Fetch single announcement (if needed)
export const getAnnouncementById = async (id) => {
  try {
    const response = await api.get(`/announcements/${id}`)
    return response.data
  } catch (error) {
    console.error(`❌ Error fetching announcement ${id}:`, error)
    throw error
  }
}
