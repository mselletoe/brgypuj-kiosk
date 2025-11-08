import api from './api'

// ============================================
// Fetch all request types
// ============================================
export const fetchRequestTypes = () => {
  return api.get('/request-types').then(res => res.data)
}

// ============================================
// Add a new request type
// ============================================
export const addRequestType = (payload) => {
  return api.post('/request-types', payload).then(res => res.data)
}

// ============================================
// Update a request type
// ============================================
export const updateRequestType = (id, payload) => {
  return api.put(`/request-types/${id}`, payload).then(res => res.data)
}

// ============================================
// Delete a request type
// ============================================
export const deleteRequestType = (id) => {
  return api.delete(`/request-types/${id}`).then(res => res.data)
}
