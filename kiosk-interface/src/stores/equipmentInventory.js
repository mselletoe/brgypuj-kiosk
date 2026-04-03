/**
 * @file stores/equipmentInventory.js
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getAvailableEquipment } from '@/api/equipmentService'

export const useEquipmentInventoryStore = defineStore('equipmentInventory', () => {
  const inventory = ref([])
  const loading   = ref(false)
  const error     = ref(null)
  const fetched   = ref(false)

  async function fetchInventory(force = false) {
    if (fetched.value && !force) return
    loading.value = true
    error.value   = null
    try {
      inventory.value = await getAvailableEquipment()
      fetched.value   = true
    } catch (err) {
      console.error('[equipmentInventory] Failed to load inventory:', err)
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  // Called by useWebSocket when equipment_inventory_updated arrives
  function handleWebSocketEvent(action, data) {
    if (action === 'created') {
      inventory.value.push(data)
    } else if (action === 'updated') {
      const idx = inventory.value.findIndex(i => i.id === data.id)
      if (idx !== -1) Object.assign(inventory.value[idx], data)
    } else if (action === 'deleted') {
      inventory.value = inventory.value.filter(i => i.id !== data.id)
    }
  }

  return { inventory, loading, error, fetched, fetchInventory, handleWebSocketEvent }
})