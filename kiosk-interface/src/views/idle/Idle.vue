<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import Display from '@/views/idle/Display.vue'
import Announcements from '@/views/idle/Announcements.vue'

const router = useRouter()

const currentView = ref('display')

let interval = null

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

const showAnnouncements = () => {
  stopAutoSwitch()
  currentView.value = 'announcements'
}

const handleTouchStart = () => {
  stopAutoSwitch()
  router.push('/login')
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