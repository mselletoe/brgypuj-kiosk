<script setup>
/**
 * @file views/auth/Register.vue
 * @description Kiosk RFID registration screen. Allows an admin to link a scanned
 * RFID card to an approved ID application. Displays a selectable list of approved
 * transactions and shows the resident's details before confirming the link.
 */

import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import Button from '@/components/shared/Button.vue'
import Modal from '@/components/shared/Modal.vue'
import { useRfidRegistrationStore } from '@/stores/registration'
import { getApprovedApplications, linkRfidToResident } from '@/api/registrationService'

const router = useRouter()
const rfidRegStore = useRfidRegistrationStore()
const { t } = useI18n()


// =============================================================================
// STATE
// =============================================================================
const applications = ref([])
const selectedApp = ref(null)
const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')
const showSuccessModal = ref(false)
const showErrorModal = ref(false)

/** Formatted expiration date of the newly linked RFID card */
const linkedExpiration = ref('')

/** RFID UID scanned on the previous screen, passed via the registration store */
const pendingUid = computed(() => rfidRegStore.pendingRfidUid)

/** True when a transaction is selected, a UID is available, and no request is in flight */
const canSubmit = computed(() =>
  selectedApp.value !== null && pendingUid.value && !isSubmitting.value
)

// =============================================================================
// FORMATTERS
// =============================================================================
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

// =============================================================================
// DATA LOADING
// =============================================================================
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

// =============================================================================
// ACTIONS
// =============================================================================
const handleSubmit = async () => {
  if (!canSubmit.value) return

  isSubmitting.value = true
  try {
    const result = await linkRfidToResident({
      rfid_uid: pendingUid.value,
      resident_id: selectedApp.value.resident_id,
      document_request_id: selectedApp.value.document_request_id,
    })
    if (result?.data?.expiration_date) {
      const d = new Date(result.data.expiration_date + 'T00:00:00')
      linkedExpiration.value = d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
    }
    showSuccessModal.value = true
  } catch (err) {
    errorMessage.value = err?.response?.data?.detail || 'Failed to link RFID. Please try again.'
    showErrorModal.value = true
  } finally {
    isSubmitting.value = false
  }
}

const handleSuccessClose = () => {
  rfidRegStore.clearAll()
  router.replace('/login')
}

const handleErrorClose = () => {
  showErrorModal.value = false
  errorMessage.value = ''
}

const handleCancel = () => {
  rfidRegStore.clearAll()
  router.replace('/login')
}

// =============================================================================
// LIFECYCLE
// =============================================================================
onMounted(() => {
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
            {{ t('registerRFID') }}
          </h1>
          <p class="text-[#03335C] -mt-2">
            {{ t('linkNewRFID') }}
          </p>
        </div>
        <div class="flex items-center gap-4">
    

          <p class="text-[#03335C] font-bold text-[45px]">{{ pendingUid || '—' }}</p>
        </div>
      </div>
    </div>

    <!-- Main content -->
    <div class="flex flex-1 gap-8 w-full min-h-0">

      <!-- Left Panel: Transaction list -->
      <div class="bg-white rounded-2xl shadow-lg p-6 flex-1 border border-gray-200 text-[#003A6B] flex flex-col">
        <p class="font-semibold text-base mb-1">{{ t('selectTransaction') }}</p>
        <p class="text-xs text-gray-400 mb-6 italic">{{ t('onlyApproved') }}</p>

        <!-- Loading -->
        <div v-if="isLoading" class="flex-1 flex items-center justify-center text-gray-400">
          <svg class="animate-spin h-8 w-8 mr-3" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
          </svg>
          {{ t('loadingApplications') }}
        </div>

        <!-- Error -->
        <div v-else-if="errorMessage && !showErrorModal" class="flex-1 flex items-center justify-center text-red-500 text-sm">
          {{ errorMessage }}
        </div>

        <!-- Empty state -->
        <div v-else-if="applications.length === 0" class="flex-1 flex flex-col items-center justify-center text-gray-400 text-sm gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p>{{ t('noApprovedApplications') }}</p>
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
        <h2 class="font-bold text-2xl text-center">{{ t('residentDetails') }}</h2>
        <p class="italic text-[9px] text-center mb-4">{{ t('verifyBeforeLinking') }}</p>

        <div v-if="!selectedApp" class="flex-1 flex items-center justify-center text-gray-400 text-sm italic text-center">
          {{ t('selectTransactionFirst') }}
        </div>

        <div v-else class="flex-1 flex flex-col gap-3 text-sm overflow-y-auto pr-1">
          <div class="bg-white rounded-xl p-4 border border-[#B0D7F8] space-y-3">
            <div>
              <p class="text-xs text-gray-400 uppercase tracking-wide font-medium">{{ t('fullName') }}</p>
              <p class="font-bold text-base text-[#013C6D]">{{ fullName(selectedApp) }}</p>
            </div>
            <div class="border-t border-gray-100 pt-2">
              <p class="text-xs text-gray-400 uppercase tracking-wide font-medium">{{ t('birthdate') }}</p>
              <p class="font-semibold text-[#013C6D]">{{ formatBirthdate(selectedApp.birthdate) }}</p>
            </div>
            <div class="border-t border-gray-100 pt-2">
              <p class="text-xs text-gray-400 uppercase tracking-wide font-medium">{{ t('address') }}</p>
              <p class="font-semibold text-[#013C6D]">{{ selectedApp.address || '—' }}</p>
            </div>
            <div class="border-t border-gray-100 pt-2">
              <p class="text-xs text-gray-400 uppercase tracking-wide font-medium">{{ t('transactionNo') }}</p>
              <p class="font-bold text-[#013C6D]">{{ selectedApp.transaction_no }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer actions -->
    <div class="flex gap-6 mt-6 justify-between items-center flex-shrink-0">
      <Button variant="outline" size="md" @click="handleCancel">
        {{ t('cancel') }}
      </Button>
      <Button
        variant="secondary"
        size="md"
        :disabled="!canSubmit"
        @click="handleSubmit"
      >
        {{ isSubmitting ? t('linking') : t('linkRFIDCard') }}
      </Button>
    </div>

    <!-- Success Modal -->
    <transition name="fade-blur">
      <div
        v-if="showSuccessModal"
        class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50"
      >
        <Modal
          :title="t('rfidRegistered')"
          :message="t('rfidLinkedSuccess', { name: fullName(selectedApp) })"
          :reference-id="pendingUid"
          :show-reference-id="true"
          :primary-button-text="t('done')"
          :show-primary-button="true"
          :show-secondary-button="false"
          @primary-click="handleSuccessClose"
        >
          <template #extra>
            <div v-if="linkedExpiration" class="mt-3 bg-blue-50 border border-blue-200 rounded-lg px-4 py-2 text-sm text-[#013C6D] text-center">
              <span class="font-medium">{{ t('cardExpiresOn') }}</span>
              <span class="font-bold ml-1">{{ linkedExpiration }}</span>
            </div>
          </template>
        </Modal>
      </div>
    </transition>

    <!-- Error Modal -->
    <transition name="fade-blur">
      <div
        v-if="showErrorModal"
        class="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50"
      >
        <Modal
          :title="t('registrationFailed')"
          :message="errorMessage"
          :primary-button-text="t('confirm')"
          :show-primary-button="true"
          :show-secondary-button="false"
          @primary-click="handleErrorClose"
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