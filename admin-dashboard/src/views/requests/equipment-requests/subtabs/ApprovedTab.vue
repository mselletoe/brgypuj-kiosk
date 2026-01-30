<script setup>
import { ref, computed, onMounted } from 'vue'
import EquipmentRequestCard from '@/views/requests/equipment-requests/EquipmentRequestCard.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'
import SendSMSModal from '@/components/shared/SendSMSModal.vue'

const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  }
})

// --- REFS ---
const approvedRequests = ref([
  // Mock data example
  {
    id: 101,
    status: 'approved',
    requestType: 'Laptop',
    requester: { firstName: 'Alice', surname: 'Johnson' },
    rfidNo: 'RFID101',
    requestedOn: '2026-01-25',
    borrowingPeriod: '1/30/26 - 2/5/26',
    amount: '100',
    isPaid: true,
    phoneNumber: '09171234567',
    borrowerName: 'Alice Johnson'
  },
  {
    id: 102,
    status: 'approved',
    requestType: 'Projector',
    requester: { firstName: 'Bob', surname: 'Lee' },
    rfidNo: 'RFID102',
    requestedOn: '2026-01-26',
    borrowingPeriod: '1/30/26 - 2/5/26',
    amount: '50',
    isPaid: false,
    phoneNumber: '09179876543',
    borrowerName: 'Bob Lee'
  }
])

const isLoading = ref(true)
const errorMessage = ref(null)
const selectedRequests = ref(new Set())
const showConfirmModal = ref(false)
const confirmTitle = ref('Are you sure?')
const confirmAction = ref(null)
const showSMSModal = ref(false)
const selectedRequest = ref(null)

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
    `Undo ${selectedRequests.value.size} selected requests back to pending?`,
    () => {
      approvedRequests.value = approvedRequests.value.filter(
        req => !selectedRequests.value.has(req.id)
      )
      selectedRequests.value.clear()
    }
  )
}

const bulkDelete = () => {
  if (selectedRequests.value.size === 0) return

  openConfirmModal(
    `Delete ${selectedRequests.value.size} selected requests?`,
    () => {
      approvedRequests.value = approvedRequests.value.filter(
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

const handleButtonClick = ({ action, requestId }) => {
  const request = approvedRequests.value.find(r => r.id === requestId)
  if (!request) return

  switch (action) {
    case 'details':
      console.log(`Opening details for request ${requestId}`)
      break
    case 'notes':
      console.log(`Opening notes for request ${requestId}`)
      break
    case 'notify':
      console.log(`Sending notification for request ${requestId}`)
      break
    case 'release':
      handleRelease(requestId)
      break
    case 'undo':
      handleUndo(requestId)
      break
    case 'delete':
      handleDelete(requestId)
      break
    default:
      console.log(`Action ${action} not implemented yet`)
  }
}

const handleRelease = (id) => {
  approvedRequests.value = approvedRequests.value.filter(req => req.id !== id)
}

const handleUndo = (id) => {
  approvedRequests.value = approvedRequests.value.filter(req => req.id !== id)
}

const handleDelete = (id) => {
  openConfirmModal(
    'Are you sure you want to delete this request?',
    () => {
      approvedRequests.value = approvedRequests.value.filter(req => req.id !== id)
    }
  )
}

const handleSelectionUpdate = (requestId, isSelected) => {
  if (isSelected) selectedRequests.value.add(requestId)
  else selectedRequests.value.delete(requestId)
}

const filteredRequests = computed(() => {
  if (!props.searchQuery) return approvedRequests.value

  const lowerQuery = props.searchQuery.toLowerCase().trim()
  return approvedRequests.value.filter(req =>
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
      <p>Loading approved requests...</p>
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
      <h3 class="text-lg font-medium text-gray-700">No Approved Requests</h3>
      <p class="text-gray-500">
        <span v-if="searchQuery">No requests match your search.</span>
        <span v-else>All approved requests have been processed.</span>
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

  <SendSMSModal
    v-model:show="showSMSModal"
    :recipient-name="selectedRequest?.borrowerName"
    :recipient-phone="selectedRequest?.phoneNumber"
    :default-message="`Your ${selectedRequest?.requestType} is approved and ready for pickup.`"
    @send="handleSMSSubmit"
  />
</template>