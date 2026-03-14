import api from './http'

// =========================================================
// EQUIPMENT INVENTORY MANAGEMENT
// =========================================================

export function getEquipmentInventory() {
  return api.get('/admin/equipment/inventory')
}

export function createEquipmentItem(payload) {
  return api.post('/admin/equipment/inventory', payload)
}

export function updateEquipmentItem(id, payload) {
  return api.put(`/admin/equipment/inventory/${id}`, payload)
}

export function deleteEquipmentItem(id) {
  return api.delete(`/admin/equipment/inventory/${id}`)
}

export function bulkDeleteEquipmentItems(ids) {
  return api.post('/admin/equipment/inventory/bulk-delete', ids)
}

// =========================================================
// EQUIPMENT REQUEST MANAGEMENT
// =========================================================

export function getEquipmentRequests() {
  return api.get('/admin/equipment/requests')
}

export function getEquipmentRequestDetail(id) {
  return api.get(`/admin/equipment/requests/${id}`)
}

// =========================================================
// REQUEST STATUS MANAGEMENT
// =========================================================

export function approveRequest(id) {
  return api.post(`/admin/equipment/requests/${id}/approve`)
}

export function rejectRequest(id) {
  return api.post(`/admin/equipment/requests/${id}/reject`)
}

export function markAsPickedUp(id) {
  return api.post(`/admin/equipment/requests/${id}/picked-up`)
}

export function markAsReturned(id) {
  return api.post(`/admin/equipment/requests/${id}/returned`)
}

export function markAsPaid(id) {
  return api.post(`/admin/equipment/requests/${id}/mark-paid`)
}

export function markAsUnpaid(id) {
  return api.post(`/admin/equipment/requests/${id}/mark-unpaid`)
}

export function toggleRefund(id) {
  return api.post(`/admin/equipment/requests/${id}/toggle-refund`)
}

export function undoRequest(id) {
  return api.post(`/admin/equipment/requests/${id}/undo`)
}

export function bulkUndoRequests(ids) {
  return api.post('/admin/equipment/requests/bulk-undo', ids)
}

// =========================================================
// REQUEST DELETION
// =========================================================

export function deleteRequest(id) {
  return api.delete(`/admin/equipment/requests/${id}`)
}

export function bulkDeleteRequests(ids) {
  return api.post('/admin/equipment/requests/bulk-delete', ids)
}

// =========================================================
// REQUEST NOTES
// =========================================================

export function getNotes(requestId) {
  return api.get(`/admin/equipment/requests/${requestId}/notes`)
}

export function updateNotes(requestId, notes) {
  return api.put(`/admin/equipment/requests/${requestId}/notes`, { notes })
}