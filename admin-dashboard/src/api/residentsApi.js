import api from './api'

// Get residents who are not yet staff members
export const getAvailableResidents = () => {
  return api.get('/residents/available-staff').then(res => res.data)
}