import api from './http'

/**
 * Fetch all blotter records for admin dashboard
 * @returns {Promise<Array>} array of blotter records
 */
export const getAllBlotters = async () => {
  try {
    const response = await api.get('/admin/blotter')
    return response.data
  } catch (err) {
    console.error('Failed to fetch blotter records:', err)
    throw err
  }
}

/**
 * Fetch a single blotter record by ID
 * @param {number} blotterId
 * @returns {Promise<Object>} blotter record detail
 */
export const getBlotterById = async (blotterId) => {
  try {
    const response = await api.get(`/admin/blotter/${blotterId}`)
    return response.data
  } catch (err) {
    console.error('Failed to fetch blotter record:', err)
    throw err
  }
}

/**
 * Create a new blotter record
 * @param {Object} payload - blotter record data
 * @returns {Promise<Object>} created blotter record
 */
export const createBlotter = async (payload) => {
  try {
    const response = await api.post('/admin/blotter', payload)
    return response.data
  } catch (err) {
    console.error('Failed to create blotter record:', err)
    throw err
  }
}

/**
 * Update an existing blotter record
 * @param {number} blotterId
 * @param {Object} payload - fields to update
 * @returns {Promise<Object>} updated blotter record
 */
export const updateBlotter = async (blotterId, payload) => {
  try {
    const response = await api.put(`/admin/blotter/${blotterId}`, payload)
    return response.data
  } catch (err) {
    console.error('Failed to update blotter record:', err)
    throw err
  }
}

/**
 * Delete a specific blotter record
 * @param {number} blotterId
 * @returns {Promise<void>}
 */
export const deleteBlotter = async (blotterId) => {
  try {
    await api.delete(`/admin/blotter/${blotterId}`)
  } catch (err) {
    console.error('Failed to delete blotter record:', err)
    throw err
  }
}

/**
 * Bulk delete blotter records
 * @param {Array<number>} ids - array of blotter IDs to delete
 * @returns {Promise<Object>} deletion count confirmation
 */
export const bulkDeleteBlotters = async (ids) => {
  try {
    const response = await api.post('/admin/blotter/bulk-delete', ids)
    return response.data
  } catch (err) {
    console.error('Failed to bulk delete blotter records:', err)
    throw err
  }
}