<script setup>
/**
 * @file views/idle/Idle.vue
 * @description Root idle screen controller. Alternates between the Display
 * (touch-to-start) and Announcements views every 5 seconds. Any tap on the
 * screen navigates to the login options screen. A 500ms readiness delay
 * prevents accidental navigation on initial mount.
 */

import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import Display from '@/views/idle/Display.vue'
import Announcements from '@/views/idle/Announcements.vue'

const router = useRouter()
const currentView = ref('display')
const isReady = ref(false)
let interval = null

// =============================================================================
// AUTO-SWITCH
// =============================================================================
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

const showAnnouncements = () => {
  stopAutoSwitch()
  currentView.value = 'announcements'
}

// =============================================================================
// NAVIGATION
// =============================================================================
const handleTouchStart = () => {
  if (!isReady.value) return

  stopAutoSwitch()
  router.push('/login')
}

// =============================================================================
// LIFECYCLE
// =============================================================================
onMounted(() => {
  startAutoSwitch()
  
  setTimeout(() => {
    isReady.value = true
  }, 500)
})

onBeforeUnmount(() => {
  stopAutoSwitch()
})
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