<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/api/api'
import { login } from '@/stores/auth'
import Keypad from '@/components/shared/Keypad.vue'
import { EyeIcon, EyeSlashIcon } from '@heroicons/vue/24/outline'
// MODIFIED: Import your ArrowBackButton
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue' 

const router = useRouter()
const route = useRoute()

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

onMounted(async () => {
  mode.value = route.query.mode || 'user'
  
  if (mode.value === 'admin') {
    residentName.value = 'Admin'
  } else {
    residentId.value = route.query.resident_id
    residentName.value = route.query.name || 'Resident' 
    
    if (!residentId.value) {
      alert('No user ID found. Please scan RFID again.')
      router.push('/login-rfid')
      return
    }

    try {
      const res = await api.get(`/users/${residentId.value}/pin`)
      hasPin.value = res.data.has_pin
      isSettingPin.value = !hasPin.value 
      
      const userRes = await api.get(`/users/${residentId.value}`)
      fullResidentData = userRes.data; 
      
    } catch (err)
 {
      alert('Error checking user data. Please try again.')
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
  if (showPin.value) return pin.value;
  let display = '• '.repeat(pin.value.length);
  display += '– '.repeat(PIN_LENGTH - pin.value.length);
  return display.trim();
});

const confirmPinDisplay = computed(() => {
  if (showPin.value) return confirmPin.value;
  let display = '• '.repeat(confirmPin.value.length);
  display += '– '.repeat(PIN_LENGTH - confirmPin.value.length);
  return display.trim();
});

// --- Submit Logic ---
const submitPin = async () => {
  if (pin.value.length !== PIN_LENGTH) {
    return alert(`PIN must be ${PIN_LENGTH} digits.`);
  }

  // Admin Mode
  if (mode.value === 'admin') {
    if (pin.value === ADMIN_PIN) {
      const userData = { name: 'Admin', isAdmin: true }
      login(userData)
      localStorage.setItem("auth_user", JSON.stringify({ user: userData, isGuest: false }));
      const uid = route.query.uid
      router.replace(`/register?uid=${uid}`)
    } else {
      alert('❌ Invalid Admin PIN')
      onClear();
    }
    return
  }

  // User Mode
  try {
    if (isSettingPin.value) {
      if (pin.value !== confirmPin.value) {
        alert('PINs do not match. Please try again.');
        onClear();
        return;
      }
      await api.post(`/users/${residentId.value}/pin`, { pin: pin.value })
      alert('✅ PIN set successfully!')
    } else {
      const res = await api.post(`/users/${residentId.value}/pin/verify`, { pin: pin.value })
      if (!res.data.valid) {
        alert('❌ Invalid PIN');
        onClear();
        return;
      }
    }

    if (fullResidentData) {
      fullResidentData.rfid_uid = route.query.uid;
    }
    
    login(fullResidentData)
    localStorage.setItem("auth_user", JSON.stringify({ user: fullResidentData, isGuest: false }));
    router.replace('/home')

  } catch (err) {
    alert('An error occurred. Please try again.');
    onClear();
  }
}

const goBack = () => {
  router.push('/login-rfid'); // Go back to the scan page
}
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#003A6B] to-[#89CFF1] flex justify-center items-center font-poppins">
    
    <div class="bg-white w-[974px] h-[550px] rounded-lg shadow-2xl flex p-10 relative">
      
      <ArrowBackButton 
        @click="goBack"
        class="absolute top-6 left-6" 
      />

      <div class="w-1/2 flex flex-col text-[#013C6D] pr-12">
        <div class="flex items-center gap-3 mb-10">
          <img src="@/assets/images/Pob1Logo.svg" alt="Barangay Logo" class="w-14 h-14">
          <div>
            <h1 class="text-lg font-bold">Brgy. Poblacion I, Amadeo, Cavite</h1>
            <p class="text-base font-light">Barangay Kiosk System</p>
          </div>
        </div>

        <div class="flex-grow flex flex-col justify-center items-center text-center">
          <h2 class="text-4xl font-bold truncate">{{ title }}</h2>
          <p class="text-xl text-gray-500 mt-2">{{ subtitle }}</p>
          
          <button v-if="mode === 'admin'" class="w-16 h-16 rounded-full border-2 border-gray-400 text-gray-500 flex items-center justify-center mt-8 hover:bg-gray-100 transition-colors">
            <SpeakerWaveIcon class="w-8 h-8" />
          </button>
        </div>
      </div>

      <div class="w-1/2 flex flex-col items-center justify-between pl-12 border-l border-gray-200">
        <div class="w-full max-w-xs">
          <label class="text-sm font-medium text-gray-500 self-start mb-1">
            {{ isSettingPin ? 'Enter 4-digit PIN' : 'Enter 4-digit PIN' }}
          </label>
          <div class="relative w-full">
            <input
              :value="pinDisplay"
              type="text"
              readonly
              class="w-full h-14 bg-gray-50 border border-gray-300 rounded-lg text-3xl text-center font-light focus:outline-none focus:ring-2 focus:ring-blue-500"
              :class="showPin ? 'tracking-normal' : 'tracking-widest'"
              placeholder="– – – –"
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
                placeholder="– – – –"
              />
            </div>
          </template>
        </div>
        
        <div class="w-full max-w-xs">
          <Keypad @press="onKeypress" @clear="onClear" @backspace="onBackspace" class="mt-4" />
          
          <button 
            @click="submitPin" 
            class="btn-primary w-full h-14 text-xl font-semibold rounded-lg mt-4 bg-[#013C6D] text-white hover:bg-blue-800"
          >
            Authenticate
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* Scoping placeholder styles to this component */
input::placeholder {
  color: #d1d5db; /* gray-300 */
  letter-spacing: 0.5em; 
  font-weight: 300;
  text-align: center;
  padding-left: 0.5em; /* Adjusts for centering */
}
</style>