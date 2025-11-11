<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api/api' // ✅ import API helper

// --- PROPS ---
const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  }
})

// --- REFS ---
const processingRequests = ref([])
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

const formatRequestDate = (isoDate) => {
  if (!isoDate) return "N/A"
  const date = new Date(isoDate)
  return date.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
}

// --- FETCH PROCESSING REQUESTS ---
const fetchProcessingRequests = async () => {
  try {
    const response = await api.get('/requests') // ✅ fetch all requests
    processingRequests.value = response.data
      .filter(req => req.status === 'processing') // ✅ only 'processing'
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
    console.error('Error fetching processing requests:', error)
    errorMessage.value = 'Failed to load processing requests.'
  } finally {
    isLoading.value = false
  }
}

// --- MARK AS READY ---
const handleMarkAsReady = async (id) => {
  try {
    await api.put(`/requests/${id}/status`, { status_name: 'ready' }) // ✅ update backend status
    processingRequests.value = processingRequests.value.filter(req => req.id !== id)
  } catch (error) {
    console.error('Error marking request as ready:', error)
  }
}

// --- REJECT REQUEST ---
const handleReject = async (id) => {
  try {
    await api.put(`/requests/${id}/status`, { status_name: 'rejected' }) // ✅ update backend status
    processingRequests.value = processingRequests.value.filter(req => req.id !== id)
  } catch (error) {
    console.error('Error rejecting request:', error)
  }
}

// --- VIEW / DOWNLOAD / DETAILS ---
const handleDownloadDocument = (id) => {
  console.log(`Downloading document for request ${id}`)
}

const handleProcessingDetails = (id) => {
  console.log(`Viewing processing details for request ${id}`)
}

// --- COMPUTED: Search Filter ---
const filteredRequests = computed(() => {
  if (!props.searchQuery) return processingRequests.value

  const lowerQuery = props.searchQuery.toLowerCase().trim()
  return processingRequests.value.filter(req => {
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
onMounted(fetchProcessingRequests)
</script>

<template>
  <div class="space-y-4">
    
    <div 
      v-if="filteredRequests.length === 0" 
      class="text-center p-10 text-gray-500"
    >
      <h3 class="text-lg font-medium text-gray-700">No Processing Requests</h3>
      <p class="text-gray-500">
        <span v-if="searchQuery">No requests match your search.</span>
        <span v-else>All processing requests have been handled.</span>
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
          @click="handleDownloadDocument(request.id)"
          class="flex items-center justify-center gap-1.5 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Download Document
        </button>
        
        <button 
          @click="handleReject(request.id)"
          class="px-3 py-2 text-sm font-medium bg-white border rounded-md shadow-sm hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 text-[#DC0000] border-[#DC0000] focus:ring-[#DC0000]"
        >
          Reject
        </button>

        <button 
          @click="handleMarkAsReady(request.id)"
          class="px-3 py-2 text-sm font-medium bg-white border rounded-md shadow-sm hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-offset-2 text-[#119500] border-[#119500] focus:ring-[#119500]"
        >
          Mark as Ready
        </button>
      </div>
    </div>
  </div>
</template>