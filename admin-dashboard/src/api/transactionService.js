/**
 * @file admin-dashboard/api/transactionService.js
 * @description Transaction History Service Module
 * Provides functions for retrieving unified transaction history
 * (document requests, equipment requests, RFID activities) for a resident.
 */
import api from './http'

export const fetchResidentTransactionHistory = async (residentId) => {
  const res = await api.get(`/admin/transactions/history/${residentId}`)
  return res.data
}