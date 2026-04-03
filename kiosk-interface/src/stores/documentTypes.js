/**
 * @file stores/documentTypes.js
 */
import { defineStore } from 'pinia'
import { getDocumentTypes } from '@/api/documentService'
import { ref } from 'vue'

export const useDocumentTypesStore = defineStore('documentTypes', () => {
  const types   = ref([])
  const loading = ref(false)
  const error   = ref(null)
  const fetched = ref(false)

  async function fetchTypes(force = false) {
    if (fetched.value && !force) return
    loading.value = true
    error.value   = null
    try {
      const data    = await getDocumentTypes()
      types.value   = data
      fetched.value  = true
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  // Called by useWebSocket when document_types_updated arrives
  function handleWebSocketEvent(action, data) {
    if (action === 'created') {
      types.value.push(data)
    } else if (action === 'updated') {
      const idx = types.value.findIndex(t => t.id === data.doctype_id)
      if (idx !== -1) Object.assign(types.value[idx], data)
    } else if (action === 'deleted') {
      types.value = types.value.filter(t => t.id !== data.doctype_id)
    }
  }

  return { types, loading, error, fetched, fetchTypes, handleWebSocketEvent }
})