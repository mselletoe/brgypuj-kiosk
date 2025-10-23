<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DocumentForm from './DocumentForm.vue'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue' 
import Modal from '@/components/shared/Modal.vue'

const route = useRoute()
const router = useRouter()

const currentStep = ref('form')
const formData = ref({})
const showSuccessModal = ref(false)
const isFadingOut = ref(false) 
const docType = computed(() => route.params.docType)

// Document configurations
const documentConfigs = {
  'barangay-clearance': {
    title: 'Barangay Clearance',
    fields: [
      { name: 'fullName', label: 'First Name', type: 'text', required: true, placeholder: 'Juan' },
      { name: 'lastName', label: 'Last Name', type: 'text', required: true, placeholder: 'Dela Cruz' },
      { name: 'purpose', label: 'Purpose', type: 'select', required: true, options: ['Financial Assistance', 'Educational Assistance','Others'] },
    ]
  },
  'barangay-id': {
    title: 'Barangay ID',
    fields: [
      { name: 'firstName', label: 'First Name', type: 'text', required: true, placeholder: 'Juan' },
      { name: 'lastName', label: 'Last Name', type: 'text', required: true, placeholder: 'Dela Cruz' },
      { name: 'address', label: 'Complete Address', type: 'textarea', required: true, placeholder: 'Street, Barangay, City' },
      { name: 'birthDate', label: 'Date of Birth', type: 'date', required: true },
      { name: 'gender', label: 'Gender', type: 'select', required: true, options: ['Male', 'Female'] },
      { name: 'civilStatus', label: 'Civil Status', type: 'select', required: true, options: ['Single', 'Married', 'Widowed', 'Separated'] },
      { name: 'contactNumber', label: 'Contact Number', type: 'tel', required: true, placeholder: '09123456789' },
      { name: 'emergencyContact', label: 'Emergency Contact Name', type: 'text', required: true, placeholder: 'Full Name' },
      { name: 'emergencyNumber', label: 'Emergency Contact Number', type: 'tel', required: true, placeholder: '09123456789' },
    ]
  },
  'indigency': {
    title: 'Certificate of Indigency',
    fields: [
      { name: 'fullName', label: 'First Name', type: 'text', required: true, placeholder: 'Juan' },
      { name: 'lastName', label: 'Last Name', type: 'text', required: true, placeholder: 'Dela Cruz' },
      { name: 'assistance', label: 'Type of Assistance', type: 'select', required: true, options: ['Financial Assistance', 'Educational Assistance','Others'] },
    ]
  },
  'business-permit': {
    title: 'Business Permit',
    fields: [
      { name: 'businessName', label: 'Business Name', type: 'text', required: true, placeholder: 'ABC Trading' },
      { name: 'businessAddress', label: 'Business Address', type: 'textarea', required: true, placeholder: 'Street, Barangay, City' },
      { name: 'businessType', label: 'Type of Business', type: 'select', required: true, options: ['Retail', 'Service', 'Food', 'Manufacturing', 'Other'] },
      { name: 'ownerName', label: 'Owner Full Name', type: 'text', required: true, placeholder: 'Juan Dela Cruz' },
      { name: 'ownerAddress', label: 'Owner Address', type: 'textarea', required: true, placeholder: 'Street, Barangay, City' },
      { name: 'tin', label: 'TIN', type: 'text', required: true, placeholder: '000-000-000-000' },
      { name: 'contactNumber', label: 'Contact Number', type: 'tel', required: true, placeholder: '09123456789' },
      { name: 'email', label: 'Email Address', type: 'email', required: false, placeholder: 'email@example.com' },
      { name: 'startDate', label: 'Expected Start Date', type: 'date', required: true },
    ]
  }
}

const config = computed(() => documentConfigs[docType.value])

const goBack = () => {
  if (currentStep.value === 'preview') {
    currentStep.value = 'form'
  } else {
    router.push('/document-services')
  }
}

const handleSubmit = async () => {
  try {
    console.log('Submitting:', { docType: docType.value, data: formData.value })
    showSuccessModal.value = true
  } catch (error) {
    console.error('Submission failed:', error)
    alert('Failed to submit request. Please try again.')
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
  }, 500) // match transition duration
}
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
          {{ config?.title || (docType)?.charAt(0).toUpperCase() + (config?.title || docType)?.slice(1)  }}
        </h1>
        <p class="text-sm text-[#002B5B] text-right leading-tight mt-4 italic">
          Kindly fill up the details needed<br />for the said document
        </p>
      </div>
    </div>

    <!-- Form Box -->
    <div class="border-[2px] border-[#00203C] rounded-2xl p-10 shadow-md bg-white">
      <DocumentForm
        v-if="currentStep === 'form' && config"
        :config="config"
        :initial-data="formData"
        @continue="handleSubmit"
      />

      <!-- Not found -->
      <div v-else class="text-center py-12">
        <p class="text-[#003A6B] text-lg">The type of document you are requesting <br/> is currently out of stock.</p>
        <button 
          @click="router.push('/document-services')"
          class="mt-4 px-6 py-2 bg-[#003A6B] text-white rounded hover:bg-[#001F40]"
        >
          Back to Documents
        </button>
      </div>
    </div>

    <!-- ✅ Success Modal with fade + blur -->
    <transition name="fade-blur">
      <div
        v-if="showSuccessModal"
        class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 transition-opacity duration-500"
        :class="{ 'opacity-0': isFadingOut, 'opacity-100': !isFadingOut }"
      >
        <Modal
          title="Application Submitted!"
          message="Your request has been successfully submitted. You will be notified once it’s processed."
          doneText="Done"
          :showNewRequest="false"
          @done="closeModal"
        />
      </div>
    </transition>
  </div>
</template>

<!-- ✅ Smooth fade and blur transition -->
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
