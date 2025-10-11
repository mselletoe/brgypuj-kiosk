<template>
  <header
    class="flex justify-between items-center bg-white shadow-md p-4 text-gray-800"
  >
    <!-- Left: Logo -->
    <div class="flex items-center space-x-2">
      <img src="/logo.png" alt="Logo" class="w-10 h-10" />
      <h1 class="text-xl font-semibold">My App</h1>
    </div>

    <!-- Center: Time and Date -->
    <div class="text-center">
      <p class="text-lg font-medium">{{ currentTime }}</p>
      <p class="text-sm text-gray-500">{{ currentDate }}</p>
    </div>

    <!-- Right: Profile & Logout -->
    <div class="flex items-center space-x-4">
      <button
        class="text-sm text-gray-700 hover:text-blue-600 font-medium"
        @click="handleLogout"
      >
        Logout
      </button>
      <img
        src="/profile.png"
        alt="Profile"
        class="w-10 h-10 rounded-full border border-gray-300"
      />
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const currentTime = ref('')
const currentDate = ref('')

function updateDateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  currentDate.value = now.toLocaleDateString(undefined, {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  })
}

let timer
onMounted(() => {
  updateDateTime()
  timer = setInterval(updateDateTime, 1000)
})
onBeforeUnmount(() => clearInterval(timer))

function handleLogout() {
  alert('You have logged out!')
}
</script>

<style scoped>
header {
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
}
</style>
