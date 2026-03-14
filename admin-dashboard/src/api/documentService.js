import api from './http'

// ──────────────────────────────────────────────────────────────
// DOCUMENT TYPES
// ──────────────────────────────────────────────────────────────

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

    // Cleanup
    link.remove()
    window.URL.revokeObjectURL(url)

    return response
  })
}


// ──────────────────────────────────────────────────────────────
// DOCUMENT REQUESTS
// NOTE: The list returned by getDocumentRequests() now includes
//       I.D Application rows (doctype_id === null).
//       Use isIDApplication(row) to detect them and apply the
//       correct card styling / action routing in the UI.
// ──────────────────────────────────────────────────────────────

/**
 * Returns true when a request row is an I.D Application.
 * These rows have doctype_id === null and doctype_name === "I.D Application".
 * The frontend should render them with the RFID (red) card variant.
 *
 * @param {{ doctype_id: number | null }} request
 * @returns {boolean}
 */
export function isIDApplication(request) {
  return request.doctype_id === null || request.doctype_id == null
}

/**
 * Fetch all document requests including I.D Applications.
 * I.D Application rows have doctype_id = null and doctype_name = "I.D Application".
 * @returns {Promise}
 */
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

/**
 * Check if a resident meets all requirements for a document type.
 * Used by admin to inspect eligibility before or during processing.
 * @param {number} residentId
 * @param {number} doctypeId
 * @returns {Promise<EligibilityCheckResult>}
 */
export function checkResidentEligibility(residentId, doctypeId) {
  return api.get(`/admin/documents/${residentId}/eligibility/${doctypeId}`)
}

/**
 * Update the requirements list for a document type.
 * @param {number} id - document type ID
 * @param {Array} requirements - array of requirement objects
 * @returns {Promise}
 */
export function updateDocumentRequirements(id, requirements) {
  return api.put(`/admin/documents/types/${id}`, { requirements })
}