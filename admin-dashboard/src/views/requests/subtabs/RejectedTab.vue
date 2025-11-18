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
const rejectedRequests = ref([])
const isLoading = ref(true)
const errorMessage = ref(null)

// --- HELPERS ---
const formatIndex = (index) => (index + 1).toString().padStart(2, '0')

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
  }).format(value)
}

// ✅ Same formatRequestDate helper
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

// --- FETCH REJECTED REQUESTS ---
const fetchRejectedRequests = async () => {
  try {
    const response = await api.get('/requests')
    rejectedRequests.value = response.data
      .filter(req => req.status === 'rejected')
      .map(req => ({
        id: req.id,
        documentType: req.document_type || 'Unknown Document',
        borrowerName: req.form_data?.borrowerName || 'N/A',
        date: formatRequestDate(req.created_at),
        via: req.form_data?.via || 'Guest User',
        viaTag: req.form_data?.viaTag || null,
        amount: req.price || 0,
        paymentStatus: req.payment_status || 'Unpaid'
      }))
  } catch (error) {
    console.error('Error fetching rejected requests:', error)
    errorMessage.value = 'Failed to load rejected requests.'
  } finally {
    isLoading.value = false
  }
}

// --- FRONT-END ACTIONS ---
const handleReview = async (id) => {
  try {
    await api.put(`/requests/${id}/status`, { status_name: 'pending' })

    rejectedRequests.value = rejectedRequests.value.filter(req => req.id !== id)
    console.log(`Request ${id} moved back to pending`)
  } catch (error) {
    console.error('Error moving request back to pending:', error)
    errorMessage.value = 'Failed to move request back to pending.'
  }
}

const handleViewDocument = async (id) => {
  try {
    // Open PDF in new browser tab using blob URL for better preview
    const response = await api.get(`/requests/${id}/download-pdf`, {
      responseType: 'blob'
    })
    
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = URL.createObjectURL(blob)
    window.open(url, '_blank')
    
    // Clean up blob URL after a delay
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch (error) {
    console.error('Error opening PDF:', error)
    alert('Failed to load document. Please try again.')
  }
}

const handleProcessingDetails = (id) => {
  console.log(`Viewing processing details for request ${id}`)
}

// --- COMPUTED: Search Filter ---
const filteredRequests = computed(() => {
  if (!props.searchQuery) return rejectedRequests.value

  const lowerQuery = props.searchQuery.toLowerCase().trim()
  return rejectedRequests.value.filter(req => {
    const nameMatch = req.borrowerName.toLowerCase().includes(lowerQuery)
    const docTypeMatch = req.documentType.toLowerCase().includes(lowerQuery)
    const dateMatch = req.date.toLowerCase().includes(lowerQuery)
    const viaMatch = req.via.toLowerCase().includes(lowerQuery)
    const amountMatch = req.amount.toString().includes(lowerQuery)
    const viaTagMatch = req.viaTag ? req.viaTag.toLowerCase().includes(lowerQuery) : false
    return nameMatch || docTypeMatch || dateMatch || viaMatch || amountMatch || viaTagMatch
  })
})

// --- Load requests on mount ---
onMounted(fetchRejectedRequests)
</script>

<template>
  <div class="space-y-4">
    
    <div 
      v-if="filteredRequests.length === 0" 
      class="text-center p-10 text-gray-500"
    >
      <h3 class="text-lg font-medium text-gray-700">No Rejected Requests</h3>
      <p class="text-gray-500">
        <span v-if="searchQuery">No requests match your search.</span>
        <span v-else>There are no rejected requests.</span>
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
              class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full"
              :class="{
                'bg-[#0957FF] text-[#FFFFFF]': request.via === 'RFID'
              }"
            >
              {{ request.viaTag }}
            </span>
          </div>
        </div>

        <div class="text-sm">
          <label class="block text-xs text-gray-500">Amount</label>
          <span class="font-semibold text-[#159E03]">{{ formatCurrency(request.amount) }}</span>
          
          <div class="mt-2.5">
            <span class="px-2.5 py-1 text-xs font-semibold rounded-md invisible">
              Unpaid
            </span>
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
          class="flex items-center justify-center gap-1.5 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
          </svg>
          View Document
        </button>

        <button 
          @click="handleReview(request.id)"
          class="px-3 py-2 text-sm font-medium bg-white border rounded-md shadow-sm hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-offset-2 text-[#119500] border-[#129B00] focus:ring-[#129B00]"
        >
          Review
        </button>
      </div>
    </div>
  </div>
</template>