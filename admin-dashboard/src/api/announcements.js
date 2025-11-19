import api from './api' // ✅ Import the shared axios instance

// ✅ Get all announcements (UPDATED for kiosk compatibility)
export const getAnnouncements = async () => {
  const response = await api.get('/announcements')

  // Keep original data
  const rawData = response.data

  // ➕ Added data transformation
  const transformed = rawData.map(a => ({
    id: a.id,
    title: a.title,
    date: a.event_date,      // <-- matches database
    location: a.location,
    start: a.event_time?.split(' - ')[0] ?? '',
    end: a.event_time?.split(' - ')[1] ?? '',
    image: a.image_name
      ? `http://127.0.0.1:8000/storage/${a.image_name}`
      : null
  }))

  return transformed
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
