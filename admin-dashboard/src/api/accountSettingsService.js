/**
 * @file accountSettingsService.js
 * @description Admin account settings service module.
 * Handles profile retrieval, profile updates, password changes, photo management,
 * and superadmin-only resident relinking.
 */
import api from './http'

/**
 * Retrieves the authenticated admin's full profile.
 * Includes the linked resident's name (read-only) and editable fields.
 * @returns {Promise<Object>} Admin profile data.
 */
export const getAdminProfile = async () => {
  const res = await api.get('/admin/auth/me')
  return res.data
}

/**
 * Updates the admin's editable profile fields (username and/or position).
 * Only send the fields you want to change.
 * @param {Object} params
 * @param {string} [params.username]
 * @param {string} [params.position]
 * @returns {Promise<Object>} Updated admin profile.
 */
export const updateAdminProfile = async ({ username, position }) => {
  const res = await api.patch('/admin/auth/me', { username, position })
  return res.data
}

/**
 * Changes the admin's password after verifying the current one.
 * @param {Object} params
 * @param {string} params.current_password - Must match the stored password.
 * @param {string} params.new_password - Must be at least 8 characters.
 * @returns {Promise<Object>} Success detail message.
 */
export const changeAdminPassword = async ({ current_password, new_password }) => {
  const res = await api.patch('/admin/auth/me/password', { current_password, new_password })
  return res.data
}

/**
 * Superadmin only — re-links the current admin account to a different resident record.
 * The target resident must not already be linked to another admin.
 * Returns the updated full AdminProfileResponse so the UI can refresh in one call.
 * @param {number} residentId - The ID of the resident to link to.
 * @returns {Promise<Object>} Updated admin profile.
 */
export const relinkAdminResident = async (residentId) => {
  const res = await api.patch('/admin/auth/me/resident', { resident_id: residentId })
  return res.data
}

/**
 * Uploads or replaces the admin's profile photo.
 * @param {File} file - A JPEG, PNG, or WebP file under 5MB.
 * @returns {Promise<void>} 204 No Content on success.
 */
export const uploadAdminPhoto = async (file) => {
  const formData = new FormData()
  formData.append('photo', file)
  await api.put('/admin/auth/me/photo', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/**
 * Returns the admin's profile photo as a blob URL for use in <img> src.
 * Returns null if no photo has been uploaded yet (404).
 * @returns {Promise<string|null>} Object URL string or null.
 */
export const getAdminPhotoUrl = async () => {
  try {
    const res = await api.get('/admin/auth/me/photo', { responseType: 'blob' })
    return URL.createObjectURL(res.data)
  } catch (err) {
    if (err.response?.status === 404) return null
    throw err
  }
}

/**
 * Removes the admin's profile photo.
 * @returns {Promise<void>}
 */
export const removeAdminPhoto = async () => {
  await api.delete('/admin/auth/me/photo')
}