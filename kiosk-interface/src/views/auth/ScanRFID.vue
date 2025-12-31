<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeftIcon, SignalIcon } from '@heroicons/vue/24/solid'
import Button from '@/components/shared/Button.vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/http'

const router = useRouter()
const authStore = useAuthStore()
const scannedUID = ref('')
const isProcessing = ref(false)
const hiddenInput = ref(null)
let inputBuffer = ''
let timeout = null

const resetScanner = () => {
  isProcessing.value = false
  inputBuffer = ''
  scannedUID.value = ''
  if (hiddenInput.value) hiddenInput.value.value = ''
}

const authenticateRFID = async (uid) => {
  try {
    isProcessing.value = true

    // 1. Backend Call
    const res = await api.post('kiosk/auth/rfid', { rfid_uid: uid })
    const data = res.data

    if (data.has_pin) {
      // 2. PIN exists: Store temporary data and redirect to PIN page
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
      // 3. Handle residents with no PIN (Security Policy)
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

const goBack = () => {
  router.replace('/login')
}

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