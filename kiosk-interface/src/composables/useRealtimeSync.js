import { onMounted, onUnmounted } from 'vue'

export function useRealtimeSync(handlers = {}) {
  let eventSource = null

  const connect = () => {
    // Admin uses /admin/sse/events, Kiosk uses /kiosk/sse/events
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const endpoint = import.meta.env.VITE_SSE_PATH || '/admin/sse/events'

    eventSource = new EventSource(`${baseUrl}${endpoint}`)

    eventSource.onopen = () => console.log('🟢 SSE connected')

    eventSource.onerror = () => {
      console.warn('🔴 SSE disconnected, retrying in 3s...')
      eventSource.close()
      setTimeout(connect, 3000)
    }

    Object.entries(handlers).forEach(([event, callback]) => {
      eventSource.addEventListener(event, (e) => {
        const data = JSON.parse(e.data)
        callback(data)
      })
    })
  }

  onMounted(connect)
  onUnmounted(() => eventSource?.close())
}