<script setup>
import { ref, computed, onMounted } from 'vue'
import RequestCard from '@/views/requests/document-requests/DocumentRequestCard.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'

// --- PROPS ---
const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  }
})

// --- REFS ---
const pendingRequests = ref([])
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

// --- HELPERS ---
const formatRequestDate = (isoDate) => {
  if (!isoDate) return "N/A"
  const date = new Date(isoDate)
  const now = new Date()
  const diffMs = now - date
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)

  if (diffMin < 1) return `${diffSec} seconds ago`
  if (diffHour < 1) return `${diffMin} minutes ago`
  if (diffHour < 24) return `${diffHour} hours ago`

  return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
}

// --- FETCH PENDING REQUESTS ---
const fetchPendingRequests = async () => {
  try {
    const response = await api.get('/requests')
    pendingRequests.value = response.data
      .filter(req => req.status === 'pending')
      .map(req => ({
        id: req.id.toString(),
        type: req.rfid_uid ? 'rfid' : 'document',
        status: 'pending',
        requestType: req.document_type || 'Unknown Document',
        requester: {
          firstName: req.requester_name?.split(' ')[0] || '',
          middleName: req.requester_name?.split(' ')[1] || '',
          surname: req.requester_name?.split(' ').slice(2).join(' ') || req.requester_name || 'N/A'
        },
        rfidNo: req.rfid_uid || 'Guest Mode',
        requestedOn: formatRequestDate(req.created_at),
        amount: req.price ? req.price.toFixed(2) : null,
        isPaid: req.payment_status === 'Paid',
        residentId: req.resident_id,
        rawData: req
      }))
  } catch (error) {
    console.error('Error fetching requests:', error)
    errorMessage.value = 'Failed to load pending requests.'
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

const bulkDelete = () => {
  if (selectedRequests.value.size === 0) return

  openConfirmModal(
    `Delete ${selectedRequests.value.size} selected requests?`,
    async () => {
      try {
        const ids = Array.from(selectedRequests.value)
        await Promise.all(ids.map(id => api.delete(`/requests/${id}`)))
        pendingRequests.value = pendingRequests.value.filter(
          req => !selectedRequests.value.has(req.id)
        )
        selectedRequests.value.clear()
      } catch (e) {
        console.error(e)
      }
    }
  )
}

// EXPOSE THESE TO THE PARENT
defineExpose({
  selectedCount: computed(() => selectedRequests.value.size),
  totalCount: computed(() => filteredRequests.value.length),
  selectAll,
  deselectAll,
  bulkDelete
})

// --- HANDLE BUTTON CLICK ---
const handleButtonClick = async ({ action, requestId, type, status }) => {
  const request = pendingRequests.value.find(r => r.id === requestId)
  if (!request) return

  try {
    switch (action) {
      case 'view':
        await handleViewDocument(requestId)
        break
      case 'notes':
        console.log(`Opening notes for request ${requestId}`)
        // TODO: Implement notes modal
        break
      case 'approve':
        await handleApprove(requestId)
        break
      case 'reject':
        await handleReject(requestId)
        break
      case 'delete':
        await handleDelete(requestId)
        break
      default:
        console.log(`Action ${action} not implemented yet`)
    }
  } catch (error) {
    console.error(`Error handling ${action}:`, error)
  }
}

// --- VIEW DOCUMENT ---
const handleViewDocument = async (id) => {
  try {
    const response = await api.get(`/requests/${id}/download-pdf`, {
      responseType: 'blob'
    })
    
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
    
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch (error) {
    console.error('Error opening PDF:', error)
    alert('Failed to load document. Please try again.')
  }
}

// --- APPROVE REQUEST ---
const handleApprove = async (id) => {
  try {
    await api.put(`/requests/${id}/status`, { status_name: 'approved' })
    pendingRequests.value = pendingRequests.value.filter(req => req.id !== id)
  } catch (error) {
    console.error('Error approving request:', error)
  }
}

// --- REJECT REQUEST ---
const handleReject = async (id) => {
  try {
    await api.put(`/requests/${id}/status`, { status_name: 'rejected' })
    pendingRequests.value = pendingRequests.value.filter(req => req.id !== id)
  } catch (error) {
    console.error('Error rejecting request:', error)
  }
}

// --- DELETE REQUEST ---
const handleDelete = (id) => {
  openConfirmModal(
    'Are you sure you want to delete this request?',
    async () => {
      try {
        await api.delete(`/requests/${id}`)
        pendingRequests.value = pendingRequests.value.filter(req => req.id !== id)
      } catch (error) {
        console.error('Error deleting request:', error)
      }
    }
  )
}

// --- TOGGLE PAYMENT STATUS ---
const handlePaymentUpdate = async (requestId, newPaidStatus) => {
  const request = pendingRequests.value.find(r => r.id === requestId)
  if (!request) return

  try {
    const newStatus = newPaidStatus ? 'Paid' : 'Unpaid'
    await api.put(`/requests/${requestId}/payment`, { payment_status: newStatus })
    request.isPaid = newPaidStatus
  } catch (error) {
    console.error('Error toggling payment status:', error)
  }
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
onMounted(fetchPendingRequests)

// --- COMPUTED: Search Filter ---
const filteredRequests = computed(() => {
  if (!props.searchQuery) return pendingRequests.value

  const lowerQuery = props.searchQuery.toLowerCase().trim()
  return pendingRequests.value.filter(req =>
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
    <div 
      v-if="isLoading" 
      class="text-center p-10 text-gray-500"
    >
      <p>Loading pending requests...</p>
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
      <h3 class="text-lg font-medium text-gray-700">No Pending Requests</h3>
      <p class="text-gray-500">
        <span v-if="searchQuery">No requests match your search.</span>
        <span v-else>All pending requests have been processed.</span>
      </p>
    </div>

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
      @update:is-paid="(value) => handlePaymentUpdate(request.id, value)"
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