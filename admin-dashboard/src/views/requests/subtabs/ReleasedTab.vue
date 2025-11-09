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
const releasedRequests = ref([
  {
    id: 8, 
    documentType: 'Barangay Clearance',
    borrowerName: 'Christian April Kim Revilla Villanueva',
    date: 'September 30, 2024',
    via: 'RFID',
    viaTag: '1234567890',
    amount: 350.00,
    releasedDate: 'September 31, 2024' // Added new field
  },
  {
    id: 9,
    documentType: 'Business Permit',
    borrowerName: 'Angela Dela Cruz',
    date: 'September 30, 2024',
    via: 'Guest User',
    viaTag: null,
    amount: 500.00,
    releasedDate: 'September 30, 2024' // Added new field
  },
]);

// --- COMPUTED PROPERTY for filtering the list ---
const filteredRequests = computed(() => {
  if (!props.searchQuery) {
    return releasedRequests.value;
  }
  
  const lowerQuery = props.searchQuery.toLowerCase().trim();
  if (lowerQuery === '') {
    return releasedRequests.value;
  }

  return releasedRequests.value.filter(req => {
    const nameMatch = req.borrowerName.toLowerCase().includes(lowerQuery);
    const docTypeMatch = req.documentType.toLowerCase().includes(lowerQuery);
    const dateMatch = req.date.toLowerCase().includes(lowerQuery);
    const viaMatch = req.via.toLowerCase().includes(lowerQuery);
    const amountMatch = req.amount.toString().includes(lowerQuery);
    const viaTagMatch = req.viaTag ? req.viaTag.toLowerCase().includes(lowerQuery) : false;
    const releasedDateMatch = req.releasedDate.toLowerCase().includes(lowerQuery); // Search logic for new field

    return nameMatch || 
           docTypeMatch || 
           dateMatch || 
           viaMatch || 
           amountMatch || 
           viaTagMatch ||
           releasedDateMatch; // Added to return
  });
});

// --- FRONT-END ACTIONS ---
function handleSendSms(id) {
  console.log(`Sending (another) SMS for request ${id}`);
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
            @click="handleDownloadDocument(request.id)"
            class="flex items-center justify-center gap-1.5 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
            </svg>
            Download Document
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

  </div>
</template>