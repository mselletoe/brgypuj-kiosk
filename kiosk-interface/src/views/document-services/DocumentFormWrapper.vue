<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DocumentForm from './DocumentForm.vue'

const route = useRoute()
const router = useRouter()

const currentStep = ref('form') // 'form' or 'preview'
const formData = ref({})
const showSuccessModal = ref(false)

const docType = computed(() => route.params.docType)

// Document configurations
const documentConfigs = {
  'barangay-certificate': {
    title: 'Barangay Certificate',
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
  'certificate-indigency': {
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
    
    // TODO: Replace with actual API call
    // await submitDocumentRequest(docType.value, formData.value)
    
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
  <div>
    <!-- Back button -->
    <button
      @click="goBack"
      class="mb-4 px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 flex items-center gap-2"
    >
      <span>←</span>
      <span>{{ currentStep === 'preview' ? 'Edit Information' : 'Back to List' }}</span>
    </button>

    <!-- Page title -->
    <h1 class="text-3xl font-bold mb-6">{{ config?.title || 'Document Request' }}</h1>

    <!-- Form Step -->
    <DocumentForm
      v-if="currentStep === 'form' && config"
      :config="config"
      :initial-data="formData"
      @continue="goToPreview"
    />

    <!-- Not found -->
    <div v-else class="text-center py-12">
      <p class="text-gray-600 text-lg">Document type not found</p>
      <button 
        @click="router.push('/document-services')"
        class="mt-4 px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
      >
        Back to Documents
      </button>
    </div>
  </div>
</template>