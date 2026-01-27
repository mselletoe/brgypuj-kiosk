<script setup>
import { ref, computed, onMounted } from 'vue'
import RequestCard from '@/views/requests/document-requests/DocumentRequestCard.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'

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
    `Undo ${selectedRequests.value.size} selected requests back to approved?`,
    async () => {
      releasedRequests.value.forEach(req => {
        if (selectedRequests.value.has(req.id)) req.status = 'approved'
      })
      selectedRequests.value.clear()
    }
  )
}

const bulkDelete = () => {
  if (selectedRequests.value.size === 0) return

  openConfirmModal(
    `Delete ${selectedRequests.value.size} selected requests?`,
    async () => {
      releasedRequests.value = releasedRequests.value.filter(
        req => !selectedRequests.value.has(req.id)
      )
      selectedRequests.value.clear()
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

  switch (action) {
    case 'view':
        alert(`Viewing request ${requestId} - implement view modal`)
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
}

const handleDelete = (id) => {
  openConfirmModal(
    'Are you sure you want to delete this request?',
    async () => {
      releasedRequests.value = releasedRequests.value.filter(req => req.id !== id)
    }
  )
}

const handleUndo = (id) => {
  openConfirmModal(
    'Move this request back to approved?',
    async () => {
      const request = releasedRequests.value.find(req => req.id === id)
      if (request) request.status = 'approved'
    }
  )
}

// --- HANDLE SELECTION ---
const handleSelectionUpdate = (requestId, isSelected) => {
  if (isSelected) {
    selectedRequests.value.add(requestId)
  } else {
    selectedRequests.value.delete(requestId)
  }
}

// --- Load on mount ---
onMounted(fetchReleasedRequests)

// --- COMPUTED: Search Filter ---
const filteredRequests = computed(() => {
  if (!props.searchQuery) return releasedRequests.value

  const lowerQuery = props.searchQuery.toLowerCase().trim()
  return releasedRequests.value.filter(req =>
    req.requester.firstName.toLowerCase().includes(lowerQuery) ||
    req.requester.surname.toLowerCase().includes(lowerQuery) ||
    req.requestType.toLowerCase().includes(lowerQuery) ||
    req.requestedOn.toLowerCase().includes(lowerQuery) ||
    req.releasedDate.toLowerCase().includes(lowerQuery) ||
    req.rfidNo.toLowerCase().includes(lowerQuery) ||
    (req.amount && req.amount.includes(lowerQuery))
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

    <div v-else class="space-y-4">
      <RequestCard
        v-for="request in filteredRequests"
        :key="request.id"
        :id="request.id"
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
      >
      </RequestCard>
    </div>
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