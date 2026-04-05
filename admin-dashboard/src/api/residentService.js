/**
 * @file admin-dashboard/api/residentsService.js
 * @description Resident Management Service Module
 * This module provides functions for managing residents including
 * CRUD operations, viewing details, and managing addresses/RFID.
 */
import api from './http'

// ============================================================================
// READ Operations
// ============================================================================

export const fetchResidents = async () => {
  const res = await api.get('/admin/residents')
  return res.data
}

export const fetchResidentDetail = async (residentId) => {
  const res = await api.get(`/admin/residents/${residentId}`)
  return res.data
}

// ============================================================================
// CREATE Operations
// ============================================================================

export const createResident = async (residentData) => {
  const res = await api.post('/admin/residents/', residentData)
  return res.data
}

// ============================================================================
// UPDATE Operations
// ============================================================================

export const updateResident = async (residentId, updateData) => {
  const res = await api.patch(`/admin/residents/${residentId}`, updateData)
  return res.data
}

export const updateResidentAddress = async (residentId, addressData) => {
  const res = await api.patch(`/admin/residents/${residentId}/address`, addressData)
  return res.data
}

export const updateResidentRFID = async (residentId, rfidData) => {
  const res = await api.patch(`/admin/residents/${residentId}/rfid`, rfidData)
  return res.data
}

// ============================================================================
// DELETE Operations
// ============================================================================

export const deleteResident = async (residentId) => {
  await api.delete(`/admin/residents/${residentId}`)
}

// ============================================================================
// Utility Services
// ============================================================================

export const fetchPuroks = async () => {
  const res = await api.get('/admin/residents/utils/puroks')
  return res.data
}