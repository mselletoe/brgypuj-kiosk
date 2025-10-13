<script setup>
import { useRouter } from 'vue-router'
import { disableTouchToStart } from '@/composables/touchToStart'

const router = useRouter()

// Sample code ko lang 'to while re-routing kanina. So you can replace this with your code na.
// But make sure to take note of this block sa baba.
const handleRfidLogin = () => {
  disableTouchToStart()
  router.push('/login-rfid')
}

const handleGuestLogin = () => {
  disableTouchToStart()
  router.push('/home')
}
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
        <button @click="handleRfidLogin" class="btn btn-primary btn-lg w-80 h-20 text-2xl">
          Use RFID
        </button>
        <button @click="handleGuestLogin" class="btn btn-outline btn-lg w-80 h-20 text-2xl">
          Continue as Guest
        </button>
      </div>
    </div>
  </div>
</template>