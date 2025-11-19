/*
 * =================================================================================
 * File: api/authApi.js
 * Description: 
 * API service layer for Authentication-related requests.
 * - Handles Login requests to the backend.
 * - Handles Logout requests.
 * =================================================================================
 */

import api from './api'

// Login staff
export const loginStaff = (email, password) => {
  return api.post('/auth/login', { email, password }).then(res => res.data)
}

// Register new staff
export const registerStaff = (registrationData) => {
  // registrationData should be an object like:
  // { resident_id, email, password, role }
  return api.post('/auth/register', registrationData).then(res => res.data)
}

// Logout
export const logoutStaff = () => {
  return api.post('/auth/logout').then(res => res.data)
}