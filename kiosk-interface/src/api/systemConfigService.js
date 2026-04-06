import api from './http'

export const getKioskSettings = async () => {
  const response = await api.get('/kiosk/settings')
  return response.data
}