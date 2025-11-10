<script setup>
import { ref, computed } from 'vue';

// --- PROPS ---
const props = defineProps({
  searchQuery: {
    type: String,
    default: ''
  }
});

// --- FRONT-END MOCK DATA ---
const rejectedRequests = ref([
  {
    id: 10, 
    documentType: 'Barangay Clearance',
    borrowerName: 'Christian April Kim Revilla Villanueva',
    date: 'September 30, 2024',
    via: 'RFID',
    viaTag: '1234567890',
    amount: 350.00,
    // reason: 'Incomplete requirements' // REMOVED
  },
  {
    id: 11,
    documentType: 'Business Permit',
    borrowerName: 'Angela Dela Cruz',
    date: 'September 30, 2024',
    via: 'Guest User',
    viaTag: null,
    amount: 500.00,
    // reason: 'Duplicate request' // REMOVED
  },
]);

// --- COMPUTED PROPERTY for filtering the list ---
const filteredRequests = computed(() => {
  if (!props.searchQuery) {
    return rejectedRequests.value;
  }
  
  const lowerQuery = props.searchQuery.toLowerCase().trim();
  if (lowerQuery === '') {
    return rejectedRequests.value;
  }

  return rejectedRequests.value.filter(req => {
    const nameMatch = req.borrowerName.toLowerCase().includes(lowerQuery);
    const docTypeMatch = req.documentType.toLowerCase().includes(lowerQuery);
    const dateMatch = req.date.toLowerCase().includes(lowerQuery);
    const viaMatch = req.via.toLowerCase().includes(lowerQuery);
    const amountMatch = req.amount.toString().includes(lowerQuery);
    const viaTagMatch = req.viaTag ? req.viaTag.toLowerCase().includes(lowerQuery) : false;
    // const reasonMatch = req.reason.toLowerCase().includes(lowerQuery); // REMOVED

    return nameMatch || 
           docTypeMatch || 
           dateMatch || 
           viaMatch || 
           amountMatch || 
           viaTagMatch;
           // reasonMatch; // REMOVED
  });
});

// --- FRONT-END ACTIONS ---
function handleReview(id) {
  console.log(`Reviewing rejected request ${id}`);
}

function handleDownloadDocument(id) {
  console.log(`Downloading document for request ${id}`);
}

function handleProcessingDetails(id) {
  console.log(`Viewing processing details for request ${id}`);
}

// Helper to format the number (01, 02, etc.)
const formatIndex = (index) => (index + 1).toString().padStart(2, '0');

// Helper to format currency
const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-PH', {
    style: 'currency',
    currency: 'PHP',
  }).format(value);
};
</script>

<template>
  <div class="p-4">
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
            @click="handleDownloadDocument(request.id)"
            class="flex items-center justify-center gap-1.5 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
            </svg>
            Download Document
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

  </div>
</template>