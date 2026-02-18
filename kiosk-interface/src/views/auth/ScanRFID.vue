<script setup>
/**
 * @file ScanRFID.vue
 * @description Handles the hardware interface for RFID scanning.
 * Captures keyboard-emulated input from hardware scanners, validates the UID 
 * against the backend, and manages the routing flow based on the resident's security status (PIN).
 */

import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeftIcon, SignalIcon } from '@heroicons/vue/24/solid'
import Button from '@/components/shared/Button.vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/http'

// --- Component State & Composables ---
const router = useRouter()
const authStore = useAuthStore()

/** @type {import('vue').Ref<string>} Reactive binding for the hidden input field */
const scannedUID = ref('')

/** @type {import('vue').Ref<boolean>} UI state toggle for processing feedback */
const isProcessing = ref(false)

/** @type {import('vue').Ref<HTMLInputElement|null>} Template ref for the auto-focus input */
const hiddenInput = ref(null)

/** @type {string} Buffer to accumulate individual keystrokes from the scanner */
let inputBuffer = ''

/** @type {ReturnType<typeof setTimeout> | null} Timer to clear the buffer on slow/manual input */
let timeout = null

// ============================================================
// DEV MODE
// ============================================================
const isDevMode = import.meta.env.VITE_ENABLE_DEV_LOGIN === 'true'
const manualUID = ref('')

// --- Logic & Handlers ---

/**
 * Resets the scanner state, buffer, and input field.
 * Prepared for subsequent scans or error recovery.
 */
const resetScanner = () => {
  isProcessing.value = false
  inputBuffer = ''
  scannedUID.value = ''
  manualUID.value = ''
  if (hiddenInput.value) hiddenInput.value.value = ''
}

/**
 * Communicates with the backend to authenticate the scanned RFID UID.
 * * @param {string} uid - The unique identifier captured from the RFID card.
 * @returns {Promise<void>}
 * @flow 
 * 1. Request status from backend.
 * 2. If 'has_pin' is true, move to PIN verification.
 * 3. If 'has_pin' is false, grant immediate access to home.
 */
const authenticateRFID = async (uid) => {
  try {
    isProcessing.value = true

    const res = await api.post('kiosk/auth/rfid', { rfid_uid: uid })
    const data = res.data

    if (data.has_pin) {
      // Residents with security enabled are stored in a temporary state
      authStore.setTemporaryRFIDData({
        resident: {
          id: data.resident_id,
          first_name: data.first_name,
          last_name: data.last_name
        },
        uid: uid
      })
      router.push('/auth-pin')
    } else {
      // Residents without security are logged in directly
      authStore.setRFID(
        {
          id: data.resident_id,
          first_name: data.first_name,
          last_name: data.last_name
        },
        uid
      )
      router.replace('/home')
    }
  } catch (err) {
    // Standard error handling for inactive/unrecognized tags
    alert('Invalid or inactive RFID card.')
    resetScanner()
  }
}

/**
 * Global Keyboard Event Listener.
 * Intercepts keyboard-emulated input from hardware scanners.
 * * @param {KeyboardEvent} event - The raw keyboard event.
 */
const handleRFIDInput = async (event) => {
  if (isProcessing.value) return

  // Scanners typically append an 'Enter' key at the end of a UID string
  if (event.key === 'Enter') {
    const uid = inputBuffer.trim()
    if (uid) await authenticateRFID(uid)
    inputBuffer = ''
  } 
  // Accept alphanumeric characters only to prevent buffer pollution
  else if (/^[0-9A-Za-z]$/.test(event.key)) {
    inputBuffer += event.key
  }
  // Clear buffer if scanning takes longer than 200ms 
  // (Prevents manual typing and ensures input comes from a fast hardware scanner)
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

/**
 * Returns user to the primary login selection screen.
 */
const goBack = () => {
  router.replace('/login')
}

// --- Lifecycle Hooks ---


onMounted(async () => {
  // Ensure the hidden input is focused immediately for hardware capture
  await nextTick()
  hiddenInput.value?.focus()
  window.addEventListener('keydown', handleRFIDInput)
})

onUnmounted(() => {
  // Cleanup listeners and timers to prevent memory leaks and unexpected behavior
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
        <p class="text-sm text-gray-400 text-center mb-2">
          Dev Mode: Manual RFID Entry
        </p>
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
      <!-- ===================== -->

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