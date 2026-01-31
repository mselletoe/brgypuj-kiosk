<script setup>
import { ref } from 'vue'
import { SpeakerWaveIcon, SpeakerXMarkIcon } from '@heroicons/vue/24/solid'
import logoPath from '@/assets/images/Pob1Logo.svg'

const isMuted = ref(false)
const currentLang = ref('FIL')

const toggleMute = () => (isMuted.value = !isMuted.value)
const toggleLang = () => (currentLang.value = currentLang.value === 'FIL' ? 'ENG' : 'FIL')
</script>

<template>
  <div class="announcement-page w-full h-screen overflow-hidden">
    <header class="flex items-center justify-between px-10 py-6">
      
      <div class="flex items-center gap-4 text-[#013C6D]">
        <img :src="logoPath" alt="Brgy Logo" class="w-[60px] h-[60px] object-contain" />
        <div class="flex flex-col justify-center">
          <h1 class="text-[18px] font-extrabold leading-tight tracking-tight uppercase">
            Brgy. Poblacion I
          </h1>
          <p class="text-[16px] font-medium leading-tight opacity-90">
            Amadeo, Cavite - Kiosk System
          </p>
        </div>
      </div>

      <div class="flex items-center gap-5">
        <button 
          @click="toggleMute" 
          class="bg-[#49759B] text-white rounded-full p-2.5 shadow-lg active:scale-95 transition-all"
        >
          <component :is="isMuted ? SpeakerXMarkIcon : SpeakerWaveIcon" class="h-7 w-7" />
        </button>

        <div 
          @click="toggleLang" 
          class="relative w-36 h-12 bg-[#49759B] rounded-2xl flex items-center cursor-pointer p-1.5 shadow-md"
        >
          <div 
            class="absolute h-9 w-[46%] bg-white rounded-xl transition-all duration-300 ease-in-out"
            :style="{ transform: currentLang === 'FIL' ? 'translateX(0)' : 'translateX(105%)' }"
          ></div>

          <div class="relative flex w-full font-bold text-[0.95rem] z-10 pointer-events-none">
            <span 
              class="flex-1 text-center transition-colors duration-300" 
              :class="currentLang === 'FIL' ? 'text-[#49759B]' : 'text-white'"
            >FIL</span>
            <span 
              class="flex-1 text-center transition-colors duration-300" 
              :class="currentLang === 'ENG' ? 'text-[#49759B]' : 'text-white'"
            >ENG</span>
          </div>
        </div>
      </div>

    </header>

    <main>
        <div>
            <!-- Arrowbackbutton and title -->
        </div>
        <div>
            <!-- Main Content here -->
        </div>
    </main>
  </div>
</template>

<style scoped>
.announcement-page {
  background: radial-gradient(circle at top left, #3291E3 0%, #ffffff 44%);
}
</style>