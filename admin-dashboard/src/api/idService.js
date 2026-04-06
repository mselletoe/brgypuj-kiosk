import api from './http'

export function getIDApplications() {
  return api.get('/admin/id-services/applications')
}

export function getRFIDReports() {
  return api.get('/admin/id-services/reports')
}

export function approveIDApplication(id) {
  return api.post(`/admin/id-services/applications/${id}/approve`)
}

export function rejectIDApplication(id) {
  return api.post(`/admin/id-services/applications/${id}/reject`)
}

export function releaseIDApplication(id) {
  return api.post(`/admin/id-services/applications/${id}/release`)
}

export function markIDApplicationPaid(id) {
  return api.post(`/admin/id-services/applications/${id}/mark-paid`)
}

export function markIDApplicationUnpaid(id) {
  return api.post(`/admin/id-services/applications/${id}/mark-unpaid`)
}

export function undoIDApplication(id) {
  return api.post(`/admin/id-services/applications/${id}/undo`)
}

export function deleteIDApplication(id) {
  return api.delete(`/admin/id-services/applications/${id}`)
}

export function bulkDeleteIDApplications(ids) {
  return api.post('/admin/id-services/applications/bulk-delete', ids)
}

export function bulkUndoIDApplications(ids) {
  return api.post('/admin/id-services/applications/bulk-undo', ids)
}

export function undoRFIDReport(id) {
  return api.post(`/admin/id-services/reports/${id}/undo`)
}

export function bulkUndoRFIDReports(ids) {
  return api.post('/admin/id-services/reports/bulk-undo', ids)
}

export function deleteRFIDReport(id) {
  return api.delete(`/admin/id-services/reports/${id}`)
}

export function bulkDeleteRFIDReports(ids) {
  return api.post('/admin/id-services/reports/bulk-delete', ids)
}

export function getIDTemplatePreviewUrl() {
  return `${api.defaults.baseURL}/admin/id-services/template/preview`
}