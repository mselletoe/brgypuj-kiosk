<script setup>
/**
 * @file ScanRFID.vue
 *
 * ADDED:
 * - Handles HTTP 423 (Locked) returned by /rfid endpoint when a resident
 *   is currently locked out. Shows inline lockout state with countdown
 *   instead of crashing into a generic alert.
 */

import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeftIcon, SignalIcon } from '@heroicons/vue/24/solid'
import { LockClosedIcon } from '@heroicons/vue/24/outline'
import Button from '@/components/shared/Button.vue'
import { useAuthStore } from '@/stores/auth'
import { useRfidRegistrationStore } from '@/stores/registration'
import { loginByRfid } from '@/api/authService'
import { checkRfidStatus } from '@/api/registrationService'

const router       = useRouter()
const authStore    = useAuthStore()
const rfidRegStore = useRfidRegistrationStore()

const scannedUID    = ref('')
const isProcessing  = ref(false)
const hiddenInput   = ref(null)

// ── Lockout state ──────────────────────────────────────────────────────────
const isLocked           = ref(false)
const lockoutSecondsLeft = ref(0)
let lockoutInterval      = null

const lockoutDisplay = computed(() => {
  const m = Math.floor(lockoutSecondsLeft.value / 60)
  const s = lockoutSecondsLeft.value % 60
  return m > 0 ? `${m}m ${String(s).padStart(2, '0')}s` : `${s}s`
})

function startLockoutCountdown(seconds) {
  isLocked.value           = true
  lockoutSecondsLeft.value = seconds
  isProcessing.value       = false
  clearInterval(lockoutInterval)

  lockoutInterval = setInterval(() => {
    lockoutSecondsLeft.value -= 1
    if (lockoutSecondsLeft.value <= 0) {
      clearInterval(lockoutInterval)
      isLocked.value = false
      resetScanner()
    }
  }, 1000)
}

// ── Dev mode ───────────────────────────────────────────────────────────────
const isDevMode  = import.meta.env.VITE_ENABLE_DEV_LOGIN === 'true'
const manualUID  = ref('')

let inputBuffer = ''
let timeout     = null

const resetScanner = () => {
  isProcessing.value = false
  inputBuffer        = ''
  scannedUID.value   = ''
  manualUID.value    = ''
  if (hiddenInput.value) hiddenInput.value.value = ''
}

// ── Main auth handler ──────────────────────────────────────────────────────
const authenticateRFID = async (uid) => {
  if (isLocked.value) return

  try {
    isProcessing.value = true

    const { is_new } = await checkRfidStatus(uid)

    if (is_new) {
      rfidRegStore.setPendingRfidUid(uid)
      await nextTick()
      router.push('/auth-pin')
      return
    }

    const data = await loginByRfid(uid)

    authStore.setTemporaryRFIDData({
      resident: {
        id:          data.resident_id,
        first_name:  data.first_name,
        middle_name: data.middle_name,
        last_name:   data.last_name,
        address:     data.address,
      },
      uid,
      has_pin: data.has_pin,
    })

    router.push('/auth-pin')

  } catch (err) {
    // ── 423 Locked ─────────────────────────────────────────────────────────
    if (err?.response?.status === 423) {
      const detail = err.response.data?.detail || {}
      const secs   = detail.lockout_seconds_remaining ?? 60
      startLockoutCountdown(secs)
      return
    }

    alert('Invalid or inactive RFID card.')
    resetScanner()
  }
}

const handleRFIDInput = async (event) => {
  if (isProcessing.value || isLocked.value) return

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

const handleManualLogin = async () => {
  if (!manualUID.value || isLocked.value) return
  await authenticateRFID(manualUID.value.trim())
}

const goBack = () => router.replace('/login')

onMounted(async () => {
  await nextTick()
  hiddenInput.value?.focus()
  window.addEventListener('keydown', handleRFIDInput)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleRFIDInput)
  clearTimeout(timeout)
  clearInterval(lockoutInterval)
})
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#003A6B] to-[#89CFF1] flex justify-center items-center font-poppins">
    <div class="bg-white w-[974px] h-[550px] rounded-lg shadow-2xl relative flex flex-col justify-center items-center p-8">

      <!-- ── LOCKOUT STATE ──────────────────────────────────────────────── -->
      <div v-if="isLocked" class="flex flex-col items-center text-center gap-6">
        <div class="bg-red-50 w-80 h-52 rounded-lg flex flex-col justify-center items-center gap-3 border border-red-200">
          <LockClosedIcon class="h-16 w-16 text-red-400" />
          <span class="text-4xl font-bold text-red-500">{{ lockoutDisplay }}</span>
        </div>
        <h2 class="text-3xl font-semibold text-red-600">Card Temporarily Locked</h2>
        <p class="text-lg text-gray-500">Too many failed PIN attempts.<br>Please wait and try again.</p>
      </div>

      <!-- ── NORMAL SCAN STATE ──────────────────────────────────────────── -->
      <div v-else class="flex flex-col items-center text-center">
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

      <!-- Dev mode -->
      <div v-if="isDevMode && !isProcessing && !isLocked" class="mt-6 w-80">
        <p class="text-sm text-gray-400 text-center mb-2">Dev Mode: Manual RFID Entry</p>
        <input v-model="manualUID" type="text" placeholder="Enter RFID UID" class="border border-gray-300 p-2 w-full rounded text-center" />
        <button @click="handleManualLogin" class="mt-2 w-full bg-[#1B5886] text-white py-2 rounded hover:bg-[#164a70]">Login</button>
      </div>

      <input ref="hiddenInput" v-model="scannedUID" type="text" class="absolute opacity-0 pointer-events-none" />

      <Button @click="goBack" class="absolute bottom-8 left-8 w-auto px-3 text-[14px] rounded-[40px] h-[40px]" variant="outline">
        <span class="flex items-center gap-x-2"><ArrowLeftIcon class="h-5 w-5" />Go Back</span>
      </Button>

    </div>
  </div>
</template>