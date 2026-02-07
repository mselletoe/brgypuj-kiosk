<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router"; 
import Pob1Logo from "@/assets/images/Pob1Logo.svg";
import { getActiveAnnouncements } from "@/api/announcementService";

const router = useRouter();
const announcements = ref([]);
const current = ref(0);
let autoSlide = null;

const loadAnnouncements = async () => {
  try {
    const data = await getActiveAnnouncements();
    announcements.value = data;
  } catch (error) {
    console.error("Failed to load announcements:", error);
  }
};

const startSlider = () => {
  if (autoSlide) clearInterval(autoSlide);
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

const formatDay = (date) => {
  if (!date) return "";
  return new Date(date).toLocaleDateString("en-US", {
    weekday: "long",
  });
};

const start = () => {
  router.push("/login"); 
};

onMounted(async () => {
  await loadAnnouncements();
  if (announcements.value.length > 0) {
    startSlider();
  }
});

onBeforeUnmount(() => {
  if (autoSlide) {
    clearInterval(autoSlide);
  }
});
</script>

<template>
  <div
    class="relative h-screen w-full overflow-hidden"
    @click.stop="start"
  >
    <!-- Background Image with fallback -->
    <div
      v-if="announcements.length && announcements[current]?.image_base64"
      class="absolute inset-0 bg-cover bg-center transition-all duration-700 pointer-events-none"
      :style="{
        backgroundImage: `url('data:image/jpeg;base64,${announcements[current].image_base64}')`,
      }"
    ></div>

    <!-- Fallback background if no image -->
    <div
      v-else
      class="absolute inset-0 bg-gradient-to-br from-[#003d73] to-[#00325D] pointer-events-none"
    ></div>

    <!-- Overlay -->
    <div class="absolute inset-0 bg-[#00325D] opacity-70 pointer-events-none"></div>

    <!-- Content -->
    <div class="relative z-10 h-full flex flex-col justify-center px-20 pointer-events-auto">
      <!-- Header -->
      <div class="flex items-center gap-4 mb-6
                  absolute top-6 left-6 z-20">
        <img :src="Pob1Logo" class="w-[110px] h-[110px]" />

        <div>
          <h2 class="text-white text-[15px] font-bold leading-tight">
            Brgy. Poblacion I
          </h2>
          <p class="text-white text-[15px] opacity-90 -mt-1">
            Amadeo, Cavite - Kiosk System
          </p>
          <h3 class="text-white text-[30px] font-bold leading-tight">
            BARANGAY ANNOUNCEMENTS
          </h3>
        </div>
      </div>

      <!-- Announcement Content -->
      <div v-if="announcements.length" class="absolute left-20 top-[230px] z-20 max-w-[60%]">
        <h1
          class="text-white font-extrabold text-[70px] tracking-tight leading-[1.05] drop-shadow-lg"
        >
          {{ announcements[current]?.title }}
        </h1>

        <p
          v-if="announcements[current]?.description"
          class="text-white text-[20px] mt-3 opacity-90 leading-[1.4] max-w-[90%]"
        >
          {{ announcements[current]?.description }}
        </p>

        <div class="mt-6 space-y-2">
          <p class="text-white text-[22px] opacity-95 leading-[1.3] flex items-center gap-3">
            <span class="opacity-75">📅</span>
            <span>
              {{ formatDate(announcements[current]?.event_date) }}, 
              {{ formatDay(announcements[current]?.event_date) }}
            </span>
          </p>

          <p 
            v-if="announcements[current]?.event_time"
            class="text-white text-[22px] opacity-95 leading-[1.3] flex items-center gap-3"
          >
            <span class="opacity-75">🕐</span>
            <span>{{ announcements[current]?.event_time }}</span>
          </p>

          <p class="text-white text-[22px] opacity-95 leading-[1.3] flex items-center gap-3">
            <span class="opacity-75">📍</span>
            <span>{{ announcements[current]?.location }}</span>
          </p>
        </div>
      </div>

      <!-- No Announcements Message -->
      <div v-else class="absolute left-20 top-[230px] z-20">
        <h1
          class="text-white font-extrabold text-[60px] tracking-tight leading-[1.05] drop-shadow-lg"
        >
          No Announcements Available
        </h1>
        <p class="text-white text-[22px] mt-4 opacity-95 leading-[1.3]">
          Check back later for updates
        </p>
      </div>
    </div>

    <!-- Navigation Buttons (only show if there are multiple announcements) -->
    <template v-if="announcements.length > 1">
      <button
        @click.stop.prevent="prevSlide"
        class="absolute top-1/2 left-6 -translate-y-1/2 text-white text-6xl opacity-80 hover:opacity-100 z-20 pointer-events-auto transition-opacity"
        aria-label="Previous announcement"
      >
        ‹
      </button>

      <button
        @click.stop.prevent="nextSlide"
        class="absolute top-1/2 right-6 -translate-y-1/2 text-white text-6xl opacity-80 hover:opacity-100 z-20 pointer-events-auto transition-opacity"
        aria-label="Next announcement"
      >
        ›
      </button>
    </template>

    <!-- Slide Indicators (only show if there are multiple announcements) -->
    <div 
      v-if="announcements.length > 1"
      class="absolute bottom-24 w-full flex justify-center space-x-3 z-20 pointer-events-auto"
    >
      <span
        v-for="(a, i) in announcements"
        :key="a.id"
        class="w-4 h-4 rounded-full bg-white transition cursor-pointer hover:opacity-100"
        :class="i === current ? 'opacity-100' : 'opacity-40'"
        @click.stop="current = i"
      ></span>
    </div>

    <!-- Start Prompt -->
    <p class="absolute bottom-10 w-full text-center text-white text-xl opacity-90 pointer-events-none">
      Touch the screen to start
    </p>
  </div>
</template>

<style scoped>
.bg-cover {
  transition: background-image 0.6s ease-in-out;
}
</style>