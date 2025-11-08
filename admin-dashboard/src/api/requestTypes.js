import api from './api'

export default {
  getAll: () => api.get('/request-types/'),
  create: (data) => api.post('/request-types/', data),
  update: (id, data) => api.put(`/request-types/${id}`, data),
  delete: (id) => api.delete(`/request-types/${id}`)
}