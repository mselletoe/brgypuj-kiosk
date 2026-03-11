/**
 * @file adminAccountsService.js
 * @description Superadmin-only service for managing all admin accounts.
 * Handles listing, status toggling, role updates, photo retrieval, and deletion.
 */
import api from './http'

/**
 * Fetches all admin accounts for the management table.
 * @returns {Promise<Array>} List of AdminAccountListItem objects.
 */
export const getAllAdmins = async () => {
  const res = await api.get('/admin/accounts')
  return res.data
}

/**
 * Returns a fully-qualified URL for an admin's photo, or null if none.
 * Uses the /admin/accounts/{id}/photo endpoint (not the /me/photo endpoint).
 * @param {number} adminId
 * @returns {Promise<string|null>}
 */
export const getAdminAccountPhotoUrl = async (adminId) => {
  try {
    const res = await api.get(`/admin/accounts/${adminId}/photo`, { responseType: 'blob' })
    return URL.createObjectURL(res.data)
  } catch (err) {
    if (err.response?.status === 404) return null
    throw err
  }
}

/**
 * Activates or deactivates an admin account.
 * @param {number} adminId
 * @param {boolean} isActive
 * @returns {Promise<Object>} { id, is_active, detail }
 */
export const setAdminStatus = async (adminId, isActive) => {
  const res = await api.patch(`/admin/accounts/${adminId}/status`, { is_active: isActive })
  return res.data
}

/**
 * Updates an admin's system role.
 * @param {number} adminId
 * @param {'admin'|'superadmin'} role
 * @returns {Promise<Object>} { id, system_role, detail }
 */
export const setAdminRole = async (adminId, role) => {
  const res = await api.patch(`/admin/accounts/${adminId}/role`, { system_role: role })
  return res.data
}

/**
 * Permanently deletes an admin account.
 * @param {number} adminId
 * @returns {Promise<Object>} { detail }
 */
export const deleteAdminAccount = async (adminId) => {
  const res = await api.delete(`/admin/accounts/${adminId}`)
  return res.data
}