import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getAllNotifications,
  markNotificationRead,
  bulkMarkRead,
  bulkDeleteNotifications,
} from '@/api/notifications'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])

  // ── Helpers ───────────────────────────────────────────────────────────────
  function mapType(event) {
    const map = {
      'new_transaction':       'Document',
      'new_equipment_request': 'Equipment',
      'new_feedback':          'Feedback',
      'new_id_application':    'ID Services',
      'new_lost_card_report':  'ID Services',
      'new_rfid_linked':       'ID Services',
    }
    return map[event] || 'Document'
  }

  function buildMsg(event, data) {
    const map = {
      'new_transaction':       `New ${data.document_type || 'Document'} request submitted by ${data.resident_name}`,
      'new_equipment_request': `New Equipment request submitted by ${data.resident_name}`,
      'new_feedback':          data.rating ? `New feedback received — rated ${data.rating}/5 stars` : 'New feedback received from a resident',
      'new_id_application':    `New ID Application submitted by ${data.resident_name}`,
      'new_lost_card_report':  `Lost card reported by ${data.resident_name}`,
      'new_rfid_linked':       `New RFID card linked for ${data.resident_name}`,
    }
    return map[event] || 'New notification'
  }

  function toUIFormat(n) {
    return {
      id:     n.id,
      type:   n.type,
      event:  n.event || '',           // persisted event name from DB
      msg:    n.msg,
      unread: !n.is_read,
      date:   new Date(n.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      time:   new Date(n.created_at).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }),
    }
  }

  // ── Load from DB on page load / refresh ───────────────────────────────────
  async function fetchNotifications() {
    try {
      const data = await getAllNotifications()
      notifications.value = data.map(toUIFormat)
    } catch (err) {
      console.error('[NotificationStore] Failed to fetch:', err)
    }
  }

  // ── Called by useWebSocket when a new event arrives ───────────────────────
  function handleWebSocketEvent(type, data) {
    const now = new Date()
    notifications.value.unshift({
      id:     data.db_id,
      type:   mapType(type),
      event:  type,                    // ws event name for navigation
      msg:    buildMsg(type, data),
      unread: true,
      date:   now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
      time:   now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }),
    })
  }

  // ── Actions ───────────────────────────────────────────────────────────────
  async function markRead(id) {
    const notif = notifications.value.find(n => n.id === id)
    if (notif) notif.unread = false
    await markNotificationRead(id)
  }

  async function markAllRead(ids) {
    ids.forEach(id => {
      const notif = notifications.value.find(n => n.id === id)
      if (notif) notif.unread = false
    })
    await bulkMarkRead(ids)
  }

  async function deleteMany(ids) {
    notifications.value = notifications.value.filter(n => !ids.includes(n.id))
    await bulkDeleteNotifications(ids)
  }

  return {
    notifications,
    fetchNotifications,
    handleWebSocketEvent,
    markRead,
    markAllRead,
    deleteMany,
  }
})