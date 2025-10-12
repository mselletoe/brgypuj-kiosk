<script setup>
import '../assets/announcements.css'
import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  document.body.classList.add('announcements-page')
})

onUnmounted(() => {
  document.body.classList.remove('announcements-page')
})
</script>

<template>
  <div class="flex items-center justify-center text-center h-screen w-screen">
    <h1 class="text-transparent bg-clip-text 
              bg-[linear-gradient(90deg,#003E71_0%,#0076D7_60%)] 
              drop-shadow-lg font-extrabold text-7xl"> BARANGAY <br /> ANNOUNCEMENTS
    </h1>
  </div>
</template>

