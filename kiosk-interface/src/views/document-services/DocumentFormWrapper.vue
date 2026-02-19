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
import Button from '@/components/shared/Button.vue'
import Loading from '@/components/shared/Loading.vue'
import { useAuthStore } from '@/stores/auth'
import { getDocumentTypes, createDocumentRequest, checkEligibility } from '@/api/documentService'
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
const documentFormRef = ref(null)
const eligibilityResult = ref(null)

const submitFromWrapper = () => {
  if (documentFormRef.value) {
    documentFormRef.value.handleContinue()
  }
}

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
        requirements: doc.requirements || [],
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
 * Fetches eligibility check results for authenticated residents.
 * Only runs if the document type has system_check requirements.
 */
const fetchEligibility = async () => {
  if (!isRfidUser.value || !config.value?.id) return

  const hasSystemChecks = config.value.requirements?.some(r => r.type === 'system_check')
  if (!hasSystemChecks) return

  try {
    eligibilityResult.value = await checkEligibility(config.value.id, auth.residentId)
  } catch (err) {
    console.error('Failed to fetch eligibility:', err)
    eligibilityResult.value = null
  }
}

/**
 * Merges static requirements with live eligibility check results.
 * Document-type requirements show as informational.
 * System checks show their pass/fail status if available.
 */
const mergedRequirements = computed(() => {
  const reqs = config.value?.requirements || []
  if (!eligibilityResult.value) {
    return reqs.map(r => ({ ...r, passed: null, message: null }))
  }

  const checksMap = {}
  for (const check of eligibilityResult.value.checks) {
    checksMap[check.id] = check
  }

  return reqs.map(r => {
    const live = checksMap[r.id]
    return {
      ...r,
      passed: live?.passed ?? null,
      message: live?.message ?? null
    }
  })
})

/**
 * True if any system_check requirement has explicitly failed.
 * Used to visually warn the resident before they submit.
 */
const hasBlockingFailure = computed(() => {
  return mergedRequirements.value.some(r => r.type === 'system_check' && r.passed === false)
})

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
  await fetchEligibility()
})
</script>

<template>
  <div class="flex flex-col w-full h-full">

    <!-- Header -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton @click="goBack" />
      <div>
        <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
          {{ config?.title || docTypeSlug?.charAt(0).toUpperCase() + docTypeSlug?.slice(1) }}
        </h1>
        <p class="text-[#03335C] -mt-2">
          Kindly fill up the details needed for the said document
        </p>
      </div>
    </div>

    <!-- SCROLLABLE CONTENT AREA -->
    <div class="flex-1 overflow-y-auto custom-scrollbar">

      <div class="grid grid-cols-5 gap-8 items-stretch mb-4">

        <!-- LEFT PANEL -->
        <div class="col-span-3">
          <div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 min-h-[400px]">

            <div v-if="isLoadingResidentData" class="text-center py-8">
              <Loading color="#03335C" size="12px" spacing="50px" />
              <p class="text-gray-600 mt-4">Loading your information...</p>
            </div>

            <DocumentForm
              ref="documentFormRef"
              v-else-if="config?.available"
              :config="config"
              :initial-data="formData"
              :resident-data="residentData"
              :is-rfid-user="isRfidUser"
              :is-submitting="isSubmitting"
              @continue="handleSubmit"
            />

            <div v-else class="text-center py-12">
              <p class="text-[#003A6B] text-lg">
                The type of document you are requesting <br />
                is currently unavailable.
              </p>
            </div>

          </div>
        </div>

        <!-- RIGHT PANEL (EMPTY) -->
        <div class="col-span-2">
          <div class="bg-[#EBF5FF] rounded-2xl shadow-lg border border-[#B0D7F8] p-6 min-h-[280px]">

            <h2 class="text-base font-bold text-[#03335C] mb-4 tracking-tight">
              Requirements
            </h2>

            <!-- No requirements -->
            <div
              v-if="!config?.requirements?.length"
              class="flex flex-col items-center justify-center py-10 text-center"
            >
              <p class="text-sm text-[#5A8DB8]">No requirements needed for this document.</p>
            </div>

            <!-- Requirements list -->
            <div v-else class="space-y-3">

              <!-- Blocking failure warning (authenticated users only) -->
              <div
                v-if="hasBlockingFailure"
                class="bg-red-50 border border-red-200 rounded-xl p-3 flex items-start gap-2"
              >
                <svg class="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                <p class="text-xs text-red-700 font-medium">
                  You may not be eligible for this document. Review the failed requirements below.
                </p>
              </div>

              <!-- Each requirement row -->
              <div
                v-for="(req, index) in mergedRequirements"
                :key="index"
                class="flex items-start gap-3 bg-white rounded-xl p-3 border"
                :class="{
                  'border-red-300 bg-red-50': req.passed === false,
                  'border-green-300 bg-green-50': req.passed === true,
                  'border-[#B0D7F8]': req.passed === null
                }"
              >
                <!-- Status icon -->
                <div class="flex-shrink-0 mt-0.5">
                  <!-- Failed -->
                  <svg v-if="req.passed === false" class="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                  </svg>
                  <!-- Passed -->
                  <svg v-else-if="req.passed === true" class="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                  </svg>
                  <!-- Neutral / document type -->
                  <svg v-else class="w-5 h-5 text-[#5A8DB8]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>

                <!-- Text -->
                <div class="flex-1 min-w-0">
                  <p
                    class="text-sm font-semibold leading-tight"
                    :class="{
                      'text-red-700': req.passed === false,
                      'text-green-700': req.passed === true,
                      'text-[#03335C]': req.passed === null
                    }"
                  >
                    {{ req.label }}
                  </p>

                  <!-- Type badge -->
                  <span
                    class="inline-block text-[10px] font-semibold px-1.5 py-0.5 rounded-full mt-1"
                    :class="req.type === 'system_check' ? 'bg-blue-100 text-blue-600' : 'bg-amber-100 text-amber-600'"
                  >
                    {{ req.type === 'system_check' ? 'System Check' : 'Document' }}
                  </span>

                  <!-- Message (only shown when eligibility data is available) -->
                  <p
                    v-if="req.message"
                    class="text-xs mt-1"
                    :class="{
                      'text-red-600': req.passed === false,
                      'text-green-600': req.passed === true,
                      'text-[#5A8DB8]': req.passed === null
                    }"
                  >
                    {{ req.message }}
                  </p>
                </div>

              </div>

              <!-- Guest mode note: system checks can't be verified -->
              <p
                v-if="!isRfidUser && config?.requirements?.some(r => r.type === 'system_check')"
                class="text-xs text-[#5A8DB8] italic pt-1"
              >
                Scan your RFID card to verify system requirements automatically.
              </p>

            </div>
          </div>
        </div>

      </div>

    </div>

    <!-- FIXED BUTTONS (IDENTICAL STRUCTURE TO BORROWING PAGE) -->
    <div class="flex gap-6 mt-6 justify-between items-center flex-shrink-0">

      <Button
        @click="goBack"
        variant="outline"
        size="md"
      >
        Cancel
      </Button>

      <Button
        @click="submitFromWrapper"
        :disabled="isSubmitting"
        :variant="isSubmitting ? 'disabled' : 'secondary'"
        size="md"
      >
        {{ isSubmitting ? 'Submitting...' : 'Submit Request' }}
      </Button>

    </div>

    <!-- Loading Overlay -->
    <transition name="fade-blur">
      <div
        v-if="isSubmitting"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
      >
        <div class="bg-white rounded-2xl p-10 shadow-2xl flex flex-col items-center gap-2 min-w-[400px]">
          <Loading color="#03335C" size="14px" spacing="70px" />
          <p class="text-[#03335C] text-lg font-semibold mt-6">
            Submitting your request...
          </p>
          <p class="text-gray-500 text-sm">
            Please wait while we generate your document
          </p>
        </div>
      </div>
    </transition>

    <!-- Success Modal -->
    <transition name="fade-blur">
      <div
        v-if="showSuccessModal"
        class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50"
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