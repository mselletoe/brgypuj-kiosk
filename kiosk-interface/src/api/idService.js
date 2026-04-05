import api from './http'

export function searchResidents(query) {
  return api.get('/kiosk/id-services/residents/search', { params: { query } })
}

export function getIDApplicationFields() {
  return api.get('/kiosk/id-services/apply/fields')
}

export function verifyBirthdate(payload) {
  return api.post('/kiosk/id-services/apply/verify-birthdate', payload)
}

export function applyForID(payload) {
  return api.post('/kiosk/id-services/apply', payload)
}

export function verifyPin(payload) {
  return api.post('/kiosk/id-services/verify-pin', payload)
}

export function changePin(payload) {
  return api.post('/kiosk/id-services/change-pin', payload)
}

export function getReportCardInfo(residentId) {
  return api.get(`/kiosk/id-services/report-lost/info/${residentId}`)
}

export function reportLostCard(payload) {
  return api.post('/kiosk/id-services/report-lost', payload)
}

export function checkIDRequirements(residentId) {
  return api.get(`/kiosk/id-services/apply/requirements-check/${residentId}`)
}

export function generateBrgyID() {
  return api.get('/kiosk/id-services/apply/generate-brgy-id')
}