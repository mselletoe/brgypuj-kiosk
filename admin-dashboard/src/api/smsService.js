/**
 * @file admin-dashboard/api/smsService.js
 * @description SMS Announcement Service Module
 *
 * Covers three recipient modes:
 *   groups   → predefined demographic/characteristic groups
 *   puroks   → geographic targeting by purok ID
 *   specific → manually entered phone numbers
 */
import api from './http'

// ============================================================================
// Constants — keep in sync with backend ResidentGroup enum
// ============================================================================

export const RESIDENT_GROUPS = [
  { id: 'female',    label: 'Female',              color: 'rose'   },
  { id: 'male',      label: 'Male',                color: 'blue'   },
  { id: 'adult',     label: '18 Years Old & Above', color: 'green'  },
  { id: 'youth',     label: 'Youth (15–30)',         color: 'cyan'   },
  { id: 'senior',    label: 'Senior Citizens',       color: 'purple' },
  { id: 'with_rfid', label: 'With RFID',             color: 'amber'  },
]

// ============================================================================
// READ — fetch puroks from database
// ============================================================================

export const fetchPuroks = async () => {
  const res = await api.get('/admin/residents/utils/puroks')
  return res.data
}

// ============================================================================
// Preview — resolve recipient count without sending
// ============================================================================

export const previewRecipients = async (recipientMode, selection, message = 'preview') => {
  const payload = _buildPayload(recipientMode, selection, message)
  const res = await api.post('/admin/sms/preview', payload)
  return res.data
}

// ============================================================================
// Send
// ============================================================================

export const sendSMSAnnouncement = async (recipientMode, selection, message) => {
  const payload = _buildPayload(recipientMode, selection, message)
  const recipientCount =
    recipientMode === 'specific'
      ? (payload.phone_numbers?.length ?? 1)
      : 50  // conservative estimate for group/purok sends
  const timeoutMs = Math.min(30_000 + recipientCount * 20_000, 300_000)

  const res = await api.post('/admin/sms/send', payload, { timeout: timeoutMs })
  return res.data
}

// ============================================================================
// History
// ============================================================================

export const fetchSMSHistory = async (limit = 20) => {
  const res = await api.get('/admin/sms/history', { params: { limit } })
  return res.data
}

// ============================================================================
// Internal helper
// ============================================================================

function _buildPayload(recipientMode, selection, message) {
  const base = { message, recipient_mode: recipientMode }

  if (recipientMode === 'groups') {
    return { ...base, groups: selection.groups ?? [] }
  }
  if (recipientMode === 'puroks') {
    return { ...base, purok_ids: selection.purokIds ?? [] }
  }
  if (recipientMode === 'specific') {
    const raw = Array.isArray(selection.phoneNumbers)
      ? selection.phoneNumbers
      : (selection.phoneNumbers ?? '').split(',')
    return { ...base, phone_numbers: raw.map(n => n.trim()).filter(Boolean) }
  }

  throw new Error(`Unknown recipientMode: ${recipientMode}`)
}