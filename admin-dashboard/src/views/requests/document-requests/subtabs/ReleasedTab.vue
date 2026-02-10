<script setup>
import { ref, computed, onMounted } from 'vue'
import RequestCard from '@/views/requests/document-requests/DocumentRequestCard.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'
import {
  getDocumentRequests,
  deleteRequest,
  undoRequest,
  bulkDeleteRequests,
  bulkUndoRequests,
  viewRequestPdf
} from '@/api/documentService'

const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  }
})

const releasedRequests = ref([])
const isLoading = ref(true)
const errorMessage = ref(null)
const selectedRequests = ref(new Set())
const showConfirmModal = ref(false)
const confirmTitle = ref('Are you sure?')
const confirmAction = ref(null)

const fetchReleasedRequests = async () => {
  isLoading.value = true
  errorMessage.value = null
  
  try {
    const response = await getDocumentRequests()
    
    const allRequests = response.data.map(req => ({
      id: req.id,
      transaction_no: req.transaction_no,
      type: req.doctype_name.toUpperCase() === 'RFID' ? 'rfid' : 'document',
      status: req.status.toLowerCase(),
      requestType: req.doctype_name,
      requester: {
        firstName: req.resident_first_name || '',
        middleName: req.resident_middle_name || '',
        lastName: req.resident_last_name || ''
      },
      rfidNo: req.resident_rfid || 'Guest Mode',
      requestedOn: new Date(req.requested_at).toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric'
      }),
      amount: req.payment_status !== 'free' ? String(req.price ?? '0.00') : null,
      isPaid: req.payment_status === 'paid',
      raw: req
    }))
    
    // Filter only released requests
    releasedRequests.value = allRequests.filter(req => req.status === 'released')
  } catch (error) {
    console.error('Error fetching released requests:', error)
    errorMessage.value = 'Failed to load released requests. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const openConfirmModal = (title, action) => {
  confirmTitle.value = title
  confirmAction.value = action
  showConfirmModal.value = true
}

const handleConfirm = async () => {
  if (confirmAction.value) {
    await confirmAction.value()
  }
  showConfirmModal.value = false
  confirmAction.value = null
}

const handleCancel = () => {
  showConfirmModal.value = false
  confirmAction.value = null
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
    `Move ${selectedRequests.value.size} selected requests back to approved?`,
    async () => {
      try {
        await bulkUndoRequests(Array.from(selectedRequests.value))
        
        // Remove from current list
        releasedRequests.value = releasedRequests.value.filter(
          req => !selectedRequests.value.has(req.id)
        )
        selectedRequests.value.clear()
      } catch (error) {
        console.error('Error during bulk undo:', error)
        alert('Failed to undo some requests. Please try again.')
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
        await bulkDeleteRequests(Array.from(selectedRequests.value))
        releasedRequests.value = releasedRequests.value.filter(
          req => !selectedRequests.value.has(req.id)
        )
        selectedRequests.value.clear()
      } catch (error) {
        console.error('Error during bulk delete:', error)
        alert('Failed to delete selected requests. Please try again.')
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
  const request = releasedRequests.value.find(r => r.id === requestId)
  if (!request) return

  try {
    switch (action) {
      case 'view':
        viewRequestPdf(requestId)
        break
      case 'notes':
        console.log(`Opening notes for request ${requestId}`)
        break
      case 'delete':
        handleDelete(requestId)
        break
      case 'undo':
        handleUndo(requestId)
        break
      default:
        console.log(`Action ${action} not implemented yet`)
    }
  } catch (error) {
    console.error(`Error handling ${action}:`, error)
    alert(`Failed to ${action} request. Please try again.`)
  }
}

const handleDelete = (id) => {
  openConfirmModal(
    'Are you sure you want to delete this request?',
    async () => {
      try {
        await deleteRequest(id)
        releasedRequests.value = releasedRequests.value.filter(req => req.id !== id)
      } catch (error) {
        console.error('Error deleting request:', error)
        alert('Failed to delete request. Please try again.')
      }
    }
  )
}

const handleUndo = (id) => {
  openConfirmModal(
    'Move this request back to approved?',
    async () => {
      try {
        await undoRequest(id)
        releasedRequests.value = releasedRequests.value.filter(req => req.id !== id)
      } catch (error) {
        console.error('Error undoing request:', error)
        alert('Failed to undo request. Please try again.')
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

onMounted(fetchReleasedRequests)

const filteredRequests = computed(() => {
  if (!props.searchQuery) return releasedRequests.value

  const q = props.searchQuery.toLowerCase()
  return releasedRequests.value.filter(req =>
    req.requester.firstName.toLowerCase().includes(q) ||
    req.requester.lastName.toLowerCase().includes(q) ||
    req.requestType.toLowerCase().includes(q) ||
    req.rfidNo.toLowerCase().includes(q) ||
    (req.transaction_no || '').toLowerCase().includes(q)
  )
})
</script>

<template>
  <div class="space-y-4">
    <div 
      v-if="isLoading" 
      class="text-center p-10 text-gray-500"
    >
      <p>Loading released requests...</p>
    </div>

    <div 
      v-else-if="errorMessage" 
      class="text-center p-10 text-red-500"
    >
      <p>{{ errorMessage }}</p>
    </div>

    <div 
      v-else-if="filteredRequests.length === 0" 
      class="text-center p-10 text-gray-500"
    >
      <h3 class="text-lg font-medium text-gray-700">No Released Requests</h3>
      <p class="text-gray-500">
        <span v-if="searchQuery">No requests match your search.</span>
        <span v-else>No documents have been released yet.</span>
      </p>
    </div>

    <RequestCard
      v-for="request in filteredRequests"
      :key="request.id"
      :id="request.id"
      :transaction-no="request.transaction_no"
      :type="request.type"
      :status="request.status"
      :request-type="request.requestType"
      :requester="request.requester"
      :rfid-no="request.rfidNo"
      :requested-on="request.requestedOn"
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