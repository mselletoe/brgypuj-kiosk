/**
 * @file admin-dashboard/src/api/documentService.js
 * @description API service functions for admin document management.
 * Covers document type configuration, template handling, request lifecycle,
 * eligibility checks, notes, and PDF viewing.
 */

import api from './http'

// =================================================================================
// DOCUMENT TYPES
// =================================================================================

export function getDocumentTypes() {
  return api.get('/admin/documents/types')
}

export function createDocumentType(payload) {
  return api.post('/admin/documents/types', payload)
}

export function updateDocumentType(id, payload) {
  return api.put(`/admin/documents/types/${id}`, payload)
}

export function deleteDocumentType(id) {
  return api.delete(`/admin/documents/types/${id}`)
}

export function bulkDeleteDocumentTypes(ids) {
  return api.post('/admin/documents/types/bulk-delete', ids)
}

// =================================================================================
// DOCUMENT TEMPLATES
// =================================================================================

export function uploadDocumentTemplate(id, file) {
  const form = new FormData()
  form.append('file', file)

  return api.post(`/admin/documents/types/${id}/file`, form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function downloadDocumentTemplate(id, filename = 'template') {
  return api.get(`/admin/documents/types/${id}/file`, {
    responseType: 'blob'
  }).then(response => {
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `${filename}.docx`)
    document.body.appendChild(link)
    link.click()

    link.remove()
    window.URL.revokeObjectURL(url)

    return response
  })
}


// =================================================================================
// ID APPLICATION
// =================================================================================

export function isIDApplication(request) {
  return request.doctype_id === null || request.doctype_id == null
}


// =================================================================================
// DOCUMENT REQUESTS
// =================================================================================

export function getDocumentRequests() {
  return api.get('/admin/documents/requests')
}

export function viewRequestPdf(requestId) {
  const backendBaseUrl = api.defaults.baseURL
  const pdfUrl = `${backendBaseUrl}/admin/documents/requests/${requestId}/pdf`

  window.open(pdfUrl, '_blank')
}

export function approveRequest(id) {
  return api.post(`/admin/documents/requests/${id}/approve`)
}

export function rejectRequest(id) {
  return api.post(`/admin/documents/requests/${id}/reject`)
}

export function releaseRequest(id) {
  return api.post(`/admin/documents/requests/${id}/release`)
}

export function markAsPaid(id) {
  return api.post(`/admin/documents/requests/${id}/mark-paid`)
}

export function markAsUnpaid(id) {
  return api.post(`/admin/documents/requests/${id}/mark-unpaid`)
}

export function undoRequest(id) {
  return api.post(`/admin/documents/requests/${id}/undo`)
}

export function bulkUndoRequests(ids) {
  return api.post(`/admin/documents/requests/bulk-undo`, ids)
}

export function deleteRequest(id) {
  return api.delete(`/admin/documents/requests/${id}`)
}

export function bulkDeleteRequests(ids) {
  return api.post(`/admin/documents/requests/bulk-delete`, ids)
}

export function getNotes(requestId) {
  return api.get(`/admin/documents/requests/${requestId}/notes`)
}

export function updateNotes(requestId, notes) {
  return api.put(`/admin/documents/requests/${requestId}/notes`, { notes })
}


// =================================================================================
// ELIGIBILITY CHECK
// =================================================================================

export function checkResidentEligibility(residentId, doctypeId) {
  return api.get(`/admin/documents/${residentId}/eligibility/${doctypeId}`)
}

export function updateDocumentRequirements(id, requirements) {
  return api.put(`/admin/documents/types/${id}`, { requirements })
}

// =================================================================================
// NOTIFY (SMS)
// =================================================================================

export function notifyResident(phoneNumber, message) {
  return api.post('/admin/sms/send', {
    message,
    recipient_mode: 'specific',
    phone_numbers: [phoneNumber],
  })
}