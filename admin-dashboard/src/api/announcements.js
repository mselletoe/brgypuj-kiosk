import api from './api' // ✅ Import the shared axios instance

// ✅ Get all announcements
export const getAnnouncements = async () => {
  const response = await api.get('/announcements')
  return response.data
}

// ✅ Get one announcement
export const getAnnouncementById = async (id) => {
  const response = await api.get(`/announcements/${id}`)
  return response.data
}

// ✅ Create announcement
export const createAnnouncement = async (formData) => {
  const response = await api.post('/announcements', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

// ✅ Update announcement
export const updateAnnouncement = async (id, formData) => {
  const response = await api.post(`/announcements/${id}?_method=PUT`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

// ✅ Delete announcement
export const deleteAnnouncement = async (id) => {
  const response = await api.delete(`/announcements/${id}`)
  return response.data
}
