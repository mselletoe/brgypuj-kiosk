<script setup>
import './display.css'
import { useTouchToStart } from '@/composables/touchToStart'

useTouchToStart()
</script>

<template>
  <div class="flex items-center justify-center text-center h-screen w-screen relative">
    <h1 class="text-transparent bg-clip-text bg-[linear-gradient(90deg,#003E71_0%,#0076D7_60%)] drop-shadow-lg font-extrabold text-7xl">
      BARANGAY <br /> ANNOUNCEMENTS
    </h1>

    <!-- Touch prompt -->
    <div class="absolute bottom-8 text-[#8EC3EF] text-xl font-semibold animate-pulse">
      Touch anywhere to start
    </div>
  </div>
</template>