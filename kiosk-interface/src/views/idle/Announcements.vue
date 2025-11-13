<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { getAnnouncements } from '@/api/announcements'
import { useTouchToStart } from '@/composables/touchToStart'

useTouchToStart()

const announcements = ref([])
const currentSlide = ref(0)
let slideTimer = null
let refreshTimer = null

// ✅ Fetch announcements from backend
const fetchAnnouncements = async () => {
  try {
    console.log('📡 Fetching announcements...')
    const data = await getAnnouncements()
    if (Array.isArray(data)) {
      announcements.value = data
      localStorage.setItem('announcements', JSON.stringify(data))
      console.log(`✅ Loaded ${data.length} announcements`)
    } else {
      console.warn('⚠️ Unexpected API response:', data)
    }
  } catch (error) {
    console.error('❌ Failed to fetch announcements:', error.message)
    const saved = localStorage.getItem('announcements')
    if (saved) {
      announcements.value = JSON.parse(saved)
      console.log('📦 Loaded cached announcements')
    }
  }
}

// ✅ Slide navigation
const nextSlide = () => {
  if (announcements.value.length > 0) {
    currentSlide.value = (currentSlide.value + 1) % announcements.value.length
  }
}
const prevSlide = () => {
  if (announcements.value.length > 0) {
    currentSlide.value =
      (currentSlide.value - 1 + announcements.value.length) %
      announcements.value.length
  }
}

onMounted(() => {
  fetchAnnouncements()
  slideTimer = setInterval(nextSlide, 8000)
  refreshTimer = setInterval(fetchAnnouncements, 60000)
})

onUnmounted(() => {
  clearInterval(slideTimer)
  clearInterval(refreshTimer)
})
</script>

<template>
  <div class="relative h-screen w-screen overflow-hidden bg-black text-white">
    <div
      v-for="(item, index) in announcements"
      :key="item.id"
      class="absolute inset-0 transition-opacity duration-700 ease-in-out"
      :class="index === currentSlide ? 'opacity-100' : 'opacity-0'"
    >
      <!-- ✅ Background Image -->
      <img
        v-if="item.image"
        :src="item.image.startsWith('http') ? item.image : `http://127.0.0.1:8000/storage/${item.image}`"
        alt="Announcement Background"
        class="w-full h-full object-cover brightness-50"
        @error="e => e.target.style.display='none'"
      />

      <!-- ✅ Overlay -->
      <div class="absolute inset-0 flex flex-col justify-start items-center text-center pt-10 px-6">
        <!-- Header -->
        <div class="flex flex-col items-center mb-6">
          <img src="/src/assets/images/Pob1Logo.svg" alt="Logo" class="w-20 mb-3" />
          <h2 class="text-lg font-semibold">Brgy. Poblacion I</h2>
          <p class="text-sm opacity-80">Amadeo, Cavite - Kiosk System</p>
          <h1 class="text-2xl md:text-3xl font-bold mt-2">BARANGAY ANNOUNCEMENTS</h1>
        </div>

        <!-- Announcement Details -->
        <div class="flex flex-col items-center justify-center flex-grow">
          <h1 class="text-5xl md:text-7xl font-extrabold leading-tight drop-shadow-lg mb-6">
            {{ item.title }}
          </h1>
          <p class="text-lg md:text-xl mb-1">
            {{
              new Date(item.date).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                weekday: 'long'
              })
            }}
          </p>
          <p class="text-lg md:text-xl mb-1">{{ item.location }}</p>
          <p class="text-lg md:text-xl">{{ item.start }} - {{ item.end }}</p>
        </div>

        <p class="absolute bottom-6 text-sm opacity-70 animate-pulse">
          Touch the screen to start
        </p>
      </div>
    </div>

    <!-- ✅ Nav Arrows -->
    <button
      v-if="announcements.length > 1"
      @click="prevSlide"
      class="absolute left-4 top-1/2 -translate-y-1/2 bg-white/20 hover:bg-white/40 text-white p-3 rounded-full"
    >
      ‹
    </button>
    <button
      v-if="announcements.length > 1"
      @click="nextSlide"
      class="absolute right-4 top-1/2 -translate-y-1/2 bg-white/20 hover:bg-white/40 text-white p-3 rounded-full"
    >
      ›
    </button>

    <!-- ✅ Pagination Dots -->
    <div
      v-if="announcements.length > 1"
      class="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2"
    >
      <div
        v-for="(item, index) in announcements"
        :key="item.id"
        class="w-3 h-3 rounded-full transition-all duration-300"
        :class="index === currentSlide ? 'bg-white' : 'bg-gray-500'"
      ></div>
    </div>
  </div>
</template>
