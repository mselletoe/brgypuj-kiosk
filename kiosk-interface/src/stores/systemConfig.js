/**
 * @file stores/systemConfig.js
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import http from '@/api/http'

export const useSystemConfigStore = defineStore('systemConfig', () => {
  const config   = ref(null)
  const loading  = ref(false)
  const error    = ref(null)
  const fetched  = ref(false)

  // Blob URL for the logo — created once, revoked on refresh/removal
  let _logoBlobUrl = null
  const logoBlobUrl = ref(null)

  const brgyName          = computed(() => config.value?.brgy_name           ?? 'Barangay')
  const brgySubname       = computed(() => config.value?.brgy_subname        ?? '')
  const hasLogo           = computed(() => !!config.value?.has_logo)
  const maintenanceMode   = computed(() => !!config.value?.maintenance_mode)
  const maintenanceMessage = computed(() =>
    config.value?.maintenance_message
    ?? 'The system is currently undergoing scheduled maintenance. Please try again later.'
  )

  async function fetchConfig(force = false) {
    if (fetched.value && !force) return
    loading.value = true
    error.value   = null
    try {
      const response = await http.get('/kiosk/settings')
      config.value  = response.data
      fetched.value = true

      if (config.value.has_logo) {
        await _fetchLogoBlobUrl()
      } else {
        _revokeLogo()
      }
    } catch (err) {
      console.error('[systemConfig] Failed to load config:', err)
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  // Lightweight poll — only updates config fields, skips logo re-fetch unless has_logo changed
  async function pollConfig() {
    try {
      const response   = await http.get('/kiosk/settings')
      const prev       = config.value?.has_logo
      config.value     = response.data
      fetched.value    = true

      if (config.value.has_logo && !prev) {
        await _fetchLogoBlobUrl()
      } else if (!config.value.has_logo && prev) {
        _revokeLogo()
      }
    } catch (err) {
      console.error('[systemConfig] Poll failed:', err)
    }
  }

  async function _fetchLogoBlobUrl() {
    try {
      const res = await http.get('/kiosk/settings/logo', { responseType: 'blob' })
      _revokeLogo()
      _logoBlobUrl      = URL.createObjectURL(res.data)
      logoBlobUrl.value = _logoBlobUrl
    } catch {
      logoBlobUrl.value = null
    }
  }

  function _revokeLogo() {
    if (_logoBlobUrl) {
      URL.revokeObjectURL(_logoBlobUrl)
      _logoBlobUrl      = null
      logoBlobUrl.value = null
    }
  }

  async function refreshLogo(hasLogoNow) {
    if (config.value) config.value.has_logo = hasLogoNow
    if (hasLogoNow) {
      await _fetchLogoBlobUrl()
    } else {
      _revokeLogo()
    }
  }

  return {
    config, loading, error, fetched,
    brgyName, brgySubname, hasLogo, logoBlobUrl,
    maintenanceMode, maintenanceMessage,
    fetchConfig, pollConfig, refreshLogo,
  }
})