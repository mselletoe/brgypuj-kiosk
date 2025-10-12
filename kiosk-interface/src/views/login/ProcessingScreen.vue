<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeftIcon, SignalIcon } from '@heroicons/vue/24/solid'

// Initialize the router to handle navigation
const router = useRouter()

// Function to navigate to the previous page
const goBack = () => {
  // In a real app, this would also cancel the RFID reading process
  router.back()
}

// --- SIMULATION LOGIC ---
// In a real application, you would receive an event from your RFID hardware.
// To simulate a successful scan, we'll wait for 2.5 seconds after the page loads,
// then automatically navigate to the next step (the keypad).
onMounted(() => {
  setTimeout(() => {
    router.push('/login/keypad')
  }, 2500) // 2.5-second delay
})
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#0F4978] to-[#487090] flex justify-center items-center font-poppins">
    
    <div class="bg-white w-[974px] h-[550px] rounded-lg shadow-2xl relative flex flex-col justify-center items-center p-8">

      <div class="flex flex-col items-center text-center">
        <div class="bg-primary w-80 h-52 rounded-lg flex justify-center items-center animate-pulse">
          <SignalIcon class="h-24 w-24 text-white" />
        </div>

        <h2 class="text-3xl font-semibold text-primary mt-8">
          Processing...
        </h2>
        <p class="text-lg text-gray-500 mt-2">
          Keep your card held near the scanner
        </p>
      </div>

      <button @click="goBack" class="btn btn-ghost absolute bottom-8 left-8">
        <ArrowLeftIcon class="h-6 w-6" />
        Go Back
      </button>

    </div>
  </div>
</template>