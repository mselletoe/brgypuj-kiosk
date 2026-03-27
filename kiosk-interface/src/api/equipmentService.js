/**
 * @file kiosk-interface/src/api/equipmentService.js
 * @description API service functions for the Resident Kiosk equipment module.
 * Handles inventory fetching, resident data autofill, request submission,
 * and personal borrowing history.
 */

import api from './http'

export const getAvailableEquipment = async () => {
  try {
    const response = await api.get('/kiosk/equipment/inventory')
    return response.data
  } catch (err) {
    console.error('Failed to fetch equipment inventory:', err)
    throw err
  }
}

export const getAutofillData = async (residentId) => {
  try {
    const response = await api.get(`/kiosk/equipment/autofill/${residentId}`)
    return response.data
  } catch (err) {
    console.error('Failed to fetch autofill data:', err)
    throw err
  }
}

export const createEquipmentRequest = async (payload) => {
  try {
    const response = await api.post('/kiosk/equipment/requests', payload)
    return response.data
  } catch (err) {
    console.error('Failed to create equipment request:', err)
    throw err
  }
}

export const getRequestHistory = async (residentId) => {
  try {
    const response = await api.get(`/kiosk/equipment/requests/history/${residentId}`)
    return response.data
  } catch (err) {
    console.error('Failed to fetch request history:', err)
    throw err
  }
}