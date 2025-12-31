<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import Keypad from '@/components/shared/Keypad.vue'
import { EyeIcon, EyeSlashIcon, XCircleIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'
import PrimaryButton from '@/components/shared/Button.vue' 
import { ArrowLeftIcon } from '@heroicons/vue/24/solid' 
import { useAuthStore } from '@/stores/auth' // Added
import api from '@/api/http' // Ensure this is correctly imported

const router = useRouter()
const authStore = useAuthStore() // Access the temp data here

const showToast = ref(false)
const toastMessage = ref('')
const isSuccess = ref(false)

const pin = ref('')
const confirmPin = ref('')

// Constants
const PIN_LENGTH = 4
const showPin = ref(false)

// --- Helper to show custom notification ---
const triggerToast = (message, success = false) => {
  toastMessage.value = message
  isSuccess.value = success
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 1500)
}

onMounted(() => {
  // Security check: If no temporary data exists, user shouldn't be here
  if (!authStore.tempResident && !authStore.tempUid) {
    triggerToast('No session found. Please scan again.')
    setTimeout(() => router.push('/login-rfid'), 1500)
  }
})

// --- Keypad Handlers ---
const onKeypress = (key) => {
  // Logic to decide which field to fill if setting a new PIN
  const isSettingPin = !authStore.tempHasPin;
  const targetPin = isSettingPin && pin.value.length === PIN_LENGTH ? confirmPin : pin;
  if (targetPin.value.length < PIN_LENGTH) {
    targetPin.value += key;
  }
}

const onClear = () => {
  pin.value = ''
  confirmPin.value = ''
}

const onBackspace = () => {
  if (!authStore.tempHasPin && confirmPin.value.length > 0) {
    confirmPin.value = confirmPin.value.slice(0, -1);
  } else if (pin.value.length > 0) {
    pin.value = pin.value.slice(0, -1);
  }
}

// --- Computed properties for display ---
const title = computed(() => {
  const firstName = authStore.tempResident?.first_name || 'Resident'
  return `Welcome, ${firstName}`
})

const subtitle = computed(() => {
  if (!authStore.tempHasPin) return 'Please set your 4-digit PIN'
  return 'Please enter your PIN to continue'
})

const pinDisplay = computed(() => {
  if (pin.value.length === 0) return ''; 
  if (showPin.value) return pin.value;
  return '• '.repeat(pin.value.length).trim();
});

const confirmPinDisplay = computed(() => {
  if (confirmPin.value.length === 0) return '';
  if (showPin.value) return confirmPin.value;
  return '• '.repeat(confirmPin.value.length).trim();
});

const isPinComplete = computed(() => {
  if (!authStore.tempHasPin) {
    return pin.value.length === PIN_LENGTH && confirmPin.value.length === PIN_LENGTH;
  }
  return pin.value.length === PIN_LENGTH;
});

// --- Submit Logic ---
const submitPin = async () => {
  if (!isPinComplete.value) return;

  try {
    if (!authStore.tempHasPin) {
      // Logic for Setting a PIN (If has_pin was false)
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
      
    } else {
      // Logic for Verifying a PIN (The most common path)
      const response = await api.post(`/kiosk/auth/verify-pin`, { 
        resident_id: authStore.tempResident.id,
        pin: pin.value
      })
      
      if (!response.data.valid) {
        triggerToast('Invalid PIN');
        onClear();
        return;
      }
      
      authStore.confirmRFIDLogin() // Promotes temp data to active data
      triggerToast('Login successful!', true);
      router.replace('/home');
    }

  } catch (err) {
    triggerToast('An error occurred. Please try again.');
    onClear();
  }
}

const goBack = () => {
  router.push('/login-rfid');
}
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#003A6B] to-[#89CFF1] flex justify-center items-center font-poppins">
    <div class="bg-white w-[974px] h-[550px] rounded-lg shadow-2xl relative flex p-10">
      
      <PrimaryButton 
        @click="goBack" 
        bgColor="bg-transparent"
        textColor="text-[#013C6D]"
        class="absolute bottom-10 left-10 w-auto px-4 text-[14px] rounded-[20px] h-[40px] border-2 border-[#013C6D] hover:bg-gray-100"
      >
        <span class="flex items-center gap-x-2">
          <ArrowLeftIcon class="h-5 w-5" />
          Go Back
        </span>
      </PrimaryButton>

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