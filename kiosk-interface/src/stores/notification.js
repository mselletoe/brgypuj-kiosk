import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])

  function handleWebSocketEvent(type, data) {
    const now  = new Date()
    const date = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    const time = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })

    const name = data.resident_name || 'Guest User'

    const eventMap = {
      'new_transaction': {
        type: 'Document',
        msg:  `New ${data.document_type || 'Document'} request submitted by ${name}`,
      },
      'new_equipment_request': {
        type: 'Equipment',
        msg:  `New Equipment request submitted by ${name}`,
      },
      'new_feedback': {
        type: 'Feedback',
        msg:  data.rating
                ? `New feedback received — rated ${data.rating}/5 stars`
                : `New feedback received from ${name}`,
      },
      'new_id_application': {
        type: 'Document',
        msg:  `New ID Application submitted by ${name}`,
      },
      'new_lost_card_report': {
        type: 'Document',
        msg:  `Lost card reported by ${name}`,
      },
      'new_rfid_linked': {
        type: 'Document',
        msg:  `New RFID card linked for ${name}`,
      },
    }

    const mapped = eventMap[type]
    if (!mapped) return

    notifications.value.unshift({
      id:     Date.now(),
      type:   mapped.type,
      msg:    mapped.msg,
      date,
      time,
      unread: true,
    })
  }

  function markRead(id) {
    const n = notifications.value.find(n => n.id === id)
    if (n) n.unread = false
  }

  function markAllRead(ids) {
    ids.forEach(id => markRead(id))
  }

  function deleteMany(ids) {
    notifications.value = notifications.value.filter(n => !ids.includes(n.id))
  }

  return { notifications, handleWebSocketEvent, markRead, markAllRead, deleteMany }
})