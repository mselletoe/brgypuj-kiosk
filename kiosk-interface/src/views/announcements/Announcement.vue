<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { SpeakerWaveIcon, SpeakerXMarkIcon } from '@heroicons/vue/24/solid'
import logoPath from '@/assets/images/Pob1Logo.svg'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'

const isMuted = ref(false)
const router = useRouter()
const currentLang = ref('FIL')

const toggleMute = () => (isMuted.value = !isMuted.value)
const toggleLang = () =>
  (currentLang.value = currentLang.value === 'FIL' ? 'ENG' : 'FIL')

const goBack = () => router.push('/home')

const announcements = ref([
  {
    id: 1,
    title: 'Linggo ng Kabataan Awarding',
    date: 'October 18, 2025, Saturday',
    location: 'Barangay Hall of Poblacion I',
    time: '9:00 AM Onwards',
    image: '/images/sample1.jpg'
  },
  {
    id: 2,
    title: 'Ugnayan sa Barangay',
    date: 'October 5, 2025, Sunday',
    location: 'Municipal Covered Court',
    time: '8:30 AM - 12:00 PM',
    image: '/images/sample2.jpg'
  },
  {
    id: 3,
    title: 'One Day Basketball League',
    date: 'October 12, 2025, Sunday',
    location: 'Loma Covered Court',
    time: '9:00 AM Onwards',
    image: '/images/sample3.jpg'
  }
])

const activeIndex = ref(1)

const visibleAnnouncements = computed(() => {
  const total = announcements.value.length
  return [
    announcements.value[(activeIndex.value - 1 + total) % total],
    announcements.value[activeIndex.value],
    announcements.value[(activeIndex.value + 1) % total]
  ]
})

const setSlide = (index) => {
  activeIndex.value = index
}
</script>

<template>
  <div class="announcement-page w-full min-h-screen px-10 py-6 flex flex-col overflow-hidden">

    <!-- HEADER -->
    <header class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4 text-[#013C6D]">
        <img :src="logoPath" class="w-[60px] h-[60px]" />
        <div>
          <h1 class="text-[18px] font-extrabold">Brgy. Poblacion I</h1>
          <p class="text-[16px] opacity-90">Amadeo, Cavite - Kiosk System</p>
        </div>
      </div>

      <div class="flex items-center gap-5">
        <button
          @click="toggleMute"
          class="bg-[#49759B] text-white rounded-full p-2.5 shadow-lg"
        >
          <component
            :is="isMuted ? SpeakerXMarkIcon : SpeakerWaveIcon"
            class="h-7 w-7"
          />
        </button>

        <div
          @click="toggleLang"
          class="w-36 h-12 bg-[#49759B] rounded-2xl flex cursor-pointer p-1"
        >
          <div
            class="flex-1 flex items-center justify-center font-bold rounded-xl transition"
            :class="currentLang === 'FIL'
              ? 'bg-white text-[#49759B]'
              : 'text-white'"
          >
            FIL
          </div>
          <div
            class="flex-1 flex items-center justify-center font-bold rounded-xl transition"
            :class="currentLang === 'ENG'
              ? 'bg-white text-[#49759B]'
              : 'text-white'"
          >
            ENG
          </div>
        </div>
      </div>
    </header>

    <!-- MAIN -->
    <main class="flex flex-col flex-1">

      <div class="fixed top-[120px] left-10 z-50">
        <ArrowBackButton @click="goBack" />
      </div>

      <div class="flex justify-center mb-6">
        <h1
          class="text-[45px] font-bold text-center leading-[0.95]
          bg-gradient-to-r from-[#03335C] to-[#3291E3]
          bg-clip-text text-transparent"
        >
          BARANGAY <br /> ANNOUNCEMENTS
        </h1>
      </div>

      <!-- CAROUSEL -->
      <div class="flex-1 flex items-center justify-center">
        <div class="overflow-visible">
          <div class="flex justify-center gap-8">

            <div
              v-for="(item, index) in visibleAnnouncements"
              :key="item.id"
              class="h-[300px] w-[420px] relative
                    text-white rounded-3xl overflow-hidden
                    transition-opacity duration-300"
              :class="index === 1
                ? 'opacity-100 z-20'
                : 'opacity-70 z-10'"
              :style="{ backgroundImage: `url(${item.image})` }"
            >
              <!-- Overlay -->
              <div class="absolute inset-0 bg-[#03335C]/75"></div>

              <!-- Content -->
              <div
                class="relative z-10 h-full w-full
                      flex flex-col items-center justify-center
                      text-center px-10"
              >
                <h2 class="text-[34px] font-extrabold leading-tight mb-3">
                  {{ item.title }}
                </h2>

                <p class="text-[16px]">
                  {{ item.date }}
                </p>
                <p class="text-[16px]">
                  {{ item.location }}
                </p>
                <p class="text-[16px]">
                  {{ item.time }}
                </p>
              </div>
            </div>

          </div>
        </div>
      </div>


      <!-- DOTS -->
      <div class="flex justify-center gap-2 mt-6">
        <button
          v-for="(item, index) in announcements"
          :key="item.id"
          @click="setSlide(index)"
          class="h-3 rounded-full transition-all"
          :class="index === activeIndex
            ? 'bg-[#1B5886] w-7'
            : 'border-[#1B5886] w-3 border-[2px]'"
        />
      </div>

    </main>
  </div>
</template>

<style scoped>
.announcement-page {
  background: radial-gradient(circle at top left, #3291E3 0%, #ffffff 44%);
}
</style>
