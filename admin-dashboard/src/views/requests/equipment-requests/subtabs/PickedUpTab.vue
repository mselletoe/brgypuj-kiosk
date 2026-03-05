<script setup>
import { ref, computed, onMounted } from 'vue'
import EquipmentRequestCard from '@/views/requests/equipment-requests/EquipmentRequestCard.vue'
import ConfirmModal from '@/components/shared/ConfirmationModal.vue'
import SMSModal from '@/components/shared/SendSMSModal.vue'
import {
  getEquipmentRequests,
  markAsReturned,
  undoRequest,
  deleteRequest,
  bulkUndoRequests,
  bulkDeleteRequests
} from '@/api/equipmentService'

const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  },
  filters: {
    type: Object,
    default: () => ({
      requestedDate: null,
      borrowingPeriodStart: null,
      borrowingPeriodEnd: null,
      paymentStatus: null
    })
  }
})

const pickedUpRequests = ref([])
const isLoading = ref(true)
const errorMessage = ref(null)
const selectedRequests = ref(new Set())
const showConfirmModal = ref(false)
const confirmTitle = ref('Are you sure?')
const confirmAction = ref(null)
const showSmsModal = ref(false)
const smsRecipientName = ref('')
const smsRecipientPhone = ref('')
const smsDefaultMessage = ref('')

const fetchPickedUpRequests = async () => {
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
        phoneNumber: req.contact_number || '',
        borrowerName: req.contact_person || '',
        contactPerson: req.contact_person,
        contactNumber: req.contact_number,
        purpose: req.purpose,
        raw: req
      }
    })

    // Filter only picked-up requests
    pickedUpRequests.value = allRequests.filter(req => req.status === 'pickedup')
  } catch (error) {
    console.error('Error fetching equipment requests:', error)
    errorMessage.value = 'Failed to load picked up equipment requests. Please try again.'
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
    `Undo ${selectedRequests.value.size} selected requests back to approved?`,
    async () => {
      try {
        await bulkUndoRequests(Array.from(selectedRequests.value))
        pickedUpRequests.value = pickedUpRequests.value.filter(
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
        pickedUpRequests.value = pickedUpRequests.value.filter(
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
  const request = pickedUpRequests.value.find(r => r.id === requestId)
  if (!request) return

  switch (action) {
    case 'details':
      alert(`Viewing request ${requestId} (frontend only)`)
      break
    case 'notes':
      console.log(`Opening notes for request ${requestId}`)
      break
    case 'notify':
      handleNotify(request)
      break
    case 'returned':
      handleReturned(requestId)
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

const handleNotify = (request) => {
  const fullName = [
    request.requester.firstName,
    request.requester.middleName,
    request.requester.lastName
  ].filter(Boolean).join(' ')

  smsRecipientName.value = fullName || 'Resident'
  smsRecipientPhone.value = request.raw?.resident_phone || ''
  smsDefaultMessage.value = `Hello ${request.requester.firstName || 'Resident'},

Just a reminder for your request ${request.requestType} request (Transaction #${request.transaction_no}) is to be returned soon.

Thank you!`

  showSmsModal.value = true
}

const handleSendSMS = async (smsData) => {
  try {
    console.log('Sending SMS:', smsData)
    
    // TODO: Implement actual SMS sending API call
    // Example:
    // await sendSMS({
    //   phone: smsData.phone,
    //   message: smsData.message,
    //   recipientName: smsData.recipientName
    // })
    
    // For now, just log the data
    console.log('SMS would be sent to:', smsData.phone)
    console.log('Message:', smsData.message)
    
  } catch (error) {
    console.error('Error sending SMS:', error)
    throw error // Re-throw to let the modal handle the error display
  }
}

const handleReturned = async (id) => {
  try {
    await markAsReturned(id)
    pickedUpRequests.value = pickedUpRequests.value.filter(req => req.id !== id)
  } catch (error) {
    console.error(error)
    alert('Failed to mark equipment as returned')
  }
}

const handleUndo = async (id) => {
  try {
    await undoRequest(id)
    pickedUpRequests.value = pickedUpRequests.value.filter(req => req.id !== id)
  } catch (error) {
    console.error(error)
    alert('Failed to undo request')
  }
}

const handleDelete = (id) => {
  openConfirmModal(
    'Are you sure you want to delete this request?',
    async () => {
      try {
        await deleteRequest(id)
        pickedUpRequests.value = pickedUpRequests.value.filter(req => req.id !== id)
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

onMounted(fetchPickedUpRequests)

const filteredRequests = computed(() => {
  let result = pickedUpRequests.value

  if (props.searchQuery) {
    const q = props.searchQuery.toLowerCase()
    result = result.filter(req =>
      req.requester.firstName.toLowerCase().includes(q) ||
      req.requester.lastName.toLowerCase().includes(q) ||
      req.requestType.toLowerCase().includes(q) ||
      (req.rfidNo || '').toLowerCase().includes(q) ||
      (req.transaction_no || '').toLowerCase().includes(q)
    )
  }

  if (props.filters?.requestedDate) {
    const selectedDate = new Date(props.filters.requestedDate).toDateString()

    result = result.filter(req =>
      new Date(req.raw.requested_at).toDateString() === selectedDate
    )
  }

  if (props.filters?.borrowingPeriodStart) {
    const start = new Date(props.filters.borrowingPeriodStart)

    result = result.filter(req =>
      new Date(req.raw.borrow_date) >= start
    )
  }

  if (props.filters?.borrowingPeriodEnd) {
    const end = new Date(props.filters.borrowingPeriodEnd)

    result = result.filter(req =>
      new Date(req.raw.return_date) <= end
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
      <p>Loading picked up equipment requests...</p>
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
      <h3 class="text-lg font-medium text-gray-700">No Picked Up Equipment Requests</h3>
      <p class="text-gray-500">
        <span v-if="searchQuery">No requests match your search.</span>
        <span v-else>No equipment has been picked up yet.</span>
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
      :contact-person="request.contactPerson"
      :contact-number="request.contactNumber"
      :purpose="request.purpose"
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

  <SMSModal
    :show="showSmsModal"
    :recipient-name="smsRecipientName"
    :recipient-phone="smsRecipientPhone"
    :default-message="smsDefaultMessage"
    @update:show="(value) => showSmsModal = value"
    @send="handleSendSMS"
  />
</template>