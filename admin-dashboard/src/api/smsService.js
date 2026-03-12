/**
 * @file smsService.js
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

/**
 * Fetches all puroks for the "By Purok" recipient tab.
 * @returns {Promise<Array<{ id: number, purok_name: string }>>}
 */
export const fetchPuroks = async () => {
  const res = await api.get('/admin/residents/utils/puroks')
  return res.data
}

// ============================================================================
// Preview — resolve recipient count without sending
// ============================================================================

/**
 * Resolves and returns the recipient count for the current selection
 * WITHOUT sending any SMS. Use this to power the live badge in the UI.
 *
 * @param {'groups'|'puroks'|'specific'} recipientMode
 * @param {Object} selection
 * @param {string[]}  [selection.groups]       - e.g. ['senior', 'with_rfid']
 * @param {number[]}  [selection.purokIds]     - e.g. [1, 3]
 * @param {string[]}  [selection.phoneNumbers] - e.g. ['+639123456789']
 * @param {string}    message                  - any non-empty string (required by schema)
 * @returns {Promise<{ recipient_mode: string, count: number, group_labels?: string[], purok_names?: string[] }>}
 */
export const previewRecipients = async (recipientMode, selection, message = 'preview') => {
  const payload = _buildPayload(recipientMode, selection, message)
  const res = await api.post('/admin/sms/preview', payload)
  return res.data
}

// ============================================================================
// Send
// ============================================================================

/**
 * Sends an SMS announcement to the resolved recipient list.
 *
 * @param {'groups'|'puroks'|'specific'} recipientMode
 * @param {Object} selection
 * @param {string[]}  [selection.groups]
 * @param {number[]}  [selection.purokIds]
 * @param {string[]}  [selection.phoneNumbers]
 * @param {string}    message
 * @returns {Promise<{ success: boolean, recipients: number, message_preview: string, failed: number, queued_at: string }>}
 */
export const sendSMSAnnouncement = async (recipientMode, selection, message) => {
  const payload = _buildPayload(recipientMode, selection, message)
  const res = await api.post('/admin/sms/send', payload)
  return res.data
}

// ============================================================================
// History
// ============================================================================

/**
 * Fetches the SMS send history for the "Recent Sends" panel.
 * @param {number} [limit=20]
 * @returns {Promise<Array<{ id: number, message: string, mode: string, recipients: number, sent_at: string }>>}
 */
export const fetchSMSHistory = async (limit = 20) => {
  const res = await api.get('/admin/sms/history', { params: { limit } })
  return res.data
}

// ============================================================================
// Internal helper
// ============================================================================

/**
 * Builds the request payload expected by the backend SMSRequest schema.
 * @private
 */
function _buildPayload(recipientMode, selection, message) {
  const base = { message, recipient_mode: recipientMode }

  if (recipientMode === 'groups') {
    return { ...base, groups: selection.groups ?? [] }
  }
  if (recipientMode === 'puroks') {
    return { ...base, purok_ids: selection.purokIds ?? [] }
  }
  if (recipientMode === 'specific') {
    // Accept a comma-separated string OR an array
    const raw = Array.isArray(selection.phoneNumbers)
      ? selection.phoneNumbers
      : (selection.phoneNumbers ?? '').split(',')
    return { ...base, phone_numbers: raw.map(n => n.trim()).filter(Boolean) }
  }

  throw new Error(`Unknown recipientMode: ${recipientMode}`)
}