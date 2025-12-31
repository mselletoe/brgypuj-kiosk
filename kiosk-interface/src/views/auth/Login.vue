<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { disableTouchToStart } from '@/composables/touchToStart'
import Button from '@/components/shared/Button.vue'
import { SignalIcon } from '@heroicons/vue/24/solid'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const timeLeft = ref(10)
let timerInterval = null
let mountTime = 0

const handleRfidLogin = () => {
  const timeSinceMount = Date.now() - mountTime;

  if (timeSinceMount < 500) {
    return;
  }

  disableTouchToStart()
  router.push('/login-rfid')
}

const continueAsGuest = () => {
  authStore.setGuest()
  router.replace('/home')
}

const startCountdown = () => {
  if (timerInterval) clearInterval(timerInterval)
  timeLeft.value = 10
  timerInterval = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      clearInterval(timerInterval)
      router.replace('/idle')
    }
  }, 1000)
}

const resetTimer = () => {
  startCountdown()
}

onMounted(() => {
  mountTime = Date.now()
  startCountdown()
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<template>
  <div 
    @click="resetTimer"
    class="h-screen w-screen bg-gradient-to-br from-[#003A6B] to-[#89CFF1] flex justify-center items-center font-poppins"
  >
    <div class="bg-white w-[974px] h-[550px] rounded-lg shadow-2xl relative flex flex-col justify-center items-center p-8">
      
      <img src="@/assets/images/Pob1Logo.svg" alt="Barangay Logo" class="h-[140px] w-[140px] mb-0 drop-shadow-lg">
      
      <div class="text-center text-gray-800">
        <h1 class="mt-1 text-5xl font-bold">Brgy. Poblacion I</h1>
        <p class="text-2xl">Amadeo, Cavite</p>
        <p class="text-[18px] italic mt-2">Barangay Kiosk System</p>
      </div>

      <div class="mt-5 flex flex-col gap-y-5">
        
        <Button 
          @click.stop="handleRfidLogin" 
          class="w-96 h-[80px] font-bold"
          variant="primary"
        >
          <span class="flex items-center justify-center gap-x-3 text-xl">
            Use RFID
            <SignalIcon class="h-8 w-8 mt-0" />
          </span>
        </Button>

        <Button 
          @click.stop="continueAsGuest()"
          variant="outline"
          class="w-96 h-[45px] text-[15px]"
        >
          Continue as Guest
        </Button>
        
      </div>

      <p class="mt-[20px] text-gray-400 text-xs font-light tracking-wide">
        Screen will close in {{ timeLeft }} seconds...
      </p>

    </div>
  </div>
</template>