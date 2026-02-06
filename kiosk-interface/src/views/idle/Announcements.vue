<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router"; 
import Pob1Logo from "@/assets/images/Pob1Logo.svg";

const router = useRouter();
const announcements = ref([]);
const current = ref(0);
let autoSlide = null;

const loadAnnouncements = async () => {
  try {
    const res = await api.get("/announcements");
    announcements.value = res.data;
  } catch (error) {
    console.error("Failed to load announcements:", error);
  }
};

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

const start = () => {
  router.push("/login"); 
};

onMounted(async () => {
  await loadAnnouncements();
  startSlider();
});
</script>

<template>
  <div
    class="relative h-screen w-full overflow-hidden"
    @click.stop="start"
  >
    <div
      v-if="announcements.length"
      class="absolute inset-0 bg-cover bg-center transition-all duration-700 pointer-events-none"
      :style="{
        backgroundImage: `url('data:image/jpeg;base64,${
          announcements[current]?.image
        }')`,
      }"
    ></div>

    <div class="absolute inset-0 bg-[#00325D] opacity-70 pointer-events-none"></div>

    <div class="relative z-10 h-full flex flex-col justify-center px-20 pointer-events-auto">
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

      <div class="absolute left-20 top-[230px] z-20">
        <h1
          class="text-white font-extrabold text-[70px] tracking-tight leading-[1.05] drop-shadow-lg"
        >
          {{ announcements[current]?.title }}
        </h1>

        <p
          class="text-white text-[22px] mt-4 opacity-95 leading-[1.3]"
        >
          {{ formatDate(announcements[current]?.event_date) }},
          {{ announcements[current]?.event_day }} <br />
          {{ announcements[current]?.location }} <br />
          {{ announcements[current]?.event_time }}
        </p>
      </div>
    </div>

    <button
      @click.stop.prevent="prevSlide"
      class="absolute top-1/2 left-6 -translate-y-1/2 text-white text-6xl opacity-80 hover:opacity-100 z-20 pointer-events-auto"
    >
      ‹
    </button>

    <button
      @click.stop.prevent="nextSlide"
      class="absolute top-1/2 right-6 -translate-y-1/2 text-white text-6xl opacity-80 hover:opacity-100 z-20 pointer-events-auto"
    >
      ›
    </button>

    <div class="absolute bottom-24 w-full flex justify-center space-x-3 z-20 pointer-events-auto">
      <span
        v-for="(a, i) in announcements"
        :key="i"
        class="w-4 h-4 rounded-full bg-white transition"
        :class="i === current ? 'opacity-100' : 'opacity-40'"
      ></span>
    </div>

    <p class="absolute bottom-10 w-full text-center text-white text-xl opacity-90 pointer-events-none">
      Touch the screen to start
    </p>
  </div>
</template>

<style>
.bg-cover {
  transition: background-image 0.6s ease-in-out;
}
</style>
```