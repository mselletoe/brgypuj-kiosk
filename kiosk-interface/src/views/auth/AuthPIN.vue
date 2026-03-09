<script setup>
/**
 * @file AuthPIN.vue
 *
 * ADDED:
 * - Handles HTTP 423 (Locked) response from /verify-pin.
 *   Shows a live countdown and prevents further input until the lockout expires.
 * - Shows remaining attempts warning when attempts_left <= 2.
 */
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSystemConfig } from '@/composables/useSystemConfig'
import Keypad from '@/components/shared/Keypad.vue'
import { EyeIcon, EyeSlashIcon, XCircleIcon, CheckCircleIcon, ShieldCheckIcon, LockClosedIcon } from '@heroicons/vue/24/outline'
import Button from '@/components/shared/Button.vue'
import { ArrowLeftIcon } from '@heroicons/vue/24/solid'
import { useAuthStore } from '@/stores/auth'
import { useRfidRegistrationStore } from '@/stores/registration'
import { setupPin, verifyPin } from '@/api/authService'
import { verifyAdminPasscode } from '@/api/registrationService'

const router      = useRouter()
const authStore   = useAuthStore()
const rfidRegStore = useRfidRegistrationStore()
const { brgyName, brgySubname, resolvedLogoUrl } = useSystemConfig()

// ── Toast ──────────────────────────────────────────────────────────────────
const showToast    = ref(false)
const toastMessage = ref('')
const isSuccess    = ref(false)

const triggerToast = (message, success = false) => {
  toastMessage.value = message
  isSuccess.value    = success
  showToast.value    = true
  setTimeout(() => { showToast.value = false }, 2000)
}

// ── PIN state ──────────────────────────────────────────────────────────────
const pin        = ref('')
const confirmPin = ref('')
const PIN_LENGTH = 4
const showPin    = ref(false)

// ── Lockout state ──────────────────────────────────────────────────────────
const isLocked            = ref(false)
const lockoutSecondsLeft  = ref(0)
const attemptsLeft        = ref(null)   // null until first wrong attempt
let lockoutInterval       = null

function startLockoutCountdown(seconds) {
  isLocked.value           = true
  lockoutSecondsLeft.value = seconds
  clearInterval(lockoutInterval)

  lockoutInterval = setInterval(() => {
    lockoutSecondsLeft.value -= 1
    if (lockoutSecondsLeft.value <= 0) {
      clearInterval(lockoutInterval)
      isLocked.value    = false
      attemptsLeft.value = null
      pin.value          = ''
      confirmPin.value   = ''
    }
  }, 1000)
}

const lockoutDisplay = computed(() => {
  const m = Math.floor(lockoutSecondsLeft.value / 60)
  const s = lockoutSecondsLeft.value % 60
  return m > 0
    ? `${m}m ${String(s).padStart(2, '0')}s`
    : `${s}s`
})

// ── Computed ───────────────────────────────────────────────────────────────
const isAdminMode      = computed(() => rfidRegStore.isAdminMode)
const title            = computed(() => {
  if (isAdminMode.value) return 'Admin Access Required'
  return `Welcome, ${authStore.tempResident?.first_name || 'Resident'}`
})
const subtitle         = computed(() => {
  if (isAdminMode.value)       return 'Enter the admin passcode to register this new RFID card.'
  if (!authStore.tempHasPin)   return 'Please set your 4-digit PIN'
  return 'Please enter your PIN to continue'
})
const inputLabel       = computed(() => {
  if (isAdminMode.value)       return 'Enter Admin Passcode'
  if (!authStore.tempHasPin)   return 'Enter New 4-digit PIN'
  return 'Enter 4-digit PIN'
})
const buttonLabel      = computed(() => isAdminMode.value ? 'Confirm' : 'Authenticate')
const pinDisplay       = computed(() => {
  if (!pin.value.length) return ''
  return showPin.value ? pin.value : '• '.repeat(pin.value.length).trim()
})
const confirmPinDisplay = computed(() => {
  if (!confirmPin.value.length) return ''
  return showPin.value ? confirmPin.value : '• '.repeat(confirmPin.value.length).trim()
})
const showConfirmField  = computed(() => !isAdminMode.value && !authStore.tempHasPin)
const isPinComplete     = computed(() => {
  if (isLocked.value) return false
  if (isAdminMode.value)     return pin.value.length === PIN_LENGTH
  if (!authStore.tempHasPin) return pin.value.length === PIN_LENGTH && confirmPin.value.length === PIN_LENGTH
  return pin.value.length === PIN_LENGTH
})

// ── Keypad handlers ────────────────────────────────────────────────────────
const onKeypress  = (key) => {
  if (isLocked.value) return
  const useConfirm = showConfirmField.value && pin.value.length === PIN_LENGTH
  const target     = useConfirm ? confirmPin : pin
  if (target.value.length < PIN_LENGTH) target.value += key
}
const onClear     = () => { pin.value = ''; confirmPin.value = '' }
const onBackspace = () => {
  if (showConfirmField.value && confirmPin.value.length > 0) {
    confirmPin.value = confirmPin.value.slice(0, -1)
  } else if (pin.value.length > 0) {
    pin.value = pin.value.slice(0, -1)
  }
}

// ── Submit ─────────────────────────────────────────────────────────────────
const submitPin = async () => {
  if (!isPinComplete.value || isLocked.value) return

  try {
    // ── Admin passcode flow ───────────────────────────────────────────────
    if (isAdminMode.value) {
      const { valid } = await verifyAdminPasscode(pin.value)
      if (!valid) { triggerToast('Incorrect passcode. Please try again.'); onClear(); return }
      triggerToast('Access granted!', true)
      rfidRegStore.clearAdminMode()
      setTimeout(() => router.replace('/register'), 1000)
      return
    }

    // ── First-time PIN setup ──────────────────────────────────────────────
    if (!authStore.tempHasPin) {
      if (pin.value !== confirmPin.value) { triggerToast('PINs do not match.'); onClear(); return }
      await setupPin({ resident_id: authStore.tempResident.id, pin: pin.value, rfid_uid: authStore.tempUid })
      authStore.confirmRFIDLogin()
      triggerToast('PIN set successfully!', true)
      setTimeout(() => router.replace('/home'), 1000)
      return
    }

    // ── Standard PIN verify ───────────────────────────────────────────────
    const response = await verifyPin({ resident_id: authStore.tempResident.id, pin: pin.value })

    if (response.valid) {
      attemptsLeft.value = null
      authStore.confirmRFIDLogin()
      triggerToast('Login successful!', true)
      router.replace('/home')
      return
    }

    // Wrong PIN — show remaining attempts
    onClear()
    attemptsLeft.value = response.attempts_left ?? null
    if (attemptsLeft.value !== null && attemptsLeft.value <= 2) {
      triggerToast(`Incorrect PIN. ${attemptsLeft.value} attempt${attemptsLeft.value !== 1 ? 's' : ''} remaining.`)
    } else {
      triggerToast('Incorrect PIN. Please try again.')
    }

  } catch (err) {
    onClear()

    // ── 423 Locked ────────────────────────────────────────────────────────
    if (err?.response?.status === 423) {
      const detail = err.response.data?.detail || {}
      const secs   = detail.lockout_seconds_remaining ?? 60
      startLockoutCountdown(secs)
      return
    }

    triggerToast('An error occurred. Please try again.')
  }
}

const goBack = () => {
  clearInterval(lockoutInterval)
  if (isAdminMode.value) rfidRegStore.clearAll()
  router.push('/login-rfid')
}

onMounted(() => {
  if (rfidRegStore.isAdminMode) {
    if (!rfidRegStore.pendingRfidUid) { triggerToast('No RFID scan found. Please try again.'); setTimeout(() => router.push('/login-rfid'), 1500) }
    return
  }
  if (!authStore.tempResident || !authStore.tempUid) { triggerToast('No session found. Please scan again.'); setTimeout(() => router.push('/login-rfid'), 1500) }
})

onUnmounted(() => clearInterval(lockoutInterval))
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#003A6B] to-[#89CFF1] flex justify-center items-center font-poppins">
    <div class="bg-white w-[974px] h-[550px] rounded-lg shadow-2xl relative flex p-10">

      <!-- Left panel -->
      <div class="flex-1 flex flex-col text-[#013C6D] pr-12">
        <div class="flex items-center gap-3 mb-10">
          <img v-if="resolvedLogoUrl" :src="resolvedLogoUrl" alt="Barangay Logo" class="w-14 h-14 min-w-[56px] object-cover rounded-full">
          <div>
            <h1 class="text-lg font-bold">{{ brgyName }}</h1>
            <p class="text-base font-light">{{ brgySubname }}</p>
          </div>
        </div>

        <div class="flex-grow flex flex-col justify-center items-center text-center">
          <div class="mb-20">
            <ShieldCheckIcon v-if="isAdminMode" class="w-16 h-16 mx-auto mb-4 text-[#013C6D] opacity-80" />
            <LockClosedIcon  v-else-if="isLocked" class="w-16 h-16 mx-auto mb-4 text-red-500" />
            <h2 class="text-4xl font-bold mb-2 leading-tight">{{ title }}</h2>
            <p class="text-lg text-gray-500 italic">{{ subtitle }}</p>
          </div>
        </div>

        <Button @click="goBack" class="absolute bottom-8 left-8 w-auto px-3 text-[14px] rounded-[40px] h-[40px]" variant="outline">
          <span class="flex items-center gap-x-2"><ArrowLeftIcon class="h-5 w-5" />Go Back</span>
        </Button>
      </div>

      <!-- Right panel -->
      <div class="flex flex-1 flex-col items-center justify-center pl-12 border-l border-gray-200 relative">

        <!-- ── LOCKOUT STATE ─────────────────────────────────────────────── -->
        <div v-if="isLocked" class="flex flex-col items-center gap-6 text-center">
          <div class="relative w-32 h-32">
            <svg class="w-full h-full -rotate-90" viewBox="0 0 100 100">
              <circle cx="50" cy="50" r="44" fill="none" stroke="#FEE2E2" stroke-width="8" />
              <circle
                cx="50" cy="50" r="44"
                fill="none"
                stroke="#EF4444"
                stroke-width="8"
                stroke-linecap="round"
                :stroke-dasharray="276.46"
                :stroke-dashoffset="276.46 * (lockoutSecondsLeft / (lockoutSecondsLeft + 1))"
                class="transition-all duration-1000"
              />
            </svg>
            <span class="absolute inset-0 flex items-center justify-center text-2xl font-bold text-red-500">
              {{ lockoutDisplay }}
            </span>
          </div>
          <div>
            <p class="text-xl font-semibold text-red-600">Account Temporarily Locked</p>
            <p class="text-sm text-gray-500 mt-1">Too many incorrect PIN attempts.<br>Please wait before trying again.</p>
          </div>
        </div>

        <!-- ── NORMAL PIN ENTRY STATE ────────────────────────────────────── -->
        <template v-else>
          <div class="w-full max-w-xs">
            <label class="text-sm font-medium text-gray-500 mb-1">{{ inputLabel }}</label>

            <!-- Attempts warning -->
            <p v-if="attemptsLeft !== null && attemptsLeft <= 2" class="text-xs text-red-500 mb-1 font-medium">
              ⚠ {{ attemptsLeft }} attempt{{ attemptsLeft !== 1 ? 's' : '' }} remaining before lockout
            </p>

            <div class="relative w-full">
              <input
                :value="pinDisplay"
                type="text"
                readonly
                class="w-full h-14 bg-gray-50 border border-gray-300 rounded-lg text-3xl text-center font-light focus:outline-none"
                :class="[showPin ? 'tracking-normal' : 'tracking-widest', attemptsLeft !== null && attemptsLeft <= 2 ? 'border-red-400' : '']"
              />
              <button @click="showPin = !showPin" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400">
                <EyeIcon v-if="!showPin" class="w-6 h-6" /><EyeSlashIcon v-else class="w-6 h-6" />
              </button>
            </div>

            <template v-if="showConfirmField">
              <label class="text-sm font-medium text-gray-500 mb-1 mt-4">Confirm 4-digit PIN</label>
              <div class="relative w-full">
                <input :value="confirmPinDisplay" type="text" readonly class="w-full h-14 bg-gray-50 border border-gray-300 rounded-lg text-3xl text-center font-light focus:outline-none" :class="showPin ? 'tracking-normal' : 'tracking-widest'" />
              </div>
            </template>
          </div>

          <div class="w-full max-w-xs">
            <Keypad @press="onKeypress" @clear="onClear" @backspace="onBackspace" class="mt-4" />
            <button
              @click="submitPin"
              :disabled="!isPinComplete"
              :class="['w-full h-14 text-xl font-semibold rounded-lg mt-4 transition-colors text-white', isPinComplete ? 'bg-[#013C6D] hover:bg-[#012f5a]' : 'bg-gray-400 cursor-not-allowed']"
            >
              {{ buttonLabel }}
            </button>
          </div>
        </template>

        <!-- Toast -->
        <Transition name="toast">
          <div v-if="showToast" class="absolute top-1/2 left-[55%] transform -translate-x-1/2 -translate-y-1/2 z-50 flex items-center gap-3 px-6 py-4 rounded-lg shadow-2xl border bg-white" :class="isSuccess ? 'border-green-500' : 'border-red-500 text-red-600'">
            <CheckCircleIcon v-if="isSuccess" class="w-8 h-8 text-green-500" />
            <XCircleIcon v-else class="w-8 h-8 text-red-500" />
            <span class="text-gray-800 font-semibold text-lg">{{ toastMessage }}</span>
          </div>
        </Transition>
      </div>

    </div>
  </div>
</template>