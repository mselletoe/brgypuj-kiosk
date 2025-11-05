<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DocumentForm from './DocumentForm.vue'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue' 
import Modal from '@/components/shared/Modal.vue'
import { fetchRequestTypes } from '@/api/requestTypes'

const route = useRoute()
const router = useRouter()

const currentStep = ref('form')
const formData = ref({})
const showSuccessModal = ref(false)
const isFadingOut = ref(false) 
const docType = computed(() => route.params.docType)


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
        title: type.request_type_name,
        fields: type.fields || []
      }
    })
  } catch (err) {
    console.error('Failed to fetch request type configs', err)
  }
}

onMounted(fetchConfigs)

// ==================================
// Computer for current config
// ==================================
const config = computed(() => documentConfigs.value[docType.value])


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
    formData.value = data
    console.log('Submitting:', { docType: docType.value, data })
    showSuccessModal.value = true
  } catch (err) {
    console.error('Submission failed', err)
    alert('Failed to submit request.')
  }
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
