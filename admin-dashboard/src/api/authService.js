/**
 * @file authService.js
 * @description API service functions for admin authentication and
 * resident dropdown data used during account registration.
 */

import api from './http'

/**
 * Authenticates an admin user with the provided credentials.
 * Returns the access token and session data on success.
 *
 * @param {string} username - The admin's username
 * @param {string} password - The admin's password
 */
export const loginAdmin = async (username, password) => {
  const res = await api.post('/admin/auth/login', { username, password })
  return res.data
}

/**
 * Fetches the currently authenticated admin's profile.
 * Requires a valid JWT token to be attached to the request via the HTTP interceptor.
 */
export const getCurrentAdmin = async () => {
  const res = await api.get('/admin/auth/me')
  return res.data
}

/**
 * Registers a new admin account linked to an existing resident record.
 *
 * @param {Object} payload                    - Registration payload
 * @param {string} payload.resident_id        - ID of the resident to link the account to
 * @param {string} payload.username           - Desired username for the new admin
 * @param {string} payload.password           - Desired password for the new admin
 * @param {string} [payload.role='Admin']     - Admin role; defaults to 'Admin' if not provided
 */
export const registerAdmin = async ({ resident_id, username, password, role = 'Admin' }) => {
  const res = await api.post('/admin/auth/register', { resident_id, username, password, role })
  return res.data
}

/**
 * Fetches a lightweight list of residents for use in dropdown/select inputs.
 * Typically used during admin registration to associate an account with a resident.
 */
export const fetchResidentsDropdown = async () => {
  const res = await api.get('/admin/residents/dropdown')
  return res.data
}