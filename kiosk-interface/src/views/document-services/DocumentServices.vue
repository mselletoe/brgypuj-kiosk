<script setup>
/**
 * @file DocumentService.vue
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

    <div v-if="loading" class="text-center text-gray-500 py-10">Loading services...</div>
    <div v-if="error" class="text-center text-red-500 py-10">{{ error }}</div>

    <!-- Document type Option box -->
    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div v-if="isParent() && !loading && !error" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <router-link
          v-for="doc in documents"
          :key="doc.request_type_name"
          :to="`/document-services/${doc.request_type_name.toLowerCase().replace(/\s+/g, '-')}`"
          class="group flex flex-col p-6 rounded-2xl border border-gray-300 shadow-md bg-white hover:bg-[#003A6B] hover:text-white transition-all duration-300 ease-in-out"
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