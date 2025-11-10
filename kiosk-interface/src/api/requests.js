import api from './api'

export const createRequest = async (payload) => {
  const response = await api.post('/requests/', payload)
  return response.data
}