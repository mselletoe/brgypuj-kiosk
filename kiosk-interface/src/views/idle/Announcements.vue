<script setup>
import { ref, onMounted } from 'vue'
import { useTouchToStart } from '@/composables/touchToStart'

useTouchToStart()

const announcements = ref([])
const currentSlide = ref(0)

const fetchAnnouncements = async () => {
  const response = await fetch('/src/data/announcements.json')
  announcements.value = await response.json()
}

const nextSlide = () => {
  currentSlide.value = (currentSlide.value + 1) % announcements.value.length
}

const prevSlide = () => {
  currentSlide.value =
    (currentSlide.value - 1 + announcements.value.length) %
    announcements.value.length
}

onMounted(fetchAnnouncements)
</script>

<template>
  <div class="relative h-screen w-screen overflow-hidden">
    <div
      v-for="(item, index) in announcements"
      :key="item.id"
      class="absolute inset-0 transition-opacity duration-700 ease-in-out"
      :class="index === currentSlide ? 'opacity-100' : 'opacity-0'"
    >
      <!-- Background Image -->
      <img
        :src="item.image"
        alt="announcement"
        class="w-full h-full object-cover brightness-50"
      />

      <!-- Overlay Content -->
      <div class="absolute inset-0 flex flex-col justify-center items-center text-center px-8">
        <img src="/src/assets/images/Pob1Logo.svg" class="w-28 mb-4" alt="Logo" />
        <h2 class="text-white text-lg font-semibold">Brgy. Poblacion I</h2>
        <p class="text-white text-sm mb-4">Amadeo, Cavite - Kiosk System</p>

        <h1 class="text-4xl md:text-6xl font-extrabold text-white mb-4 leading-tight drop-shadow-lg">
          {{ item.title }}
        </h1>

        <div class="text-white text-lg md:text-xl font-medium space-y-1">
          <p>{{ new Date(item.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }) }}</p>
          <p>{{ item.location }}</p>
          <p>{{ item.start }} - {{ item.end }}</p>
        </div>

        <p class="absolute bottom-6 text-white opacity-70 text-sm animate-pulse">
          Touch the screen to start
        </p>
      </div>
    </div>

    <!-- Navigation Buttons -->
    <button
      @click="prevSlide"
      class="absolute left-6 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-20 hover:bg-opacity-40 text-white p-3 rounded-full"
    >
      ‹
    </button>
    <button
      @click="nextSlide"
      class="absolute right-6 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-20 hover:bg-opacity-40 text-white p-3 rounded-full"
    >
      ›
    </button>

    <!-- Pagination Dots -->
    <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2">
      <div
        v-for="(item, index) in announcements"
        :key="item.id"
        class="w-3 h-3 rounded-full transition-all duration-300"
        :class="index === currentSlide ? 'bg-white' : 'bg-gray-400'"
      ></div>
    </div>
  </div>
</template>
