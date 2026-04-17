import { ref, watch, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getKioskSettings } from '@/api/systemConfigService'
import { useSystemConfigStore } from '@/stores/systemConfig'

const EXCLUDED_ROUTES = ['/idle', '/login', '/login-rfid', '/auth-pin']

// Routes where the timer should NOT run (unauthenticated active use)
const UNAUTHENTICATED_ACTIVE_ROUTES = ['/login', '/login-rfid', '/auth-pin']

const secondsRemaining = ref(0)
let logoutDuration = 1800
let timer          = null
let tickInterval   = null
let initialized    = false

export function useAutoLogout() {
  const router = useRouter()
  const route  = useRoute()
  const auth   = useAuthStore()
  const systemConfigStore = useSystemConfigStore()

  async function loadConfig() {
    try {
      const config   = await getKioskSettings()
      logoutDuration = Math.max(config.auto_logout_duration ?? 1800, 10)
    } catch {}
  }

  function clearTimer() {
    clearTimeout(timer)
    clearInterval(tickInterval)
    timer        = null
    tickInterval = null
  }

  // ✅ Unified guard: only run the timer for authenticated users
  //    on non-excluded routes. Guests browsing login/pin screens are
  //    active users — never time them out.
  function shouldRunTimer() {
    return auth.isAuthenticated && !EXCLUDED_ROUTES.includes(route.path)
  }

  function startTimer() {
    clearTimer()

    if (!shouldRunTimer()) {
      secondsRemaining.value = 0
      return
    }

    secondsRemaining.value = logoutDuration

    tickInterval = setInterval(() => {
      if (secondsRemaining.value > 0) secondsRemaining.value -= 1
    }, 1000)

    timer = setTimeout(performLogout, logoutDuration * 1000)
  }

  function resetTimer() {
    if (!shouldRunTimer()) return
    startTimer()
  }

  function performLogout() {
    clearTimer()
    secondsRemaining.value = 0
    auth.logout()
    router.replace('/idle')
  }

  const ACTIVITY_EVENTS = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll', 'click']

  function attachListeners() {
    ACTIVITY_EVENTS.forEach(e => window.addEventListener(e, resetTimer, { passive: true }))
  }

  function detachListeners() {
    ACTIVITY_EVENTS.forEach(e => window.removeEventListener(e, resetTimer))
  }

  watch(() => route.path, () => startTimer())

  watch(
    () => auth.isAuthenticated,
    (authenticated) => {
      if (authenticated) startTimer()
      else { clearTimer(); secondsRemaining.value = 0 }
    }
  )

  watch(
    () => systemConfigStore.config?.auto_logout_duration,
    (newDuration) => {
      if (newDuration == null) return
      logoutDuration = Math.max(newDuration, 10)
      // ✅ Only restart the timer if the user is actually in a timed session
      if (shouldRunTimer()) startTimer()
    }
  )

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