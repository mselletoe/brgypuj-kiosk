import { onUnmounted } from 'vue'
import { useNotificationStore } from '@/stores/notification'
import { useSystemConfigStore } from '@/stores/systemConfig'

let socket = null
let reconnectTimer = null

export function useWebSocket() {
  const notificationStore = useNotificationStore()
  const systemConfigStore = useSystemConfigStore()

  function connect() {
    if (socket && socket.readyState === WebSocket.OPEN) return

    socket = new WebSocket('ws://localhost:8000/ws/kiosk')

    socket.onopen = () => {
      console.log('[WS] Kiosk connected')
      if (reconnectTimer) clearTimeout(reconnectTimer)
    }

    socket.onmessage = (event) => {
      try {
        const { event: type, data } = JSON.parse(event.data)

        // ── Config changes from admin ──────────────────────────────────────
        if (type === 'config_updated') {
          if (systemConfigStore.config) {
            Object.assign(systemConfigStore.config, data)  // merge partial payload
          }
          if ('has_logo' in data) {
            systemConfigStore.refreshLogo(data.has_logo)   // re-fetch or revoke blob URL
          }
          return
        }

        notificationStore.handleWebSocketEvent(type, data)
      } catch (err) {
        console.error('[WS] Failed to parse message', err)
      }
    }

    socket.onclose = () => {
      console.warn('[WS] Disconnected. Reconnecting in 3s...')
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

  onUnmounted(disconnect)

  return { connect, disconnect }
}