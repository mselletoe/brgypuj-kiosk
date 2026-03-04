<script setup>
/**
 * @file AuthPIN.vue
 * @description Secure PIN entry interface. Handles three workflows:
 *
 * 1. ADMIN PASSCODE  — triggered when a new/unregistered RFID is scanned.
 *    rfidRegStore.isAdminMode = true → "Admin Access Required" UI,
 *    verifies via verifyAdminPasscode(), then routes to /register.
 *
 * 2. PIN SETUP  — resident has no PIN yet (has_pin: false).
 *    Collects + confirms a new 4-digit PIN via setupPin(), then routes to /home.
 *
 * 3. PIN VERIFY  — returning resident with an existing PIN.
 *    Verifies via verifyPin(), then routes to /home.
 */

import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import Keypad from '@/components/shared/Keypad.vue'
import { EyeIcon, EyeSlashIcon, XCircleIcon, CheckCircleIcon, ShieldCheckIcon } from '@heroicons/vue/24/outline'
import Button from '@/components/shared/Button.vue'
import { ArrowLeftIcon } from '@heroicons/vue/24/solid'
import { useAuthStore } from '@/stores/auth'
import { useRfidRegistrationStore } from '@/stores/registration'
import { setupPin, verifyPin } from '@/api/authService'
import { verifyAdminPasscode } from '@/api/registrationService'

// --- Composables ---
const router = useRouter()
const authStore = useAuthStore()
const rfidRegStore = useRfidRegistrationStore()

// --- State ---
const showToast = ref(false)
const toastMessage = ref('')
const isSuccess = ref(false)

const pin = ref('')
const confirmPin = ref('')
const PIN_LENGTH = 4
const showPin = ref(false)

// --- Helpers ---

const triggerToast = (message, success = false) => {
  toastMessage.value = message
  isSuccess.value = success
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 1500)
}

// ============================================================
// COMPUTED — mode-aware derived state
// ============================================================

/** True when opened for the admin passcode gate (new RFID flow) */
const isAdminMode = computed(() => rfidRegStore.isAdminMode)

/** Left panel title */
const title = computed(() => {
  if (isAdminMode.value) return 'Admin Access Required'
  const firstName = authStore.tempResident?.first_name || 'Resident'
  return `Welcome, ${firstName}`
})

/** Left panel subtitle */
const subtitle = computed(() => {
  if (isAdminMode.value) return 'Enter the admin passcode to register this new RFID card.'
  if (!authStore.tempHasPin) return 'Please set your 4-digit PIN'
  return 'Please enter your PIN to continue'
})

/** Label above the primary input field */
const inputLabel = computed(() => {
  if (isAdminMode.value) return 'Enter Admin Passcode'
  if (!authStore.tempHasPin) return 'Enter New 4-digit PIN'
  return 'Enter 4-digit PIN'
})

/** Authenticate button label */
const buttonLabel = computed(() => isAdminMode.value ? 'Confirm' : 'Authenticate')

const pinDisplay = computed(() => {
  if (pin.value.length === 0) return ''
  if (showPin.value) return pin.value
  return '• '.repeat(pin.value.length).trim()
})

const confirmPinDisplay = computed(() => {
  if (confirmPin.value.length === 0) return ''
  if (showPin.value) return confirmPin.value
  return '• '.repeat(confirmPin.value.length).trim()
})

/** Show confirm field only during resident PIN setup, never in admin mode */
const showConfirmField = computed(() => !isAdminMode.value && !authStore.tempHasPin)

const isPinComplete = computed(() => {
  if (isAdminMode.value) return pin.value.length === PIN_LENGTH
  if (!authStore.tempHasPin) {
    return pin.value.length === PIN_LENGTH && confirmPin.value.length === PIN_LENGTH
  }
  return pin.value.length === PIN_LENGTH
})

// ============================================================
// KEYPAD HANDLERS
// ============================================================

const onKeypress = (key) => {
  const useConfirm = showConfirmField.value && pin.value.length === PIN_LENGTH
  const target = useConfirm ? confirmPin : pin
  if (target.value.length < PIN_LENGTH) target.value += key
}

const onClear = () => {
  pin.value = ''
  confirmPin.value = ''
}

const onBackspace = () => {
  if (showConfirmField.value && confirmPin.value.length > 0) {
    confirmPin.value = confirmPin.value.slice(0, -1)
  } else if (pin.value.length > 0) {
    pin.value = pin.value.slice(0, -1)
  }
}

// ============================================================
// SUBMIT — branches by mode
// ============================================================

const submitPin = async () => {
  if (!isPinComplete.value) return

  try {
    // ── WORKFLOW A: Admin Passcode ──────────────────────────────
    if (isAdminMode.value) {
      const { valid } = await verifyAdminPasscode(pin.value)

      if (!valid) {
        triggerToast('Incorrect passcode. Please try again.')
        onClear()
        return
      }

      triggerToast('Access granted!', true)
      rfidRegStore.clearAdminMode()   // keep pendingRfidUid, just drop the flag
      setTimeout(() => router.replace('/register'), 1000)
      return
    }

    // ── WORKFLOW B: First-time PIN Setup ────────────────────────
    if (!authStore.tempHasPin) {
      if (pin.value !== confirmPin.value) {
        triggerToast('PINs do not match.')
        onClear()
        return
      }

      await setupPin({
        resident_id: authStore.tempResident.id,
        pin: pin.value,
        rfid_uid: authStore.tempUid,
      })

      authStore.confirmRFIDLogin()
      triggerToast('PIN set successfully!', true)
      setTimeout(() => router.replace('/home'), 1000)
      return
    }

    // ── WORKFLOW C: Standard PIN Verification ───────────────────
    const { valid } = await verifyPin({
      resident_id: authStore.tempResident.id,
      pin: pin.value,
    })

    if (!valid) {
      triggerToast('Invalid PIN')
      onClear()
      return
    }

    authStore.confirmRFIDLogin()
    triggerToast('Login successful!', true)
    router.replace('/home')

  } catch (err) {
    triggerToast('An error occurred. Please try again.')
    onClear()
  }
}

// ============================================================
// NAVIGATION
// ============================================================

const goBack = () => {
  if (isAdminMode.value) {
    rfidRegStore.clearAll()
  }
  router.push('/login-rfid')
}

// ============================================================
// LIFECYCLE
// ============================================================

onMounted(() => {
  // Admin mode — only needs a pending UID, no resident session required
  if (rfidRegStore.isAdminMode) {
    if (!rfidRegStore.pendingRfidUid) {
      triggerToast('No RFID scan found. Please try again.')
      setTimeout(() => router.push('/login-rfid'), 1500)
    }
    return   // ← exit early, do NOT run the resident guard below
  }

  // Resident mode — must have temp data from ScanRFID
  if (!authStore.tempResident || !authStore.tempUid) {
    triggerToast('No session found. Please scan again.')
    setTimeout(() => router.push('/login-rfid'), 1500)
  }
})
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#003A6B] to-[#89CFF1] flex justify-center items-center font-poppins">
    <div class="bg-white w-[974px] h-[550px] rounded-lg shadow-2xl relative flex p-10">

      <!-- Left panel -->
      <div class="flex-1 flex flex-col text-[#013C6D] pr-12">
        <div class="flex items-center gap-3 mb-10">
          <img src="@/assets/images/Pob1Logo.svg" alt="Barangay Logo" class="w-14 h-14">
          <div>
            <h1 class="text-lg font-bold">Brgy. Poblacion I</h1>
            <p class="text-base font-light">Kiosk System</p>
          </div>
        </div>

        <div class="flex-grow flex flex-col justify-center items-center text-center">
          <div class="mb-20">
            <ShieldCheckIcon v-if="isAdminMode" class="w-16 h-16 mx-auto mb-4 text-[#013C6D] opacity-80" />
            <h2 class="text-4xl font-bold mb-2 leading-tight">{{ title }}</h2>
            <p class="text-lg text-gray-500 italic">{{ subtitle }}</p>
          </div>
        </div>

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

      <!-- Right panel: keypad -->
      <div class="flex flex-1 flex-col items-center justify-center pl-12 border-l border-gray-200 relative">
        <div class="w-full max-w-xs">

          <label class="text-sm font-medium text-gray-500 mb-1">
            {{ inputLabel }}
          </label>
          <div class="relative w-full">
            <input
              :value="pinDisplay"
              type="text"
              readonly
              class="w-full h-14 bg-gray-50 border border-gray-300 rounded-lg text-3xl text-center font-light focus:outline-none"
              :class="showPin ? 'tracking-normal' : 'tracking-widest'"
            />
            <button @click="showPin = !showPin" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400">
              <EyeIcon v-if="!showPin" class="w-6 h-6" />
              <EyeSlashIcon v-else class="w-6 h-6" />
            </button>
          </div>

          <!-- Confirm PIN field — only during resident PIN setup -->
          <template v-if="showConfirmField">
            <label class="text-sm font-medium text-gray-500 mb-1 mt-4">Confirm 4-digit PIN</label>
            <div class="relative w-full">
              <input
                :value="confirmPinDisplay"
                type="text"
                readonly
                class="w-full h-14 bg-gray-50 border border-gray-300 rounded-lg text-3xl text-center font-light focus:outline-none"
                :class="showPin ? 'tracking-normal' : 'tracking-widest'"
              />
            </div>
          </template>
        </div>

        <div class="w-full max-w-xs">
          <Keypad @press="onKeypress" @clear="onClear" @backspace="onBackspace" class="mt-4" />

          <button
            @click="submitPin"
            :disabled="!isPinComplete"
            :class="[
              'w-full h-14 text-xl font-semibold rounded-lg mt-4 transition-colors text-white',
              isPinComplete ? 'bg-[#013C6D] hover:bg-[#012f5a]' : 'bg-gray-400 cursor-not-allowed'
            ]"
          >
            {{ buttonLabel }}
          </button>
        </div>

        <Transition name="toast">
          <div
            v-if="showToast"
            class="absolute top-1/2 left-[55%] transform -translate-x-1/2 -translate-y-1/2 z-50 flex items-center gap-3 px-6 py-4 rounded-lg shadow-2xl border bg-white"
            :class="isSuccess ? 'border-green-500' : 'border-red-500 text-red-600'"
          >
            <CheckCircleIcon v-if="isSuccess" class="w-8 h-8 text-green-500" />
            <XCircleIcon v-else class="w-8 h-8 text-red-500" />
            <span class="text-gray-800 font-semibold text-lg">{{ toastMessage }}</span>
          </div>
        </Transition>
      </div>

    </div>
  </div>
</template>