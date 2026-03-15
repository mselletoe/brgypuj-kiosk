/**
 * @file admin-dashboard/api/authService.js
 * @description API service functions for admin authentication and
 * resident dropdown data used during account registration.
 */

import api from './http'

// =================================================================================
// LOGIN ADMIN
// =================================================================================
export const loginAdmin = async (username, password) => {
  const res = await api.post('/admin/auth/login', { username, password })
  return res.data
}

// =================================================================================
// FETCH CURRENT ADMIN PROFILE
// =================================================================================
export const getCurrentAdmin = async () => {
  const res = await api.get('/admin/auth/me')
  return res.data
}

// =================================================================================
// CREATE ADMIN ACCOUNT
// =================================================================================
export const registerAdmin = async ({ resident_id, username, password, role = 'Admin' }) => {
  const res = await api.post('/admin/auth/register', { resident_id, username, password, role })
  return res.data
}

// =================================================================================
// FETCH RESIDENT LIST ON CREATE ACCOUNT DROPDOWN
// =================================================================================
export const fetchResidentsDropdown = async () => {
  const res = await api.get('/admin/residents/dropdown')
  return res.data
}