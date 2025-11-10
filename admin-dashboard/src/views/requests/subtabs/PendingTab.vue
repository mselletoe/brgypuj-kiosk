<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api/api'

// --- PROPS ---
const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  }
});

// --- REFS ---
const pendingRequests = ref([])
const isLoading = ref(true)
const errorMessage = ref(null)

// --- FETCH PENDING REQUESTS ---
const fetchPendingRequests = async () => {
  try {
    const response = await api.get('/requests') // using centralized API
    pendingRequests.value = response.data
      .filter(req => req.status === 'pending')
      .map(req => ({
        id: req.id,
        documentType: req.document_type || 'Unknown Document',
        borrowerName: req.form_data?.borrowerName || 'N/A',
        date: req.form_data?.date || new Date(req.created_at).toLocaleDateString('en-PH'),
        via: req.form_data?.via || 'Guest User',
        viaTag: req.form_data?.viaTag || null,
        amount: req.price || 0,   // <-- use request type price here
        paymentStatus: req.form_data?.paymentStatus || 'Unpaid',
      }))
  } catch (error) {
    console.error('Error fetching requests:', error)
    errorMessage.value = 'Failed to load pending requests.'
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchPendingRequests)

// --- COMPUTED: Filtered by search ---
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

// --- HELPERS ---
const formatIndex = (index) => (index + 1).toString().padStart(2, '0')

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP'
  }).format(value)
}
</script>

<template>
  <div class="space-y-4">
    <!-- Empty State -->
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

    <!-- Request Item Card -->
    <div 
      v-for="(request, index) in filteredRequests" 
      :key="request.id" 
      class="flex items-start p-4 bg-white border border-gray-200 rounded-lg shadow-sm"
      :class="{
        'border-l-4 border-l-[#0957FF]': request.via === 'RFID', 
        'border-l-4 border-l-[#FFB109]': request.via === 'Guest User'
      }"
    >
      <!-- 1. Number -->
      <div 
        class="flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-full font-bold text-lg"
        :class="{
          'bg-[#D8E4FF] text-[#083491]': request.via === 'RFID',
          'bg-[#FFF1D2] text-[#B67D03]': request.via === 'Guest User'
        }"
      >
        {{ formatIndex(index) }}
      </div>

      <!-- 2. Request Details (Grid) -->
      <div class="flex-grow grid grid-cols-1 md:grid-cols-3 gap-x-6 gap-y-2 ml-4">
        
        <!-- Col 1 -->
        <div class="text-sm">
          <label class="block text-xs text-gray-500">Document Type</label>
          <span class="font-semibold text-gray-800">{{ request.documentType }}</span>
          
          <label class="block text-xs text-gray-500 mt-2">Request from</label>
          <span class="font-bold text-gray-700">{{ request.borrowerName }}</span>
        </div>

        <!-- Col 2 -->
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

        <!-- Col 3 -->
        <div class="text-sm">
          <label class="block text-xs text-gray-500">Amount</label>
          <span class="font-semibold text-[#159E03]">{{ formatCurrency(request.amount) }}</span>
          
          <div class="mt-2.5">
            <span 
              class="px-2.5 py-1 text-xs font-semibold rounded-md"
              :class="{
                'bg-[#BAF9B2] text-[#216917]': request.paymentStatus === 'Paid',
                'bg-[#E0E0E0] text-[#5D5D5D]': request.paymentStatus !== 'Paid'
              }"
            >
              {{ request.paymentStatus === 'Paid' ? 'Paid' : 'Unpaid' }}
            </span>
          </div>
        </div>
      </div>

      <!-- 3. Action Buttons -->
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
            <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
          </svg>
          View Document
        </button>
        
        <!-- *** UPDATED REJECT BUTTON COLORS *** -->
        <button 
          @click="handleReject(request.id)"
          :disabled="request.paymentStatus !== 'Paid'"
          class="px-3 py-2 text-sm font-medium bg-white border rounded-md shadow-sm hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 text-[#DC0000] border-[#DC0000] focus:ring-[#DC0000]"
          :class="{ 'opacity-50 cursor-not-allowed': request.paymentStatus !== 'Paid' }"
        >
          Reject
        </button>
        
        <!-- *** UPDATED APPROVE BUTTON COLORS *** -->
        <button 
          @click="handleApprove(request.id)"
          :disabled="request.paymentStatus !== 'Paid'"
          class="px-3 py-2 text-sm font-medium bg-white border rounded-md shadow-sm hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-offset-2 text-[#119500] border-[#119500] focus:ring-[#119500]"
          :class="{ 'opacity-50 cursor-not-allowed': request.paymentStatus !== 'Paid' }"
        >
          Approve
        </button>
      </div>
    </div>
  </div>
</template>