<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api/api'
import { login } from '@/stores/auth'
import Keypad from '@/components/shared/Keypad.vue'
// MODIFIED: Removed SpeakerWaveIcon from imports
import { EyeIcon, EyeSlashIcon, XCircleIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'
import PrimaryButton from '@/components/shared/PrimaryButton.vue' 
import { ArrowLeftIcon } from '@heroicons/vue/24/solid' 

const router = useRouter()
const route = useRoute()

// --- Notification State ---
const showToast = ref(false)
const toastMessage = ref('')
const isSuccess = ref(false)

const pin = ref('')
const confirmPin = ref('')
const residentId = ref(null)
const residentName = ref('')
const hasPin = ref(false)
const isSettingPin = ref(false)
const mode = ref('user')
const ADMIN_PIN = '7890'
const PIN_LENGTH = 4

const showPin = ref(false)
let fullResidentData = null; 

// --- Helper to show custom notification instead of alert() ---
const triggerToast = (message, success = false) => {
  toastMessage.value = message
  isSuccess.value = success
  showToast.value = true
  
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}

onMounted(async () => {
  mode.value = route.query.mode || 'user'
  
  if (mode.value === 'admin') {
    residentName.value = 'Admin'
  } else {
    residentId.value = route.query.resident_id
    residentName.value = route.query.name || 'Resident' 
    
    if (!residentId.value) {
      triggerToast('No user ID found. Please scan RFID again.')
      setTimeout(() => router.push('/login-rfid'), 2000)
      return
    }

    try {
      const res = await api.get(`/users/${residentId.value}/pin`)
      hasPin.value = res.data.has_pin
      isSettingPin.value = !hasPin.value 
      
      const userRes = await api.get(`/users/${residentId.value}`)
      fullResidentData = userRes.data; 
      
    } catch (err) {
      triggerToast('Error checking user data. Please try again.')
    }
  }
})

// --- Keypad Handlers ---
const onKeypress = (key) => {
  const targetPin = isSettingPin.value && pin.value.length === PIN_LENGTH ? confirmPin : pin;
  if (targetPin.value.length < PIN_LENGTH) {
    targetPin.value += key;
  }
}

const onClear = () => {
  pin.value = ''
  confirmPin.value = ''
}

const onBackspace = () => {
  if (isSettingPin.value && confirmPin.value.length > 0) {
    confirmPin.value = confirmPin.value.slice(0, -1);
  } else if (pin.value.length > 0) {
    pin.value = pin.value.slice(0, -1);
  }
}

// --- Computed properties for display ---
const title = computed(() => {
  if (mode.value === 'admin') return 'Welcome, Admin'
  const firstName = residentName.value.split(' ')[0]
  return `Welcome, ${firstName}`
})

const subtitle = computed(() => {
  if (mode.value === 'admin') return 'Please enter your PIN to register'
  if (isSettingPin.value) return 'Please set your 4-digit PIN'
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
  if (mode.value === 'admin') return pin.value.length === PIN_LENGTH;
  
  if (isSettingPin.value) {
    return pin.value.length === PIN_LENGTH && confirmPin.value.length === PIN_LENGTH;
  }
  return pin.value.length === PIN_LENGTH;
});

// --- Submit Logic ---
const submitPin = async () => {
  if (!isPinComplete.value) return;

  if (mode.value === 'admin') {
    if (pin.value === ADMIN_PIN) {
      const userData = { name: 'Admin', isAdmin: true }
      login(userData)
      localStorage.setItem("auth_user", JSON.stringify({ user: userData, isGuest: false }));
      const uid = route.query.uid
      router.replace(`/register?uid=${uid}`)
    } else {
      triggerToast('Invalid Admin PIN')
      onClear();
    }
    return
  }

  try {
    if (isSettingPin.value) {
      if (pin.value !== confirmPin.value) {
        triggerToast('PINs do not match. Please try again.');
        onClear();
        return;
      }
      await api.post(`/users/${residentId.value}/pin`, { pin: pin.value })
      triggerToast('PIN set successfully!', true)
    } else {
      const res = await api.post(`/users/${residentId.value}/pin/verify`, { pin: pin.value })
      if (!res.data.valid) {
        triggerToast('Invalid PIN');
        onClear();
        return;
      }
      triggerToast('Login successful!', true);
    }

    if (fullResidentData) {
      fullResidentData.rfid_uid = route.query.uid;
    }
    
    login(fullResidentData)
    localStorage.setItem("auth_user", JSON.stringify({ user: fullResidentData, isGuest: false }));
    
    if (isSettingPin.value) {
      setTimeout(() => router.replace('/home'), 1000);
    } else {
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
        class="absolute bottom-10 left-10 w-auto px-4 text-[14px] rounded-[20px] h-[40px] border-2 border-[#013C6D] hover:bg-gray-100 transition-colors"
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
            <h1 class="text-lg font-bold">Brgy. Poblacion I, Amadeo, Cavite</h1>
            <p class="text-base font-light">Barangay Kiosk System</p>
          </div>
        </div>

        <div class="flex-grow flex flex-col justify-center items-center text-center">
          <div class="mb-20"> 
            <h2 class="text-4xl font-bold truncate mb-1 leading-tight">{{ title }}</h2> 
            <p class="text-xl text-gray-500 leading-tight">{{ subtitle }}</p> 
          </div>
          
          </div>
      </div>

      <div class="w-1/2 flex flex-col items-center justify-center pl-12 border-l border-gray-200">
        <div class="w-full max-w-xs">
          <label class="text-sm font-medium text-gray-500 self-start mb-1">
            {{ isSettingPin ? 'Enter New 4-digit PIN' : 'Enter 4-digit PIN' }}
          </label>
          <div class="relative w-full">
            <input
              :value="pinDisplay"
              type="text"
              readonly
              class="w-full h-14 bg-gray-50 border border-gray-300 rounded-lg text-3xl text-center font-light focus:outline-none focus:ring-2 focus:ring-blue-500"
              :class="showPin ? 'tracking-normal' : 'tracking-widest'"
              placeholder="" 
            />
            <button @click="showPin = !showPin" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
              <EyeIcon v-if="!showPin" class="w-6 h-6" />
              <EyeSlashIcon v-else class="w-6 h-6" />
            </button>
          </div>

          <template v-if="isSettingPin">
            <label class="text-sm font-medium text-gray-500 self-start mb-1 mt-4">Confirm 4-digit PIN</label>
            <div class="relative w-full">
              <input
                :value="confirmPinDisplay"
                type="text"
                readonly
                class="w-full h-14 bg-gray-50 border border-gray-300 rounded-lg text-3xl text-center font-light focus:outline-none focus:ring-2 focus:ring-blue-500"
                :class="[
                  showPin ? 'tracking-normal' : 'tracking-widest',
                  confirmPin.length > 0 && pin !== confirmPin ? 'border-red-500' : ''
                ]"
                placeholder="" 
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
                isPinComplete 
                  ? 'bg-[#013C6D] hover:bg-blue-800' 
                  : 'bg-gray-400 cursor-not-allowed'
            ]"
          >
            Authenticate
          </button>
        </div>
      </div>

    </div>

    <Transition name="toast">
      <div v-if="showToast" class="fixed top-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border-l-4 bg-white"
           :class="isSuccess ? 'border-green-500' : 'border-red-500'">
        <CheckCircleIcon v-if="isSuccess" class="w-6 h-6 text-green-500" />
        <XCircleIcon v-else class="w-6 h-6 text-red-500" />
        <span class="text-gray-700 font-medium">{{ toastMessage }}</span>
      </div>
    </Transition>

  </div>
</template>

<style scoped>
input::placeholder {
  color: transparent;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>