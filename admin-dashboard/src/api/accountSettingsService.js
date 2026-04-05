/**
 * @file admin-dashboard/api/accountSettingsService.js
 * @description Admin account settings service module.
 * Handles profile retrieval, profile updates, password changes, photo management,
 * and superadmin-only resident relinking.
 */
import api from './http'

export const getAdminProfile = async () => {
  const res = await api.get('/admin/auth/me')
  return res.data
}

export const updateAdminProfile = async ({ username, position }) => {
  const res = await api.patch('/admin/auth/me', { username, position })
  return res.data
}

export const changeAdminPassword = async ({ current_password, new_password }) => {
  const res = await api.patch('/admin/auth/me/password', { current_password, new_password })
  return res.data
}

export const relinkAdminResident = async (residentId) => {
  const res = await api.patch('/admin/auth/me/resident', { resident_id: residentId })
  return res.data
}

export const uploadAdminPhoto = async (file) => {
  const formData = new FormData()
  formData.append('photo', file)
  await api.put('/admin/auth/me/photo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const getAdminPhotoUrl = async () => {
  try {
    const res = await api.get('/admin/auth/me/photo', { responseType: 'blob' })
    return URL.createObjectURL(res.data)
  } catch (err) {
    if (err.response?.status === 404) return null
    throw err
  }
}

export const removeAdminPhoto = async () => {
  await api.delete('/admin/auth/me/photo')
}