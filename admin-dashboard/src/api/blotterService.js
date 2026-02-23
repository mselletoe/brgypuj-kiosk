/**
 * @file blotterService.js
 * @description Blotter Records Service Module
 * Provides functions for managing barangay blotter records.
 */
import api from './http'

// ============================================================================
// READ Operations
// ============================================================================

export const getAllBlotters = async () => {
  const res = await api.get('/admin/blotter')
  return res.data
}

export const fetchResidentBlotterRecords = async (residentId) => {
  const res = await api.get(`/admin/blotter/resident/${residentId}`)
  return res.data
}

export const fetchBlotterRecordDetail = async (blotterId) => {
  const res = await api.get(`/admin/blotter/${blotterId}`)
  return res.data
}

// ============================================================================
// CREATE Operations
// ============================================================================

export const createBlotter = async (payload) => {
  const res = await api.post('/admin/blotter', payload)
  return res.data
}

// ============================================================================
// UPDATE Operations
// ============================================================================

export const updateBlotter = async (blotterId, updateData) => {
  const res = await api.put(`/admin/blotter/${blotterId}`, updateData)
  return res.data
}

// ============================================================================
// DELETE Operations
// ============================================================================

export const deleteBlotter = async (blotterId) => {
  await api.delete(`/admin/blotter/${blotterId}`)
}

export const bulkDeleteBlotters = async (ids) => {
  const res = await api.post('/admin/blotter/bulk-delete', ids)
  return res.data
}