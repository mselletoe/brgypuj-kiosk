import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

export function useTouchToStart() {
  const router = useRouter()

  onMounted(() => {
    const handleScreenTouch = (event) => {
      if (event.target.closest('button')) return
      router.push('/login')
    }

    window.addEventListener('click', handleScreenTouch)
    window.addEventListener('touchstart', handleScreenTouch)

    onUnmounted(() => {
      window.removeEventListener('click', handleScreenTouch)
      window.removeEventListener('touchstart', handleScreenTouch)
    })
  })
}