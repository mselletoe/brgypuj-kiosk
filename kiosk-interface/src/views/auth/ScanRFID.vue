<script setup>
/**
 * @file ScanRFID.vue
 * @description Handles hardware RFID scanning with two distinct flows:
 *
 * EXISTING CARD  → normal resident auth → /auth-pin (PIN verify / setup)
 * NEW CARD       → admin passcode gate  → /auth-pin (admin mode) → /register
 */

import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeftIcon, SignalIcon } from '@heroicons/vue/24/solid'
import Button from '@/components/shared/Button.vue'
import { useAuthStore } from '@/stores/auth'
import { useRfidRegistrationStore } from '@/stores/registration'
import { loginByRfid } from '@/api/authService'
import { checkRfidStatus } from '@/api/registrationService'

const router = useRouter()
const authStore = useAuthStore()
const rfidRegStore = useRfidRegistrationStore()

const scannedUID = ref('')
const isProcessing = ref(false)
const hiddenInput = ref(null)

let inputBuffer = ''
let timeout = null

// ============================================================
// DEV MODE
// ============================================================
const isDevMode = import.meta.env.VITE_ENABLE_DEV_LOGIN === 'true'
const manualUID = ref('')

// --- Helpers ---

const resetScanner = () => {
  isProcessing.value = false
  inputBuffer = ''
  scannedUID.value = ''
  manualUID.value = ''
  if (hiddenInput.value) hiddenInput.value.value = ''
}

/**
 * Main handler called after a full UID is captured from the scanner.
 *
 * Step 1: Check if the UID is new or already registered.
 * Step 2a (known card):  proceed to normal resident PIN auth.
 * Step 2b (new card):    store the UID, activate admin mode, go to /auth-pin.
 */
const authenticateRFID = async (uid) => {
  try {
    isProcessing.value = true

    // Step 1 — is this card new?
    const { is_new } = await checkRfidStatus(uid)

    if (is_new) {
      // Step 2b — new card: set store state FIRST, then navigate
      rfidRegStore.setPendingRfidUid(uid)  // sets pendingRfidUid + isAdminMode = true
      await nextTick()                     // wait for Pinia state to flush before route change
      router.push('/auth-pin')
      return
    }

    // Step 2a — known card: normal resident auth
    const data = await loginByRfid(uid)

    authStore.setTemporaryRFIDData({
      resident: {
        id: data.resident_id,
        first_name: data.first_name,
        middle_name: data.middle_name,
        last_name: data.last_name,
        address: data.address,
      },
      uid,
      has_pin: data.has_pin,
    })

    router.push('/auth-pin')

  } catch (err) {
    alert('Invalid or inactive RFID card.')
    resetScanner()
  }
}

const handleRFIDInput = async (event) => {
  if (isProcessing.value) return

  if (event.key === 'Enter') {
    const uid = inputBuffer.trim()
    if (uid) await authenticateRFID(uid)
    inputBuffer = ''
  } else if (/^[0-9A-Za-z]$/.test(event.key)) {
    inputBuffer += event.key
  }

  clearTimeout(timeout)
  timeout = setTimeout(() => { inputBuffer = '' }, 200)
}

// ============================================================
// DEV MODE
// ============================================================
const handleManualLogin = async () => {
  if (!manualUID.value) return
  await authenticateRFID(manualUID.value.trim())
}

const goBack = () => router.replace('/login')

// --- Lifecycle ---
onMounted(async () => {
  await nextTick()
  hiddenInput.value?.focus()
  window.addEventListener('keydown', handleRFIDInput)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleRFIDInput)
  clearTimeout(timeout)
})
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#003A6B] to-[#89CFF1] flex justify-center items-center font-poppins">
    <div class="bg-white w-[974px] h-[550px] rounded-lg shadow-2xl relative flex flex-col justify-center items-center p-8">

      <div class="flex flex-col items-center text-center">
        <div v-if="!isProcessing" class="flex flex-col items-center">
          <div class="bg-gray-200 w-80 h-52 rounded-lg flex justify-center items-center">
            <SignalIcon class="h-24 w-24 text-gray-400 animate-[pulse_2s_infinite]" />
          </div>
          <h2 class="text-3xl font-semibold text-gray-700 mt-8">Please tap your RFID</h2>
          <p class="text-lg text-gray-500 mt-2">Tap your card once and wait for processing.</p>
        </div>

        <div v-else class="flex flex-col items-center">
          <div class="bg-[#1B5886] w-80 h-52 rounded-lg flex justify-center items-center">
            <SignalIcon class="h-24 w-24 text-white animate-pulse" />
          </div>
          <h2 class="text-3xl font-semibold text-[#295B83] mt-8">Processing...</h2>
          <p class="text-lg text-gray-500 mt-2">Keep your card near the scanner.</p>
        </div>
      </div>

      <!-- ===== DEV MODE ===== -->
      <div v-if="isDevMode && !isProcessing" class="mt-6 w-80">
        <p class="text-sm text-gray-400 text-center mb-2">Dev Mode: Manual RFID Entry</p>
        <input
          v-model="manualUID"
          type="text"
          placeholder="Enter RFID UID"
          class="border border-gray-300 p-2 w-full rounded text-center"
        />
        <button
          @click="handleManualLogin"
          class="mt-2 w-full bg-[#1B5886] text-white py-2 rounded hover:bg-[#164a70]"
        >
          Login
        </button>
      </div>
      <!-- ==================== -->

      <input
        ref="hiddenInput"
        v-model="scannedUID"
        type="text"
        class="absolute opacity-0 pointer-events-none"
      />

      <Button
        @click="goBack"
        class="absolute bottom-8 left-8 w-auto px-3 text-[14px] rounded-[40px] h-[40px]"
        variant="outline"
      >
        <span class="flex items-center gap-x-2">
          <ArrowLeftIcon class="h-5 w-5" />
          Go Back
        </span>
      </Button>

    </div>
  </div>
</template>