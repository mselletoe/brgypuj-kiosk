<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api/api'

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

// --- HELPERS ---
const formatIndex = (index) => (index + 1).toString().padStart(2, '0')

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP'
  }).format(value)
}

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
        id: req.id,
        documentType: req.document_type || 'Unknown Document',
        borrowerName: req.form_data?.borrowerName || 'N/A',
        date: formatRequestDate(req.created_at),
        via: req.form_data?.via || 'Guest User',
        viaTag: req.form_data?.viaTag || null,
        amount: req.price || 0,
        paymentStatus: req.payment_status || 'Unpaid' // ✅ use database column directly
      }))
  } catch (error) {
    console.error('Error fetching requests:', error)
    errorMessage.value = 'Failed to load pending requests.'
  } finally {
    isLoading.value = false
  }
}

// --- TOGGLE PAYMENT STATUS ---
const togglePaymentStatus = async (request) => {
  try {
    const newStatus = request.paymentStatus === 'Paid' ? 'Unpaid' : 'Paid'
    await api.put(`/requests/${request.id}/payment`, { payment_status: newStatus }) // ✅ match backend key
    request.paymentStatus = newStatus // ✅ update local value for instant UI feedback
  } catch (error) {
    console.error('Error toggling payment status:', error)
  }
}

// --- Load on mount ---
onMounted(fetchPendingRequests)

// --- COMPUTED: Search Filter ---
const filteredRequests = computed(() => {
  if (!props.searchQuery) return pendingRequests.value

  const lowerQuery = props.searchQuery.toLowerCase().trim()
  return pendingRequests.value.filter(req =>
    req.borrowerName.toLowerCase().includes(lowerQuery) ||
    req.documentType.toLowerCase().includes(lowerQuery) ||
    req.date.toLowerCase().includes(lowerQuery) ||
    req.via.toLowerCase().includes(lowerQuery) ||
    req.paymentStatus.toLowerCase().includes(lowerQuery) ||
    req.amount.toString().includes(lowerQuery) ||
    (req.viaTag && req.viaTag.toLowerCase().includes(lowerQuery))
  )
})

// --- ACTIONS ---
function handleApprove(id) {
  console.log(`Approving request ${id}`)
  pendingRequests.value = pendingRequests.value.filter(req => req.id !== id)
}

function handleReject(id) {
  console.log(`Rejecting request ${id}`)
  pendingRequests.value = pendingRequests.value.filter(req => req.id !== id)
}

function handleViewDocument(id) {
  console.log(`Viewing document for request ${id}`)
}

function handleProcessingDetails(id) {
  console.log(`Viewing processing details for request ${id}`)
}
</script>

<template>
  <div class="space-y-4">
    <div 
      v-if="filteredRequests.length === 0" 
      class="text-center p-10 text-gray-500"
    >
      <h3 class="text-lg font-medium text-gray-700">No Pending Requests</h3>
      <p class="text-gray-500">
        <span v-if="searchQuery">No requests match your search.</span>
        <span v-else>All pending requests have been processed.</span>
      </p>
    </div>

    <div 
      v-for="(request, index) in filteredRequests" 
      :key="request.id" 
      class="flex items-start p-4 bg-white border border-gray-200 rounded-lg shadow-sm"
      :class="{
        'border-l-4 border-l-[#0957FF]': request.via === 'RFID', 
        'border-l-4 border-l-[#FFB109]': request.via === 'Guest User'
      }"
    >
      <div 
        class="flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-full font-bold text-lg"
        :class="{
          'bg-[#D8E4FF] text-[#083491]': request.via === 'RFID',
          'bg-[#FFF1D2] text-[#B67D03]': request.via === 'Guest User'
        }"
      >
        {{ formatIndex(index) }}
      </div>

      <div class="flex-grow grid grid-cols-1 md:grid-cols-3 gap-x-6 gap-y-2 ml-4">
        <div class="text-sm">
          <label class="block text-xs text-gray-500">Document Type</label>
          <span class="font-semibold text-gray-800">{{ request.documentType }}</span>
          <label class="block text-xs text-gray-500 mt-2">Request from</label>
          <span class="font-bold text-gray-700">{{ request.borrowerName }}</span>
        </div>

        <div class="text-sm">
          <label class="block text-xs text-gray-500">Requested on</label>
          <span class="font-bold text-gray-700">{{ request.date }}</span>
          <label class="block text-xs text-gray-500 mt-2">Requested via</label>
          <div>
            <span 
              class="font-bold" 
              :class="{
                'text-[#B67D03]': request.via === 'Guest User', 
                'text-[#0957FF]': request.via === 'RFID'
              }"
            >
              {{ request.via }}
            </span>
            <span 
              v-if="request.via === 'RFID'" 
              class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-[#0957FF] text-white"
            >
              {{ request.viaTag }}
            </span>
          </div>
        </div>

        <div class="text-sm">
          <label class="block text-xs text-gray-500">Amount</label>
          <span class="font-semibold text-[#159E03]">{{ formatCurrency(request.amount) }}</span>
          
          <div class="mt-2.5">
            <!-- ✅ “Unpaid” / “Paid” are clickable buttons -->
            <button
              @click="togglePaymentStatus(request)"
              :class="[ 
                'px-3 py-1 rounded text-white text-sm font-semibold', 
                request.paymentStatus === 'Paid' 
                  ? 'bg-green-600 hover:bg-green-700' 
                  : 'bg-gray-400 hover:bg-gray-500'
              ]"
            >
              {{ request.paymentStatus }}
            </button>
          </div>
        </div>
      </div>

      <div class="flex-shrink-0 flex flex-col md:flex-row md:items-center gap-2 ml-4">
        <button 
          @click="handleProcessingDetails(request.id)"
          class="px-3 py-1 text-sm text-blue-600 hover:underline"
        >
          Processing Details
        </button>
        <button 
          @click="handleViewDocument(request.id)"
          class="flex items-center justify-center gap-1.5 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md shadow-sm hover:bg-blue-700"
        >
          View Document
        </button>
        <button 
          @click="handleReject(request.id)"
          :disabled="request.paymentStatus !== 'Paid'"
          class="px-3 py-2 text-sm font-medium bg-white border rounded-md text-[#DC0000] border-[#DC0000] hover:bg-red-50"
          :class="{ 'opacity-50 cursor-not-allowed': request.paymentStatus !== 'Paid' }"
        >
          Reject
        </button>
        <button 
          @click="handleApprove(request.id)"
          :disabled="request.paymentStatus !== 'Paid'"
          class="px-3 py-2 text-sm font-medium bg-white border rounded-md text-[#119500] border-[#119500] hover:bg-green-50"
          :class="{ 'opacity-50 cursor-not-allowed': request.paymentStatus !== 'Paid' }"
        >
          Approve
        </button>
      </div>
    </div>
  </div>
</template>