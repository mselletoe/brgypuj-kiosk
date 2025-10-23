<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeftIcon, SignalIcon } from '@heroicons/vue/24/solid'
import PrimaryButton from '@/components/shared/PrimaryButton.vue'
import api from '@/api/api'
import { login } from '@/stores/auth'

const router = useRouter()
const scannedUID = ref('')
const isProcessing = ref(false)
let inputBuffer = ''
let timeout = null
const hiddenInput = ref(null)

const checkRFID = async (uid) => {
  try {
    const { data } = await api.get(`/rfid/check/${uid}`)

    if (data.exists) {
      const userRes = await api.get(`/users/${data.resident_id}`);

      const userData = {
        id: data.resident_id,
        name: `${userRes.data.first_name} ${userRes.data.last_name}`,
      };

      login(userData);

      localStorage.setItem('auth_user', JSON.stringify({ user: userData, isGuest: false }));

      router.replace({
        path: '/login-pin',
        query: { resident_id: data.resident_id },
      });
    } else {
      router.push(`/register?uid=${uid}`)
    }
  } catch (error) {
    router.push('/register')
  }
}

const handleRFIDInput = (event) => {
  const key = event.key

  if (isProcessing.value) return

  if (key === 'Enter') {
    const uid = inputBuffer.trim()
    if (!uid) return

    scannedUID.value = uid

    isProcessing.value = true
    checkRFID(uid)

    inputBuffer = ''
    if (hiddenInput.value) hiddenInput.value.value = ''
  } 
  else if (/^[0-9A-Za-z]$/.test(key)) {
    inputBuffer += key
  }

  clearTimeout(timeout)
  timeout = setTimeout(() => {
    inputBuffer = ''
  }, 1000)
}

const goBack = () => {
  router.push('/login')
}

onMounted(async () => {
  await nextTick()
  if (hiddenInput.value) hiddenInput.value.focus()
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

      <!-- Main Content -->
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

      <!-- Hidden Input (for keyboard emulator scanners) -->
      <input
        ref="hiddenInput"
        v-model="scannedUID"
        type="text"
        class="absolute opacity-0 pointer-events-none"
      />

      <!-- Back Button -->
      <PrimaryButton 
        @click="goBack" 
        bgColor="bg-transparent"
        textColor="text-[#013C6D]"
        class="absolute bottom-8 left-8 w-auto px-4 text-[14px] rounded-[20px] h-[40px]"
      >
        <span class="flex items-center gap-x-2">
          <ArrowLeftIcon class="h-5 w-5" />
          Go Back
        </span>
      </PrimaryButton>
    </div>
  </div>
</template>