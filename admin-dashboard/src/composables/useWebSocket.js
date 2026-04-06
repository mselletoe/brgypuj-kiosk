import { onUnmounted } from 'vue'
import { useNotificationStore } from '@/stores/notification'

let socket = null
let reconnectTimer = null

export function useWebSocket() {
  const notificationStore = useNotificationStore()

  function connect() {
    // Avoid duplicate connections
    if (socket && socket.readyState === WebSocket.OPEN) return

    const host     = window.location.hostname
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    socket = new WebSocket(`${protocol}://${host}:8000/ws/admin`)

    socket.onopen = () => {
      console.log('[WS] Admin connected')
      // Clear any pending reconnect timer
      if (reconnectTimer) clearTimeout(reconnectTimer)
    }

    socket.onmessage = (event) => {
      try {
        const { event: type, data } = JSON.parse(event.data)
        // Hand off to notification store
        notificationStore.handleWebSocketEvent(type, data)
      } catch (err) {
        console.error('[WS] Failed to parse message', err)
      }
    }

    socket.onclose = () => {
      console.warn('[WS] Disconnected. Reconnecting in 3s...')
      // Auto-reconnect after 3 seconds
      reconnectTimer = setTimeout(connect, 3000)
    }

    socket.onerror = (err) => {
      console.error('[WS] Error:', err)
      socket.close()
    }
  }

  function disconnect() {
    if (reconnectTimer) clearTimeout(reconnectTimer)
    if (socket) socket.close()
  }

  // Clean up when component using this is unmounted
  onUnmounted(disconnect)

  return { connect, disconnect }
}