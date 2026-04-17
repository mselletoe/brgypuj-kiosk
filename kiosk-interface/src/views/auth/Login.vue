<script setup>
/**
 * @file views/auth/Login.vue
 * @description Kiosk login selection screen. Presented after the idle/touch-to-start
 * screen. Allows the user to authenticate via RFID or continue as a guest.
 * Auto-returns to the idle screen after a 10-second inactivity countdown.
 * Any click on the screen resets the countdown.
 */

import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { disableTouchToStart } from '@/composables/touchToStart'
import { useSystemConfig } from '@/composables/useSystemConfig'
import Button from '@/components/shared/Button.vue'
import { SignalIcon } from '@heroicons/vue/24/solid'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { brgyName, brgySubname, resolvedLogoUrl } = useSystemConfig()
const { t } = useI18n()

const timeLeft = ref(10)
let timerInterval = null
let mountTime = 0

// =============================================================================
// ACTIONS
// =============================================================================
const handleRfidLogin = () => {
  if (Date.now() - mountTime < 500) return
  disableTouchToStart()
  router.push('/login-rfid')
}

const continueAsGuest = () => {
  authStore.setGuest()
  router.replace('/home')
}

// =============================================================================
// INACTIVITY COUNTDOWN
// =============================================================================
const stopCountdown = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

const startCountdown = () => {
  stopCountdown()
  timeLeft.value = 10
  timerInterval = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      stopCountdown()
      router.replace('/idle')
    }
  }, 1000)
}

const resetTimer = () => startCountdown()

// =============================================================================
// LIFECYCLE
// =============================================================================
onMounted(() => {
  mountTime = Date.now()
  startCountdown()
})

// KeepAlive keeps this component alive even when navigating away, so
// onUnmounted never fires and timerInterval keeps running — causing it to
// redirect to /idle while the user is on /login-rfid or /auth-pin.
// Watching the route and stopping the countdown when we leave /login fixes this.
watch(
  () => route.path,
  (newPath) => {
    if (newPath !== '/login') stopCountdown()
    else startCountdown()
  }
)

// Still clean up on true unmount (e.g. if KeepAlive max is exceeded)
onUnmounted(() => stopCountdown())
</script>

<template>
  <div @click="resetTimer" class="h-screen w-screen bg-gradient-to-br from-[#003A6B] to-[#89CFF1] flex justify-center items-center font-poppins">
    <div class="bg-white w-[974px] h-[550px] rounded-lg shadow-2xl relative flex flex-col justify-center items-center p-8">

      <img v-if="resolvedLogoUrl" :src="resolvedLogoUrl" alt="Barangay Logo" class="h-[120px] w-[120px] min-w-[120px] object-cover rounded-full mb-0 drop-shadow-lg">

      <div class="flex flex-col gap-2 mt-2 text-center text-gray-800">
        <h1 class="mt-3 text-5xl font-bold">{{ brgyName }}</h1>
        <p class="text-xl">{{ brgySubname }}</p>
      </div>

      <div class="mt-5 flex flex-col gap-y-5">
        <Button @click.stop="handleRfidLogin" class="w-96 h-[80px] font-bold" variant="primary">
          <span class="flex items-center justify-center gap-x-3 text-xl">
            {{ t('useRFID') }}
            <SignalIcon class="h-8 w-8 mt-0" />
          </span>
        </Button>

        <Button @click.stop="continueAsGuest()" variant="outline" class="w-96 h-[45px] text-[15px]">
          {{ t('continueAsGuest') }}
        </Button>
      </div>

      <p class="mt-[20px] text-gray-400 text-xs font-light tracking-wide">
        {{ t('screenCloses', { n: timeLeft }) }}
      </p>

    </div>
  </div>
</template>