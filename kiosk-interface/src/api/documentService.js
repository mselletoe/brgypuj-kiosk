/**
 * @file kiosk-interface/src/api/documentService.js
 * @description API service functions for kiosk document requests.
 * Covers document type listing, eligibility checks, and request submission.
 */

import api from './http'

// =================================================================================
// DOCUMENT TYPES
// =================================================================================
export const getDocumentTypes = async () => {
  try {
    const response = await api.get('/kiosk/documents/types')
    return response.data
  } catch (err) {
    console.error('Failed to fetch document types:', err)
    throw err
  }
}

// =================================================================================
// DOCUMENT REQUEST
// =================================================================================
export const createDocumentRequest = async (payload) => {
  try {
    const response = await api.post('/kiosk/documents/requests', payload)
    return response.data
  } catch (err) {
    console.error('Failed to create document request:', err)
    throw err
  }
}

// =================================================================================
// ELIGIBILITY CHECK
// =================================================================================
export const checkEligibility = async (doctypeId, residentId) => {
  try {
    const response = await api.get(`/kiosk/documents/types/${doctypeId}/eligibility`, {
      params: { resident_id: residentId }
    })
    return response.data
  } catch (err) {
    console.error('Failed to check eligibility:', err)
    throw err
  }
}