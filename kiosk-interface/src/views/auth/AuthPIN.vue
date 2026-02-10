<script setup>
/**
 * @file AuthPIN.vue
 * @description Secure PIN entry interface for resident authentication.
 * Handles two primary workflows:
 * 1. Initial PIN Setup: For residents without a registered PIN.
 * 2. PIN Verification: For standard authenticated access.
 * Utilizes a temporary global state (Pinia) to bridge data between Scan and Home.
 */

import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import Keypad from '@/components/shared/Keypad.vue'
import { EyeIcon, EyeSlashIcon, XCircleIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'
import Button from '@/components/shared/Button.vue' 
import { ArrowLeftIcon } from '@heroicons/vue/24/solid' 
import { useAuthStore } from '@/stores/auth'
import api from '@/api/http'

// --- Component State & Composables ---
const router = useRouter()
const authStore = useAuthStore()


/** @type {import('vue').Ref<boolean>} Visibility toggle for custom toast notifications */
const showToast = ref(false)

/** @type {import('vue').Ref<string>} Message content for the toast notification */
const toastMessage = ref('')

/** @type {import('vue').Ref<boolean>} Success/Failure state for toast styling */
const isSuccess = ref(false)

/** @type {import('vue').Ref<string>} Buffer for the primary 4-digit PIN */
const pin = ref('')

/** @type {import('vue').Ref<string>} Buffer for PIN confirmation (used during setup only) */
const confirmPin = ref('')

// Constants
const PIN_LENGTH = 4

/** @type {import('vue').Ref<boolean>} Toggle for masking/unmasking PIN characters */
const showPin = ref(false)

// --- Logic & Helpers ---

/**
 * Triggers a visual feedback notification (Toast).
 * @param {string} message - Text to display.
 * @param {boolean} [success=false] - If true, displays green/check icon; else red/X icon.
 */
const triggerToast = (message, success = false) => {
  toastMessage.value = message
  isSuccess.value = success
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 1500)
}

/**
 * Keypad Input Handler.
 * Directs numerical input to either the primary PIN or Confirmation buffer.
 * @param {string} key - The numerical character pressed on the keypad.
 */
const onKeypress = (key) => {
  const isSettingPin = !authStore.tempHasPin;
  // If setting PIN, switch to 'confirmPin' once 'pin' reaches full length
  const targetPin = isSettingPin && pin.value.length === PIN_LENGTH ? confirmPin : pin;

  if (targetPin.value.length < PIN_LENGTH) {
    targetPin.value += key;
  }
}

/** Resets all PIN buffers */
const onClear = () => {
  pin.value = ''
  confirmPin.value = ''
}

/** Handles digit deletion with support for confirmation buffer */
const onBackspace = () => {
  if (!authStore.tempHasPin && confirmPin.value.length > 0) {
    confirmPin.value = confirmPin.value.slice(0, -1);
  } else if (pin.value.length > 0) {
    pin.value = pin.value.slice(0, -1);
  }
}

// --- Computed Properties ---

/** @returns {string} Dynamic header title using resident data from store */
const title = computed(() => {
  const firstName = authStore.tempResident?.first_name || 'Resident'
  return `Welcome, ${firstName}`
})

/** @returns {string} Contextual instruction based on PIN registration status */
const subtitle = computed(() => {
  if (!authStore.tempHasPin) return 'Please set your 4-digit PIN'
  return 'Please enter your PIN to continue'
})

/** @returns {string} Formatted display of the PIN (Masked or Unmasked) */
const pinDisplay = computed(() => {
  if (pin.value.length === 0) return ''; 
  if (showPin.value) return pin.value;
  return '• '.repeat(pin.value.length).trim();
});

/** @returns {string} Formatted display of the confirmation PIN (Masked or Unmasked) */
const confirmPinDisplay = computed(() => {
  if (confirmPin.value.length === 0) return '';
  if (showPin.value) return confirmPin.value;
  return '• '.repeat(confirmPin.value.length).trim();
});

/** @returns {boolean} True if required buffers are filled according to current mode */
const isPinComplete = computed(() => {
  if (!authStore.tempHasPin) {
    return pin.value.length === PIN_LENGTH && confirmPin.value.length === PIN_LENGTH;
  }
  return pin.value.length === PIN_LENGTH;
});


/**
 * Final Submission Handler.
 * Routes to either 'set-pin' or 'verify-pin' endpoints based on store state.
 */
const submitPin = async () => {
  if (!isPinComplete.value) return;

  try {
    // WORKFLOW: PIN Registration
    if (!authStore.tempHasPin) {
      if (pin.value !== confirmPin.value) {
        triggerToast('PINs do not match.');
        onClear();
        return;
      }
      
      await api.post(`/kiosk/auth/set-pin`, { 
        resident_id: authStore.tempResident.id,
        pin: pin.value,
        rfid_uid: authStore.tempUid 
      })
      
      authStore.confirmRFIDLogin() 
      triggerToast('PIN set successfully!', true)
      setTimeout(() => router.replace('/home'), 1000);
      
    }
    // WORKFLOW: Standard Authentication
    else {
      const response = await api.post(`/kiosk/auth/verify-pin`, { 
        resident_id: authStore.tempResident.id,
        pin: pin.value
      })
      
      if (!response.data.valid) {
        triggerToast('Invalid PIN');
        onClear();
        return;
      }
      
      authStore.confirmRFIDLogin()
      triggerToast('Login successful!', true);
      router.replace('/home');
    }

  } catch (err) {
    triggerToast('An error occurred. Please try again.');
    onClear();
  }
}

/** Navigates back to the scanning interface */
const goBack = () => {
  router.push('/login-rfid');
}

// --- Lifecycle Hooks ---
onMounted(() => {
  // Security Guard: Redirect if no resident data exists in temp store
  if (!authStore.tempResident && !authStore.tempUid) {
    triggerToast('No session found. Please scan again.')
    setTimeout(() => router.push('/login-rfid'), 1500)
  }
})
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#003A6B] to-[#89CFF1] flex justify-center items-center font-poppins">
    <div class="bg-white w-[974px] h-[550px] rounded-lg shadow-2xl relative flex p-10">
      
      <Button 
        @click="goBack" 
        bgColor="bg-transparent"
        textColor="text-[#013C6D]"
        class="absolute bottom-10 left-10 w-auto px-4 text-[14px] rounded-[20px] h-[40px] border-2 border-[#013C6D] hover:bg-gray-100"
      >
        <span class="flex items-center gap-x-2">
          <ArrowLeftIcon class="h-5 w-5" />
          Go Back
        </span>
      </Button>

      <div class="w-1/2 flex flex-col text-[#013C6D] pr-12">
        <div class="flex items-center gap-3 mb-10">
          <img src="@/assets/images/Pob1Logo.svg" alt="Barangay Logo" class="w-14 h-14">
          <div>
            <h1 class="text-lg font-bold">Brgy. Poblacion I</h1>
            <p class="text-base font-light">Kiosk System</p>
          </div>
        </div>

        <div class="flex-grow flex flex-col justify-center items-center text-center">
          <div class="mb-20"> 
            <h2 class="text-4xl font-bold mb-1 leading-tight">{{ title }}</h2> 
            <p class="text-xl text-gray-500 leading-tight">{{ subtitle }}</p> 
          </div>
        </div>
      </div>

      <div class="w-1/2 flex flex-col items-center justify-center pl-12 border-l border-gray-200 relative">
        <div class="w-full max-w-xs">
          <label class="text-sm font-medium text-gray-500 mb-1">
            {{ !authStore.tempHasPin ? 'Enter New 4-digit PIN' : 'Enter 4-digit PIN' }}
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

          <template v-if="!authStore.tempHasPin">
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
                isPinComplete ? 'bg-[#013C6D] hover:bg-blue-800' : 'bg-gray-400 cursor-not-allowed'
            ]"
          >
            Authenticate
          </button>
        </div>

        <Transition name="toast">
          <div v-if="showToast" 
               class="absolute top-1/2 left-[55%] transform -translate-x-1/2 -translate-y-1/2 z-50 flex items-center gap-3 px-6 py-4 rounded-lg shadow-2xl border bg-white"
               :class="isSuccess ? 'border-green-500' : 'border-red-500 text-red-600'">
            <CheckCircleIcon v-if="isSuccess" class="w-8 h-8 text-green-500" />
            <XCircleIcon v-else class="w-8 h-8 text-red-500" />
            <span class="text-gray-800 font-semibold text-lg">{{ toastMessage }}</span>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>