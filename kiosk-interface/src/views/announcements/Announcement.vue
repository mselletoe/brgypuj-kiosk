<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useSystemConfig } from '@/composables/useSystemConfig'
import ArrowBackButton from '@/components/shared/ArrowBackButton.vue'
import { getActiveAnnouncements } from '@/api/announcementService'

const router = useRouter()
const { locale, t } = useI18n()
const { brgyName, brgySubname, resolvedLogoUrl } = useSystemConfig()

const announcements = ref([])
const loading = ref(true)
const error = ref(null)
const goBack = () => router.push('/home')

const isFilipino = computed(() => locale.value === 'tl')

const toggleLang = () => {
  locale.value = locale.value === 'tl' ? 'en' : 'tl'
  localStorage.setItem('lang', locale.value)
}

const getImageUrl = (base64) => { if (!base64) return null; return `data:image/jpeg;base64,${base64}` }
const formatDate = (date) => { if (!date) return ''; return new Date(date + 'T00:00:00').toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) }
const formatDay  = (date) => { if (!date) return ''; return new Date(date + 'T00:00:00').toLocaleDateString('en-US', { weekday: 'long' }) }
const formatTime = (timeStr) => { if (!timeStr) return ''; const [h, m] = timeStr.split(':').map(Number); const period = h >= 12 ? 'PM' : 'AM'; const hour = h % 12 || 12; return `${hour}:${String(m).padStart(2, '0')} ${period}` }

const fetchAnnouncements = async () => {
  try {
    loading.value = true; error.value = null
    announcements.value = await getActiveAnnouncements()
  } catch (err) {
    console.error('Failed to fetch announcements:', err)
    error.value = true
    setTimeout(fetchAnnouncements, 10000)
  } finally { loading.value = false }
}

let pollInterval = null
onMounted(() => { fetchAnnouncements(); pollInterval = setInterval(fetchAnnouncements, 300000) })
onBeforeUnmount(() => { if (pollInterval) clearInterval(pollInterval) })

const activeIndex = ref(0)
const displayIndex = ref(0)
const isAnimating = ref(false)
const translateX = ref(0)
const CARD_W = 420
const GAP = 32
const CARD_SLOT = CARD_W + GAP

const windowItems = computed(() => {
  const total = announcements.value.length
  if (total === 0) return []
  return [-2, -1, 0, 1, 2].map(offset => {
    const idx = (activeIndex.value + offset + total) % total
    return { ...announcements.value[idx], _offset: offset }
  })
})

const animateTo = (direction) => {
  if (isAnimating.value) return
  isAnimating.value = true
  translateX.value = -direction * CARD_SLOT
  displayIndex.value = (displayIndex.value + direction + announcements.value.length) % announcements.value.length
  setTimeout(() => {
    activeIndex.value = (activeIndex.value + direction + announcements.value.length) % announcements.value.length
    translateX.value = 0
    isAnimating.value = false
  }, 450)
}

const nextSlide = () => animateTo(1)
const prevSlide = () => animateTo(-1)
const setSlide = (index) => { if (isAnimating.value || index === displayIndex.value) return; animateTo(index > displayIndex.value ? 1 : -1) }
</script>

<template>
  <div class="announcement-page w-full min-h-screen px-10 py-6 flex flex-col">

    <header class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4 text-[#013C6D]">
        <img v-if="resolvedLogoUrl" :src="resolvedLogoUrl" class="w-[60px] h-[60px] min-w-[60px] object-cover rounded-full" />
        <div>
          <h1 class="text-[18px] font-extrabold">{{ brgyName }}</h1>
          <p class="text-[16px] opacity-90 -mt-1">{{ brgySubname }}</p>
        </div>
      </div>

      <div class="flex items-center gap-5">
        <div
          @click="toggleLang"
          class="w-36 h-12 bg-[#49759B] rounded-2xl flex cursor-pointer p-1"
          style="position: relative;"
        >
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
              transform: !isFilipino ? 'translateX(calc(100% + 0px))' : 'translateX(0px)'
            }"
          ></div>
          <div
            class="flex-1 flex items-center justify-center font-bold rounded-xl"
            style="position: relative; z-index: 1; transition: color 0.3s ease;"
            :style="{ color: isFilipino ? '#49759B' : 'white' }"
          >
            FIL
          </div>
          <div
            class="flex-1 flex items-center justify-center font-bold rounded-xl"
            style="position: relative; z-index: 1; transition: color 0.3s ease;"
            :style="{ color: !isFilipino ? '#49759B' : 'white' }"
          >
            ENG
          </div>
        </div>
      </div>
    </header>

    <main class="flex flex-col flex-1">
      <div class="flex items-center justify-between mb-6">
        <ArrowBackButton @click="goBack" />
        <h1 class="text-[45px] font-bold text-center leading-[0.95] bg-gradient-to-r from-[#03335C] to-[#3291E3] bg-clip-text text-transparent">
          {{ t('brgyAnnouncements') }}
        </h1>
        <div style="visibility: hidden; pointer-events: none;"><ArrowBackButton /></div>
      </div>

      <div v-if="loading" class="flex-1 flex items-center justify-center">
        <div class="text-center flex flex-col items-center">
          <div class="loader-dots mb-4"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
          <p class="text-[#03335C] text-lg font-semibold">{{ t('loadingAnnouncements') }}</p>
        </div>
      </div>

      <div v-else-if="error" class="flex-1 flex items-center justify-center">
        <div class="text-center px-6">
          <svg class="w-16 h-16 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          <h2 class="text-[#03335C] text-2xl font-bold mb-2">{{ t('connectionError') }}</h2>
          <p class="text-[#03335C] text-lg opacity-80">{{ t('unableToLoad') }}</p>
          <p class="text-[#03335C] text-sm mt-3 opacity-60">{{ t('retrying') }}</p>
        </div>
      </div>

      <div v-else-if="announcements.length === 0" class="flex-1 flex items-center justify-center">
        <div class="text-center">
          <p class="text-[#03335C] text-2xl font-semibold opacity-70">{{ t('noAnnouncementsAvailable') }}</p>
          <p class="text-[#03335C] text-base mt-2 opacity-50">{{ t('checkBackLater') }}</p>
        </div>
      </div>

      <template v-else>
        <div class="flex flex-1 items-center justify-center gap-4">
          <button v-if="announcements.length > 1" @click.stop.prevent="prevSlide" class="text-[#03335C] transition-opacity duration-300 hover:opacity-100 opacity-70 flex-shrink-0">
            <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>
          </button>

          <div class="flex-1 overflow-hidden" style="mask-image: linear-gradient(to right, transparent 0%, black 15%, black 85%, transparent 100%); -webkit-mask-image: linear-gradient(to right, transparent 0%, black 15%, black 85%, transparent 100%);">
            <div class="flex items-center justify-center">
              <div class="flex flex-shrink-0" :style="{ gap: `${GAP}px`, transform: `translateX(${translateX}px)`, transition: isAnimating ? 'transform 0.45s cubic-bezier(0.25, 0.46, 0.45, 0.94)' : 'none' }">
                <div
                  v-for="item in windowItems"
                  :key="`${item.id}-${item._offset}`"
                  class="h-[300px] flex-shrink-0 text-white rounded-3xl overflow-hidden"
                  :style="{ width: `${CARD_W}px`, backgroundImage: item.image_base64 ? `url(${getImageUrl(item.image_base64)})` : 'none', backgroundColor: item.image_base64 ? undefined : '#03335C', backgroundSize: 'cover', backgroundPosition: 'center', position: 'relative' }"
                >
                  <div class="h-full w-full flex flex-col items-center justify-center text-center px-10" style="background: rgba(3, 51, 92, 0.75);">
                    <h2 class="text-[34px] font-extrabold leading-tight mb-3">{{ item.title }}</h2>
                    <p v-if="item.event_date" class="text-[16px]">{{ formatDate(item.event_date) }}, {{ formatDay(item.event_date) }}</p>
                    <p v-if="item.location" class="text-[16px]">{{ item.location }}</p>
                    <p v-if="item.event_time" class="text-[16px]">{{ formatTime(item.event_time) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <button v-if="announcements.length > 1" @click.stop.prevent="nextSlide" class="text-[#03335C] transition-opacity duration-300 hover:opacity-100 opacity-70 flex-shrink-0">
            <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" /></svg>
          </button>
        </div>

        <div class="flex justify-center gap-2 mt-6">
          <button
            v-for="(item, index) in announcements"
            :key="item.id"
            @click="setSlide(index)"
            class="h-3 rounded-full transition-all duration-300 ease-in-out"
            :class="index === displayIndex ? 'bg-[#1B5886] w-7' : 'border-[#1B5886] w-3 border-[2px]'"
          />
        </div>
      </template>
    </main>
  </div>
</template>

<style scoped>
.announcement-page { background: radial-gradient(circle at top left, #3291E3 0%, #ffffff 44%); }
.loader-dots { display: flex; justify-content: space-around; align-items: center; width: 60px; height: 15px; }
.dot { width: 12px; height: 12px; background-color: #03335C; border-radius: 50%; animation: pulse 1.4s infinite ease-in-out both; }
.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }
@keyframes pulse { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
</style>