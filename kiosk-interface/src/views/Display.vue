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

const goToAnnouncements = (event) => {
  event.stopPropagation() 
  window.location.href = '/announcements' // use router.push('/announcements') if using Vue Router
}

// ✅ Added function for "touch anywhere to start"
const goToLogin = () => {
  window.location.href = '/login'
}

onMounted(() => {
  document.body.classList.add('display-page')
  const header = document.querySelector('header')
  if (header) header.style.display = 'none'

  const handleScreenTouch = (event) => {
    // Prevent if user clicked the announcements button
    if (event.target.closest('button')) return
    goToLogin()
  }

  window.addEventListener('click', handleScreenTouch)
  window.addEventListener('touchstart', handleScreenTouch)

  onUnmounted(() => {
    window.removeEventListener('click', handleScreenTouch)
    window.removeEventListener('touchstart', handleScreenTouch)
  })
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
    <div class="text-left">
      <h1 class="text-[140px] tracking-tight font-bold 
                 bg-gradient-to-r from-[#003E71] to-[#016BC6] 
                 bg-clip-text text-transparent drop-shadow-[3px_3px_5px_rgba(0,0,0,0.5)]">
        POBLACION I
      </h1>

      <h2 class="text-[60px] leading-[1] font-semibold 
                 text-[#0c2d57] -mt-10 
                 bg-gradient-to-r from-[#003E71] to-[#016BC6] 
                 bg-clip-text text-transparent 
                 tracking-wide drop-shadow-[3px_3px_5px_rgba(0,0,0,0.5)]">
        AMADEO, CAVITE
      </h2>

      <!-- Button -->
      <button
        @click="goToAnnouncements"
        class="mt-8 bg-transparent border-2 border-[#003E71] text-[13px] 
               text-[#003E71] font-bold px-6 py-2 rounded-lg shadow-sm 
               hover:bg-[#003E71] hover:text-white
               transition-colors duration-300 ease-in-out">
        See Announcements
      </button>

      <!-- Text info -->
      <div class="mt-6 text-[22px] text-[#003E71] font-bold leading-tight">
        <p><strong>Emergency:</strong> 911</p>
        <p><strong>Barangay:</strong> (02) 123-4567</p>
      </div>

      <!-- Touch prompt -->
      <div class="text-[#8EC3EF] mt-2 text-left">
        <p class="font-normal animate-pulse">Touch the screen to start</p>
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
