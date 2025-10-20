<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DocumentForm from './DocumentForm.vue'

const route = useRoute()
const router = useRouter()

const currentStep = ref('form')
const formData = ref({})
const showSuccessModal = ref(false)
const docType = computed(() => route.params.docType)

// Document configurations (same as your original)
const documentConfigs = {
  'barangay-clearance': {
    title: 'Barangay Clearance',
    fields: [
      { name: 'fullName', label: 'Full Name', type: 'text', required: true, placeholder: 'Juan Dela Cruz' },
      { name: 'address', label: 'Complete Address', type: 'textarea', required: true, placeholder: 'Street, Barangay, City' },
      { name: 'birthDate', label: 'Date of Birth', type: 'date', required: true },
      { name: 'civilStatus', label: 'Civil Status', type: 'select', required: true, options: ['Single', 'Married', 'Widowed', 'Separated'] },
      { name: 'contactNumber', label: 'Contact Number', type: 'tel', required: true, placeholder: '09123456789' },
      { name: 'purpose', label: 'Purpose', type: 'textarea', required: true, placeholder: 'State the purpose of this certificate' },
    ]
  },
  'barangay-id': {
    title: 'Barangay ID',
    fields: [
      { name: 'fullName', label: 'Full Name', type: 'text', required: true, placeholder: 'Juan Dela Cruz' },
      { name: 'address', label: 'Complete Address', type: 'textarea', required: true, placeholder: 'Street, Barangay, City' },
      { name: 'birthDate', label: 'Date of Birth', type: 'date', required: true },
      { name: 'birthPlace', label: 'Place of Birth', type: 'text', required: true, placeholder: 'City, Province' },
      { name: 'gender', label: 'Gender', type: 'select', required: true, options: ['Male', 'Female'] },
      { name: 'civilStatus', label: 'Civil Status', type: 'select', required: true, options: ['Single', 'Married', 'Widowed', 'Separated'] },
      { name: 'contactNumber', label: 'Contact Number', type: 'tel', required: true, placeholder: '09123456789' },
      { name: 'emergencyContact', label: 'Emergency Contact Name', type: 'text', required: true, placeholder: 'Full Name' },
      { name: 'emergencyNumber', label: 'Emergency Contact Number', type: 'tel', required: true, placeholder: '09123456789' },
    ]
  },
  'cedula': {
    title: 'Cedula (Community Tax Certificate)',
    fields: [
      { name: 'fullName', label: 'Full Name', type: 'text', required: true, placeholder: 'Juan Dela Cruz' },
      { name: 'address', label: 'Complete Address', type: 'textarea', required: true, placeholder: 'Street, Barangay, City' },
      { name: 'birthDate', label: 'Date of Birth', type: 'date', required: true },
      { name: 'civilStatus', label: 'Civil Status', type: 'select', required: true, options: ['Single', 'Married', 'Widowed', 'Separated'] },
      { name: 'citizenship', label: 'Citizenship', type: 'text', required: true, placeholder: 'Filipino' },
      { name: 'tin', label: 'TIN (if available)', type: 'text', required: false, placeholder: '000-000-000-000' },
      { name: 'occupation', label: 'Occupation', type: 'text', required: true, placeholder: 'Employee, Self-employed, etc.' },
      { name: 'employer', label: 'Employer/Business', type: 'text', required: false, placeholder: 'Company/Business Name' },
      { name: 'salary', label: 'Salary/Income Range', type: 'select', required: true, options: ['Below ₱5,000', '₱5,000 - ₱10,000', '₱10,000 - ₱20,000', '₱20,000 - ₱50,000', 'Above ₱50,000'] },
      { name: 'height', label: 'Height (cm)', type: 'number', required: true, placeholder: '170' },
      { name: 'weight', label: 'Weight (kg)', type: 'number', required: true, placeholder: '65' },
    ]
  },
  'indigency': {
    title: 'Certificate of Indigency',
    fields: [
      { name: 'fullName', label: 'Full Name', type: 'text', required: true, placeholder: 'Juan Dela Cruz' },
      { name: 'address', label: 'Complete Address', type: 'textarea', required: true, placeholder: 'Street, Barangay, City' },
      { name: 'birthDate', label: 'Date of Birth', type: 'date', required: true },
      { name: 'civilStatus', label: 'Civil Status', type: 'select', required: true, options: ['Single', 'Married', 'Widowed', 'Separated'] },
      { name: 'occupation', label: 'Occupation', type: 'text', required: true, placeholder: 'Unemployed, Laborer, etc.' },
      { name: 'monthlyIncome', label: 'Monthly Income', type: 'number', required: true, placeholder: '0' },
      { name: 'familyMembers', label: 'Number of Family Members', type: 'number', required: true, placeholder: '4' },
      { name: 'purpose', label: 'Purpose', type: 'textarea', required: true, placeholder: 'Medical assistance, financial aid, etc.' },
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
  showSuccessModal.value = false
  formData.value = {}
  currentStep.value = 'form'
  router.push('/document-services')
}
</script>

<template>
  <div class="p-8 max-w-5xl mx-auto font-poppins">
    <!-- Header -->
    <div class="flex items-center mb-6">
      <!-- Back Button (Top Left like in your image) -->
      <button 
        @click="goBack"
        class="flex items-center justify-center w-14 h-14 border border-[#002B5B] rounded-2xl hover:bg-[#002B5B] group transition"
      >
        <svg xmlns="http://www.w3.org/2000/svg" 
             fill="none" 
             viewBox="0 0 24 24" 
             stroke-width="2" 
             stroke="currentColor"
             class="w-6 h-6 text-[#002B5B] group-hover:text-white transition">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <!-- Title and Subtext -->
      <div class="flex justify-between items-center w-full ml-6">
        <h1 class="text-[40px] font-extrabold text-[#002B5B] leading-none">{{ config?.title || 'Document Request' }}</h1>
        <p class="text-sm text-gray-600 text-right leading-tight">
          Kindly fill up the details needed<br />for the said document
        </p>
      </div>
    </div>

    <!-- Form Box -->
    <div class="border border-[#002B5B]/40 rounded-2xl p-10 shadow-md bg-white">
      <DocumentForm
        v-if="currentStep === 'form' && config"
        :config="config"
        :initial-data="formData"
        @continue="handleSubmit"
      />

      <!-- Not found -->
      <div v-else class="text-center py-12">
        <p class="text-gray-600 text-lg">Document type not found</p>
        <button 
          @click="router.push('/document-services')"
          class="mt-4 px-6 py-2 bg-[#002B5B] text-white rounded hover:bg-[#001F40]"
        >
          Back to Documents
        </button>
      </div>

      <!-- Buttons (Next only) -->
      <div class="flex justify-end mt-8">
        <button 
          @click="handleSubmit" 
          class="px-8 py-3 bg-[#002B5B] text-white font-semibold rounded-full hover:bg-[#001F40] transition"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.font-poppins {
  font-family: 'Poppins', sans-serif;
}
</style>
