<script setup>
import { ref, computed, onMounted } from 'vue'
import EquipmentRequestCard from '@/views/requests/equipment-requests/EquipmentRequestCard.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'
import {
  getEquipmentRequests,
  undoRequest,
  deleteRequest,
  bulkUndoRequests,
  bulkDeleteRequests
} from '@/api/equipmentService'

const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  }
})

const rejectedRequests = ref([])
const isLoading = ref(true)
const errorMessage = ref(null)
const selectedRequests = ref(new Set())
const showConfirmModal = ref(false)
const confirmTitle = ref('Are you sure?')
const confirmAction = ref(null)

const fetchRejectedRequests = async () => {
  isLoading.value = true
  errorMessage.value = null

  try {
    const response = await getEquipmentRequests()

    const allRequests = response.data.map(req => {
      // Format equipment items list
      const equipmentList = req.items
        .map(item => `${item.quantity}x ${item.item_name}`)
        .join(', ')

      return {
        id: req.id,
        transaction_no: req.transaction_no,
        status: req.status.toLowerCase().replace('-', ''),
        requestType: equipmentList,
        requester: {
          firstName: req.resident_first_name || '',
          middleName: req.resident_middle_name || '',
          lastName: req.resident_last_name || ''
        },
        rfidNo: req.resident_rfid,
        requestedOn: new Date(req.requested_at).toLocaleDateString('en-US', {
          month: 'long',
          day: 'numeric',
          year: 'numeric'
        }),
        borrowingPeriod: {
          from: new Date(req.borrow_date).toLocaleDateString('en-US', {
            month: '2-digit',
            day: '2-digit',
            year: '2-digit'
          }),
          to: new Date(req.return_date).toLocaleDateString('en-US', {
            month: '2-digit',
            day: '2-digit',
            year: '2-digit'
          })
        },
        amount: req.payment_status !== 'free' ? String(req.total_cost ?? '0.00') : null,
        isPaid: req.payment_status === 'paid',
        raw: req
      }
    })

    // Filter only rejected requests
    rejectedRequests.value = allRequests.filter(req => req.status === 'rejected')
  } catch (error) {
    console.error('Error fetching equipment requests:', error)
    errorMessage.value = 'Failed to load rejected equipment requests. Please try again.'
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
    `Undo ${selectedRequests.value.size} selected requests back to pending?`,
    async () => {
      try {
        await bulkUndoRequests(Array.from(selectedRequests.value))
        rejectedRequests.value = rejectedRequests.value.filter(
          req => !selectedRequests.value.has(req.id)
        )
        selectedRequests.value.clear()
      } catch (error) {
        console.error(error)
        alert('Failed to undo selected requests')
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
        rejectedRequests.value = rejectedRequests.value.filter(
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
  bulkUndo,
  bulkDelete
})

const handleButtonClick = ({ action, requestId }) => {
  const request = rejectedRequests.value.find(r => r.id === requestId)
  if (!request) return

  switch (action) {
    case 'details':
      alert(`Viewing request ${requestId} (frontend only)`)
      break
    case 'notes':
      console.log(`Opening notes for request ${requestId}`)
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

const handleUndo = async (id) => {
  openConfirmModal(
    'Move this request back to pending for review?',
    async () => {
      try {
        await undoRequest(id)
        rejectedRequests.value = rejectedRequests.value.filter(req => req.id !== id)
      } catch (error) {
        console.error(error)
        alert('Failed to undo request')
      }
    }
  )
}

const handleDelete = (id) => {
  openConfirmModal(
    'Are you sure you want to delete this request?',
    async () => {
      try {
        await deleteRequest(id)
        rejectedRequests.value = rejectedRequests.value.filter(req => req.id !== id)
      } catch (error) {
        console.error(error)
        alert('Failed to delete request')
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

onMounted(fetchRejectedRequests)

const filteredRequests = computed(() => {
  if (!props.searchQuery) return rejectedRequests.value

  const q = props.searchQuery.toLowerCase()
  return rejectedRequests.value.filter(req =>
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
      <p>Loading rejected equipment requests...</p>
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
      <h3 class="text-lg font-medium text-gray-700">No Rejected Equipment Requests</h3>
      <p class="text-gray-500">
        <span v-if="searchQuery">No requests match your search.</span>
        <span v-else>There are no rejected requests.</span>
      </p>
    </div>

    <EquipmentRequestCard
      v-for="request in filteredRequests"
      :key="request.id"
      :id="request.id"
      :transaction-no="request.transaction_no"
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