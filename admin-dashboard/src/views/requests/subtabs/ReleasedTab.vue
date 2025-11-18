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
const releasedRequests = ref([])
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

// ✅ formatRequestDate helper for consistency
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
        id: req.id,
        documentType: req.document_type || 'Unknown Document',
        borrowerName: req.form_data?.borrowerName || 'N/A',
        date: formatRequestDate(req.created_at),
        releasedDate: formatRequestDate(req.updated_at), // Use updated_at as released date
        via: req.form_data?.via || 'Guest User',
        viaTag: req.form_data?.viaTag || null,
        amount: req.price || 0,
        paymentStatus: req.payment_status || 'Unpaid'
      }))
  } catch (error) {
    console.error('Error fetching released requests:', error)
    errorMessage.value = 'Failed to load released requests.'
  } finally {
    isLoading.value = false
  }
}

// --- FRONT-END ACTIONS ---
const handleSendSms = (id) => {
  console.log(`Sending SMS for released request ${id}`)
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
  console.log(`Viewing processing details for released request ${id}`)
}

// --- COMPUTED: Search Filter ---
const filteredRequests = computed(() => {
  if (!props.searchQuery) return releasedRequests.value

  const lowerQuery = props.searchQuery.toLowerCase().trim()
  return releasedRequests.value.filter(req => {
    const nameMatch = req.borrowerName.toLowerCase().includes(lowerQuery)
    const docTypeMatch = req.documentType.toLowerCase().includes(lowerQuery)
    const dateMatch = req.date.toLowerCase().includes(lowerQuery)
    const releasedDateMatch = req.releasedDate.toLowerCase().includes(lowerQuery)
    const viaMatch = req.via.toLowerCase().includes(lowerQuery)
    const amountMatch = req.amount.toString().includes(lowerQuery)
    const viaTagMatch = req.viaTag ? req.viaTag.toLowerCase().includes(lowerQuery) : false

    return nameMatch || docTypeMatch || dateMatch || releasedDateMatch || viaMatch || amountMatch || viaTagMatch
  })
})

// --- Load requests on mount ---
onMounted(fetchReleasedRequests)
</script>

<template>
  <div class="space-y-4">
    
    <div 
      v-if="filteredRequests.length === 0" 
      class="text-center p-10 text-gray-500"
    >
      <h3 class="text-lg font-medium text-gray-700">No Released Requests</h3>
      <p class="text-gray-500">
        <span v-if="searchQuery">No requests match your search.</span>
        <span v-else>No documents have been released yet.</span>
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
          
          <label class="block text-xs text-gray-500 mt-2">Released on</label>
          <span class="font-bold text-gray-700">{{ request.releasedDate }}</span>
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
          View Document
        </button>
        
        <button 
          @click="handleSendSms(request.id)"
          class="flex items-center justify-center gap-1.5 px-3 py-2 text-sm font-medium text-white rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 bg-[#00CA39] hover:bg-green-700 focus:ring-[#00CA39]"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.195H6.75A2.25 2.25 0 0 1 4.5 16.83V7.5a2.25 2.25 0 0 1 2.25-2.25h10.5c.884 0 1.672.478 2.042 1.22zM9 12h6M9 14.25h6" />
          </svg>
          Send SMS
        </button>
      </div>
    </div>
  </div>
</template>