import api from './http'

// ──────────────────────────────────────────────────────────────
// ADMIN — LIST
// ──────────────────────────────────────────────────────────────

/**
 * Fetch all ID Applications (DocumentRequests with doctype_id = NULL).
 * Displayed in the admin Document Requests dashboard.
 * @returns {Promise}
 */
export function getIDApplications() {
  return api.get('/admin/id-services/applications')
}

/**
 * Fetch all RFID lost-card reports.
 * Displayed in the admin Reports dashboard.
 * @returns {Promise}
 */
export function getRFIDReports() {
  return api.get('/admin/id-services/reports')
}


// ──────────────────────────────────────────────────────────────
// ADMIN — ID APPLICATION ACTIONS
// (ID Applications live in the DocumentRequest table with doctype_id = NULL,
//  so these call the dedicated id-services admin endpoints which are thin
//  pass-throughs to the shared document_service helpers.)
// ──────────────────────────────────────────────────────────────

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


// ──────────────────────────────────────────────────────────────
// ADMIN — RFID REPORT ACTIONS
// ──────────────────────────────────────────────────────────────

export function resolveRFIDReport(id) {
  return api.post(`/admin/id-services/reports/${id}/resolve`)
}

export function deleteRFIDReport(id) {
  return api.delete(`/admin/id-services/reports/${id}`)
}