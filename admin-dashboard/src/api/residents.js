import api from './api'

// Fetch paginated residents
export const fetchResidents = (params = {}) => {
  return api.get('/residents', { params }).then(res => res.data)
}

// Fetch puroks for dropdown
export const fetchPuroks = () => {
  return api.get('/residents/puroks').then(res => res.data)
}