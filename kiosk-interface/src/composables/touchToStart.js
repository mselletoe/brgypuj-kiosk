import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

// Module-level flag: controls whether a click/touch on the idle screen
// should navigate to /login.
// Starts as false — enableTouchToStart() must be called explicitly when
// the idle screen mounts, so the flag is always in a known state regardless
// of how many times the user has navigated through the app.
let active = false

/**
 * Called by the idle screen on mount.
 * Re-arms the touch-to-start behaviour for this session.
 */
export function enableTouchToStart() {
  active = true
}

/**
 * Called by Login.vue when the user chooses "Use RFID".
 * Prevents the idle screen's click listener from firing during the
 * Login → ScanRFID navigation transition.
 */
export function disableTouchToStart() {
  active = false
}

export function useTouchToStart() {
  const router = useRouter()

  const handleTouch = () => {
    if (active) router.push('/login')
  }

  onMounted(() => {
    window.addEventListener('click', handleTouch)
    window.addEventListener('touchstart', handleTouch)
  })

  onUnmounted(() => {
    window.removeEventListener('click', handleTouch)
    window.removeEventListener('touchstart', handleTouch)
  })
}