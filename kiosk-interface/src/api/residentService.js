import api from './http'

export function getResidentAutofillData(residentId) {
  return api.get(`/kiosk/residents/${residentId}/autofill`)
}

export function getResidentById(residentId) {
  return api.get(`/kiosk/residents/${residentId}`)
}