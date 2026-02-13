<script setup>
import { ref, computed, onMounted } from 'vue'
import RequestCard from '@/views/requests/document-requests/DocumentRequestCard.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'
import {
  getDocumentRequests,
  approveRequest,
  rejectRequest,
  deleteRequest,
  markAsPaid,
  markAsUnpaid,
  bulkDeleteRequests,
  viewRequestPdf 
} from '@/api/documentService'

const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  },
  filters: {
    type: Object,
    default: () => ({
      requestedDate: null,
      documentType: null,
      paymentStatus: null
    })
  }
})

const pendingRequests = ref([])
const isLoading = ref(true)
const errorMessage = ref(null)
const selectedRequests = ref(new Set())
const showConfirmModal = ref(false)
const confirmTitle = ref('Are you sure?')
const confirmAction = ref(null)

const fetchPendingRequests = async () => {
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
    
    // Filter only pending requests
    pendingRequests.value = allRequests.filter(req => req.status === 'pending')
  } catch (error) {
    console.error('Error fetching requests:', error)
    errorMessage.value = 'Failed to load requests. Please try again.'
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

const bulkDelete = () => {
  if (selectedRequests.value.size === 0) return

  openConfirmModal(
    `Delete ${selectedRequests.value.size} selected requests?`,
    async () => {
      try {
        await bulkDeleteRequests(Array.from(selectedRequests.value))
        pendingRequests.value = pendingRequests.value.filter(
          req => !selectedRequests.value.has(req.id)
        )
        selectedRequests.value.clear()
      } catch (error) {
        console.error(error)
        alert('Failed to delete selected requests')
      }
    }
  )
}

defineExpose({
  selectedCount: computed(() => selectedRequests.value.size),
  totalCount: computed(() => filteredRequests.value.length),
  selectAll,
  deselectAll,
  bulkDelete
})

const handleButtonClick = ({ action, requestId }) => {
  const request = pendingRequests.value.find(r => r.id === requestId)
  if (!request) return

  switch (action) {
    case 'view':
      viewRequestPdf(requestId)
      break
    case 'notes':
      console.log(`Opening notes for request ${requestId}`)
      break
    case 'approve':
      handleApprove(requestId)
      break
    case 'reject':
      handleReject(requestId)
      break
    case 'delete':
      handleDelete(requestId)
      break
    default:
      console.log(`Action ${action} not implemented`)
  }
}

const handleApprove = async (id) => {
  try {
    await approveRequest(id)
    pendingRequests.value = pendingRequests.value.filter(req => req.id !== id)
  } catch (error) {
    console.error(error)
    alert('Failed to approve request')
  }
}

const handleReject = async (id) => {
  try {
    await rejectRequest(id)
    pendingRequests.value = pendingRequests.value.filter(req => req.id !== id)
  } catch (error) {
    console.error(error)
    alert('Failed to reject request')
  }
}

const handleDelete = async (id) => {
  openConfirmModal(
    'Are you sure you want to delete this request?',
    async () => {
      try {
        await deleteRequest(id)
        pendingRequests.value = pendingRequests.value.filter(req => req.id !== id)
      } catch (error) {
        console.error(error)
        alert('Failed to delete request')
      }
    }
  )
}

const handlePaymentUpdate = async (requestId, newPaidStatus) => {
  try {
    if (newPaidStatus) {
      await markAsPaid(requestId)
    } else {
      await markAsUnpaid(requestId)
    }
    const request = pendingRequests.value.find(r => r.id === requestId)
    if (request) request.isPaid = newPaidStatus
  } catch (error) {
    console.error(error)
    alert('Failed to update payment status')
  }
}

const handleSelectionUpdate = (requestId, isSelected) => {
  if (isSelected) {
    selectedRequests.value.add(requestId)
  } else {
    selectedRequests.value.delete(requestId)
  }
}

onMounted(fetchPendingRequests)

const filteredRequests = computed(() => {
  let result = pendingRequests.value

  if (props.searchQuery) {
    const q = props.searchQuery.toLowerCase()
    result = result.filter(req =>
      req.requester.firstName.toLowerCase().includes(q) ||
      req.requester.lastName.toLowerCase().includes(q) ||
      req.requestType.toLowerCase().includes(q) ||
      req.rfidNo.toLowerCase().includes(q) ||
      (req.transaction_no || '').toLowerCase().includes(q)
    )
  }

  if (props.filters?.requestedDate) {
    const selectedDate = new Date(props.filters.requestedDate).toDateString()

    result = result.filter(req =>
      new Date(req.raw.requested_at).toDateString() === selectedDate
    )
  }

  if (props.filters?.documentType) {
    result = result.filter(req =>
      req.raw.doctype_id === props.filters.documentType
    )
  }

  if (props.filters?.paymentStatus) {
    result = result.filter(req =>
      props.filters.paymentStatus === 'paid'
        ? req.isPaid
        : !req.isPaid
    )
  }

  return result
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