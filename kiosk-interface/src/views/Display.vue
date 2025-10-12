<script setup>
import '@/assets/display.css'
import { onMounted, onUnmounted, ref } from 'vue'

// === added states and functions ===
const isMuted = ref(false)
const currentLang = ref('FIL')

const toggleMute = () => {
  isMuted.value = !isMuted.value
}

const toggleLang = () => {
  currentLang.value = currentLang.value === 'FIL' ? 'ENG' : 'FIL'
}

const goToAnnouncements = () => {
  window.location.href = '/announcements' // change to router.push('/announcements') if using Vue Router
}

onMounted(() => {
  document.body.classList.add('display-page')
  const header = document.querySelector('header')
  if (header) header.style.display = 'none'
})

onUnmounted(() => {
  document.body.classList.remove('display-page')
  const header = document.querySelector('header')
  if (header) header.style.display = ''
})
</script>

<template>
  <div class="flex items-center justify-center text-center 
                h-full w-full overflow-hidden relative select-none text-[#0c2d57]">
    
    <!-- === added content starts here === -->

    <!-- Top-right buttons -->
    <div class="absolute top-6 right-6 flex items-center gap-2">
      <!-- Mute -->
      <button
        @click="toggleMute"
        class="bg-[#0c2d57] text-white rounded-full p-2 shadow-md hover:opacity-90 transition"
        title="Toggle Sound"
      >
        <span v-if="!isMuted">🔊</span>
        <span v-else>🔇</span>
      </button>

      <!-- Language -->
      <button
        @click="toggleLang"
        class="bg-[#0c2d57] text-white font-semibold px-4 py-1 rounded-lg shadow-md hover:opacity-90 transition"
      >
        {{ currentLang }}
      </button>
    </div>

    <!-- Center text -->
    <div class="relative">
      <h1 class="text-[140px] tracking-tight font-bold
                  bg-gradient-to-r from-[#003E71] to-[#016BC6] 
                  bg-clip-text text-transparent">POBLACION I</h1>
      
      <h1 class="absolute top-0 left-0 text-[140px] tracking-tight font-bold text-transparent"
          style="-webkit-text-stroke: 1px rgba(0,0,0,0.1);
                  filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.9))">POBLACION I</h1>

      <h2 class="text-2xl font-semibold text-[#0c2d57] mt-2 tracking-wide">AMADEO, CAVITE</h2>

      <!-- Button -->
      <button
        @click="goToAnnouncements"
        class="mt-8 bg-white border-2 border-[#0c2d57] text-[#0c2d57] font-medium px-6 py-2 rounded-lg shadow-sm hover:bg-[#0c2d57] hover:text-white transition"
      >
        See Announcements
      </button>

      <!-- Text info -->
      <div class="mt-6 text-[16px] leading-tight">
        <p><strong>Emergency:</strong> 911</p>
        <p><strong>Barangay:</strong> (02) 123-4567</p>
        <p class="text-gray-600 mt-2">Touch the screen to start</p>
      </div>
    </div>

    <!-- Logo bottom-right -->
    <img
      src="@/assets/images/Pob1Logo.svg"  
      alt="Barangay Logo"
      class="absolute bottom-[-230px] right-[-100px] w-[600px] h-[600px] object-contain select-none pointer-events-none"
    />

  </div>
</template>
