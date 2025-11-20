<script setup>
import { ref } from 'vue'

// We emit an event so the Parent (Idle.vue) knows to switch the view
const emit = defineEmits(['see-announcements'])

const isMuted = ref(false)
const currentLang = ref('FIL')

// --- Toggle buttons ---
const toggleMute = () => (isMuted.value = !isMuted.value)
const toggleLang = () => (currentLang.value = currentLang.value === 'FIL' ? 'ENG' : 'FIL')

const handleSeeAnnouncements = () => {
  emit('see-announcements')
}
</script>

<template>
  <div class="display-page flex items-center justify-center text-center h-full w-full overflow-hidden relative select-none text-[#0c2d57]">
    
    <div class="absolute top-6 right-6 flex items-center gap-2">
      <button 
        @click.stop="toggleMute" 
        class="bg-[#0c2d57] text-white rounded-full p-2 shadow-md hover:opacity-90 transition" 
        title="Toggle Sound"
      >
        <span v-if="!isMuted">🔊</span>
        <span v-else>🔇</span>
      </button>

      <button 
        @click.stop="toggleLang" 
        class="bg-[#0c2d57] text-white font-semibold px-4 py-1 rounded-lg shadow-md hover:opacity-90 transition"
      >
        {{ currentLang }}
      </button>
    </div>

    <div class="text-left">
      <h1 class="text-[140px] tracking-tight font-bold bg-gradient-to-r from-[#003E71] to-[#016BC6] bg-clip-text text-transparent drop-shadow-[3px_3px_5px_rgba(0,0,0,0.5)]">
        POBLACION I
      </h1>
      <h2 class="text-[60px] leading-[1] font-semibold text-[#0c2d57] -mt-10 bg-gradient-to-r from-[#003E71] to-[#016BC6] bg-clip-text text-transparent tracking-wide drop-shadow-[3px_3px_5px_rgba(0,0,0,0.5)]">
        AMADEO, CAVITE
      </h2>

      <button
        @click.stop="handleSeeAnnouncements"
        class="mt-8 bg-transparent border-2 border-[#003E71] text-[13px] text-[#003E71] font-bold px-6 py-2 rounded-lg shadow-sm hover:bg-[#003E71] hover:text-white transition-colors duration-300 ease-in-out"
      >
        See Announcements
      </button>

      <div class="mt-6 text-[22px] text-[#003E71] font-bold leading-tight">
        <p><strong>Emergency:</strong> 911</p>
        <p><strong>Barangay:</strong> (02) 123-4567</p>
      </div>
    </div>

    <div class="absolute bottom-11 left-[80px] text-[#8EC3EF] text-xl font-semibold animate-pulse">
      Touch anywhere to start
    </div>

    <img src="@/assets/images/Pob1Logo.svg" alt="Barangay Logo"
      class="absolute bottom-[-230px] right-[-100px] w-[600px] h-[600px] object-contain select-none pointer-events-none"
    />
  </div>
</template>

<style scoped>
.display-page {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: hidden;
  background: radial-gradient(circle at top left, #3291E3 0%, #ffffff 44%);
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
  background-attachment: local;
  font-family: 'Poppins', sans-serif;
}
</style>