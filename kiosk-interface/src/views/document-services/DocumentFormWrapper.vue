<script setup>
/**
 * @file DocumentFormWrapper.vue
 * @description Orchestrates the document application lifecycle.
 * Manages dynamic form configuration fetching, resident data autofill for RFID users,
 * and handles the multi-step submission process including loading and success states.
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DocumentForm from './DocumentForm.vue'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue' 
import Modal from '@/components/shared/Modal.vue'
import Loading from '@/components/shared/Loading.vue'
import { useAuthStore } from '@/stores/auth'
import { getDocumentTypes, createDocumentRequest } from '@/api/documentService'
import { getResidentAutofillData } from '@/api/residentService'

// --- Composition Utilities ---
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

// --- UI & Navigation State ---
const currentStep = ref('form')
const formData = ref({})
const showSuccessModal = ref(false)
const isFadingOut = ref(false)

// --- Business Logic State ---
const residentData = ref(null)
const isLoadingResidentData = ref(false)
const isSubmitting = ref(false)

// --- Data Fetching State ---
const documents = ref({})
const loadingDocuments = ref(true)
const errorDocuments = ref(null)
const transactionNo = ref('')

/**
 * Normalizes the URL parameter into a slug format for configuration lookup.
 */
const docTypeSlug = computed(() =>
  route.params.docType?.toLowerCase().replace(/\s+/g, '-')
)

/**
 * Retrieves the specific configuration for the currently selected document.
 */
const config = computed(() => documents.value[docTypeSlug.value])

/**
 * Checks if the current session belongs to a resident identified via RFID.
 */
const isRfidUser = computed(() => {
  return auth.isAuthenticated && auth.residentId !== null
})

/**
 * Fetches all document templates and maps them by slug for O(1) access.
 */
const fetchDocuments = async () => {
  loadingDocuments.value = true
  errorDocuments.value = null
  try {
    const data = await getDocumentTypes()
    const mapping = {}
    data.forEach(doc => {
      const slug = doc.doctype_name.toLowerCase().replace(/\s+/g, '-')
      mapping[slug] = {
        id: doc.id,
        title: doc.doctype_name,
        fields: doc.fields || [],
        available: true
      }
    })
    documents.value = mapping
  } catch (err) {
    console.error(err)
    errorDocuments.value = 'Failed to load document fields'
  } finally {
    loadingDocuments.value = false
  }
}

/**
 * Retrieves resident profile data to facilitate the 'Autofill' feature.
 * Occurs only for authenticated RFID users.
 */
const fetchResidentData = async () => {
  if (!isRfidUser.value) {
    residentData.value = null
    return
  }

  isLoadingResidentData.value = true
  try {
    const data = await getResidentAutofillData(auth.residentId)
    residentData.value = data
  } catch (err) {
    console.error('Failed to fetch resident data for autofill:', err)
    // Don't block the form - just proceed without autofill
    residentData.value = null
  } finally {
    isLoadingResidentData.value = false
  }
}

/**
 * Handles backwards navigation between preview/form steps or exits to the list.
 */
const goBack = () => {
  if (currentStep.value === 'preview') {
    currentStep.value = 'form'
  } else {
    router.push('/document-services')
  }
}

const handleDone = () => {
  router.push('/home')
}

/**
 * Submits the finalized form data to the backend.
 * Captures the transaction number for the user's reference upon success.
 * 
 * FIXED: Properly handles async PDF generation without race conditions
 */
const handleSubmit = async (data) => {
  if (isSubmitting.value) return
  isSubmitting.value = true

  if (!config.value?.id) {
    alert("Invalid document type.")
    isSubmitting.value = false
    return
  }

  // Resident ID - can be null for guest mode (RFID requests only)
  const residentId = auth.residentId || null

  try {
    // Construct payload for backend
    const payload = {
      doctype_id: config.value.id,
      form_data: data,
      resident_id: residentId
    }

    // Call backend (this may take time due to PDF generation)
    const response = await createDocumentRequest(payload)

    // Store form data
    formData.value = data
    transactionNo.value = response.transaction_no

    // IMPORTANT: Set isSubmitting to false BEFORE showing modal
    // This ensures the loading overlay is removed first
    isSubmitting.value = false

    // Small delay to ensure loading overlay transition completes
    await new Promise(resolve => setTimeout(resolve, 100))

    // Show success modal
    showSuccessModal.value = true

  } catch (err) {
    console.error('Document submission error:', err)
    
    // Set isSubmitting to false before showing error
    isSubmitting.value = false
    
    // Show user-friendly error message
    const errorMessage = err?.response?.data?.detail || 'Failed to submit document request. Please try again.'
    alert(errorMessage)
  }
}

onMounted(async () => {
  await fetchDocuments()
  await fetchResidentData()
})
</script>

<template>
  <div class="flex flex-col w-full h-full">
    <!-- Header -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBack"/>
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
          {{ config?.title || docTypeSlug?.charAt(0).toUpperCase() + docTypeSlug?.slice(1) }}
        </h1>
        <p class="text-[#03335C] -mt-2">
          Kindly fill up the details needed for the said document
        </p>
      </div>
    </div>

    <div v-if="isLoadingResidentData" class="text-center py-8 flex-shrink-0">
      <Loading color="#03335C" size="12px" spacing="50px" />
      <p class="text-gray-600 mt-4">Loading your information...</p>
    </div>

    <div 
      v-else 
      class="border-[2px] border-[#00203C] h-full rounded-2xl p-10 shadow-md bg-white overflow-y-auto custom-scrollbar"
    >
      <DocumentForm
        v-if="currentStep === 'form' && config?.available"
        :config="config"
        :initial-data="formData"
        :resident-data="residentData"
        :is-rfid-user="isRfidUser"
        :is-submitting="isSubmitting"
        @continue="handleSubmit"
      />

      <div v-else class="text-center py-12">
        <p class="text-[#003A6B] text-lg">The type of document you are requesting <br/> is currently unavailable.</p>
        <button 
          @click="router.push('/document-services')"
          class="mt-4 px-6 py-2 bg-[#003A6B] text-white rounded hover:bg-[#001F40]"
        >
          Back to Documents
        </button>
      </div>
    </div>

    <transition name="fade-blur">
      <div
        v-if="isSubmitting"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      >
        <div class="bg-white rounded-2xl p-10 shadow-2xl flex flex-col items-center gap-2 min-w-[400px]">
          <Loading color="#03335C" size="14px" spacing="70px" />
          <p class="text-[#003A6B] text-lg font-semibold mt-6">Submitting your request...</p>
          <p class="text-gray-500 text-sm">Please wait while we generate your document</p>
        </div>
      </div>
    </transition>

    <transition name="fade-blur">
      <div
        v-if="showSuccessModal"
        class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 transition-opacity duration-500"
        :class="{ 'opacity-0': isFadingOut, 'opacity-100': !isFadingOut }"
      >
        <Modal
          title="Application Submitted!"
          :message="`Pay the fee at the counter and be informed of further details. Please take note of the Request ID number below for reference.`"
          :referenceId="transactionNo"
          :showReferenceId="true"
          primaryButtonText="Done"
          :showPrimaryButton="true"
          :showSecondaryButton="false"
          :showNewRequest="false"
          @primary-click="handleDone"
        />
      </div>
    </transition>
  </div>
</template>

<style scoped>
.fade-blur-enter-active,
.fade-blur-leave-active {
  transition: opacity 0.5s ease-in-out;
}
.fade-blur-enter-from,
.fade-blur-leave-to {
  opacity: 0;
}
</style>