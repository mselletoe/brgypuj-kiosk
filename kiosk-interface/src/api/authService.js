/**
 * @file kiosk-interface/api/authService.js
 * @description API service functions for kiosk authentication.
 * Covers RFID scanning, PIN setup, and PIN verification.
 */

import api from './http'


// =================================================================================
// RFID LOGIN
// =================================================================================
export const loginByRfid = async (rfidUid) => {
  try {
    const response = await api.post('/kiosk/auth/rfid', { rfid_uid: rfidUid })
    return response.data
  } catch (err) {
    console.error('Failed to authenticate RFID:', err)
    throw err
  }
}

// =================================================================================
// SETUP PIN
// =================================================================================
export const setupPin = async (payload) => {
  try {
    const response = await api.post('/kiosk/auth/set-pin', payload)
    return response.data
  } catch (err) {
    console.error('Failed to set PIN:', err)
    throw err
  }
}

export const verifyPin = async (payload) => {
  try {
    const response = await api.post('/kiosk/auth/verify-pin', payload)
    return response.data
  } catch (err) {
    console.error('Failed to verify PIN:', err)
    throw err
  }
}