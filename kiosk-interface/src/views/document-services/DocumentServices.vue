<script setup>
/**
 * @file DocumentServices.vue
 * @description Kiosk Document Services Selection View.
 * This component serves as the primary gateway for residents to browse 
 * available barangay documents. It fetches dynamic document types from 
 * the backend and handles conditional routing between the service list 
 * and specific application forms.
 */
import { useRoute, useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import { getDocumentTypes } from '@/api/documentService'
import { useRealtimeSync } from '@/composables/useRealtimeSync'

const route = useRoute()
const router = useRouter()

/**
 * Navigates back to the main Kiosk Home.
 */
const goBack = () => router.push('/home')

/**
 * Determines if the user is on the main selection page or a child form route.
 * @returns {boolean} True if no specific document type is selected.
 */
const isParent = () => !route.params.docType

// --- Data Management ---
const documents = ref([])
const loading = ref(false)
const error = ref(null)

/**
 * Fetches available document templates from the API.
 * Maps backend 'doctype_name' to the UI's 'request_type_name' for consistency.
 */
const fetchDocuments = async () => {
  loading.value = true
  error.value = null

  try {
    const data = await getDocumentTypes()
    documents.value = data.map(doc => ({
      request_type_name: doc.doctype_name,
      description: doc.description,
      price: doc.price
    }))
  } catch (err) {
    error.value = 'Failed to load documents'
  } finally {
    loading.value = false
  }
}

// Initialize data on component mount
onMounted(fetchDocuments)

useRealtimeSync({
  doctype_created: () => {
    fetchDocuments()
  },
  doctype_updated: () => {
    fetchDocuments()
  },
  doctype_deleted: (data) => {
    documents.value = documents.value.filter(
      doc => doc.id !== data.id
    )
  }
})
</script>

<template>
  <div class="flex flex-col w-full h-full">
    
    <div v-if="isParent()" class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBack"/>
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
          Document Services
        </h1>
        <p class="text-[#03335C] -mt-2">
          Select and apply for barangay documents. Take note of the requirements for each document type.
        </p>
      </div>
    </div>

    <div v-if="loading" class="flex flex-col justify-center items-center py-20 flex-1">
      <div class="loader-dots mb-4">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>
      <p class="text-[#03335C] text-lg font-semibold">Loading services...</p>
    </div>

    <div v-if="error" class="text-center text-red-500 py-10">{{ error }}</div>

    <div class="flex-1 overflow-y-auto">
      <div v-if="isParent() && !loading && !error" class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
        <router-link
          v-for="doc in documents"
          :key="doc.request_type_name"
          :to="`/document-services/${doc.request_type_name.toLowerCase().replace(/\s+/g, '-')}`"
          class="group flex flex-col p-6 rounded-2xl border border-gray-200 shadow-lg bg-white hover:bg-[#003A6B] hover:text-white transition-all duration-300 ease-in-out"
        >
          <h2 class="text-[30px] text-[#003A6B] font-bold mb-2 group-hover:text-white transition-all duration-300 ease-in-out">
            {{ doc.request_type_name }}
          </h2>
          
          <p class="text-gray-500 group-hover:text-gray-100 text-sm mb-6 transition-all duration-300 ease-in-out">
            {{ doc.description }}
          </p>

          <div class="mt-auto flex justify-between items-center font-semibold text-[#003A6B] group-hover:text-white transition-all duration-300 ease-in-out">
            <span>Fee:</span>
            <span class="text-[#09AA44] group-hover:text-white transition-all">₱{{ doc.price || 0 }}</span>
          </div>
        </router-link>
      </div>
    </div>

    <router-view v-if="!isParent()" />
  </div>
</template>

<style scoped>
/* Loader Dots CSS */
.loader-dots {
  display: flex;
  justify-content: space-around;
  align-items: center;
  width: 60px; 
  height: 15px; 
}

.dot {
  width: 12px; 
  height: 12px;
  background-color: #03335C; 
  border-radius: 50%;
  animation: pulse 1.4s infinite ease-in-out both;
}

.dot:nth-child(1) {
  animation-delay: -0.32s;
}

.dot:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes pulse {
  0%, 80%, 100% { 
    transform: scale(0); 
    opacity: 0.3; 
  }
  40% { 
    transform: scale(1); 
    opacity: 1;
  }
}
</style>