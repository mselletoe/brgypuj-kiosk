<script setup>
/**
 * @file Login.vue
 * @description Main entry point for the Kiosk authentication selection. 
 * Allows users to choose between RFID authentication or Guest access.
 * Includes an automated session timeout to return the kiosk to the Idle state.
 */

import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { disableTouchToStart } from '@/composables/touchToStart'
import Button from '@/components/shared/Button.vue'
import { SignalIcon } from '@heroicons/vue/24/solid'
import { useAuthStore } from '@/stores/auth'

// --- Component State & Composables ---
const router = useRouter()
const authStore = useAuthStore()

/** @type {import('vue').Ref<number>} Seconds remaining before auto-redirect */
const timeLeft = ref(10)

/** @type {ReturnType<typeof setInterval> | null} Reference to the countdown timer */
let timerInterval = null

/** @type {number} Timestamp used to prevent accidental double-clicks during transition */
let mountTime = 0

// --- Logic & Handlers ---

/**
 * Handles navigation to the RFID scanning interface.
 * Implements a 500ms debounce to prevent "ghost touches" from the Idle screen.
 */
const handleRfidLogin = () => {
  const timeSinceMount = Date.now() - mountTime;

  // Prevent immediate execution if triggered too fast after mount
  if (timeSinceMount < 500) {
    return;
  }

  disableTouchToStart()
  router.push('/login-rfid')
}

/**
 * Initializes a Guest session.
 * Bypasses RFID authentication and sets the global auth mode to 'guest'.
 */
const continueAsGuest = () => {
  authStore.setGuest()
  router.replace('/home')
}

/**
 * Manages the inactivity countdown.
 * Automatically redirects the application to the Idle screen if no action is taken.
 */
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

/**
 * Resets the inactivity timer. 
 * Invoked on user interaction to prevent premature session termination.
 */
const resetTimer = () => {
  startCountdown()
}

// --- Lifecycle Hooks ---

onMounted(() => {
  mountTime = Date.now()
  startCountdown()
})

onUnmounted(() => {
  // Ensure background intervals are cleared to prevent memory leaks
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