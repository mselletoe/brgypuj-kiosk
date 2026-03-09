<script setup>
import { ref } from 'vue'
import { useSystemConfig } from '@/composables/useSystemConfig'

const emit = defineEmits(['see-announcements'])
const currentLang = ref('FIL')
const { resolvedLogoUrl } = useSystemConfig()

const toggleLang = () => (currentLang.value = currentLang.value === 'FIL' ? 'ENG' : 'FIL')
</script>

<template>
  <div class="display-page flex items-center justify-center text-center relative select-none text-[#0c2d57]">
    
    <div class="absolute top-8 right-10 flex items-center gap-4 z-20">
      <div
        @click.stop="toggleLang"
        class="w-36 h-12 bg-[#49759B] rounded-2xl flex cursor-pointer p-1"
        style="position: relative;"
      >
        <div
          class="rounded-xl bg-white"
          style="
            position: absolute;
            top: 4px;
            bottom: 4px;
            width: calc(50% - 4px);
            transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
          "
          :style="{
            transform: currentLang === 'ENG' ? 'translateX(calc(100% + 0px))' : 'translateX(0px)'
          }"
        ></div>

        <div
          class="flex-1 flex items-center justify-center font-bold rounded-xl"
          style="position: relative; z-index: 1; transition: color 0.3s ease;"
          :style="{ color: currentLang === 'FIL' ? '#49759B' : 'white' }"
        >
          FIL
        </div>
        <div
          class="flex-1 flex items-center justify-center font-bold rounded-xl"
          style="position: relative; z-index: 1; transition: color 0.3s ease;"
          :style="{ color: currentLang === 'ENG' ? '#49759B' : 'white' }"
        >
          ENG
        </div>
      </div>
    </div>

    <div class="text-left">
      <h1 class="text-[140px] tracking-tight font-bold bg-gradient-to-r from-[#003E71] to-[#016BC6] bg-clip-text text-transparent drop-shadow-lg">
        POBLACION I
      </h1>
      <h2 class="text-[60px] leading-none font-semibold -mt-10 bg-gradient-to-r from-[#003E71] to-[#016BC6] bg-clip-text text-transparent tracking-wide drop-shadow-lg">
        AMADEO, CAVITE
      </h2>

      <button
        @click.stop="emit('see-announcements')"
        class="mt-8 border-2 border-[#003E71] text-[13px] text-[#003E71] font-bold px-6 py-2 rounded-lg hover:bg-[#003E71] hover:text-white transition-all"
      >
        See Announcements
      </button>

      <div class="mt-6 text-[22px] text-[#003E71] font-bold">
        <p>Emergency: 911</p>
        <p>Barangay: (02) 123-4567</p>
      </div>

      <div class="mt-10 text-[#6399c5] text-xl font-medium animate-pulse">
        Touch anywhere to start
      </div>      
    </div>

    <img
      :src="resolvedLogoUrl"
      alt="Barangay Logo"
      class="absolute -bottom-56 -right-24 w-[600px] h-[600px] object-cover rounded-full opacity-50 pointer-events-none"
    />
  </div>
</template>

<style scoped>
.display-page {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background: radial-gradient(circle at top left, #3291E3 0%, #ffffff 44%);
  font-family: 'Poppins', sans-serif;
}
</style>