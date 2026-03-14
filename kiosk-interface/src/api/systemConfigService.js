import api from './http'

/**
 * Fetches kiosk-relevant system config (brgy info + security settings).
 * Used by useAutoLogout to read auto_logout_duration.
 *
 * @returns {Promise<{
 *   brgy_name: string,
 *   brgy_subname: string,
 *   has_logo: boolean,
 *   auto_logout_duration: number,  // seconds
 *   max_failed_attempts: number,
 *   lockout_minutes: number
 * }>}
 */
export const getKioskSettings = async () => {
  const response = await api.get('/kiosk/settings')
  return response.data
}