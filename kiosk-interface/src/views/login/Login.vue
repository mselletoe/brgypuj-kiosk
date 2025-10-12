<script setup>
// No script logic is needed for this static page yet.
// This is where you would add functions for button clicks later.
// For example:
// import { useRouter } from 'vue-router'
// const router = useRouter()
// const handleRfidLogin = () => { router.push('/rfid-scan') }
// const handleGuestLogin = () => { router.push('/services') }
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#003A6B] to-[#89CFF1] flex justify-center items-center font-poppins">
    
    <div class="bg-white w-[974px] h-[550px] rounded-lg shadow-2xl flex flex-col justify-center items-center p-8">
      
      <img src="@/assets/LogoTransparent.svg" alt="Barangay Logo" class="h-28 w-28 mb-4">
      
      <div class="text-center text-gray-800">
        <h1 class="text-4xl font-bold">Brgy. Poblacion I</h1>
        <p class="text-2xl mt-1">Amadeo, Cavite</p>
        <p class="text-xl italic mt-4">Barangay Kiosk System</p>
      </div>

      <div class="mt-12 flex flex-col gap-y-5">
        
        <button class="btn btn-primary btn-lg w-80 h-20 text-2xl">
          Use RFID
        </button>

        <button class="btn btn-outline btn-lg w-80 h-20 text-2xl">
          Continue as Guest
        </button>

      </div>
    </div>
  </div>
</template>