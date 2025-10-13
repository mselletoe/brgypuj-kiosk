import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

let active = true // controls whether touch-to-start should trigger

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