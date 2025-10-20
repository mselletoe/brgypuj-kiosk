<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import Display from '@/views/idle/Display.vue'
import Announcements from '@/views/idle/Announcements.vue'

const router = useRouter()

// Default screen
const currentView = ref('display')

// Interval for automatic switching
let interval = null

// Auto-toggle between Display and Announcements every 5 seconds
const startAutoSwitch = () => {
  interval = setInterval(() => {
    currentView.value = currentView.value === 'display' ? 'announcements' : 'display'
  }, 5000)
}

const stopAutoSwitch = () => {
  if (interval) {
    clearInterval(interval)
    interval = null
  }
}

onMounted(() => {
  startAutoSwitch()
})

onBeforeUnmount(() => {
  stopAutoSwitch()
})

// Manual switch triggered by "See Announcements" button
const showAnnouncements = () => {
  stopAutoSwitch() // stop auto-switch once manually triggered
  currentView.value = 'announcements'
}

// Navigate to login or home on touch anywhere
const handleTouchStart = () => {
  stopAutoSwitch()
  router.push('/login') // or '/home' depending on your kiosk flow
}
</script>

<template>
  <div
    class="h-screen w-screen flex items-center justify-center relative"
    @click="handleTouchStart"
  >
    <component
      :is="currentView === 'display' ? Display : Announcements"
      @see-announcements="showAnnouncements"
    />
  </div>
</template>