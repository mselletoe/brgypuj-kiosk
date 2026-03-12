<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue"
import { useRouter } from "vue-router"
import { useSystemConfig } from "@/composables/useSystemConfig"
import { getActiveAnnouncements } from "@/api/announcementService"

const router = useRouter()
const { brgyName, brgySubname, resolvedLogoUrl } = useSystemConfig()

const current = ref(0)
const announcements = ref([])
const loading = ref(true)
const error = ref(null)
let autoSlide = null

const fetchAnnouncements = async () => {
  try {
    loading.value = true; error.value = null
    const data = await getActiveAnnouncements()
    announcements.value = data
    if (announcements.value.length > 0) startSlider()
  } catch (err) {
    console.error('Failed to fetch announcements:', err)
    error.value = 'Unable to load announcements. Please try again later.'
    setTimeout(fetchAnnouncements, 10000)
  } finally { loading.value = false }
}

const startSlider = () => {
  if (autoSlide) clearInterval(autoSlide)
  autoSlide = setInterval(() => nextSlide(), 5000)
}
const nextSlide = () => { if (announcements.value.length === 0) return; current.value = (current.value + 1) % announcements.value.length }
const prevSlide = () => { if (announcements.value.length === 0) return; current.value = (current.value - 1 + announcements.value.length) % announcements.value.length }

const formatDate = (date) => { if (!date) return ""; return new Date(date + 'T00:00:00').toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" }) }
const formatDay  = (date) => { if (!date) return ""; return new Date(date + 'T00:00:00').toLocaleDateString("en-US", { weekday: "long" }) }
const formatTime = (timeStr) => { if (!timeStr) return ""; const [h, m] = timeStr.split(":").map(Number); const period = h >= 12 ? "PM" : "AM"; const hour = h % 12 || 12; return `${hour}:${String(m).padStart(2, "0")} ${period}` }
const getImageUrl = (base64) => { if (!base64) return null; return `data:image/jpeg;base64,${base64}` }
const start = () => router.push("/login")

onMounted(() => {
  fetchAnnouncements()
  const pollInterval = setInterval(fetchAnnouncements, 300000)
  onBeforeUnmount(() => clearInterval(pollInterval))
})
onBeforeUnmount(() => { if (autoSlide) clearInterval(autoSlide) })
</script>

<template>
  <div class="h-screen w-full overflow-hidden cursor-pointer" @click.stop="start">
    <div v-if="loading" class="fixed inset-0 bg-gradient-to-br from-[#003d73] to-[#00325D] flex items-center justify-center z-50">
      <div class="text-center flex flex-col items-center">
        <div class="loader-dots mb-4"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
        <p class="text-white text-xl mt-4 opacity-90">{{ $t('loadingAnnouncements') }}</p>
      </div>
    </div>

    <div v-else-if="error" class="fixed inset-0 bg-gradient-to-br from-[#003d73] to-[#00325D] flex items-center justify-center z-50">
      <div class="text-center px-6">
        <svg class="w-20 h-20 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
        <h2 class="text-white text-3xl font-bold mb-2">{{ $t('connectionError') }}</h2>
        <p class="text-white text-xl opacity-90">{{ error }}</p>
        <p class="text-white text-sm mt-4 opacity-75">{{ $t('retrying') }}</p>
      </div>
    </div>

    <template v-else>
      <div class="fixed inset-0 pointer-events-none">
        <transition name="fade">
          <div v-if="announcements.length && announcements[current]?.image_base64" :key="current" class="fixed inset-0 bg-cover bg-center" :style="{ backgroundImage: `url('${getImageUrl(announcements[current].image_base64)}')` }"></div>
          <div v-else :key="'fallback-' + current" class="fixed inset-0 bg-gradient-to-br from-[#003d73] to-[#00325D]"></div>
        </transition>
        <div class="fixed inset-0 bg-[#00325D] opacity-70"></div>
      </div>

      <div class="relative z-10 h-full flex flex-col">
        <div class="flex items-center gap-4 p-6">
          <img v-if="resolvedLogoUrl" :src="resolvedLogoUrl" class="w-[90px] h-[90px] min-w-[90px] object-cover rounded-full" />
          <div>
            <h2 class="text-white text-[15px] font-bold leading-tight">{{ brgyName }}</h2>
            <p class="text-white text-[15px] opacity-90 -mt-1">{{ brgySubname }}</p>
            <h3 class="text-white text-[30px] font-bold leading-tight">{{ $t('brgyAnnouncements') }}</h3>
          </div>
        </div>

        <div class="flex-1 flex items-center px-20">
          <transition name="fade" mode="out-in">
            <div v-if="announcements.length" :key="current" class="max-w-[60%]">
              <h1 class="text-white font-extrabold text-[70px] tracking-tight leading-[1.05] drop-shadow-lg">{{ announcements[current]?.title }}</h1>
              <p v-if="announcements[current]?.description" class="text-white text-[20px] mt-3 opacity-90 leading-[1.4] max-w-[90%]">{{ announcements[current]?.description }}</p>
              <div class="mt-6 space-y-2">
                <p class="text-white text-[22px] opacity-95 leading-[1.3] flex items-center gap-3"><svg class="w-6 h-6 opacity-75 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clip-rule="evenodd" /></svg><span>{{ formatDate(announcements[current]?.event_date) }}, {{ formatDay(announcements[current]?.event_date) }}</span></p>
                <p v-if="announcements[current]?.event_time" class="text-white text-[22px] opacity-95 leading-[1.3] flex items-center gap-3"><svg class="w-6 h-6 opacity-75 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd" /></svg><span>{{ formatTime(announcements[current]?.event_time) }}</span></p>
                <p class="text-white text-[22px] opacity-95 leading-[1.3] flex items-center gap-3"><svg class="w-6 h-6 opacity-75 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" /></svg><span>{{ announcements[current]?.location }}</span></p>
              </div>
            </div>
            <div v-else key="no-announcements">
              <h1 class="text-white font-extrabold text-[60px] tracking-tight leading-[1.05] drop-shadow-lg">{{ $t('noAnnouncements') }}</h1>
              <p class="text-white text-[22px] mt-4 opacity-95 leading-[1.3]">{{ $t('checkBackLater') }}</p>
            </div>
          </transition>
        </div>

        <div class="flex items-center justify-between px-6 pb-10">
          <button v-if="announcements.length > 1" @click.stop.prevent="prevSlide" class="text-white transition-all duration-300 hover:scale-110 hover:opacity-100 opacity-70"><svg class="w-16 h-16" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" /></svg></button>
          <div v-else class="w-16"></div>

          <div class="flex flex-col items-center gap-4 flex-1">
            <div v-if="announcements.length > 1" class="flex justify-center gap-3">
              <span v-for="(a, i) in announcements" :key="a.id" class="w-3 h-3 rounded-full bg-white transition-all duration-300 cursor-pointer hover:opacity-100 hover:scale-125" :class="i === current ? 'opacity-100 scale-110' : 'opacity-40'" @click.stop="current = i"></span>
            </div>
            <p class="text-white text-xl opacity-90 pointer-events-none animate-pulse">{{ $t('touchScreen') }}</p>
          </div>

          <button v-if="announcements.length > 1" @click.stop.prevent="nextSlide" class="text-white transition-all duration-300 hover:scale-110 hover:opacity-100 opacity-70"><svg class="w-16 h-16" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" /></svg></button>
          <div v-else class="w-16"></div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.8s ease-in-out; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.loader-dots { display: flex; justify-content: space-around; align-items: center; width: 60px; height: 15px; margin: 0 auto; }
.dot { width: 12px; height: 12px; background-color: #ffffff; border-radius: 50%; animation: pulse 1.4s infinite ease-in-out both; }
.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }
@keyframes pulse { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
</style>