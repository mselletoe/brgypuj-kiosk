<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DocumentForm from './DocumentForm.vue'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue' 
import Modal from '@/components/shared/Modal.vue'
import Loading from '@/components/shared/Loading.vue'
import { useAuthStore } from '@/stores/auth'
import { getDocumentTypes, createDocumentRequest } from '@/api/documentService'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const currentStep = ref('form')
const formData = ref({})
const showSuccessModal = ref(false)
const isFadingOut = ref(false)

const residentData = ref(null)
const isLoadingResidentData = ref(false)
const isSubmitting = ref(false)

const documents = ref({})
const loadingDocuments = ref(true)
const errorDocuments = ref(null)
const transactionNo = ref('')

const currentResidentId = ref(null)

const docTypeSlug = computed(() =>
  route.params.docType?.toLowerCase().replace(/\s+/g, '-')
)
const config = computed(() => documents.value[docTypeSlug.value])

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

const goBack = () => {
  if (currentStep.value === 'preview') {
    currentStep.value = 'form'
  } else {
    router.push('/document-services')
  }
}

const closeModal = () => {
  isFadingOut.value = true
  setTimeout(() => {
    showSuccessModal.value = false
    formData.value = {}
    currentStep.value = 'form'
    isFadingOut.value = false
    router.push('/home')
  }, 500)
}

const handleYes = () => {
  router.push('/document-services')
}

const handleNo = () => {
  closeModal()
}

const handleSubmit = async (data) => {
  if (isSubmitting.value) return
  isSubmitting.value = true

  if (!config.value?.id) {
    alert("Invalid document type.")
    isSubmitting.value = false
    return
  }

  // Resident ID
  const residentId = auth.residentId
  if (!residentId) {
    alert("No resident found. Please log in via RFID or guest mode.")
    isSubmitting.value = false
    return
  }

  try {
    // Construct payload for backend
    const payload = {
      doctype_id: config.value.id,
      form_data: data,
      resident_id: residentId
    }

    // Call backend
    const response = await createDocumentRequest(payload)

    formData.value = data

    // Show modal with transaction number
    showSuccessModal.value = true
    transactionNo.value = response.transaction_no

  } catch (err) {
    console.error(err)
    alert(err?.response?.data?.detail || 'Failed to submit document request.')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(async () => {
  await fetchDocuments()
})
</script>

<template>
  <div class="py-0 p-8">
    <!-- Header -->
    <div class="relative flex items-center mb-10">
      <ArrowBackButton
        @click="goBack" 
        class="absolute top-0 left-0 mt-2 mr-6"
      />

      <div class="flex justify-between items-center w-full ml-20">
        <h1 class="text-[40px] font-extrabold text-[#03335C] leading-tight mt-2">
          {{ config?.title || docTypeSlug?.charAt(0).toUpperCase() + docTypeSlug?.slice(1) }}
        </h1>
        <p class="text-sm text-[#002B5B] text-right leading-tight mt-4 italic">
          Kindly fill up the details needed<br />for the said document
        </p>
      </div>
    </div>

    <!-- Loading indicator -->
    <div v-if="isLoadingResidentData" class="text-center py-8">
      <p class="text-gray-600">Loading your information...</p>
    </div>

    <!-- Form Box -->
    <div v-else class="border-[2px] border-[#00203C] rounded-2xl p-10 shadow-md bg-white">
      <DocumentForm
        v-if="currentStep === 'form' && config?.available"
        :config="config"
        :initial-data="formData"
        :resident-data="residentData"
        :is-rfid-user="false"
        :is-submitting="isSubmitting"
        @continue="handleSubmit"
      />

      <!-- Not found -->
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
          <p class="text-gray-500 text-sm">Please wait a moment</p>
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
          message="Your request has been successfully submitted. You will be notified once it's processed. Transaction No: ${transactionNo}"
          primaryButtonText="Yes"
          secondaryButtonText="No"
          :showPrimaryButton="true"
          :showSecondaryButton="true"
          :showNewRequest="false"
          @primary-click="handleYes"
          @secondary-click="handleNo"
          @done="closeModal"
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
