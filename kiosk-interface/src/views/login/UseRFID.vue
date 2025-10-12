<script setup>
import { useRouter } from 'vue-router'
import { ArrowLeftIcon, SignalIcon } from '@heroicons/vue/24/solid'

// Initialize the router to handle navigation
const router = useRouter()

// Function to navigate to the previous page
const goBack = () => {
  router.back()
}
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#0F4978] to-[#487090] flex justify-center items-center font-poppins">
    
    <div class="bg-white w-[974px] h-[550px] rounded-lg shadow-2xl relative flex flex-col justify-center items-center p-8">

      <div class="flex flex-col items-center">
        <div class="bg-gray-200 w-80 h-52 rounded-lg flex justify-center items-center">
          <SignalIcon class="h-24 w-24 text-gray-400" />
        </div>

        <h2 class="text-3xl font-semibold text-gray-700 mt-8">
          Please tap your RFID
        </h2>
      </div>

      <button @click="goBack" class="btn btn-ghost absolute bottom-8 left-8">
        <ArrowLeftIcon class="h-6 w-6" />
        Go Back
      </button>

    </div>
  </div>
</template>