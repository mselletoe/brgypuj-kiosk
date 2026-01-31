import api from './http'

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

export function getDocumentRequests() {
  return api.get('/admin/documents/requests')
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