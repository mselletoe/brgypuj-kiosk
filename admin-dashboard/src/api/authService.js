/**
 * @file authService.js (Admin API Services)
 * @description Administrative authentication and resident management service module.
 * This module provides functions to interact with admin-specific endpoints,
 * including session management and data retrieval for the dashboard.
 */
import api from './http'

/**
 * Authenticates an administrator.
 * @param {string} username - The admin username.
 * @param {string} password - The admin password.
 * @returns {Promise<Object>} The authentication response containing the JWT.
 */
export const loginAdmin = async (username, password) => {
  const res = await api.post('/admin/auth/login', { username, password })
  return res.data
}

/**
 * Retrieves the profile of the currently authenticated administrator.
 * @returns {Promise<Object>} The admin user data.
 */
export const getCurrentAdmin = async () => {
  const res = await api.get('/admin/auth/me')
  return res.data
}

/**
 * Registers a new administrator account.
 * @param {Object} params - Registration details.
 * @param {number} params.resident_id - The ID of the resident to promote to admin.
 * @param {string} params.email - Admin email address.
 * @param {string} params.password - Secure password for the account.
 * @param {string} [params.role='Admin'] - The administrative role/permissions level.
 * @returns {Promise<Object>} The created admin record.
 */
export const registerAdmin = async ({ resident_id, username, password, role = 'Admin' }) => {
  const res = await api.post('/admin/auth/register', { resident_id, username, password, role })
  return res.data
}

/**
 * Fetches the list of all residents for administrative management.
 * @returns {Promise<Array>} List of resident records.
 */
export const fetchResidents = async () => {
  const res = await api.get('/admin/residents')
  return res.data
}