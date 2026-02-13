<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router"; 
import Pob1Logo from "@/assets/images/Pob1Logo.svg";

const router = useRouter();
const current = ref(0);
let autoSlide = null;

// Sample announcements data - replace with your own
const announcements = ref([
  {
    id: 1,
    title: "Community Clean-Up Drive",
    description: "Join us for a community-wide clean-up initiative to keep our barangay clean and green.",
    event_date: "2024-03-15",
    event_time: "8:00 AM - 12:00 PM",
    location: "Barangay Hall",
    image_base64: null // Optional: add base64 image string here
  },
  {
    id: 2,
    title: "Barangay Assembly Meeting",
    description: "Monthly assembly meeting to discuss community concerns and upcoming projects.",
    event_date: "2024-03-20",
    event_time: "6:00 PM",
    location: "Community Center",
    image_base64: null
  },
  {
    id: 3,
    title: "Free Medical Mission",
    description: "Free check-ups, consultations, and medicine distribution for all residents.",
    event_date: "2024-03-25",
    event_time: "9:00 AM - 3:00 PM",
    location: "Barangay Health Center",
    image_base64: null
  }
]);

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

onMounted(() => {
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
  <div class="h-screen w-full overflow-hidden cursor-pointer" @click.stop="start">
    <!-- Background Layer  -->
    <div class="fixed inset-0 pointer-events-none">
      <transition name="fade">
        <div
          v-if="announcements.length && announcements[current]?.image_base64"
          :key="current"
          class="fixed inset-0 bg-cover bg-center"
          :style="{
            backgroundImage: `url('data:image/jpeg;base64,${announcements[current].image_base64}')`,
          }"
        ></div>
        <div
          v-else
          :key="'fallback-' + current"
          class="fixed inset-0 bg-gradient-to-br from-[#003d73] to-[#00325D]"
        ></div>
      </transition>
      <div class="fixed inset-0 bg-[#00325D] opacity-70"></div>
    </div>

    <!-- Main Content using Flexbox -->
    <div class="relative z-10 h-full flex flex-col">
      <!-- Header -->
      <div class="flex items-center gap-4 p-6">
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

      <!-- Announcement Content Area (Flex Grow) -->
      <div class="flex-1 flex items-center px-20">
        <transition name="fade" mode="out-in">
          <div v-if="announcements.length" :key="current" class="max-w-[60%]">
            <h1 class="text-white font-extrabold text-[70px] tracking-tight leading-[1.05] drop-shadow-lg">
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
                <svg class="w-6 h-6 opacity-75 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" />
                </svg>
                <span>
                  {{ formatDate(announcements[current]?.event_date) }}, 
                  {{ formatDay(announcements[current]?.event_date) }}
                </span>
              </p>

              <p 
                v-if="announcements[current]?.event_time"
                class="text-white text-[22px] opacity-95 leading-[1.3] flex items-center gap-3"
              >
                <svg class="w-6 h-6 opacity-75 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" />
                </svg>
                <span>{{ announcements[current]?.event_time }}</span>
              </p>

              <p class="text-white text-[22px] opacity-95 leading-[1.3] flex items-center gap-3">
                <svg class="w-6 h-6 opacity-75 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
                </svg>
                <span>{{ announcements[current]?.location }}</span>
              </p>
            </div>
          </div>

          <!-- No Announcements Message -->
          <div v-else key="no-announcements">
            <h1 class="text-white font-extrabold text-[60px] tracking-tight leading-[1.05] drop-shadow-lg">
              No Announcements Available
            </h1>
            <p class="text-white text-[22px] mt-4 opacity-95 leading-[1.3]">
              Check back later for updates
            </p>
          </div>
        </transition>
      </div>

      <!-- Navigation & Footer Section -->
      <div class="flex items-center justify-between px-6 pb-10">
        <!-- Left Navigation Button -->
        <button
          v-if="announcements.length > 1"
          @click.stop.prevent="prevSlide"
          class="text-white transition-all duration-300 hover:scale-110 hover:opacity-100 opacity-70"
          aria-label="Previous announcement"
        >
          <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
        </button>
        <div v-else class="w-16"></div>

        <!-- Center: Indicators & Start Prompt -->
        <div class="flex flex-col items-center gap-4 flex-1">
          <!-- Slide Indicators -->
          <div 
            v-if="announcements.length > 1"
            class="flex justify-center gap-3"
          >
            <span
              v-for="(a, i) in announcements"
              :key="a.id"
              class="w-3 h-3 rounded-full bg-white transition-all duration-300 cursor-pointer hover:opacity-100 hover:scale-125"
              :class="i === current ? 'opacity-100 scale-110' : 'opacity-40'"
              @click.stop="current = i"
            ></span>
          </div>

          <!-- Start Prompt -->
          <p class="text-white text-xl opacity-90 pointer-events-none animate-pulse">
            Touch the screen to start
          </p>
        </div>

        <!-- Right Navigation Button -->
        <button
          v-if="announcements.length > 1"
          @click.stop.prevent="nextSlide"
          class="text-white transition-all duration-300 hover:scale-110 hover:opacity-100 opacity-70"
          aria-label="Next announcement"
        >
          <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
        </button>
        <div v-else class="w-16"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Smooth fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.8s ease-in-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>