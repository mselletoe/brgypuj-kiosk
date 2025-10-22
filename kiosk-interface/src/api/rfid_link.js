import api from './api'

export const checkRFID = (uid) => api.get(`/rfid/check/${uid}`)
export const registerRFID = (residentId, uid) => 
  api.post('/rfid/register', { resident_id: residentId, rfid_uid: uid })