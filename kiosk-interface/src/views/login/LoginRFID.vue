<script setup>
import { ref, onUnmounted } from 'vue' // <-- Import onUnmounted
import { useRouter } from 'vue-router'
import { ArrowLeftIcon, SignalIcon } from '@heroicons/vue/24/solid'

const router = useRouter()
const isScanning = ref(false)

// 1. A variable to hold the ID of our timer
let scanTimer = null

const goBack = () => {
  // 2. Before navigating, check if a timer is active and cancel it
  if (scanTimer) {
    clearTimeout(scanTimer)
  }
  router.push('/login')
}

const startScan = () => {
  isScanning.value = true

  // 3. Store the timer's ID in our variable
  scanTimer = setTimeout(() => {
    router.push('/login-keypad')
  }, 5000)
}

// 4. (Failsafe) This function runs automatically when the page is left
//    It ensures the timer is cancelled no matter how the user navigates away.
onUnmounted(() => {
  clearTimeout(scanTimer)
})
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#0F4878] to-[#487090] flex justify-center items-center font-poppins">
    
    <div class="bg-white w-[974px] h-[550px] rounded-lg shadow-2xl relative flex flex-col justify-center items-center p-8">

      <div class="flex flex-col items-center text-center">

        <div v-if="!isScanning" class="flex flex-col items-center">
          <div 
            @click="startScan" 
            class="bg-gray-200 w-80 h-52 rounded-lg flex justify-center items-center cursor-pointer hover:bg-gray-300 transition-colors"
          >
            <SignalIcon class="h-24 w-24 text-gray-400" />
          </div>

          <h2 class="text-3xl font-semibold text-gray-700 mt-8">
            Please tap your RFID
          </h2>
          <p class="text-lg text-gray-500 mt-2">
            Tap and Hold your card steady on the scanner.
          </p>
        </div>

        <div v-else class="flex flex-col items-center">
          <div class="bg-[#295B83] w-80 h-52 rounded-lg flex justify-center items-center">
            <SignalIcon class="h-24 w-24 text-white [animation:pulse_1s_infinite]" />
          </div>

          <h2 class="text-3xl font-semibold text-[#295B83] mt-8">
            Processing...
          </h2>
          <p class="text-lg text-gray-500 mt-2">
            Keep your card held near the scanner.
          </p>
        </div>
      </div>

      <button @click="goBack" class="btn btn-ghost absolute bottom-8 left-8">
        <ArrowLeftIcon class="h-6 w-6" />
        Go Back
      </button>

    </div>
  </div>
</template>