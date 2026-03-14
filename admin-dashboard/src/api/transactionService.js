/**
 * @file transactionService.js
 * @description Transaction History Service Module
 * Provides functions for retrieving unified transaction history
 * (document requests, equipment requests, RFID activities) for a resident.
 */
import api from './http'

/**
 * Fetches the unified transaction history for a specific resident.
 * Returns all completed or rejected transactions ordered by most recent first.
 * @param {number} residentId - The resident's ID.
 * @returns {Promise<Array>} List of transaction history records.
 * Each record contains: id, transaction_type, transaction_name,
 * transaction_no, rfid_uid, status, created_at
 */
export const fetchResidentTransactionHistory = async (residentId) => {
  const res = await api.get(`/admin/transactions/history/${residentId}`)
  return res.data
}