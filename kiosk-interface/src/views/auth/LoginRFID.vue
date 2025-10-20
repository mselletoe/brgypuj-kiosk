<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeftIcon, SignalIcon } from '@heroicons/vue/24/solid'
import PrimaryButton from '@/components/shared/PrimaryButton.vue'
import api from '@/api/api' // your axios instance

const router = useRouter()
const isScanning = ref(false)
const scannedUID = ref('')
const isProcessing = ref(false)

let inputBuffer = ''
let timeout = null

const startScan = () => {
  isScanning.value = true
  isProcessing.value = false
  scannedUID.value = ''
  inputBuffer = ''
  console.log('%c[RFID Scanner Ready]', 'color: #007ACC; font-weight: bold;')
}

const handleRFIDInput = (event) => {
  // Log every key
  console.log('[DEBUG] Key pressed:', event.key);

  if (!isScanning.value) return;

  const key = event.key;

  if (key === 'Enter') {
    const uid = inputBuffer.trim();
    console.log('[DEBUG] Enter detected, full buffer:', uid);
    if (!uid) return;

    scannedUID.value = uid;
    console.log('✅ RFID UID Detected:', uid);

    // Switch to processing mode
    isProcessing.value = true;
    isScanning.value = false;

    // TODO: call backend here later
    inputBuffer = '';
  } else if (/^[0-9A-Za-z]$/.test(key)) {
    // Only add valid characters
    inputBuffer += key;
  }

  clearTimeout(timeout);
  timeout = setTimeout(() => {
    inputBuffer = '';
  }, 1500);
};


const goBack = () => {
  router.push('/login')
}

onMounted(() => {
  window.addEventListener('keydown', handleRFIDInput);
  window.focus(); // ensures focus when page loads
});


onUnmounted(() => {
  window.removeEventListener('keydown', handleRFIDInput)
  clearTimeout(timeout)
})
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#003A6B] to-[#89CFF1] flex justify-center items-center font-poppins">
    <div class="bg-white w-[974px] h-[550px] rounded-lg shadow-2xl relative flex flex-col justify-center items-center p-8">
      <div class="flex flex-col items-center text-center">
        <div v-if="!isScanning && !isProcessing" class="flex flex-col items-center">
          <div 
            @click="startScan" 
            class="bg-gray-200 w-80 h-52 rounded-lg flex justify-center items-center cursor-pointer hover:bg-gray-300 transition-colors"
          >
            <SignalIcon class="h-24 w-24 text-gray-400" />
          </div>
          <h2 class="text-3xl font-semibold text-gray-700 mt-8">
            Please tap your RFID
          </h2>
          <p class="text-lg text-gray-500 mt-2">Tap and hold your card steady on the scanner.</p>
        </div>

        <div v-else-if="isProcessing" class="flex flex-col items-center">
          <div class="bg-[#1B5886] w-80 h-52 rounded-lg flex justify-center items-center">
            <SignalIcon class="h-24 w-24 text-white animate-[pulse_1s_infinite]" />
          </div>
          <h2 class="text-3xl font-semibold text-[#295B83] mt-8">Processing...</h2>
          <p class="text-lg text-gray-500 mt-2">Keep your card near the scanner.</p>
        </div>
      </div>

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