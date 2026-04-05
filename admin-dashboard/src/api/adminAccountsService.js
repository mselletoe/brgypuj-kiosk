/**
 * @file admin-dashboard/api/adminAccountsService.js
 * @description Superadmin-only service for managing all admin accounts.
 * Handles listing, status toggling, role updates, photo retrieval, and deletion.
 */
import api from './http'

export const getAllAdmins = async () => {
  const res = await api.get('/admin/accounts')
  return res.data
}

export const getAdminAccountPhotoUrl = async (adminId) => {
  try {
    const res = await api.get(`/admin/accounts/${adminId}/photo`, { responseType: 'blob' })
    return URL.createObjectURL(res.data)
  } catch (err) {
    if (err.response?.status === 404) return null
    throw err
  }
}

export const setAdminStatus = async (adminId, isActive) => {
  const res = await api.patch(`/admin/accounts/${adminId}/status`, { is_active: isActive })
  return res.data
}

export const setAdminRole = async (adminId, role) => {
  const res = await api.patch(`/admin/accounts/${adminId}/role`, { system_role: role })
  return res.data
}

export const deleteAdminAccount = async (adminId) => {
  const res = await api.delete(`/admin/accounts/${adminId}`)
  return res.data
}