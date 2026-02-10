/**
 * @file residentsService.js
 * @description Resident Management Service Module
 * This module provides functions for managing residents including
 * CRUD operations, viewing details, and managing addresses/RFID.
 */
import api from './http'

// ============================================================================
// READ Operations
// ============================================================================

/**
 * Fetches the list of all residents for table display.
 * Returns lightweight data: id, full_name, phone_number, rfid_no, current_address
 * @returns {Promise<Array>} List of resident records for table.
 */
export const fetchResidents = async () => {
  const res = await api.get('/admin/residents')
  return res.data
}

/**
 * Fetches detailed information for a specific resident.
 * Includes all personal info, address, RFID, and computed fields.
 * @param {number} residentId - The resident's ID.
 * @returns {Promise<Object>} Detailed resident data.
 */
export const fetchResidentDetail = async (residentId) => {
  const res = await api.get(`/admin/residents/${residentId}`)
  return res.data
}

// ============================================================================
// CREATE Operations
// ============================================================================

/**
 * Registers a new resident with address and RFID.
 * @param {Object} residentData - The resident data.
 * @param {string} residentData.first_name - First name (required).
 * @param {string} residentData.last_name - Last name (required).
 * @param {string} [residentData.middle_name] - Middle name (optional).
 * @param {string} [residentData.suffix] - Suffix (optional).
 * @param {string} residentData.gender - Gender: 'male', 'female', or 'other' (required).
 * @param {string} residentData.birthdate - Birthdate in YYYY-MM-DD format (required).
 * @param {string} [residentData.email] - Email address (optional).
 * @param {string} [residentData.phone_number] - Phone number (optional).
 * @param {string} [residentData.residency_start_date] - Start date in YYYY-MM-DD (defaults to today).
 * @param {Object} residentData.address - Address information (required).
 * @param {string} residentData.address.house_no_street - House/Block/Street (required).
 * @param {number} residentData.address.purok_id - Purok ID (required).
 * @param {string} [residentData.address.barangay='Poblacion Uno'] - Barangay (optional).
 * @param {string} [residentData.address.municipality='Amadeo'] - Municipality (optional).
 * @param {string} [residentData.address.province='Cavite'] - Province (optional).
 * @param {string} [residentData.address.region='Region IV-A'] - Region (optional).
 * @param {Object} residentData.rfid - RFID information (required).
 * @param {string} residentData.rfid.rfid_uid - RFID UID (required).
 * @param {boolean} [residentData.rfid.is_active=true] - RFID active status (defaults to true).
 * @returns {Promise<Object>} The created resident with full details.
 */
export const createResident = async (residentData) => {
  const res = await api.post('/admin/residents', residentData)
  return res.data
}

// ============================================================================
// UPDATE Operations
// ============================================================================

/**
 * Updates resident's basic information.
 * All fields are optional - only provided fields will be updated.
 * @param {number} residentId - The resident's ID.
 * @param {Object} updateData - Fields to update.
 * @param {string} [updateData.first_name] - First name.
 * @param {string} [updateData.middle_name] - Middle name.
 * @param {string} [updateData.last_name] - Last name.
 * @param {string} [updateData.suffix] - Suffix.
 * @param {string} [updateData.gender] - Gender.
 * @param {string} [updateData.birthdate] - Birthdate in YYYY-MM-DD format.
 * @param {string} [updateData.email] - Email address.
 * @param {string} [updateData.phone_number] - Phone number.
 * @param {string} [updateData.residency_start_date] - Residency start date.
 * @returns {Promise<Object>} Updated resident with full details.
 */
export const updateResident = async (residentId, updateData) => {
  const res = await api.patch(`/admin/residents/${residentId}`, updateData)
  return res.data
}

/**
 * Updates resident's current address.
 * All fields are optional - only provided fields will be updated.
 * @param {number} residentId - The resident's ID.
 * @param {Object} addressData - Address fields to update.
 * @param {string} [addressData.house_no_street] - House/Block/Street.
 * @param {number} [addressData.purok_id] - Purok ID.
 * @param {string} [addressData.barangay] - Barangay.
 * @param {string} [addressData.municipality] - Municipality.
 * @param {string} [addressData.province] - Province.
 * @param {string} [addressData.region] - Region.
 * @returns {Promise<Object>} Updated resident with full details.
 */
export const updateResidentAddress = async (residentId, addressData) => {
  const res = await api.patch(`/admin/residents/${residentId}/address`, addressData)
  return res.data
}

/**
 * Updates resident's active RFID information.
 * All fields are optional - only provided fields will be updated.
 * @param {number} residentId - The resident's ID.
 * @param {Object} rfidData - RFID fields to update.
 * @param {string} [rfidData.rfid_uid] - New RFID UID.
 * @param {boolean} [rfidData.is_active] - Active status.
 * @returns {Promise<Object>} Updated resident with full details.
 */
export const updateResidentRFID = async (residentId, rfidData) => {
  const res = await api.patch(`/admin/residents/${residentId}/rfid`, rfidData)
  return res.data
}

// ============================================================================
// DELETE Operations
// ============================================================================

/**
 * Deletes a resident and all associated data.
 * This cascades to addresses, RFIDs, feedbacks, reports, and requests.
 * @param {number} residentId - The resident's ID.
 * @returns {Promise<void>}
 */
export const deleteResident = async (residentId) => {
  await api.delete(`/admin/residents/${residentId}`)
}

// ============================================================================
// Utility Services
// ============================================================================

/**
 * Fetches all puroks for dropdown selections.
 * @returns {Promise<Array>} List of {id, purok_name} objects.
 */
export const fetchPuroks = async () => {
  const res = await api.get('/admin/residents/utils/puroks')
  return res.data
}