<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api/api'
import RequestCard from '@/components/shared/RequestCard.vue'
import SendSMSModal from '@/components/shared/SendSMSModal.vue'

// --- PROPS ---
const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  }
})

// --- REFS ---
const releasedRequests = ref([])
const isLoading = ref(true)
const errorMessage = ref(null)
const selectedRequests = ref(new Set())

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

// --- FETCH RELEASED REQUESTS ---
const fetchReleasedRequests = async () => {
  try {
    const response = await api.get('/requests')
    releasedRequests.value = response.data
      .filter(req => req.status === 'released')
      .map(req => ({
        id: req.id.toString(),
        type: req.rfid_uid ? 'rfid' : 'document',
        status: 'released',
        requestType: req.document_type || 'Unknown Document',
        requester: {
          firstName: req.requester_name?.split(' ')[0] || '',
          middleName: req.requester_name?.split(' ')[1] || '',
          surname: req.requester_name?.split(' ').slice(2).join(' ') || req.requester_name || 'N/A'
        },
        rfidNo: req.rfid_uid || 'Guest Mode',
        requestedOn: formatRequestDate(req.created_at),
        releasedDate: formatRequestDate(req.updated_at),
        amount: req.price ? req.price.toFixed(2) : null,
        isPaid: req.payment_status === 'Paid',
        residentId: req.resident_id,
        phoneNumber: req.phone_number || null,
        borrowerName: req.requester_name || 'Guest',
        rawData: req
      }))
  } catch (error) {
    console.error('Error fetching released requests:', error)
    errorMessage.value = 'Failed to load released requests.'
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

const bulkUndo = async () => {
  if (selectedRequests.value.size === 0) return
  try {
    const ids = Array.from(selectedRequests.value)
    await Promise.all(ids.map(id => api.put(`/requests/${id}/status`, { status_name: 'approved' })))
    
    approvedRequests.value = approvedRequests.value.filter(req => !selectedRequests.value.has(req.id))
    selectedRequests.value.clear()
  } catch (e) { 
    console.error('Bulk undo failed:', e) 
  }
}

const bulkDelete = async () => {
  if (selectedRequests.value.size === 0) return
  if (!confirm(`Are you sure you want to delete ${selectedRequests.value.size} items?`)) return
  
  try {
    const ids = Array.from(selectedRequests.value)
    await Promise.all(ids.map(id => api.delete(`/requests/${id}`)))
    
    approvedRequests.value = approvedRequests.value.filter(req => !selectedRequests.value.has(req.id))
    selectedRequests.value.clear()
  } catch (e) { 
    console.error('Bulk delete failed:', e) 
  }
}

// EXPOSE TO PARENT (DocumentRequest.vue)
defineExpose({
  selectedCount: computed(() => selectedRequests.value.size),
  totalCount: computed(() => filteredRequests.value.length),
  selectAll,
  deselectAll,
  bulkUndo,
  bulkDelete
})

// --- HANDLE BUTTON CLICK ---
const handleButtonClick = async ({ action, requestId, type, status }) => {
  const request = releasedRequests.value.find(r => r.id === requestId)
  if (!request) return

  try {
    switch (action) {
      case 'view':
        await handleViewDocument(requestId)
        break
      case 'notes':
        console.log(`Opening notes for request ${requestId}`)
        break
      case 'delete':
        await handleDelete(requestId)
        break
      case 'undo':
        await handleUndo(requestId)
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

// --- DELETE REQUEST ---
const handleDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this request?')) return
  
  try {
    await api.delete(`/requests/${id}`)
    releasedRequests.value = releasedRequests.value.filter(req => req.id !== id)
  } catch (error) {
    console.error('Error deleting request:', error)
  }
}

// --- UNDO (BACK TO APPROVED) ---
const handleUndo = async (id) => {
  try {
    await api.put(`/requests/${id}/status`, { status_name: 'processing' })
    releasedRequests.value = releasedRequests.value.filter(req => req.id !== id)
  } catch (error) {
    console.error('Error undoing request:', error)
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
</template>