import api from './http'

export const checkRfidStatus = async (rfidUid) => {
  try {
    const response = await api.get(`/kiosk/rfid-registration/check/${rfidUid}`)
    return response.data
  } catch (err) {
    console.error('Failed to check RFID status:', err)
    throw err
  }
}

export const verifyAdminPasscode = async (passcode) => {
  try {
    const response = await api.post('/kiosk/rfid-registration/verify-passcode', { passcode })
    return response.data
  } catch (err) {
    console.error('Failed to verify admin passcode:', err)
    throw err
  }
}

export const getApprovedApplications = async () => {
  try {
    const response = await api.get('/kiosk/rfid-registration/approved-applications')
    return response.data
  } catch (err) {
    console.error('Failed to fetch approved applications:', err)
    throw err
  }
}

export const linkRfidToResident = async (payload) => {
  try {
    const response = await api.post('/kiosk/rfid-registration/link', payload)
    return response.data
  } catch (err) {
    console.error('Failed to link RFID to resident:', err)
    throw err
  }
}