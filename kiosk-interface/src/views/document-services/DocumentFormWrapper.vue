<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DocumentForm from './DocumentForm.vue'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue' 
import Modal from '@/components/shared/Modal.vue'
import { fetchRequestTypes } from '@/api/requestTypes'
import { createRequest } from '@/api/requests'
import { fetchResidentData } from '@/api/residents'
import { auth, isRfidUser, getResidentId } from '@/stores/auth'

const route = useRoute()
const router = useRouter()

const currentStep = ref('form')
const formData = ref({})
const showSuccessModal = ref(false)
const isFadingOut = ref(false)

const residentData = ref(null)
const isLoadingResidentData = ref(false)

// Placeholder for resident id (RFID or guest)
const currentResidentId = ref(null)

// ==================================
// Slugified route param
// ==================================
const docTypeSlug = computed(() =>
  route.params.docType?.toLowerCase().replace(/\s+/g, '-')
)

// ==================================
// Fetch dynamic configs
// ==================================
const documentConfigs = ref({})

const fetchConfigs = async () => {
  try {
    const types = await fetchRequestTypes()
    types.forEach(type => {
      const slug = type.request_type_name.toLowerCase().replace(/\s+/g, '-')
      documentConfigs.value[slug] = {
        id: type.id,
        title: type.request_type_name,
        fields: type.fields || [],
        available: type.available ?? true
      }
    })
  } catch (err) {
    console.error('Failed to fetch request type configs', err)
  }
}

// ==================================
// Fetch resident data for RFID users
// ==================================
const loadResidentData = async () => {
  // Only fetch if user is authenticated via RFID
  if (!isRfidUser() || !auth.token) {
    console.log('Guest user or no token - skipping resident data fetch')
    return
  }

  isLoadingResidentData.value = true
  try {
    const data = await fetchResidentData(auth.token)
    residentData.value = data
    console.log('✅ Resident data loaded:', data)
  } catch (err) {
    console.error('Failed to fetch resident data:', err)
    // Don't block the form if data fetch fails
    residentData.value = null
  } finally {
    isLoadingResidentData.value = false
  }
}

// ==================================
// Computed current config
// ==================================
const config = computed(() => documentConfigs.value[docTypeSlug.value])

// ==================================
// Navigation
// ==================================
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

// ==================================
// Form Submission
// ==================================
const handleSubmit = async (data) => {
  try {
    if (!config.value?.id) {
      alert("Invalid document type.")
      return
    }

    formData.value = data

    const payload = {
      request_type_id: config.value.id,
      form_data: data // dynamic fields go here
    }

    await createRequest(payload, auth.token)
    showSuccessModal.value = true

  } catch (err) {
    console.error('Submission failed', err)
    alert('Failed to submit request.')
  }
}

// ==================================
// Initialize on mount
// ==================================
onMounted(async () => {
  await fetchConfigs()
  await loadResidentData()
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

      <!-- Title and Subtext -->
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
        :is-rfid-user="isRfidUser()"
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

    <!-- ✅ Success Modal -->
    <transition name="fade-blur">
      <div
        v-if="showSuccessModal"
        class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 transition-opacity duration-500"
        :class="{ 'opacity-0': isFadingOut, 'opacity-100': !isFadingOut }"
      >
        <Modal
          title="Application Submitted!"
          message="Your request has been successfully submitted. You will be notified once it's processed."
          doneText="Done"
          :showNewRequest="false"
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
