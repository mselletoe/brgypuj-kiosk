<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: String, // 'document', 'equipment', or 'rfid'
  reference: String,
  title: String,
  rfidNo: String,
  createdAt: String,
  status: String // 'completed' or 'rejected'
})

const typeConfig = computed(() => {
  switch (props.type) {
    case 'document':  return { sideColor: '#2C67E7', iconBg: '#E4EEFF', iconColor: '#2C67E7' }
    case 'equipment': return { sideColor: '#F16C14', iconBg: '#FFF0E6', iconColor: '#F16C14' }
    case 'rfid':      return { sideColor: '#21C05C', iconBg: '#E2F9EC', iconColor: '#21C05C' }
    default:          return { sideColor: '#2C67E7', iconBg: '#E4EEFF', iconColor: '#2C67E7' }
  }
})

const sideColor = computed(() => typeConfig.value.sideColor)
const iconBg    = computed(() => typeConfig.value.iconBg)
const iconColor = computed(() => typeConfig.value.iconColor)

const statusBg   = computed(() => props.status === 'completed' ? '#16A34A' : '#EF4444')
const statusText = computed(() => props.status === 'completed' ? 'Completed' : 'Rejected')

const typeLabel = computed(() => {
  switch (props.type) {
    case 'document':  return 'Document Request'
    case 'equipment': return 'Equipment Request'
    case 'rfid':      return 'RFID Activity'
    default:          return ''
  }
})
</script>

<template>
  <div
    class="flex w-full rounded-2xl shadow-sm overflow-hidden"
    :style="{ border: `2.5px solid ${sideColor}` }"
  >
    <!-- LEFT COLOR STRIP -->
    <div class="w-2 flex-shrink-0" :style="{ backgroundColor: sideColor }"></div>

    <!-- MAIN CONTENT -->
    <div class="flex items-center justify-between w-full px-6 py-4">

      <!-- LEFT: Icon + Text -->
      <div class="flex items-center gap-5">

        <!-- ICON CIRCLE -->
        <div
          class="flex items-center justify-center w-14 h-14 rounded-full flex-shrink-0"
          :style="{ backgroundColor: iconBg }"
        >
          <!-- Document Icon -->
          <svg
            v-if="type === 'document'"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="w-7 h-7"
            :style="{ stroke: iconColor }"
          >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
            <line x1="10" y1="9" x2="8" y2="9" />
          </svg>

          <!-- Equipment / Box Icon -->
          <svg
            v-else-if="type === 'equipment'"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="w-7 h-7"
            :style="{ stroke: iconColor }"
          >
            <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
            <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
            <line x1="12" y1="22.08" x2="12" y2="12" />
          </svg>

          <!-- RFID / Signal Icon -->
          <svg
            v-else-if="type === 'rfid'"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="w-7 h-7"
            :style="{ stroke: iconColor }"
          >
            <path d="M5 12.55a11 11 0 0 1 14.08 0" />
            <path d="M1.42 9a16 16 0 0 1 21.16 0" />
            <path d="M8.53 16.11a6 6 0 0 1 6.95 0" />
            <circle cx="12" cy="20" r="1" :fill="iconColor" stroke="none" />
          </svg>
        </div>

        <!-- TEXT INFO -->
        <div class="flex flex-col gap-0.5">
          <span class="text-xs font-semibold uppercase tracking-wide" :style="{ color: sideColor }">
            {{ typeLabel }}
          </span>
          <h2 class="text-base font-bold text-[#003A6B] leading-tight">
            {{ reference }}
          </h2>
          <p class="text-sm text-[#003A6B] font-medium italic">
            {{ title }}
          </p>
          <!-- RFID No. shown on all card types -->
          <p v-if="rfidNo" class="text-xs text-gray-500 font-medium mt-0.5">
            RFID No.: <span class="font-semibold text-[#003A6B]">{{ rfidNo }}</span>
          </p>
        </div>
      </div>

      <!-- RIGHT: Date + Status -->
      <div class="flex items-center gap-8 flex-shrink-0">
        <p class="text-sm text-[#003A6B]">
          Created on: <span class="font-medium">{{ createdAt }}</span>
        </p>

        <div
          class="flex items-center justify-center px-5 py-1.5 rounded-full text-white text-sm font-semibold"
          :style="{ backgroundColor: statusBg }"
        >
          {{ statusText }}
        </div>
      </div>

    </div>
  </div>
</template>