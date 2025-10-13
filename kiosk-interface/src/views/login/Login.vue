<script setup>
import { useRouter } from 'vue-router'
import { disableTouchToStart } from '@/composables/touchToStart'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import PrimaryButton from '@/components/shared/PrimaryButton.vue'
import { SignalIcon } from '@heroicons/vue/24/solid'

const router = useRouter()

const handleRfidLogin = () => {
  disableTouchToStart()
  router.push('/login-rfid')
}

const handleGuestLogin = () => {
  disableTouchToStart()
  router.push('/home')
}

const goBack = () => {
  router.push('/idle')
}
</script>

<template>
  <div class="h-screen w-screen bg-gradient-to-br from-[#003A6B] to-[#89CFF1] flex justify-center items-center font-poppins">
    <div class="bg-white w-[974px] h-[550px] rounded-lg shadow-2xl relative flex flex-col justify-center items-center p-8">
      
      <ArrowBackButton 
        @click="goBack"
        class="absolute top-6 left-6" 
      />

      <img src="@/assets/LogoTransparent.svg" alt="Barangay Logo" class="h-28 w-28 mb-3 drop-shadow-lg">
      
      <div class="text-center text-gray-800">
        <h1 class="mt-1 text-5xl font-bold">Brgy. Poblacion I</h1>
        <p class="text-2xl">Amadeo, Cavite</p>
        <p class="text-[18px] italic mt-2">Barangay Kiosk System</p>
      </div>

      <div class="mt-5 flex flex-col gap-y-5">
        
        <PrimaryButton 
          @click="handleRfidLogin" 
          class="w-96 h-[80px] text-[25px] font-bold"
        >
          <span class="flex items-center justify-center gap-x-3">
            Use RFID
            <SignalIcon class="h-8 w-8 mt-0" />
          </span>
        </PrimaryButton>

        <PrimaryButton 
          @click="handleGuestLogin"
          bgColor="bg-transparent"
          textColor="text-[#013C6D]"
          class="w-96 h-[45px] text-[15px]"
        >
          Continue as Guest
        </PrimaryButton>
        
      </div>
    </div>
  </div>
</template>