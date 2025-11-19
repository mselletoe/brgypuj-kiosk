<script setup>
import { ref, onMounted } from "vue";
import api from "@/api/api"; 
import Pob1Logo from "@/assets/images/Pob1Logo.svg";

const announcements = ref([]);
const current = ref(0);
let autoSlide = null;

// Fetch announcements from API
const loadAnnouncements = async () => {
  try {
    const res = await api.get("/announcements");
    announcements.value = res.data;
  } catch (error) {
    console.error("Failed to load announcements:", error);
  }
};

// Auto slide every 5 seconds
const startSlider = () => {
  autoSlide = setInterval(() => {
    nextSlide();
  }, 5000);
};

const nextSlide = () => {
  if (announcements.value.length === 0) return;
  current.value = (current.value + 1) % announcements.value.length;
};

const prevSlide = () => {
  if (announcements.value.length === 0) return;
  current.value =
    (current.value - 1 + announcements.value.length) %
    announcements.value.length;
};

const formatDate = (date) => {
  if (!date) return "";
  return new Date(date).toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });
};

// Navigate to kiosk home
const start = () => {
  window.location.href = "/home"; // change if needed
};

onMounted(async () => {
  await loadAnnouncements();
  startSlider();
});
</script>

<template>
  <div
    class="relative h-screen w-full overflow-hidden"
    @click="start"
  >
    <!-- Background Image -->
    <div
      v-if="announcements.length"
      class="absolute inset-0 bg-cover bg-center transition-all duration-700"
      :style="{
        backgroundImage: `url('data:image/jpeg;base64,${
          announcements[current].image
        }')`,
      }"
    ></div>

    <!-- Blue overlay -->
    <div class="absolute inset-0 bg-blue-900/60"></div>

    <!-- Slider Content -->
    <div class="relative z-10 h-full flex flex-col justify-center px-16">
      <!-- Header -->
      <div class="flex items-center gap-4 mb-6">
        <img :src="Pob1Logo" class="w-20 h-20" />

        <div>
          <h2 class="text-white text-3xl font-bold leading-tight">
            Brgy. Poblacion I
          </h2>
          <p class="text-white text-xl opacity-90">
            Amadeo, Cavite • Kiosk System
          </p>
        </div>
      </div>

      <!-- Announcement Title -->
      <h1
        class="text-white font-extrabold text-6xl w-[60%] leading-tight drop-shadow-lg"
      >
        {{ announcements[current]?.title }}
      </h1>

      <!-- Details -->
      <p class="text-white text-2xl mt-6 opacity-95 leading-relaxed">
        {{ formatDate(announcements[current]?.event_date) }},
        {{ announcements[current]?.event_day }} <br />
        {{ announcements[current]?.location }} <br />
        {{ announcements[current]?.event_time }}
      </p>
    </div>

    <!-- Left Button -->
    <button
      @click.stop="prevSlide"
      class="absolute top-1/2 left-6 -translate-y-1/2 text-white text-6xl opacity-80 hover:opacity-100"
    >
      ‹
    </button>

    <!-- Right Button -->
    <button
      @click.stop="nextSlide"
      class="absolute top-1/2 right-6 -translate-y-1/2 text-white text-6xl opacity-80 hover:opacity-100"
    >
      ›
    </button>

    <!-- Pagination Dots -->
    <div class="absolute bottom-24 w-full flex justify-center space-x-3 z-20">
      <span
        v-for="(a, i) in announcements"
        :key="i"
        class="w-4 h-4 rounded-full bg-white transition"
        :class="i === current ? 'opacity-100' : 'opacity-40'"
      ></span>
    </div>

    <!-- Touch to Start -->
    <p class="absolute bottom-10 w-full text-center text-white text-xl opacity-90">
      Touch the screen to start
    </p>
  </div>
</template>

<style>
/* smooth fade for background switching */
.bg-cover {
  transition: background-image 0.6s ease-in-out;
}
</style>
