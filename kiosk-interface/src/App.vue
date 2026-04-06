<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useAutoLogout } from '@/composables/useAutoLogout'
import { useSystemConfigStore } from '@/stores/systemConfig'
import { useWebSocket } from '@/composables/useWebSocket'
import { storeToRefs } from 'pinia'

useAutoLogout()

const { connect } = useWebSocket()
connect()

const store = useSystemConfigStore()
const { maintenanceMode, maintenanceMessage, brgyName } = storeToRefs(store)

store.fetchConfig()

let pollInterval = null
onMounted(() => {
  pollInterval = setInterval(() => store.pollConfig(), 30_000)
})
onUnmounted(() => {
  clearInterval(pollInterval)
})
</script>

<template>
  <!-- Maintenance wall -->
  <Transition name="maintenance-fade">
    <div
      v-if="maintenanceMode"
      class="fixed inset-0 z-[9999] flex flex-col items-center justify-center gap-6 bg-[#0f172a] text-white px-8 text-center"
    >
      <div class="flex items-center justify-center w-20 h-20 rounded-full bg-yellow-400/10 border border-yellow-400/30">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-10 h-10 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M11.42 15.17 17.25 21A2.652 2.652 0 0 0 21 17.25l-5.877-5.877M11.42 15.17l2.496-3.03c.317-.384.74-.626 1.208-.766M11.42 15.17l-4.655 5.653a2.548 2.548 0 1 1-3.586-3.586l5.654-4.654m5.879-4.252a3.5 3.5 0 0 0-4.95-4.95l-1.51 1.51" />
        </svg>
      </div>
      <p class="text-sm font-medium tracking-widest uppercase text-yellow-400/70">{{ brgyName }}</p>
      <h1 class="text-3xl font-bold tracking-tight">System Under Maintenance</h1>
      <p class="text-base text-slate-300 max-w-md leading-relaxed">{{ maintenanceMessage }}</p>
      <div class="flex items-center gap-2 mt-4 text-xs text-slate-500">
        <span class="w-1.5 h-1.5 rounded-full bg-yellow-400 animate-pulse" />
        Please approach the barangay staff for assistance.
      </div>
    </div>
  </Transition>

  <!-- Normal kiosk UI — KeepAlive caches pages so they don't remount on every navigation -->
  <router-view v-if="!maintenanceMode" v-slot="{ Component, route }">
    <KeepAlive :max="5" :exclude="['CameraPhase', 'ApplyID']">
      <component :is="Component" :key="route.path" />
    </KeepAlive>
  </router-view>
</template>

<style scoped>
.maintenance-fade-enter-active,
.maintenance-fade-leave-active {
  transition: opacity 0.4s ease;
}
.maintenance-fade-enter-from,
.maintenance-fade-leave-to {
  opacity: 0;
}
</style>