<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { SpeakerWaveIcon, SpeakerXMarkIcon } from '@heroicons/vue/24/solid'
import logoPath from '@/assets/images/Pob1Logo.svg'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import lnk from '@/assets/images/lnk.jpg'
import ugnayan from '@/assets/images/ugnayan.jpg'
import odl from '@/assets/images/odl.jpg'
import mlp from '@/assets/images/mlp.png'
import ganda from '@/assets/images/ig.png'

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
    image: lnk
  },
  {
    id: 2,
    title: 'Ugnayan sa Barangay',
    date: 'October 5, 2025, Sunday',
    location: 'Municipal Covered Court',
    time: '8:30 AM - 12:00 PM',
    image: ugnayan
  },
  {
    id: 3,
    title: 'One Day Basketball League',
    date: 'October 12, 2025, Sunday',
    location: 'Loma Covered Court',
    time: '9:00 AM Onwards',
    image: odl
  },
  {
    id: 4,
    title: 'My Little Pony',
    date: 'October 12, 2025, Sunday',
    location: 'Loma Covered Court',
    time: '9:00 AM Onwards',
    image: mlp
  },
  {
    id: 5,
    title: 'IG ni Ganda',
    date: 'March 23, 2026, Monday',
    location: 'Amadeo, Cavite',
    time: '9:00 AM Onwards',
    image: ganda
  }
])

const activeIndex = ref(0)

// displayIndex updates immediately when a slide is triggered so dots move with the cards
const displayIndex = ref(0)

// Track sliding animation state
const isAnimating = ref(false)
const translateX = ref(0)

// Card width + gap
const CARD_W = 420
const GAP = 32
const CARD_SLOT = CARD_W + GAP

// Always render exactly 5 cards (-2,-1,0,+1,+2) around active.
// Viewport clips to 3 cards wide. Track always full — no blank edges.
const windowItems = computed(() => {
  const total = announcements.value.length
  return [-2, -1, 0, 1, 2].map(offset => {
    const idx = (activeIndex.value + offset + total) % total
    return { ...announcements.value[idx], _offset: offset }
  })
})

const animateTo = (direction) => {
  if (isAnimating.value) return
  isAnimating.value = true
  translateX.value = -direction * CARD_SLOT

  // Update displayIndex immediately so dots move with the sliding cards
  displayIndex.value =
    (displayIndex.value + direction + announcements.value.length) %
    announcements.value.length

  setTimeout(() => {
    activeIndex.value =
      (activeIndex.value + direction + announcements.value.length) %
      announcements.value.length
    translateX.value = 0
    isAnimating.value = false
  }, 450)
}

const nextSlide = () => animateTo(1)
const prevSlide = () => animateTo(-1)

const setSlide = (index) => {
  if (isAnimating.value || index === displayIndex.value) return
  animateTo(index > displayIndex.value ? 1 : -1)
}

// ── Language helpers ──────────────────────────────────────────────

const isFil = computed(() => currentLang.value === 'FIL')

// Filipino month names
const filMonths = {
  January: 'Enero', February: 'Pebrero', March: 'Marso',
  April: 'Abril', May: 'Mayo', June: 'Hunyo',
  July: 'Hulyo', August: 'Agosto', September: 'Setyembre',
  October: 'Oktubre', November: 'Nobyembre', December: 'Disyembre'
}

// "October 18, 2025, Saturday" → "Ika-18 ng Oktubre, 2025"
const translateDate = (dateStr) => {
  if (!isFil.value) return dateStr
  const match = dateStr.match(/^(\w+)\s+(\d+),\s+(\d{4})/)
  if (!match) return dateStr
  const [, month, day, year] = match
  const filMonth = filMonths[month] || month
  return `Ika-${day} ng ${filMonth}, ${year}`
}

// Returns "umaga", "tanghali", "hapon", or "gabi" based on hour + period
const getPartOfDay = (clock, period) => {
  const hour = parseInt(clock.split(':')[0])
  if (period.toUpperCase() === 'AM') return 'umaga'
  if (hour === 12) return 'tanghali'
  if (hour >= 6) return 'gabi'
  return 'hapon'
}

// Translates a single time token e.g. "9:00 AM" → "Ika-9:00 ng umaga"
const translateSingle = (t) => {
  const m = t.trim().match(/^(\d+:\d+)\s*(AM|PM)$/i)
  if (!m) return t.trim()
  const [, clock, period] = m
  return `Ika-${clock} ng ${getPartOfDay(clock, period)}`
}

// "9:00 AM Onwards"    → "Mula Ika-9:00 ng umaga"
// "8:30 AM - 12:00 PM" → "Ika-8:30 ng umaga - Ika-12:00 ng tanghali"
const translateTime = (timeStr) => {
  if (!isFil.value) return timeStr

  if (timeStr.toLowerCase().includes('onwards')) {
    const timePart = timeStr.replace(/\s*onwards/i, '').trim()
    return `Mula ${translateSingle(timePart)}`
  }

  if (timeStr.includes(' - ')) {
    return timeStr.split(' - ').map(translateSingle).join(' - ')
  }

  return translateSingle(timeStr)
}

// "Barangay Hall of Poblacion I" → "Barangay Hall ng Poblacion I"
const translateLocation = (location) => {
  if (!isFil.value) return location
  return location.replace('Barangay Hall of', 'Barangay Hall ng')
}
</script>

<template>
  <div class="announcement-page w-full min-h-screen px-10 py-6 flex flex-col">

    <!-- HEADER -->
    <header class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4 text-[#013C6D]">
        <img :src="logoPath" class="w-[70px] h-[70px]" />
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

        <!-- TOGGLE: sliding pill that moves left↔right smoothly -->
        <div
          @click="toggleLang"
          class="w-36 h-12 bg-[#49759B] rounded-2xl flex cursor-pointer p-1"
          style="position: relative;"
        >
          <!-- Sliding white pill -->
          <div
            class="rounded-xl bg-white"
            style="
              position: absolute;
              top: 4px;
              bottom: 4px;
              width: calc(50% - 4px);
              transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            "
            :style="{
              transform: currentLang === 'ENG' ? 'translateX(calc(100% + 0px))' : 'translateX(0px)'
            }"
          ></div>

          <!-- Labels — always visible, color changes based on which side is active -->
          <div
            class="flex-1 flex items-center justify-center font-bold rounded-xl"
            style="position: relative; z-index: 1; transition: color 0.3s ease;"
            :style="{ color: currentLang === 'FIL' ? '#49759B' : 'white' }"
          >
            FIL
          </div>
          <div
            class="flex-1 flex items-center justify-center font-bold rounded-xl"
            style="position: relative; z-index: 1; transition: color 0.3s ease;"
            :style="{ color: currentLang === 'ENG' ? '#49759B' : 'white' }"
          >
            ENG
          </div>
        </div>
      </div>
    </header>

    <!-- MAIN -->
    <main class="flex flex-col flex-1">

      <!-- BACK BUTTON + TITLE on the same row -->
      <div class="flex items-center justify-between mb-6">
        <ArrowBackButton @click="goBack" />

        <h1
          class="text-[45px] font-bold text-center leading-[0.95]
          bg-gradient-to-r from-[#03335C] to-[#3291E3]
          bg-clip-text text-transparent lang-fade"
        >
          <template v-if="isFil">
            MGA ANUNSYO NG<br /> BARANGAY
          </template>
          <template v-else>
            BARANGAY <br /> ANNOUNCEMENTS
          </template>
        </h1>

        <!-- Invisible spacer to keep title truly centered -->
        <div style="visibility: hidden; pointer-events: none;">
          <ArrowBackButton />
        </div>
      </div>

      <!-- CAROUSEL -->
      <div class="flex flex-1 items-center justify-center gap-4">

        <!-- LEFT ARROW — flex-shrink-0 so it never gets squeezed off screen -->
        <button
          v-if="announcements.length > 1"
          @click.stop.prevent="prevSlide"
          class="text-[#03335C] transition-opacity duration-300 hover:opacity-100 opacity-70 flex-shrink-0"
        >
          <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
          </svg>
        </button>

        <!--
          Viewport: flex-1 fills all remaining space between the arrows.
          overflow-hidden clips the sliding track.
          mask-image fades edges to transparent — solid center, fade to nothing on sides.
          Fully responsive at any screen size.
        -->
        <div
          class="flex-1 overflow-hidden"
          style="
            mask-image: linear-gradient(to right, transparent 0%, black 22%, black 78%, transparent 100%);
            -webkit-mask-image: linear-gradient(to right, transparent 0%, black 22%, black 78%, transparent 100%);
          "
        >
          <!-- Centering wrapper keeps the 5-card track centered. Flexbox places card[2] at center. -->
          <div class="flex items-center justify-center">
            <!-- Sliding track: translateX shifts ±CARD_SLOT, snaps back after animation -->
            <div
              class="flex flex-shrink-0"
              :style="{
                gap: `${GAP}px`,
                transform: `translateX(${translateX}px)`,
                transition: isAnimating ? 'transform 0.45s cubic-bezier(0.25, 0.46, 0.45, 0.94)' : 'none'
              }"
            >
              <div
                v-for="(item) in windowItems"
                :key="`${item.id}-${item._offset}`"
                class="h-[300px] flex-shrink-0 text-white rounded-3xl overflow-hidden"
                :style="{
                  width: `${CARD_W}px`,
                  backgroundImage: `url(${item.image})`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                  position: 'relative'
                }"
              >
                <!-- Dark content overlay -->
                <div
                  class="h-full w-full flex flex-col items-center justify-center text-center px-10"
                  style="background: rgba(3, 51, 92, 0.75);"
                >
                  <h2 class="text-[34px] font-extrabold leading-tight mb-3 lang-fade">
                    {{ item.title }}
                  </h2>
                  <p class="text-[16px] lang-fade">{{ translateDate(item.date) }}</p>
                  <p class="text-[16px] lang-fade">{{ translateLocation(item.location) }}</p>
                  <p class="text-[16px] lang-fade">{{ translateTime(item.time) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT ARROW — flex-shrink-0 so it never gets squeezed off screen -->
        <button
          v-if="announcements.length > 1"
          @click.stop.prevent="nextSlide"
          class="text-[#03335C] transition-opacity duration-300 hover:opacity-100 opacity-70 flex-shrink-0"
        >
          <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
          </svg>
        </button>

      </div>

      <!-- DOTS — bound to displayIndex so they move immediately with the cards -->
      <div class="flex justify-center gap-2 mt-6">
        <button
          v-for="(item, index) in announcements"
          :key="item.id"
          @click="setSlide(index)"
          class="h-3 rounded-full transition-all duration-300 ease-in-out"
          :class="index === displayIndex
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

/* Smooth fade transition on all translated text when language toggles */
.lang-fade {
  transition: opacity 0.35s ease;
}
</style>