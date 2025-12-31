<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ref, onMounted } from 'vue'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import SuccessModal from '@/components/shared/Modal.vue'

const route = useRoute()
const router = useRouter() 

// ==========================================
// Modal control
// ==========================================
const showModal = ref(false)
const handleContinue = () => {
  showModal.value = true
}
const handleDone = () => {
  showModal.value = false
  router.push('/home')  
}

// ==========================================
// Go back handler
// ==========================================
const goBack = () => router.push('/home')

// ==========================================
// Checks if no document type selected
// ==========================================
const isParent = () => !route.params.docType

// ==========================================
// Documents type fetched from backend
// ==========================================
const documents = ref([])
const loading = ref(false)
const error = ref(null)

// ==========================================
// Fetch data from backend API
// ==========================================
const fetchDocuments = async () => {
  loading.value = true
  try {
    const data = await fetchRequestTypes()
    documents.value = data.filter(item => item.status === 'active')
  } catch (err) {
    console.error('Error fetching request types:', err)
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchDocuments)
</script>

<template>
  <div>
    <!-------------------- Header -------------------->
    <div  v-if="isParent()" class="relative py-0 p-8 flex items-start gap-4 mb-6">
      <ArrowBackButton 
        @click="goBack"
        class="absolute top-0 left-6 mt-2"/>

      <div class="ml-20">
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
          Document Services
        </h1>
        <p class="text-[#03335C] -mt-2">
          Select and apply for barangay documents
        </p>
      </div>
    </div>

    <!-------------------- Loading / Error States -------------------->
    <div v-if="loading" class="text-center text-gray-500">Loading services...</div>
    <div v-if="error" class="text-center text-red-500">Failed to load: {{ error }}</div>

    <!-------------------- Parent view -------------------->
    <div v-if="isParent() && !loading && !error" class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <router-link
        v-for="doc in documents"
        :key="doc.type"
        :to="`/document-services/${doc.request_type_name.toLowerCase().replace(/\s+/g, '-')}`"
        class="group block p-6 rounded-2xl border border-gray-300 shadow-md bg-white 
               hover:bg-[#003A6B] hover:text-white transition-all duration-300 ease-in-out"
      >
        <h2 class="text-[30px] text-[#003A6B] font-bold mb-2 group-hover:text-white
        transition-all duration-300 ease-in-out">
          {{ doc.request_type_name }}
        </h2>
        <p class="text-gray-500 group-hover:text-gray-100 text-sm mb-4
                  transition-all duration-300 ease-in-out">
          {{ doc.description }}
        </p>

        <!-------------------- Fee row -------------------->
        <div class="flex justify-between items-center font-semibold text-[#003A6B] group-hover:text-white
            transition-all duration-300 ease-in-out">
          <span>Fee:</span>
          <span>₱{{ doc.price || 0 }}</span>
        </div>
      </router-link>
    </div>

    <!-------------------- Child view (the form page) -------------------->
    <router-view v-if="!isParent()" />
  </div>
</template>