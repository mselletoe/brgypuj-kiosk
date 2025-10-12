<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import Display from '@/views/idle/Display.vue'
import Announcements from '@/views/idle/Announcements.vue'

// Default Screen
const currentView = ref('display')

// Interval for automatic switching
let interval = null

// Auto-toggle between Display and Announcements every 5 seconds
onMounted(() => {
  interval = setInterval(() => {
    currentView.value = currentView.value === 'display' ? 'announcements' : 'display'
  }, 5000)
})

onBeforeUnmount(() => {
  if (interval) clearInterval(interval)
})

// Manual switch triggered by "See Announcements" button
const showAnnouncements = () => {
  currentView.value = 'announcements'
}
</script>

<template>
  <div class="h-screen w-screen bg-blue-100 flex items-center justify-center relative">
    <component
      :is="currentView === 'display' ? Display : Announcements"
      @see-announcements="showAnnouncements"
    />
  </div>
</template>