/**
 * @file useAutoLogout.js
 * @description Tracks user inactivity and silently logs out the kiosk session
 * after the configured duration, redirecting to /idle.
 *
 * Exposes `secondsRemaining` so any component (e.g. Header.vue) can show
 * a live countdown like "Session will logout after 10s..."
 *
 * Usage in App.vue:
 *   useAutoLogout()
 *
 * Usage in Header.vue (or any component):
 *   import { useAutoLogout } from '@/composables/useAutoLogout'
 *   const { secondsRemaining } = useAutoLogout()
 *
 * NOTE: useAutoLogout() is a shared singleton — calling it multiple times
 * returns the same reactive state. The timer is only started once (in App.vue).
 */

import { ref, watch, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getKioskSettings } from '@/api/systemConfigService'

// Routes where the timer should NOT run
const EXCLUDED_ROUTES = ['/idle', '/login', '/login-rfid', '/auth-pin']

// ── Shared singleton state (module-level so all callers share the same refs) ──
const secondsRemaining = ref(0)
let logoutDuration     = 1800
let timer              = null
let tickInterval       = null
let initialized        = false

export function useAutoLogout() {
  const router = useRouter()
  const route  = useRoute()
  const auth   = useAuthStore()

  // ── Load duration from backend config ───────────────────────────────────
  async function loadConfig() {
    try {
      const config   = await getKioskSettings()
      logoutDuration = Math.max(config.auto_logout_duration ?? 1800, 10)
    } catch {
      // Offline fallback — use default
    }
  }

  // ── Timer ────────────────────────────────────────────────────────────────
  function clearTimer() {
    clearTimeout(timer)
    clearInterval(tickInterval)
    timer        = null
    tickInterval = null
  }

  function startTimer() {
    clearTimer()

    if (EXCLUDED_ROUTES.includes(route.path) || !auth.isAuthenticated) {
      secondsRemaining.value = 0
      return
    }

    secondsRemaining.value = logoutDuration

    // Tick every second to update the display
    tickInterval = setInterval(() => {
      if (secondsRemaining.value > 0) secondsRemaining.value -= 1
    }, 1000)

    // Actual logout after full duration
    timer = setTimeout(performLogout, logoutDuration * 1000)
  }

  function resetTimer() {
    if (EXCLUDED_ROUTES.includes(route.path) || !auth.isAuthenticated) return
    startTimer()
  }

  // ── Logout ───────────────────────────────────────────────────────────────
  function performLogout() {
    clearTimer()
    secondsRemaining.value = 0
    auth.logout()
    router.replace('/idle')
  }

  // ── Activity listeners ───────────────────────────────────────────────────
  const ACTIVITY_EVENTS = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll', 'click']

  function attachListeners() {
    ACTIVITY_EVENTS.forEach(e => window.addEventListener(e, resetTimer, { passive: true }))
  }

  function detachListeners() {
    ACTIVITY_EVENTS.forEach(e => window.removeEventListener(e, resetTimer))
  }

  // ── Watchers ─────────────────────────────────────────────────────────────
  watch(() => route.path, () => startTimer())

  watch(
    () => auth.isAuthenticated,
    (authenticated) => {
      if (authenticated) startTimer()
      else { clearTimer(); secondsRemaining.value = 0 }
    }
  )

  // ── Init — only run once from App.vue ────────────────────────────────────
  if (!initialized) {
    initialized = true
    loadConfig().then(() => {
      attachListeners()
      startTimer()
    })
  }

  onUnmounted(() => {
    clearTimer()
    detachListeners()
  })

  return { secondsRemaining }
}