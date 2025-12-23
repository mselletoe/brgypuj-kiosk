<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api/api'
import EquipmentRequestCard from '@/views/requests/equipment-requests/EquipmentRequestCard.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'

const props = defineProps({
  searchQuery: { type: String, default: '' }
})

const returnedRequests = ref([])
const isLoading = ref(true)
const errorMessage = ref(null)
const selectedRequests = ref(new Set())
const showConfirmModal = ref(false)
const confirmTitle = ref('Are you sure?')
const confirmAction = ref(null)

const openConfirmModal = (title, action) => {
  confirmTitle.value = title
  confirmAction.value = action
  showConfirmModal.value = true
}

const handleConfirm = async () => {
  if (confirmAction.value) await confirmAction.value()
  showConfirmModal.value = false
  confirmAction.value = null
}

const handleCancel = () => {
  showConfirmModal.value = false
  confirmAction.value = null
}

const formatRequestDate = (isoDate) => {
  if (!isoDate) return "N/A"
  const date = new Date(isoDate)
  return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
}

const formatDate = (isoDate) => {
  if (!isoDate) return "N/A"
  const date = new Date(isoDate)
  return date.toLocaleDateString('en-US', { month: '2-digit', day: '2-digit', year: '2-digit' })
}

const fetchReturnedRequests = async () => {
  try {
    const response = await api.get('/requests')
    returnedRequests.value = response.data
      .filter(req => req.status === 'returned')
      .map(req => ({
        id: req.id.toString(),
        status: 'returned',
        requestType: req.equipment_name || 'Unknown Equipment',
        requester: {
          firstName: req.requester_name?.split(' ')[0] || '',
          middleName: req.requester_name?.split(' ')[1] || '',
          surname: req.requester_name?.split(' ').slice(2).join(' ') || req.requester_name || 'N/A'
        },
        rfidNo: req.rfid_uid || 'Guest Mode',
        requestedOn: formatRequestDate(req.created_at),
        borrowingPeriod: {
          from: formatDate(req.borrow_start_date),
          to: formatDate(req.borrow_end_date)
        },
        amount: req.price ? req.price.toFixed(2) : null,
        isPaid: req.payment_status === 'Paid',
        rawData: req
      }))
  } catch (error) {
    console.error('Error fetching requests:', error)
    errorMessage.value = 'Failed to load returned requests.'
  } finally {
    isLoading.value = false
  }
}

const selectAll = () => {
  selectedRequests.value = new Set(filteredRequests.value.map(r => r.id))
}

const deselectAll = () => {
  selectedRequests.value.clear()
}

const bulkUndo = () => {
  if (selectedRequests.value.size === 0) return
  openConfirmModal(
    `Undo ${selectedRequests.value.size} selected requests back to picked up?`,
    async () => {
      try {
        const ids = Array.from(selectedRequests.value)
        await Promise.all(ids.map(id => api.put(`/requests/${id}/status`, { status_name: 'pickedup' })))
        returnedRequests.value = returnedRequests.value.filter(req => !selectedRequests.value.has(req.id))
        selectedRequests.value.clear()
      } catch (e) {
        console.error(e)
      }
    }
  )
}

const bulkDelete = () => {
  if (selectedRequests.value.size === 0) return
  openConfirmModal(
    `Delete ${selectedRequests.value.size} selected requests?`,
    async () => {
      try {
        const ids = Array.from(selectedRequests.value)
        await Promise.all(ids.map(id => api.delete(`/requests/${id}`)))
        returnedRequests.value = returnedRequests.value.filter(req => !selectedRequests.value.has(req.id))
        selectedRequests.value.clear()
      } catch (e) {
        console.error(e)
      }
    }
  )
}

defineExpose({
  selectedCount: computed(() => selectedRequests.value.size),
  totalCount: computed(() => filteredRequests.value.length),
  selectAll,
  deselectAll,
  bulkUndo,
  bulkDelete
})

const handleButtonClick = async ({ action, requestId }) => {
  try {
    switch (action) {
      case 'details':
        console.log(`Opening details for request ${requestId}`)
        break
      case 'notes':
        console.log(`Opening notes for request ${requestId}`)
        break
      case 'undo':
        await handleUndo(requestId)
        break
      case 'delete':
        await handleDelete(requestId)
        break
    }
  } catch (error) {
    console.error(`Error handling ${action}:`, error)
  }
}

const handleUndo = (id) => {
  openConfirmModal(
    'Move this request back to picked up?',
    async () => {
      try {
        await api.put(`/requests/${id}/status`, { status_name: 'pickedup' })
        returnedRequests.value = returnedRequests.value.filter(req => req.id !== id)
      } catch (error) {
        console.error('Error undoing request:', error)
      }
    }
  )
}

const handleDelete = (id) => {
  openConfirmModal(
    'Are you sure you want to delete this request?',
    async () => {
      try {
        await api.delete(`/requests/${id}`)
        returnedRequests.value = returnedRequests.value.filter(req => req.id !== id)
      } catch (error) {
        console.error('Error deleting request:', error)
      }
    }
  )
}

const handleSelectionUpdate = (requestId, isSelected) => {
  if (isSelected) {
    selectedRequests.value.add(requestId)
  } else {
    selectedRequests.value.delete(requestId)
  }
}

onMounted(fetchReturnedRequests)

const filteredRequests = computed(() => {
  if (!props.searchQuery) return returnedRequests.value
  const lowerQuery = props.searchQuery.toLowerCase().trim()
  return returnedRequests.value.filter(req =>
    req.requester.firstName.toLowerCase().includes(lowerQuery) ||
    req.requester.surname.toLowerCase().includes(lowerQuery) ||
    req.requestType.toLowerCase().includes(lowerQuery) ||
    req.requestedOn.toLowerCase().includes(lowerQuery) ||
    req.rfidNo.toLowerCase().includes(lowerQuery) ||
    (req.amount && req.amount.includes(lowerQuery))
  )
})
</script>

<template>
  <div class="space-y-4">
    <div v-if="isLoading" class="text-center p-10 text-gray-500">
      <p>Loading returned requests...</p>
    </div>
    <div v-else-if="errorMessage" class="text-center p-10 text-red-500">
      <p>{{ errorMessage }}</p>
    </div>
    <div v-else-if="filteredRequests.length === 0" class="text-center p-10 text-gray-500">
      <h3 class="text-lg font-medium text-gray-700">No Returned Requests</h3>
      <p class="text-gray-500">
        <span v-if="searchQuery">No requests match your search.</span>
        <span v-else>No equipment has been returned yet.</span>
      </p>
    </div>
    <EquipmentRequestCard
      v-for="request in filteredRequests"
      :key="request.id"
      :id="request.id"
      :status="request.status"
      :request-type="request.requestType"
      :requester="request.requester"
      :rfid-no="request.rfidNo"
      :requested-on="request.requestedOn"
      :borrowing-period="request.borrowingPeriod"
      :amount="request.amount"
      :is-paid="request.isPaid"
      :is-selected="selectedRequests.has(request.id)"
      @button-click="handleButtonClick"
      @update:selected="(value) => handleSelectionUpdate(request.id, value)"
    />
  </div>
  <ConfirmModal
    :show="showConfirmModal"
    :title="confirmTitle"
    confirm-text="Yes"
    cancel-text="Cancel"
    @confirm="handleConfirm"
    @cancel="handleCancel"
  />
</template>