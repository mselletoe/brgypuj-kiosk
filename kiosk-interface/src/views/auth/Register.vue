<script setup>
/**
 * @file Register.vue
 * @description Links a newly scanned RFID card to an approved ID Application resident.
 *
 * Flow:
 *   1. On mount, fetch all approved ID Applications awaiting RFID linking.
 *   2. Admin selects a transaction card (left panel).
 *   3. Right panel shows the resident's Name, Birthdate, and Address.
 *   4. Admin clicks Submit → linkRfidToResident() → success toast → clear state.
 *
 * The pending RFID UID comes from rfidRegStore.pendingRfidUid (set in ScanRFID.vue).
 * Only reachable after passing the admin passcode gate in AuthPIN.vue.
 */

import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { CheckCircleIcon, XCircleIcon } from '@heroicons/vue/24/outline'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import Button from '@/components/shared/Button.vue'
import { useRfidRegistrationStore } from '@/stores/registration'
import { getApprovedApplications, linkRfidToResident } from '@/api/registrationService'

const router = useRouter()
const rfidRegStore = useRfidRegistrationStore()

// ---- State ----
const applications = ref([])
const selectedApp = ref(null)
const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')

// Toast
const showToast = ref(false)
const toastMessage = ref('')
const toastSuccess = ref(false)

// ---- Computed ----
const pendingUid = computed(() => rfidRegStore.pendingRfidUid)

const canSubmit = computed(() =>
  selectedApp.value !== null && pendingUid.value && !isSubmitting.value
)

// ---- Helpers ----

/** Format "YYYY-MM-DD" → "Month DD, YYYY" */
const formatBirthdate = (dateStr) => {
  if (!dateStr) return '—'
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

const fullName = (app) => {
  if (!app) return '—'
  return [app.first_name, app.middle_name, app.last_name, app.suffix]
    .filter(Boolean)
    .join(' ')
}

const triggerToast = (message, success = false) => {
  toastMessage.value = message
  toastSuccess.value = success
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 2000)
}

// ---- Handlers ----

const loadApplications = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    applications.value = await getApprovedApplications()
  } catch (err) {
    errorMessage.value = 'Failed to load applications. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const handleSubmit = async () => {
  if (!canSubmit.value) return

  isSubmitting.value = true
  try {
    await linkRfidToResident({
      rfid_uid: pendingUid.value,
      resident_id: selectedApp.value.resident_id,
      document_request_id: selectedApp.value.document_request_id,
    })

    triggerToast(`RFID linked to ${fullName(selectedApp.value)} successfully!`, true)

    setTimeout(() => {
      rfidRegStore.clearAll()
      router.replace('/login')
    }, 2000)

  } catch (err) {
    const detail = err?.response?.data?.detail || 'Failed to link RFID. Please try again.'
    triggerToast(detail, false)
  } finally {
    isSubmitting.value = false
  }
}

const handleCancel = () => {
  rfidRegStore.clearAll()
  router.replace('/login')
}

// ---- Lifecycle ----
onMounted(() => {
  // Guard: no pending UID means admin landed here directly — send back
  if (!rfidRegStore.pendingRfidUid) {
    router.replace('/login-rfid')
    return
  }
  loadApplications()
})
</script>

<template>
  <div class="flex flex-col w-full h-full">

    <!-- Header -->
    <div class="flex items-center mb-6 gap-7 flex-shrink-0">
      <ArrowBackButton />
      <div class="flex justify-between items-center w-full">
        <div>
          <h1 class="text-[45px] text-[#03335C] font-bold tracking-tight -mt-2">
            Register RFID
          </h1>
          <p class="text-[#03335C] -mt-2">
            Link a new RFID card to an approved ID application.
          </p>
        </div>

        <!-- Scanned UID badge -->
        <div class="text-right">
          <p class="text-[#03335C] font-bold text-[45px]">{{ pendingUid || '—' }}</p>
        </div>
      </div>
    </div>

    <!-- Main content -->
    <div class="flex flex-1 gap-8 w-full min-h-0">

      <!-- Left Panel: Transaction list -->
      <div class="bg-white rounded-2xl shadow-lg p-6 flex-1 border border-gray-200 text-[#003A6B] flex flex-col">
        <p class="font-semibold text-base mb-1">Select a transaction number</p>
        <p class="text-xs text-gray-400 mb-6 italic">Only approved applications without an active RFID are shown.</p>

        <!-- Loading -->
        <div v-if="isLoading" class="flex-1 flex items-center justify-center text-gray-400">
          <svg class="animate-spin h-8 w-8 mr-3" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
          Loading applications...
        </div>

        <!-- Error -->
        <div v-else-if="errorMessage" class="flex-1 flex items-center justify-center text-red-500 text-sm">
          {{ errorMessage }}
        </div>

        <!-- Empty state -->
        <div v-else-if="applications.length === 0" class="flex-1 flex flex-col items-center justify-center text-gray-400 text-sm gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p>No approved applications pending RFID assignment.</p>
        </div>

        <!-- Transaction grid -->
        <div v-else class="grid grid-cols-4 gap-4 overflow-y-auto pr-1">
          <button
            v-for="app in applications"
            :key="app.document_request_id"
            @click="selectedApp = app"
            :class="[
              'rounded-xl shadow-sm px-4 py-3 border-2 text-center font-bold text-xl transition-all',
              selectedApp?.document_request_id === app.document_request_id
                ? 'bg-[#013C6D] text-white border-[#013C6D] shadow-md'
                : 'text-[#B1202A] bg-red-50 border-red-200'
            ]"
          >
            {{ app.transaction_no }}
          </button>
        </div>
      </div>

      <!-- Right Panel: Resident details -->
      <div class="flex flex-col text-[#003A6B] bg-[#EBF5FF] rounded-2xl shadow-lg p-6 w-[380px] border border-[#B0D7F8]">
        <h2 class="font-bold text-2xl text-center">Resident Details</h2>
        <p class="italic text-[9px] text-center mb-4">Please verify resident details before linking the RFID card.</p>

        <div v-if="!selectedApp" class="flex-1 flex items-center justify-center text-gray-400 text-sm italic text-center">
          Select a transaction number<br>to view resident details.
        </div>

        <div v-else class="flex-1 flex flex-col gap-3 text-sm">
          <div class="bg-white rounded-xl p-4 border border-[#B0D7F8] space-y-3">

            <div>
              <p class="text-xs text-gray-400 uppercase tracking-wide font-medium">Full Name</p>
              <p class="font-bold text-base text-[#013C6D]">{{ fullName(selectedApp) }}</p>
            </div>

            <div class="border-t border-gray-100 pt-2">
              <p class="text-xs text-gray-400 uppercase tracking-wide font-medium">Birthdate</p>
              <p class="font-semibold text-[#013C6D]">{{ formatBirthdate(selectedApp.birthdate) }}</p>
            </div>

            <div class="border-t border-gray-100 pt-2">
              <p class="text-xs text-gray-400 uppercase tracking-wide font-medium">Address</p>
              <p class="font-semibold text-[#013C6D]">{{ selectedApp.address || '—' }}</p>
            </div>

            <div class="border-t border-gray-100 pt-2">
              <p class="text-xs text-gray-400 uppercase tracking-wide font-medium">Transaction No.</p>
              <p class="font-bold text-[#013C6D]">{{ selectedApp.transaction_no }}</p>
            </div>
          </div>

          <!-- RFID being assigned -->
          <div class="bg-blue-100 rounded-xl p-3 border border-blue-300 text-center">
            <p class="text-xs text-gray-500 font-medium">RFID Card to Link</p>
            <p class="font-bold font-mono text-[#013C6D] text-base mt-0.5">{{ pendingUid }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer actions -->
    <div class="flex gap-6 mt-6 justify-between items-center flex-shrink-0 relative">
      <Button variant="outline" size="md" @click="handleCancel">
        Cancel
      </Button>

      <Button
        variant="secondary"
        size="md"
        :disabled="!canSubmit"
        @click="handleSubmit"
      >
        {{ isSubmitting ? 'Linking...' : 'Link RFID Card' }}
      </Button>

      <!-- Toast -->
      <Transition name="toast">
        <div
          v-if="showToast"
          class="absolute left-1/2 -translate-x-1/2 bottom-16 z-50 flex items-center gap-3 px-6 py-4 rounded-lg shadow-2xl border bg-white"
          :class="toastSuccess ? 'border-green-500' : 'border-red-500'"
        >
          <CheckCircleIcon v-if="toastSuccess" class="w-7 h-7 text-green-500" />
          <XCircleIcon v-else class="w-7 h-7 text-red-500" />
          <span class="text-gray-800 font-semibold text-base">{{ toastMessage }}</span>
        </div>
      </Transition>
    </div>

  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(8px);
}
</style>